#!/usr/bin/env python3

import argparse
import logging
import re
import subprocess
import sys
from typing import Dict, List

import dns.resolver

logger = logging.getLogger(__name__)


def subprocess_run_wrapper(cmd: List[str], dry_run=False, *args, **kwargs):
    if dry_run:
        logger.info("DRY RUN: %s", ' '.join(cmd))
        return
    return subprocess.run(cmd, *args, **kwargs)


def run_firewalld(cmd: List[str], dry_run=False):
    try:
        s = subprocess_run_wrapper(
            ["firewall-cmd"] + cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            dry_run=dry_run,
        )
        if s is not None and s.returncode != 0:
            logger.error("firewalld failure:\nSTDOUT: %s\nSTDERR: %s", s.stdout, s.stderr)
    except Exception as e:
        logger.error("Unknown firewalld error: %s", str(e))


def get_new_addresses(domains: List[str]) -> List[Dict[str, str]]:
    ret = []
    for d in domains:
        for qtype in ('A', 'AAAA'):
            try:
                # EL8 ships with dnspython 1.15
                # Consider checking version and using resolve() for 2.0+
                answers = dns.resolver.query(d, qtype)
                for answer in answers:
                    ret.append({"type": qtype, "address": answer.address})
                    logger.debug("Found %s record '%s' for '%s'", qtype, answer.address, d)
            except dns.resolver.NoAnswer:
                logger.debug("No %s records found for '%s'", qtype, d)
                continue
            except Exception as e:
                logger.error("Unknown DNS error: %s", str(e))
    return ret


def update_firewalld(addresses: List[Dict[str, str]], zone: str, port: int, dry_run=False) -> List[str]:
    existing_raw_rules = subprocess.run(
        ["firewall-cmd", "--permanent", "--zone", zone, "--list-rich-rules"],
        check=True,
        universal_newlines=True,
        stdout=subprocess.PIPE,
    )
    existing_rules = existing_raw_rules.stdout.split('\n')
    new_rules = []
    changed = False
    # Generate new rules
    for addr in addresses:
        family = "ipv4" if addr['type'] == 'A' else "ipv6"
        new_rules.append(
            'rule family="{}" source address="{}" port port="{}" protocol="tcp" accept'.format(
                family, addr["address"], port
            )
        )
    # Add missing
    for rule in new_rules:
        if rule not in existing_rules:
            logger.info("Adding rule '%s'", rule)
            run_firewalld(["--permanent", "--zone", zone, "--add-rich-rule", rule], dry_run=dry_run)
            changed = True
    # Remove old
    re_rule = re.compile(r'^rule.*address=\"(.+?)\".*port=\"(\d+)\"\s+protocol=\"tcp\"\s+accept$')
    for rule in existing_rules:
        m = re_rule.match(rule)
        if not m:
            continue
        old_port = m.group(2)
        # Ignore different ports, assume it's from a different rule
        if str(port) != old_port:
            continue
        if rule not in new_rules:
            logger.info("Removing rule '%s'", rule)
            run_firewalld(["--permanent", "--zone", zone, "--remove-rich-rule", rule], dry_run=dry_run)

    if changed:
        logger.info("Reloading firewalld")
        run_firewalld(["--reload"], dry_run=dry_run)
    else:
        logger.info("No changes required")
    return changed


def parse_args():
    parser = argparse.ArgumentParser(description="Update firewall rules for acme-dns")
    parser.add_argument("domains", nargs='+', help="Domains to update")
    parser.add_argument("--firewall", default='firewalld', choices=['firewalld'], help="Firewall frontend to use")
    parser.add_argument("--port", type=int, default=443, help="Port to edit in firewall")
    parser.add_argument("--firewalld-zone", default='public', help="FirewallD zone to edit")
    parser.add_argument("--log-level", type=str.upper, choices=['CRITICAL', 'FATAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG'])
    parser.add_argument("--log-no-timestamp", action='store_true', help="Disable timestamps in logs")
    parser.add_argument("-n", "--dry-run", action='store_true', help="Don't make any changes")

    return parser.parse_args()


def main():
    args = parse_args()
    if args.log_no_timestamp:
        log_format = "%(levelname)s - %(message)s"
    else:
        log_format = "%(asctime)s - %(levelname)s - %(message)s"
    logging.basicConfig(
        level=max(logging.getLevelName(args.log_level), logging.INFO),
        format=log_format,
    )
    logger.setLevel(args.log_level)

    logger.debug("Managing port %d", args.port)
    logger.debug('Will check domains: %s', ', '.join(args.domains))

    addresses = get_new_addresses(args.domains)
    if not addresses:
        logging.error("Could not resolve any addresses")
        sys.exit(1)
    changed = False
    if args.firewall == "firewalld":
        logger.debug("Managing firewalld zone %s", args.firewalld_zone)
        changed = update_firewalld(addresses, args.firewalld_zone, args.port, dry_run=args.dry_run)
    if changed:
        sys.exit(100)
    sys.exit(0)


if __name__ == '__main__':
    main()

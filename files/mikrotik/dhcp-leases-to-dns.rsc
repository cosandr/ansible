# https://gist.githubusercontent.com/SmartFinn/acc7953eaeb43cece034/raw/5fa290c81f928d3c6929c432180664196c6e3f43/dhcp-leases-to-dns.rsc
# MikroTik (RouterOS) script for automatically setting DNS records
# for clients when they obtain a DHCP lease.
#
# author SmartFinn <https://gist.github.com/SmartFinn>

:local dnsTTL "00:15:00";
:local token "$leaseServerName-$leaseActMAC";

# Normalize hostname (e.g. "-= My Phone =-" -> "My-Phone")
# - truncate length to 63 chars
# - substitute disallowed chars with a hyphen
# param: name
:local normalizeHostname do={
  :local result;
  :local isInvalidChar true;
  :for i from=0 to=([:len $name]-1) do={
    :local char [:pick $name $i];
    :if ($i < 63) do={
      :if ($char~"[a-zA-Z0-9]") do={
        :set result ($result . $char);
        :set isInvalidChar false;
      } else={
        :if (!$isInvalidChar) do={
          :set result ($result . "-");
          :set isInvalidChar true;
        };
      };
    };
  };
# delete trailing hyphen
  :if ($isInvalidChar) do={
    :set result [:pick $result 0 ([:len $result]-1)];
  }
  :return $result;
};

:if ($leaseBound = 1) do={
# Getting the hostname and delete all disallowed chars from it
  :local hostName $"lease-hostname";
  :set hostName [$normalizeHostname name=$hostName];

# Use MAC address as a hostname if the hostname is missing or contains only
# disallowed chars
  :if ([:len $hostName] = 0) do={
    :set hostName [$normalizeHostname name=$leaseActMAC];
  };

# Getting the domain name from DHCP server. If a domain name is not
# specified will use hostname only
  /ip dhcp-server network {
    :local domainName [get [:pick [find $leaseActIP in address] 0] domain];
    :if ([:len $domainName] > 0) do={
#     Append domain name to the hostname
      :set hostName ($hostName . "." . $domainName);
    };
  };

  :do {
    /ip dns static {
      add name=$hostName address=$leaseActIP ttl=$dnsTTL comment=$token;
    };
  } on-error={
    :log error "Fail to add DNS entry: $hostname -> $leaseActIP ($leaseActMAC)";
  };
} else={
  /ip dns static remove [find comment=$token];
};

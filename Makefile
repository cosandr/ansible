.PHONY: git-hooks inventory

git-hooks:
	./git-init.sh

inventory:
	./playbooks/generate_inventory.yml -t network -D
	./playbooks/generate_inventory.yml -t hosts -D

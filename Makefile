VENV_NAME := $(shell cat .python-version)

.PHONY: git-hooks inventory

git-hooks:
	./git-init.sh

inventory:
	./playbooks/generate_inventory.yml -t network -D
	./playbooks/generate_inventory.yml -t hosts -D

venv:
	test -d ~/.pyenv/versions/${VENV_NAME} || pyenv virtualenv system ${VENV_NAME}
	~/.pyenv/versions/${VENV_NAME}/bin/pip install -U pip wheel setuptools
	~/.pyenv/versions/${VENV_NAME}/bin/pip install -U -r requirements-venv.txt
	~/.pyenv/versions/${VENV_NAME}/bin/pip install -U -r requirements.txt

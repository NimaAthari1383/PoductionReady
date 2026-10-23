#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

command -v ansible-playbook >/dev/null 2>&1 || {
  echo "ERROR: ansible-playbook is not installed on the controller."
  exit 1
}

ansible-galaxy collection install -r requirements.yml
ansible-playbook playbooks/site.yml --syntax-check

ARGS=()
[[ "${ASK_BECOME_PASS:-0}" == "1" ]] && ARGS+=(--ask-become-pass)
[[ -n "${LIMIT:-}" ]] && ARGS+=(--limit "$LIMIT")

ansible-playbook playbooks/site.yml "${ARGS[@]}"

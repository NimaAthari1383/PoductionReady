# ISC Kea DHCPv4 One-Click Ansible Deployment

Automates Ubuntu + ISC Kea 3.2 + PostgreSQL host reservations with validation and hardened generated credentials.

See `README_FA.md` for the Persian operating guide.

Run using this command:

```bash
LIMIT=it-tools-server-1 \
ASK_BECOME_PASS=1 \
./scripts/deploy.sh
```

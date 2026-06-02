# network-automation-scripts
Network automation scripts using Python, Ansible, and API integrations.
# Network Automation Scripts

Automation scripts for network engineering using Python, Ansible, and API integrations.

## 📁 Folder Structure

- **python/** - Python automation scripts
  - `device_backup.py` - Backup device configs

- **ansible/** - Ansible automation
  - `playbooks/` - Automation playbooks

- **api-integrations/** - API scripts
  - `netbox/` - NetBox IPAM/DCIM automation
  - `prtg/` - PRTG monitoring data

- **configs/** - Stored device configurations

## 🚀 Quick Start

```bash
git clone https://github.com/ProNetworkEngineer/network-automation-scripts.git
cd network-automation-scripts
pip install netmiko requests
python python/device_backup.py

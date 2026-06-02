#!/usr/bin/env python3
"""
Network Device Configuration Backup Script
Backs up configurations from routers, switches, firewalls
"""

import os
import datetime
from netmiko import ConnectHandler

# Device list
devices = [
    {
        'device_type': 'cisco_ios',
        'ip': '192.168.1.1',
        'username': 'admin',
        'password': 'password',
    },
]

backup_dir = '../configs/'
timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')

for device in devices:
    try:
        connection = ConnectHandler(**device)
        output = connection.send_command('show running-config')
        
        filename = f"{backup_dir}{device['ip']}_{timestamp}.cfg"
        with open(filename, 'w') as f:
            f.write(output)
            
        print(f"✅ Backed up {device['ip']}")
        connection.disconnect()
        
    except Exception as e:
        print(f"❌ Failed to backup {device['ip']}: {e}")

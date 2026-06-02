#!/usr/bin/env python3
"""
PRTG Network Monitor API Poller
Fetches sensor data, device status, and creates reports
"""

import requests
import json
import csv
import datetime
import os
from typing import Dict, List, Any

# PRTG Configuration
PRTG_URL = "https://your-prtg-server.com"
PRTG_USERNAME = "your-username"
PRTG_PASSHASH = "your-passhash"  # Get from Setup > Account Settings > Passhash
PRTG_API_KEY = "your-api-key"  # Alternative auth method

# Folder paths
REPORT_DIR = "../../configs/prtg_reports/"
os.makedirs(REPORT_DIR, exist_ok=True)

class PRTGPoller:
    def __init__(self, server_url, username=None, passhash=None, api_key=None):
        self.server_url = server_url.rstrip('/')
        self.username = username
        self.passhash = passhash
        self.api_key = api_key
        self.session = requests.Session()
        
    def _make_request(self, params: Dict) -> Dict:
        """Make API request to PRTG"""
        if self.api_key:
            params['apitoken'] = self.api_key
        else:
            params['username'] = self.username
            params['passhash'] = self.passhash
            
        params['output'] = 'json'
        
        try:
            response = self.session.get(
                f"{self.server_url}/api/table.json",
                params=params,
                verify=False  # Set to True in production
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"❌ API Request failed: {e}")
            return {}

    def get_all_sensors(self, sensor_id: int = 0) -> List[Dict]:
        """Get all sensors from PRTG"""
        params = {
            'content': 'sensors',
            'columns': 'objid,device,group,sensor,status,lastvalue,lastup,lastdown,message',
            'id': sensor_id if sensor_id else -1  # -1 = all objects
        }
        result = self._make_request(params)
        return result.get('sensors', [])

    def get_device_status(self) -> List[Dict]:
        """Get all devices and their status"""
        params = {
            'content': 'devices',
            'columns': 'objid,device,host,group,status,uptime,lastup,lastdown'
        }
        result = self._make_request(params)
        return result.get('devices', [])

    def get_sensor_history(self, sensor_id: int, hours: int = 24) -> List[Dict]:
        """Get historical data for a specific sensor"""
        params = {
            'content': 'historicdata',
            'id': sensor_id,
            'avg': 3600,  # Average over 1 hour
            'pct': 100,
            'sdate': f'datetime-{hours}h'
        }
        result = self._make_request(params)
        return result.get('histdata', [])

    def get_down_sensors(self) -> List[Dict]:
        """Get all sensors with 'Down' status"""
        all_sensors = self.get_all_sensors()
        down_sensors = []
        
        for sensor in all_sensors:
            if sensor.get('status') in ['Down', 'Warning', 'Unusual']:
                down_sensors.append({
                    'name': sensor.get('sensor'),
                    'device': sensor.get('device'),
                    'status': sensor.get('status'),
                    'message': sensor.get('message'),
                    'lastdown': sensor.get('lastdown')
                })
        return down_sensors

    def generate_report(self):
        """Generate a comprehensive report of PRTG status"""
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Get all data
        print("📊 Collecting PRTG data...")
        devices = self.get_device_status()
        sensors = self.get_all_sensors()
        down_sensors = self.get_down_sensors()
        
        # Save to JSON
        json_file = f"{REPORT_DIR}/prtg_report_{timestamp}.json"
        report_data = {
            'timestamp': timestamp,
            'total_devices': len(devices),
            'total_sensors': len(sensors),
            'down_sensors': down_sensors,
            'devices': devices,
            'sensors': sensors[:100]  # Limit to 100 for readability
        }
        
        with open(json_file, 'w') as f:
            json.dump(report_data, f, indent=2)
        print(f"✅ JSON report saved: {json_file}")
        
        # Generate CSV for down sensors
        if down_sensors:
            csv_file = f"{REPORT_DIR}/down_sensors_{timestamp}.csv"
            with open(csv_file, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=['device', 'name', 'status', 'message', 'lastdown'])
                writer.writeheader()
                writer.writerows(down_sensors)
            print(f"✅ CSV report saved: {csv_file}")
        
        # Print summary
        print("\n📈 PRTG SUMMARY")
        print(f"   Total Devices: {len(devices)}")
        print(f"   Total Sensors: {len(sensors)}")
        print(f"   ⚠️  Down/Warning Sensors: {len(down_sensors)}")
        
        for ds in down_sensors[:5]:  # Show first 5
            print(f"   - {ds['device']}/{ds['name']}: {ds['status']}")
        
        return report_data

def main():
    # Initialize PRTG poller
    poller = PRTGPoller(
        server_url=PRTG_URL,
        username=PRTG_USERNAME,
        passhash=PRTG_PASSHASH
        # api_key=PRTG_API_KEY  # Alternative auth
    )
    
    # Get down sensors
    print("🔍 Checking for down sensors...")
    down = poller.get_down_sensors()
    
    if down:
        print(f"\n⚠️  Found {len(down)} sensors with issues:")
        for sensor in down[:10]:
            print(f"   - {sensor['device']} - {sensor['name']}: {sensor['status']}")
    else:
        print("✅ All sensors are healthy!")
    
    # Generate full report
    poller.generate_report()

if __name__ == "__main__":
    main()

# Backup of overwritten tkinter __init__.py
# This file was copied from your Python installation's tkinter package
# It appears to contain your ForenX application code and was accidentally
# placed in the standard library location. Keep this backup safe.

#!/usr/bin/env python3
"""
ForenX AI - Complete Digital Forensics Tool
Features: Evidence Collector, Browser History, USB/Disk Analysis, Deleted File Recovery
"""

import os
import sys
import json
import sqlite3
import shutil
import hashlib
import platform
import datetime
import subprocess
import threading
import winreg
from pathlib import Path
from tkinter import *
from tkinter import ttk, scrolledtext, filedialog, messagebox
import webbrowser

class ForensicEngine:
    def __init__(self, output_dir, log_callback):
        self.output_dir = output_dir
        self.log = log_callback
        self.data = {}
        
    def collect_evidence_from_drive(self, drive_path, deep_scan=False):
        """Collect evidence from any drive with deep analysis"""
        self.log(f"Scanning drive: {drive_path}", "info")
        evidence = {
            'files': [],
            'deleted_files': [],
            'metadata': {},
            'total_size': 0,
            'file_count': 0
        }
        
        try:
            drive = Path(drive_path)
            if not drive.exists():
                self.log(f"Drive not found: {drive_path}", "error")
                return evidence
                
            # Get drive info
            if platform.system() == "Windows":
                try:
                    result = subprocess.run(
                        f'wmic logicaldisk where deviceid="{drive_path}" get size,freespace,volumename',
                        shell=True, capture_output=True, text=True, timeout=10
                    )
                    evidence['metadata']['drive_info'] = result.stdout
                except:
                    pass
                    
            # Scan for files
            extensions = {
                'Documents': ['.pdf', '.doc', '.docx', '.txt', '.rtf', '.odt'],
                'Spreadsheets': ['.xls', '.xlsx', '.csv'],
                'Images': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff'],
                'Archives': ['.zip', '.rar', '.7z', '.tar', '.gz'],
                'Executables': ['.exe', '.msi', '.bat', '.cmd', '.ps1'],
                'Databases': ['.db', '.sqlite', '.mdb', '.accdb'],
                'Emails': ['.pst', '.ost', '.msg', '.eml'],
                'Logs': ['.log', '.evtx', '.txt']
            }
            
            file_count = 0
            for category, exts in extensions.items():
                for ext in exts:
                    try:
                        for file in drive.rglob(f"*{ext}"):
                            if file_count > 500 and not deep_scan:
                                break
                            try:
                                stat = file.stat()
                                file_info = {
                                    'name': file.name,
                                    'path': str(file),
                                    'size': stat.st_size,
                                    'size_mb': round(stat.st_size / (1024*1024), 2),
                                    'created': datetime.datetime.fromtimestamp(stat.st_ctime).strftime('%Y-%m-%d %H:%M:%S'),
                                    'modified': datetime.datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
                                    'accessed': datetime.datetime.fromtimestamp(stat.st_atime).strftime('%Y-%m-%d %H:%M:%S'),
                                    'category': category,
                                    'hash': self.calculate_hash(file)[:16] + "..."
                                }
                                evidence['files'].append(file_info)
                                evidence['total_size'] += stat.st_size
                                file_count += 1
                            except Exception as e:
                                pass
                    except:
                        pass
                        
            evidence['file_count'] = file_count
            evidence['total_size_mb'] = round(evidence['total_size'] / (1024*1024), 2)
            
            # Scan for deleted files (using native Windows API via cmd)
            if deep_scan and platform.system() == "Windows":
                self.log("Performing deep scan for deleted files...", "warning")
                evidence['deleted_files'] = self.scan_deleted_files(drive_path)
                
            self.log(f"Found {file_count} files ({evidence['total_size_mb']} MB)", "success")
            
        except Exception as e:
            self.log(f"Error scanning drive: {e}", "error")
            
        return evidence
        
    def scan_deleted_files(self, drive_path):
        """Attempt to recover deleted file information"""
        deleted = []
        try:
            # Use Windows native commands to find deleted files
            drive_letter = drive_path[0]
            
            # Try to use chkdsk to find orphaned files
            result = subprocess.run(
                f'chkdsk {drive_letter}: /scan /perf',
                shell=True, capture_output=True, text=True, timeout=60
            )
            
            for line in result.stdout.split('\n'):
                if 'orphaned' in line.lower() or 'deleted' in line.lower():
                    deleted.append({
                        'info': line.strip(),
                        'status': 'Potential deleted file',
                        'recoverable': True
                    })
                    
            # Check recycle bin
            recycle_path = f"{drive_letter}:\\$Recycle.Bin"
            if os.path.exists(recycle_path):
                for item in os.listdir(recycle_path):
                    deleted.append({
                        'name': item,
                        'path': os.path.join(recycle_path, item),
                        'status': 'In Recycle Bin',
                        'recoverable': True
                    })
                    
        except Exception as e:
            self.log(f"Deleted file scan error: {e}", "error")
            
        return deleted
        
    def calculate_hash(self, filepath):
        """Calculate SHA256 hash of file"""
        sha256 = hashlib.sha256()
        try:
            with open(filepath, 'rb') as f:
                for block in iter(lambda: f.read(4096), b''):
                    sha256.update(block)
            return sha256.hexdigest()
        except:
            return "N/A"
            
    def analyze_browsers(self):
        """Extract browser history"""
        browsers = {}
        
        # Chrome
        chrome_path = os.path.expanduser("~\\AppData\\Local\\Google\\Chrome\\User Data\\Default\\History")
        if os.path.exists(chrome_path):
            try:
                temp_db = Path(self.output_dir) / "chrome_temp.db"
                shutil.copy2(chrome_path, temp_db)
                conn = sqlite3.connect(temp_db)
                cursor = conn.cursor()
                cursor.execute("SELECT url, title, visit_count, last_visit_time FROM urls ORDER BY visit_count DESC LIMIT 100")
                history = []
                for row in cursor.fetchall():
                    history.append({
                        'url': row[0][:100] if row[0] else 'N/A',
                        'title': row[1][:80] if row[1] else 'No Title',
                        'visits': row[2],
                        'last_visit': str(row[3]) if row[3] else 'N/A'
                    })
                browsers['Chrome'] = history
                conn.close()
                temp_db.unlink()
                self.log(f"Chrome: {len(history)} entries", "success")
            except Exception as e:
                self.log(f"Chrome error: {e}", "error")
                
        # Firefox
        ff_path = os.path.expanduser("~\\AppData\\Roaming\\Mozilla\\Firefox\\Profiles")
        if os.path.exists(ff_path):
            for profile in Path(ff_path).glob("*.default"):
                places = profile / "places.sqlite"
                if places.exists():
                    try:
                        temp_db = Path(self.output_dir) / "ff_temp.db"
                        shutil.copy2(places, temp_db)
                        conn = sqlite3.connect(temp_db)
                        cursor = conn.cursor()
                        cursor.execute("SELECT url, title, visit_count FROM moz_places ORDER BY visit_count DESC LIMIT 100")
                        history = []
                        for row in cursor.fetchall():
                            history.append({
                                'url': row[0][:100] if row[0] else 'N/A',
                                'title': row[1][:80] if row[1] else 'No Title',
                                'visits': row[2]
                            })
                        browsers['Firefox'] = history
                        conn.close()
                        temp_db.unlink()
                        self.log(f"Firefox: {len(history)} entries", "success")
                    except Exception as e:
                        self.log(f"Firefox error: {e}", "error")
                        
        return browsers
        
    def analyze_usb(self):
        """Analyze USB devices"""
        devices = []
        try:
            result = subprocess.run(
                'reg query "HKLM\\SYSTEM\\CurrentControlSet\\Enum\\USBSTOR" /s',
                shell=True, capture_output=True, text=True, timeout=20
            )
            for line in result.stdout.split('\n'):
                if 'FriendlyName' in line:
                    name = line.split('REG_SZ')[-1].strip()
                    if name:
                        devices.append({
                            'name': name[:80],
                            'found_time': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        })
            self.log(f"Found {len(devices)} USB devices", "success")
        except Exception as e:
            self.log(f"USB error: {e}", "error")
        return devices
        
    def analyze_disks(self):
        """Analyze disk partitions"""
        disks = []
        try:
            result = subprocess.run(
                'wmic logicaldisk get deviceid,size,freespace,filesystem,volumename',
                shell=True, capture_output=True, text=True, timeout=10
            )
            for line in result.stdout.strip().split('\n')[1:]:
                if line.strip():
                    parts = line.split()
                    if len(parts) >= 2:
                        try:
                            size_gb = round(int(parts[1]) / (1024**3), 2) if parts[1].isdigit() else 0
                            free_gb = round(int(parts[2]) / (1024**3), 2) if len(parts) > 2 and parts[2].isdigit() else 0
                            used_gb = round(size_gb - free_gb, 2)
                            disks.append({
                                'drive': parts[0],
                                'filesystem': parts[3] if len(parts) > 3 else 'Unknown',
                                'volume_name': parts[4] if len(parts) > 4 else '',
                                'size_gb': size_gb,
                                'free_gb': free_gb,
                                'used_gb': used_gb,
                                'used_percent': round((used_gb / size_gb) * 100, 1) if size_gb > 0 else 0
                            })
                        except:
                            pass
            self.log(f"Found {len(disks)} disk partitions", "success")
        except Exception as e:
            self.log(f"Disk error: {e}", "error")
        return disks
        
    def generate_report(self, data, report_type="full"):
        """Generate forensic report"""
        report_path = Path(self.output_dir) / f"forensic_report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        full_data = {
            'timestamp': datetime.datetime.now().isoformat(),
            'system': platform.platform(),
            'hostname': platform.node(),
            'user': os.getlogin(),
            'report_type': report_type,
            'data': data
        }
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(full_data, f, indent=2, default=str)
            
        self.log(f"Report saved: {report_path}", "success")
        return str(report_path)

# End of backup

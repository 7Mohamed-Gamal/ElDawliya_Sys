#!/usr/bin/env python
"""
إنشاء نسخة احتياطية سريعة قبل إرجاع التطبيقات
===============================================
"""

import os
import shutil
import sqlite3
from pathlib import Path
from datetime import datetime

def create_backup():
    """إنشاء نسخة احتياطية سريعة"""
    base_dir = Path(__file__).parent.parent
    backup_dir = base_dir / 'backups'
    backup_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_name = f"pre_restore_backup_{timestamp}"
    backup_path = backup_dir / backup_name
    backup_path.mkdir(exist_ok=True)
    
    print(f"إنشاء نسخة احتياطية: {backup_name}")
    
    # نسخ قاعدة البيانات
    db_files = ['db.sqlite3', 'db_migration.sqlite3', 'db_migration_backup.sqlite3']
    for db_file in db_files:
        db_path = base_dir / db_file
        if db_path.exists():
            shutil.copy2(db_path, backup_path / db_file)
            print(f"تم نسخ: {db_file}")
    
    # نسخ ملف الإعدادات
    settings_file = base_dir / 'ElDawliya_sys' / 'settings' / 'base.py'
    if settings_file.exists():
        shutil.copy2(settings_file, backup_path / 'base_settings.py')
        print("تم نسخ ملف الإعدادات")
    
    # نسخ ملف requirements
    req_file = base_dir / 'requirements.txt'
    if req_file.exists():
        shutil.copy2(req_file, backup_path / 'requirements.txt')
        print("تم نسخ ملف المتطلبات")
    
    print(f"تم إنشاء النسخة الاحتياطية في: {backup_path}")
    return backup_path

if __name__ == '__main__':
    create_backup()
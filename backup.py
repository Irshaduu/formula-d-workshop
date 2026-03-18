"""
Formula D Workshop - Automatic Backup Script
Run this daily to backup your database safely!

Usage:
    python backup.py
"""

import os
import shutil
from datetime import datetime

def create_backup():
    """Create a backup of the database"""
    
    # Create backups folder if it doesn't exist
    if not os.path.exists('backups'):
        os.makedirs('backups')
        print("📁 Created 'backups' folder")
    
    # Generate backup filename with current date and time
    today = datetime.now().strftime('%Y-%m-%d_%H-%M')
    backup_name = f'backups/db_backup_{today}.sqlite3'
    
    # Check if database exists
    if not os.path.exists('db.sqlite3'):
        print("❌ Error: db.sqlite3 not found!")
        print("   Make sure you're in the project root directory")
        return False
    
    # Create backup
    try:
        shutil.copy('db.sqlite3', backup_name)
        file_size = os.path.getsize(backup_name) / 1024  # Convert to KB
        print(f"✅ Backup created: {backup_name}")
        print(f"📊 Size: {file_size:.2f} KB")
        
        # Clean up old backups (keep only last 7)
        cleanup_old_backups()
        
        return True
        
    except Exception as e:
        print(f"❌ Backup failed: {e}")
        return False

def cleanup_old_backups():
    """Keep only the last 7 backups, delete older ones"""
    
    # Get all backup files
    backups = sorted([
        f for f in os.listdir('backups') 
        if f.startswith('db_backup') and f.endswith('.sqlite3')
    ])
    
    # If more than 7 backups, delete the oldest ones
    if len(backups) > 7:
        print(f"\n🧹 Cleaning up old backups...")
        for old_backup in backups[:-7]:  # Keep last 7, delete rest
            os.remove(f'backups/{old_backup}')
            print(f"   🗑️  Deleted: {old_backup}")
        print(f"✅ Kept {len(backups[-7:])} most recent backups")
    else:
        print(f"✅ Currently have {len(backups)} backup(s)")

def list_backups():
    """Show all available backups"""
    
    if not os.path.exists('backups'):
        print("No backups found")
        return
    
    backups = sorted([
        f for f in os.listdir('backups') 
        if f.startswith('db_backup') and f.endswith('.sqlite3')
    ], reverse=True)
    
    if not backups:
        print("No backups found")
        return
    
    print("\n📋 Available Backups:")
    print("-" * 60)
    for i, backup in enumerate(backups, 1):
        size = os.path.getsize(f'backups/{backup}') / 1024
        # Extract date from filename
        date_part = backup.replace('db_backup_', '').replace('.sqlite3', '')
        print(f"{i}. {date_part} ({size:.2f} KB)")
    print("-" * 60)

if __name__ == "__main__":
    print("=" * 60)
    print("     FORMULA D WORKSHOP - DATABASE BACKUP")
    print("=" * 60)
    print()
    
    # Create backup
    success = create_backup()
    
    if success:
        print()
        # Show all available backups
        list_backups()
        print()
        print("💡 TIP: To restore a backup:")
        print("   1. Stop your Django server")
        print("   2. Copy the backup file:")
        print("      copy backups\\db_backup_YYYY-MM-DD_HH-MM.sqlite3 db.sqlite3")
        print("   3. Restart your server")
        print()
        print("💡 IMPORTANT: Run this backup script DAILY!")
    
    print()
    print("=" * 60)

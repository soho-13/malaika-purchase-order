import shutil
from pathlib import Path
import schedule
import time
import logging
import sys
import signal
import pandas as pd
from datetime import datetime

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    handlers=[
        logging.FileHandler('sync_log.txt'),
        logging.StreamHandler(sys.stdout)
    ]
)

def signal_handler(signum, frame):
    logging.info("Stopping sync service...")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)


def sync_files():
    try:
        local_file = Path('updated_order_list.csv')
        gdrive_file = Path('/Users/sophiehollerbach/Google Drive/My Drive/Malaika/updated_order_list.csv')
        
        if not local_file.exists() or not gdrive_file.exists():
            logging.error("One of the files is missing")
            return
            
        # Compare modification times
        local_mtime = local_file.stat().st_mtime
        gdrive_mtime = gdrive_file.stat().st_mtime
        
        if gdrive_mtime > local_mtime:
            # Google Sheet was modified more recently
            shutil.copy2(gdrive_file, local_file)
            logging.info("✅ Downloaded changes from Google Sheets")
        elif local_mtime > gdrive_mtime:
            # Local file was modified more recently
            shutil.copy2(local_file, gdrive_file)
            logging.info("✅ Uploaded changes to Google Sheets")
        else:
            logging.info("👍 Files are in sync")
            
    except Exception as e:
        logging.error(f"❌ Sync failed: {str(e)}")

# First sync immediately
sync_files()

# Then schedule future syncs
schedule.every(1).minutes.do(sync_files)

if __name__ == '__main__':
    logging.info("🚀 Two-way sync service started - Press Ctrl+C to stop")
    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        logging.info("👋 Sync service stopped by user")

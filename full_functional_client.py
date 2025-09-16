#!/usr/bin/env python3
"""
Fully functional client API example that demonstrates real operations:
1. Leeching Telegram files (specifically https://t.me/c/3021633087/50)
2. Getting status information
3. Managing downloads
4. Error handling and monitoring
"""

import time
import json
from bot_api_client import BotAPIClient

class TelegramLeecher:
    """Complete client for Telegram file operations"""
    
    def __init__(self, base_url: str, api_secret: str, user_id: str, chat_id: str):
        """
        Initialize the Telegram Leecher
        
        Args:
            base_url (str): Base URL of the bot API
            api_secret (str): Shared secret key for HMAC authentication
            user_id (str): User ID for executing commands
            chat_id (str): Chat ID for notifications
        """
        self.client = BotAPIClient(base_url, api_secret)
        self.user_id = user_id
        self.chat_id = chat_id
        
    def check_bot_health(self) -> dict:
        """
        Check if the bot is healthy and available
        
        Returns:
            dict: Health status information
        """
        try:
            status = self.client.get_status()
            return {
                "available": status.get('bot_available', False),
                "status": status.get('bot_status', 'unknown'),
                "active_downloads": status.get('active_downloads', 0),
                "timestamp": status.get('timestamp', 0)
            }
        except Exception as e:
            return {"available": False, "error": str(e)}
            
    def get_download_status(self) -> dict:
        """
        Get current download status
        
        Returns:
            dict: Download information
        """
        try:
            return self.client.get_downloads()
        except Exception as e:
            return {"error": f"Failed to get downloads: {e}"}
            
    def leech_telegram_file(self, file_url: str, custom_name: str = None) -> dict:
        """
        Leech a Telegram file with full functionality
        
        Args:
            file_url (str): Telegram file URL to leech
            custom_name (str, optional): Custom filename
            
        Returns:
            dict: Result of the leech operation
        """
        try:
            # Create the leech command
            if custom_name:
                command = f"/leech {file_url} -n {custom_name}"
            else:
                command = f"/leech {file_url}"
                
            print(f"Executing leech command: {command}")
            
            result = self.client.start_leech(
                command=command,
                user_id=self.user_id,
                chat_id=self.chat_id
            )
            
            return result
        except Exception as e:
            return {"error": f"Failed to start leech: {e}"}
            
    def leech_with_url_method(self, file_url: str, custom_name: str = None) -> dict:
        """
        Alternative method using URL parameter
        
        Args:
            file_url (str): Telegram file URL to leech
            custom_name (str, optional): Custom filename
            
        Returns:
            dict: Result of the leech operation
        """
        try:
            result = self.client.start_leech(
                url=file_url,
                custom_name=custom_name,
                user_id=self.user_id,
                chat_id=self.chat_id
            )
            
            return result
        except Exception as e:
            return {"error": f"Failed to start leech: {e}"}
            
    def monitor_download(self, task_id: str, max_wait_time: int = 300) -> dict:
        """
        Monitor a download task
        
        Args:
            task_id (str): Task ID to monitor
            max_wait_time (int): Maximum time to wait in seconds
            
        Returns:
            dict: Final status of the download
        """
        print(f"Monitoring download task: {task_id}")
        start_time = time.time()
        
        while time.time() - start_time < max_wait_time:
            try:
                downloads = self.get_download_status()
                
                if 'error' in downloads:
                    return {"status": "error", "message": downloads['error']}
                
                # Look for our specific task
                for download in downloads.get('downloads', []):
                    if str(download.get('task_id', '')) == task_id:
                        progress = download.get('progress', '0%')
                        speed = download.get('speed', '0 B/s')
                        status = download.get('status', 'unknown')
                        
                        print(f"  Progress: {progress} | Speed: {speed} | Status: {status}")
                        
                        if status.lower() in ['completed', 'finished', 'done']:
                            return {"status": "completed", "download": download}
                        elif status.lower() in ['error', 'failed']:
                            return {"status": "failed", "download": download}
                
                # If no active downloads, task might be completed
                if downloads.get('count', 0) == 0:
                    print("  No active downloads. Task may be completed.")
                    return {"status": "possibly_completed", "message": "No active downloads"}
                    
                time.sleep(10)  # Check every 10 seconds
                
            except Exception as e:
                print(f"  Error monitoring download: {e}")
                time.sleep(10)
        
        return {"status": "timeout", "message": f"Task did not complete within {max_wait_time} seconds"}

def main():
    """Main function demonstrating all functionality"""
    # Configuration
    BASE_URL = "http://139.162.28.139:7392"
    API_SECRET = "wzmlx_bot_api_secret_2025"  # Same as in bot/__main__.py
    USER_ID = "7859877609"  # Your user ID
    CHAT_ID = "-1002934661749"  # Your supergroup ID
    
    # Initialize the leecher
    leecher = TelegramLeecher(BASE_URL, API_SECRET, USER_ID, CHAT_ID)
    
    print("Telegram File Leecher - Full Functionality Demo")
    print("=" * 60)
    
    # 1. Check bot health
    print("\n1. Checking bot health...")
    health = leecher.check_bot_health()
    if health.get('available', False):
        print(f"   ✅ Bot is {health['status']} with {health['active_downloads']} active downloads")
    else:
        print(f"   ❌ Bot is not available: {health.get('error', 'Unknown error')}")
        return
    
    # 2. Get current downloads
    print("\n2. Checking current downloads...")
    downloads = leecher.get_download_status()
    if 'error' in downloads:
        print(f"   Error: {downloads['error']}")
    else:
        count = downloads.get('count', 0)
        if count > 0:
            print(f"   Found {count} active download(s):")
            for i, download in enumerate(downloads.get('downloads', []), 1):
                name = download.get('name', 'Unknown')
                progress = download.get('progress', '0%')
                print(f"     {i}. {name} - {progress}")
        else:
            print("   No active downloads")
    
    # 3. Leech the specific Telegram file requested by user
    print("\n3. Leeching Telegram file: https://t.me/c/3021633087/50")
    file_url = "https://t.me/c/3021633087/50"
    
    # Method 1: Using full command
    print("   Using full command method...")
    result = leecher.leech_telegram_file(file_url, "requested_file.mp4")
    
    if 'error' in result:
        print(f"   Error: {result['error']}")
    else:
        task_id = result.get('task_id', 'unknown')
        print(f"   ✅ Leech task started successfully!")
        print(f"   Task ID: {task_id}")
        print(f"   Command: {result.get('telegram_command', 'N/A')}")
        
        # 4. Monitor the download for a short time
        print("\n4. Monitoring download progress (for 60 seconds)...")
        status = leecher.monitor_download(task_id, max_wait_time=60)
        print(f"   Monitoring result: {status.get('status', 'unknown')}")
    
    # 5. Demonstrate URL method as alternative
    print("\n5. Alternative method using URL parameter...")
    result2 = leecher.leech_with_url_method(file_url, "alt_method_file.mp4")
    
    if 'error' in result2:
        print(f"   Error: {result2['error']}")
    else:
        print(f"   ✅ Alternative leech method also successful!")
        print(f"   Task ID: {result2.get('task_id', 'unknown')}")
    
    # 6. Show API help
    print("\n6. Getting API documentation...")
    try:
        help_info = leecher.client.get_help()
        if 'error' in help_info:
            print(f"   Error getting help: {help_info['error']}")
        else:
            print(f"   API Version: {help_info.get('api_version', 'Unknown')}")
            print(f"   Available endpoints: {list(help_info.get('endpoints', {}).keys())}")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n" + "=" * 60)
    print("DEMO COMPLETED SUCCESSFULLY")
    print("=" * 60)
    print("\n💡 To use this in production:")
    print("   1. Update API_SECRET with your actual secret key")
    print("   2. Adjust USER_ID and CHAT_ID as needed")
    print("   3. Use leech_telegram_file() method for real operations")
    print("   4. Monitor downloads with get_download_status()")
    print("   5. Handle errors appropriately in your application")

if __name__ == "__main__":
    main()
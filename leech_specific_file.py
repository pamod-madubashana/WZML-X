#!/usr/bin/env python3
"""
Leech Specific File - Demonstration of leeching the specific Telegram file mentioned by the user
"""

from perfect_bot_api_client import PerfectBotAPIClient
import time

def leech_specific_file():
    # Configuration
    BASE_URL = "http://139.162.28.139:7392"
    API_SECRET = "wzmlx_bot_api_secret_2025"
    USER_ID = "7859877609"
    CHAT_ID = "-1002934661749"
    
    # File to leech (the specific one mentioned by the user)
    TELEGRAM_FILE_URL = "https://t.me/c/3021633087/50"
    
    print("🚀 Leeching Specific Telegram File")
    print("=" * 50)
    print(f"File URL: {TELEGRAM_FILE_URL}")
    print(f"User ID: {USER_ID}")
    print(f"Chat ID: {CHAT_ID}")
    print("=" * 50)
    
    # Initialize client
    client = PerfectBotAPIClient(BASE_URL, API_SECRET)
    
    # Check if API is available
    if not client.is_api_available():
        print("❌ API is not available!")
        return
    
    print(f"✅ API is available (Version: {client.get_api_version()})")
    
    # Get initial status
    print("\n📊 Initial Bot Status:")
    status = client.get_status()
    if status.get('status') == 'success':
        print(f"   Bot Status: {status.get('bot_status')}")
        print(f"   Active Downloads: {status.get('active_downloads')}")
    
    # Get initial downloads
    print("\n📥 Current Downloads:")
    downloads = client.get_downloads()
    initial_count = downloads.get('count', 0)
    print(f"   Active Downloads: {initial_count}")
    
    # Submit leech task for the specific file
    print(f"\n⚡ Submitting Leech Task for: {TELEGRAM_FILE_URL}")
    result = client.start_leech(
        command=f"/leech {TELEGRAM_FILE_URL}",
        user_id=USER_ID,
        chat_id=CHAT_ID
    )
    
    if result.get('status') == 'success':
        task_id = result.get('task_id')
        print(f"   ✅ Leech task submitted successfully!")
        print(f"   Task ID: {task_id}")
        print(f"   Command: {result.get('telegram_command')}")
        print(f"   Auto Status Sent: {result.get('auto_status')}")
    else:
        print(f"   ❌ Failed to submit leech task: {result.get('error')}")
        return
    
    # Monitor the download progress
    print(f"\n🔍 Monitoring Download Progress:")
    print("   (Press Ctrl+C to stop monitoring, but the download will continue)")
    
    try:
        for i in range(30):  # Monitor for 5 minutes (30 * 10 seconds)
            time.sleep(10)  # Wait 10 seconds between checks
            
            downloads = client.get_downloads()
            if downloads.get('status') == 'success':
                current_downloads = downloads.get('downloads', [])
                
                # Find our specific download
                target_download = None
                for download in current_downloads:
                    if task_id.split('_')[-1] in str(download.get('task_id', '')):
                        target_download = download
                        break
                
                if target_download:
                    name = target_download.get('name', 'Unknown')
                    progress = target_download.get('progress', '0%')
                    speed = target_download.get('speed', '0 B/s')
                    eta = target_download.get('eta', 'Unknown')
                    status = target_download.get('status', 'Unknown')
                    
                    print(f"   📄 {name}")
                    print(f"      Progress: {progress}")
                    print(f"      Speed: {speed}")
                    print(f"      ETA: {eta}")
                    print(f"      Status: {status}")
                    print()
                else:
                    print("   ⚠️  Download not found in current downloads list")
                    print(f"   Active downloads: {downloads.get('count', 0)}")
                    print()
            else:
                print(f"   ❌ Error getting downloads: {downloads.get('error')}")
                break
            
            # Check if download is complete (100%)
            if target_download and target_download.get('progress') == '100.00%':
                print("   🎉 Download completed!")
                break
                
    except KeyboardInterrupt:
        print("\n   ⚠️  Monitoring stopped by user (download continues in background)")
    
    # Final status
    print("\n🏁 Final Status:")
    final_downloads = client.get_downloads()
    if final_downloads.get('status') == 'success':
        print(f"   Active Downloads: {final_downloads.get('count')}")
        for download in final_downloads.get('downloads', []):
            print(f"   📄 {download.get('name')}: {download.get('progress')}")
    
    print("\n✨ Leech process demonstration completed!")
    print("   The file will continue downloading in the background.")
    print("   Check the bot's Telegram chat for status updates.")

if __name__ == "__main__":
    leech_specific_file()
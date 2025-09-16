#!/usr/bin/env python3
"""
Leech Specific Telegram File - Focused example for leeching the exact file mentioned by the user
"""

from leech_client import LeechAPIClient
import time

def leech_specific_file():
    """Leech the specific Telegram file mentioned by the user"""
    # Configuration
    BASE_URL = "http://139.162.28.139:7392"
    API_SECRET = "wzmlx_bot_api_secret_2025"
    USER_ID = "7859877609"  # Pamod's user ID
    CHAT_ID = "-1002934661749"  # Supergroup ID
    
    # The specific file mentioned by the user
    TELEGRAM_FILE_URL = "https://t.me/c/3021633087/50"
    
    print("🎯 Leeching Specific Telegram File")
    print("=" * 50)
    print(f"File: {TELEGRAM_FILE_URL}")
    print(f"User: {USER_ID} (Pamod)")
    print(f"Chat: {CHAT_ID}")
    print("=" * 50)
    
    # Initialize client
    client = LeechAPIClient(BASE_URL, API_SECRET)
    
    # Verify bot is available
    if not client.is_bot_available():
        print("❌ Bot is not available!")
        return
    
    print("✅ Bot is online and ready")
    
    # Get initial status
    status = client.get_bot_status()
    print(f"📊 Initial Status: {status.get('bot_status')}")
    print(f"   Active Downloads: {status.get('active_downloads')}")
    
    # Submit leech task for the specific file
    print(f"\n⚡ Submitting leech task...")
    result = client.leech_telegram_file(
        telegram_url=TELEGRAM_FILE_URL,
        user_id=USER_ID,
        chat_id=CHAT_ID,
        custom_name="Kingdom_Return_of_the_Great_General_2024.mkv"
    )
    
    if result.get('status') == 'success':
        task_id = result.get('task_id')
        print("✅ Leech task submitted successfully!")
        print(f"   Task ID: {task_id}")
        print(f"   File will be named: Kingdom_Return_of_the_Great_General_2024.mkv")
    else:
        print(f"❌ Failed to submit leech task: {result.get('error')}")
        return
    
    # Monitor progress for 2 minutes
    print(f"\n🔍 Monitoring download progress:")
    print("   (This will run for 2 minutes, but the download continues in background)")
    
    try:
        for i in range(12):  # 12 * 10 seconds = 2 minutes
            time.sleep(10)
            
            # Get current downloads
            downloads = client.get_task_status()
            if downloads.get('status') == 'success':
                current_downloads = downloads.get('downloads', [])
                
                # Find our specific download
                our_download = None
                for download in current_downloads:
                    if download.get('name', '').startswith('Kingdom'):
                        our_download = download
                        break
                
                if our_download:
                    progress = our_download.get('progress', '0%')
                    speed = our_download.get('speed', '0 B/s')
                    eta = our_download.get('eta', 'Unknown')
                    print(f"   [{progress}] at {speed} (ETA: {eta})")
                else:
                    print("   ⚠️  Download not visible in current list")
            else:
                print(f"   ❌ Error checking downloads: {downloads.get('error')}")
                break
            
            # Check if download is complete
            if our_download and our_download.get('progress') == '100.00%':
                print("   🎉 Download completed!")
                break
                
    except KeyboardInterrupt:
        print("\n   ⚠️  Monitoring stopped by user")
    
    # Final status
    print(f"\n🏁 Final Status:")
    final_downloads = client.get_task_status()
    if final_downloads.get('status') == 'success':
        count = final_downloads.get('count', 0)
        print(f"   Active Downloads: {count}")
        for download in final_downloads.get('downloads', []):
            name = download.get('name', 'Unknown')
            progress = download.get('progress', '0%')
            print(f"   📄 {name}: {progress}")
    
    print(f"\n✨ Leech process completed!")
    print(f"   Check your Telegram chat for the downloaded file.")

if __name__ == "__main__":
    leech_specific_file()
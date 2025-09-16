#!/usr/bin/env python3
"""
Perfect Bot API Client - Fully functional client for the Telegram Mirror Bot API
This client provides comprehensive access to all bot API endpoints with proper error handling,
authentication, and real-world usage examples.
"""

import hmac
import hashlib
import json
import requests
from time import time
from typing import Dict, Any, Optional, Union
from dataclasses import dataclass
from urllib.parse import urljoin

@dataclass
class APITask:
    """Represents a task submitted to the bot API"""
    task_id: str
    command: str
    user_id: str
    chat_id: str
    timestamp: int
    status: str = "pending"

class PerfectBotAPIClient:
    """Perfect client for interacting with the Telegram Mirror Bot API"""
    
    def __init__(self, base_url: str, api_secret: str):
        """
        Initialize the Perfect Bot API Client
        
        Args:
            base_url (str): Base URL of the bot API (e.g., 'http://139.162.28.139:7392')
            api_secret (str): Shared secret key for HMAC authentication
        """
        self.base_url = base_url.rstrip('/')
        self.api_secret = api_secret
        self.session = requests.Session()
        self.session.headers.update({'Content-Type': 'application/json'})
        
    def _generate_signature(self, body: bytes) -> str:
        """
        Generate HMAC-SHA256 signature for API requests
        
        Args:
            body (bytes): Request body as bytes
            
        Returns:
            str: Hex digest of the HMAC signature
        """
        return hmac.new(
            self.api_secret.encode(),
            body,
            hashlib.sha256
        ).hexdigest()
        
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict:
        """
        Make authenticated request to the bot API
        
        Args:
            method (str): HTTP method (GET, POST, etc.)
            endpoint (str): API endpoint (e.g., '/api/status')
            data (dict, optional): Request data for POST requests
            
        Returns:
            dict: JSON response from the API
        """
        url = urljoin(self.base_url, endpoint)
        
        # Prepare headers
        headers = {
            'Content-Type': 'application/json'
        }
        
        # Handle request body and signature
        if data is not None:
            body = json.dumps(data, separators=(',', ':')).encode()
            headers['X-Bot-Signature'] = self._generate_signature(body)
            response = self.session.request(method, url, headers=headers, data=body)
        else:
            # For GET requests, body is empty
            headers['X-Bot-Signature'] = self._generate_signature(b'')
            response = self.session.request(method, url, headers=headers)
            
        try:
            return response.json()
        except json.JSONDecodeError:
            return {"error": f"Invalid JSON response: {response.text}", "status_code": response.status_code}
        
    def get_status(self) -> Dict:
        """
        Get bot status information
        
        Returns:
            dict: Bot status information
        """
        return self._make_request('GET', '/api/status')
        
    def get_downloads(self) -> Dict:
        """
        Get list of current downloads
        
        Returns:
            dict: Current downloads information
        """
        return self._make_request('GET', '/api/downloads')
        
    def start_mirror(self, url: str, user_id: Optional[str] = None, chat_id: Optional[str] = None) -> Dict:
        """
        Start a mirror task - REAL EXECUTION
        
        Args:
            url (str): URL to mirror
            user_id (str, optional): User ID for the task
            chat_id (str, optional): Chat ID for the task
            
        Returns:
            dict: Response from the API with task information
        """
        data = {"url": url}
        if user_id:
            data["user_id"] = user_id
        if chat_id:
            data["chat_id"] = chat_id
            
        return self._make_request('POST', '/api/mirror', data)
        
    def start_leech(self, command: Optional[str] = None, url: Optional[str] = None, 
                   custom_name: Optional[str] = None, user_id: Optional[str] = None, 
                   chat_id: Optional[str] = None) -> Dict:
        """
        Start a leech task - REAL EXECUTION with full command support
        
        Args:
            command (str, optional): Full leech command text (e.g., '/leech https://t.me/c/123456789/10')
            url (str, optional): URL to leech (legacy mode)
            custom_name (str, optional): Custom filename (with url)
            user_id (str, optional): User ID for the task
            chat_id (str, optional): Chat ID for the task
            
        Returns:
            dict: Response from the API with task information
        """
        data = {}
        
        if command:
            data["command"] = command
        elif url:
            data["url"] = url
            if custom_name:
                data["custom_name"] = custom_name
        else:
            return {"error": "Either 'command' or 'url' must be provided"}
            
        if user_id:
            data["user_id"] = user_id
        if chat_id:
            data["chat_id"] = chat_id
            
        return self._make_request('POST', '/api/leech', data)
        
    def get_help(self) -> Dict:
        """
        Get API documentation
        
        Returns:
            dict: API documentation
        """
        # Help endpoint doesn't require authentication
        url = urljoin(self.base_url, '/api/help')
        response = self.session.get(url)
        try:
            return response.json()
        except json.JSONDecodeError:
            return {"error": f"Invalid JSON response: {response.text}", "status_code": response.status_code}
    
    def get_api_version(self) -> str:
        """
        Get the API version
        
        Returns:
            str: API version string
        """
        help_info = self.get_help()
        return help_info.get('api_version', 'Unknown')
    
    def is_api_available(self) -> bool:
        """
        Check if the API is available and responding
        
        Returns:
            bool: True if API is available, False otherwise
        """
        try:
            response = self.get_status()
            return response.get('status') == 'success'
        except:
            return False


class BotTaskManager:
    """Manager for tracking and monitoring bot tasks"""
    
    def __init__(self, client: PerfectBotAPIClient):
        self.client = client
        self.tasks: Dict[str, APITask] = {}
        
    def submit_leech_task(self, command: str, user_id: str, chat_id: str) -> Optional[APITask]:
        """
        Submit a leech task and track it
        
        Args:
            command (str): Full leech command
            user_id (str): User ID
            chat_id (str): Chat ID
            
        Returns:
            APITask: Task object or None if submission failed
        """
        response = self.client.start_leech(
            command=command,
            user_id=user_id,
            chat_id=chat_id
        )
        
        if response.get('status') == 'success':
            task = APITask(
                task_id=response['task_id'],
                command=command,
                user_id=user_id,
                chat_id=chat_id,
                timestamp=response['timestamp'],
                status='submitted'
            )
            self.tasks[task.task_id] = task
            return task
        else:
            print(f"Failed to submit task: {response.get('error', 'Unknown error')}")
            return None
            
    def submit_mirror_task(self, url: str, user_id: str, chat_id: str) -> Optional[APITask]:
        """
        Submit a mirror task and track it
        
        Args:
            url (str): URL to mirror
            user_id (str): User ID
            chat_id (str): Chat ID
            
        Returns:
            APITask: Task object or None if submission failed
        """
        response = self.client.start_mirror(
            url=url,
            user_id=user_id,
            chat_id=chat_id
        )
        
        if response.get('status') == 'success':
            task = APITask(
                task_id=response['task_id'],
                command=f"/mirror {url}",
                user_id=user_id,
                chat_id=chat_id,
                timestamp=response['timestamp'],
                status='submitted'
            )
            self.tasks[task.task_id] = task
            return task
        else:
            print(f"Failed to submit task: {response.get('error', 'Unknown error')}")
            return None
    
    def get_active_downloads(self) -> Dict:
        """
        Get current active downloads
        
        Returns:
            dict: Downloads information
        """
        return self.client.get_downloads()
    
    def get_bot_status(self) -> Dict:
        """
        Get bot status
        
        Returns:
            dict: Bot status information
        """
        return self.client.get_status()


def demo_usage():
    """
    Demonstration of how to use the Perfect Bot API Client
    """
    # Configuration - Update these values as needed
    BASE_URL = "http://139.162.28.139:7392"
    API_SECRET = "wzmlx_bot_api_secret_2025"  # Same as in bot/__main__.py
    USER_ID = "7859877609"  # Your user ID
    CHAT_ID = "-1002934661749"  # Default chat ID used by the bot
    
    print("Initializing Perfect Bot API Client...")
    client = PerfectBotAPIClient(BASE_URL, API_SECRET)
    
    # Check if API is available
    if not client.is_api_available():
        print("❌ API is not available!")
        return
    
    print(f"✅ API is available (Version: {client.get_api_version()})")
    
    # Initialize task manager
    task_manager = BotTaskManager(client)
    
    print("\n" + "="*60)
    print("PERFECT BOT API CLIENT DEMO")
    print("="*60)
    
    # Demo 1: Get API Help
    print("\n1. Getting API Documentation:")
    try:
        help_info = client.get_help()
        print(f"   API Version: {help_info.get('api_version', 'Unknown')}")
        print(f"   Description: {help_info.get('description', 'N/A')}")
        endpoints = list(help_info.get('endpoints', {}).keys())
        print(f"   Available Endpoints: {', '.join(endpoints)}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Demo 2: Get Bot Status
    print("\n2. Checking Bot Status:")
    try:
        status = client.get_status()
        if "error" in status:
            print(f"   Error: {status['error']}")
        else:
            print(f"   Bot Status: {status.get('bot_status', 'Unknown')}")
            print(f"   Active Downloads: {status.get('active_downloads', 0)}")
            print(f"   Bot Available: {status.get('bot_available', False)}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Demo 3: Get Downloads
    print("\n3. Checking Current Downloads:")
    try:
        downloads = client.get_downloads()
        if "error" in downloads:
            print(f"   Error: {downloads['error']}")
        else:
            count = downloads.get('count', 0)
            print(f"   Active Downloads: {count}")
            if count > 0:
                for download in downloads.get('downloads', []):
                    print(f"     - {download.get('name', 'Unknown')}: {download.get('progress', '0%')}")
            else:
                print("     No active downloads")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Demo 4: Submit Mirror Task (Example)
    print("\n4. Submitting Mirror Task (Example):")
    try:
        result = client.start_mirror(
            url="https://example.com/file.zip",
            user_id=USER_ID,
            chat_id=CHAT_ID
        )
        if "error" in result:
            print(f"   Expected Error: {result['error']}")
        else:
            print(f"   ✅ Mirror Task Submitted Successfully")
            print(f"   Task ID: {result.get('task_id')}")
            print(f"   Command: {result.get('telegram_command')}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Demo 5: Submit Leech Task with Full Command
    print("\n5. Submitting Leech Task with Full Command:")
    try:
        result = client.start_leech(
            command="/leech https://t.me/c/3021633087/50",
            user_id=USER_ID,
            chat_id=CHAT_ID
        )
        if "error" in result:
            print(f"   Expected Error: {result['error']}")
        else:
            print(f"   ✅ Leech Task Submitted Successfully")
            print(f"   Task ID: {result.get('task_id')}")
            print(f"   Command: {result.get('telegram_command')}")
            print(f"   Auto Status: {result.get('auto_status')}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Demo 6: Submit Leech Task with URL (Legacy Mode)
    print("\n6. Submitting Leech Task with URL (Legacy Mode):")
    try:
        result = client.start_leech(
            url="https://example.com/file.zip",
            custom_name="MyFile.zip",
            user_id=USER_ID,
            chat_id=CHAT_ID
        )
        if "error" in result:
            print(f"   Expected Error: {result['error']}")
        else:
            print(f"   ✅ Leech Task Submitted Successfully")
            print(f"   Task ID: {result.get('task_id')}")
            print(f"   Command: {result.get('telegram_command')}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Demo 7: Using Task Manager
    print("\n7. Using Task Manager:")
    try:
        # Submit a task using the task manager
        task = task_manager.submit_leech_task(
            command="/leech https://t.me/c/3021633087/50",
            user_id=USER_ID,
            chat_id=CHAT_ID
        )
        
        if task:
            print(f"   Task Manager - Submitted Task: {task.task_id}")
            print(f"   Command: {task.command}")
            
            # Check active downloads through task manager
            downloads = task_manager.get_active_downloads()
            print(f"   Active Downloads Count: {downloads.get('count', 0)}")
            
            # Check bot status through task manager
            status = task_manager.get_bot_status()
            print(f"   Bot Status: {status.get('bot_status', 'Unknown')}")
        else:
            print("   Failed to submit task through task manager")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n" + "="*60)
    print("PERFECT BOT API CLIENT DEMO COMPLETED")
    print("="*60)


def advanced_usage_example():
    """
    Advanced usage example showing real-world scenarios
    """
    # Configuration
    BASE_URL = "http://139.162.28.139:7392"
    API_SECRET = "wzmlx_bot_api_secret_2025"
    USER_ID = "7859877609"
    CHAT_ID = "-1002934661749"
    
    # Initialize client
    client = PerfectBotAPIClient(BASE_URL, API_SECRET)
    
    print("Advanced Usage Examples:")
    print("-" * 30)
    
    # Example 1: Leech a Telegram file
    print("1. Leeching a Telegram file:")
    result = client.start_leech(
        command="/leech https://t.me/c/3021633087/50",
        user_id=USER_ID,
        chat_id=CHAT_ID
    )
    
    if result.get('status') == 'success':
        print(f"   ✅ Successfully submitted leech task")
        print(f"   Task ID: {result['task_id']}")
        print(f"   You can monitor progress with get_downloads()")
    else:
        print(f"   ❌ Failed: {result.get('error')}")
    
    # Example 2: Mirror a file
    print("\n2. Mirroring a file:")
    result = client.start_mirror(
        url="https://releases.ubuntu.com/22.04/ubuntu-22.04.3-desktop-amd64.iso",
        user_id=USER_ID,
        chat_id=CHAT_ID
    )
    
    if result.get('status') == 'success':
        print(f"   ✅ Successfully submitted mirror task")
        print(f"   Task ID: {result['task_id']}")
    else:
        print(f"   ❌ Failed: {result.get('error')}")
    
    # Example 3: Monitor downloads
    print("\n3. Monitoring active downloads:")
    downloads = client.get_downloads()
    
    if downloads.get('status') == 'success':
        count = downloads.get('count', 0)
        print(f"   Active downloads: {count}")
        
        for download in downloads.get('downloads', []):
            name = download.get('name', 'Unknown')
            progress = download.get('progress', '0%')
            speed = download.get('speed', '0 B/s')
            print(f"   - {name}: {progress} at {speed}")
    else:
        print(f"   ❌ Failed to get downloads: {downloads.get('error')}")


if __name__ == "__main__":
    # Run the demo
    demo_usage()
    
    print("\n" + "="*60)
    print("ADVANCED USAGE EXAMPLE")
    print("="*60)
    
    # Run advanced example
    advanced_usage_example()
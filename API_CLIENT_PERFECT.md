# Perfect Bot API Client

A fully functional and comprehensive API client for the Telegram Mirror Bot with complete authentication, error handling, and all available endpoints.

## Features

- **Complete API Coverage**: Supports all available bot API endpoints
- **HMAC-SHA256 Authentication**: Secure requests with signature verification
- **Real Task Execution**: Direct access to bot functions with real execution
- **Comprehensive Error Handling**: Proper error responses and debugging
- **Task Management**: Built-in task tracking and monitoring
- **Easy to Use**: Simple interface with clear documentation

## Available Endpoints

1. **GET /api/status** - Get bot status information
2. **GET /api/downloads** - Get list of current downloads
3. **POST /api/leech** - Start a leech task (REAL EXECUTION)
4. **POST /api/mirror** - Start a mirror task (REAL EXECUTION)
5. **GET /api/help** - Get API documentation

## Installation

No additional installation required. The client uses standard Python libraries:
- `requests`
- `hmac`
- `hashlib`
- `json`

## Usage Examples

### Basic Usage

```python
from perfect_bot_api_client import PerfectBotAPIClient

# Initialize client
client = PerfectBotAPIClient(
    base_url="http://139.162.28.139:7392",
    api_secret="wzmlx_bot_api_secret_2025"
)

# Check if API is available
if client.is_api_available():
    print(f"API Version: {client.get_api_version()}")

# Get bot status
status = client.get_status()
print(f"Bot Status: {status.get('bot_status')}")

# Get current downloads
downloads = client.get_downloads()
print(f"Active Downloads: {downloads.get('count')}")
```

### Leech a Telegram File

```python
# Leech a specific Telegram file
result = client.start_leech(
    command="/leech https://t.me/c/3021633087/50",
    user_id="7859877609",
    chat_id="-1002934661749"
)

if result.get('status') == 'success':
    print(f"Task submitted: {result.get('task_id')}")
else:
    print(f"Error: {result.get('error')}")
```

### Mirror a File

```python
# Mirror a file to cloud storage
result = client.start_mirror(
    url="https://example.com/largefile.zip",
    user_id="7859877609",
    chat_id="-1002934661749"
)

if result.get('status') == 'success':
    print(f"Mirror task submitted: {result.get('task_id')}")
```

### Using Task Manager

```python
from perfect_bot_api_client import BotTaskManager

# Initialize task manager
task_manager = BotTaskManager(client)

# Submit and track a leech task
task = task_manager.submit_leech_task(
    command="/leech https://t.me/c/3021633087/50",
    user_id="7859877609",
    chat_id="-1002934661749"
)

if task:
    print(f"Task {task.task_id} submitted successfully")
    
    # Monitor downloads
    downloads = task_manager.get_active_downloads()
    print(f"Active downloads: {downloads.get('count')}")
```

## Authentication

All requests (except `/api/help`) require HMAC-SHA256 authentication:

1. Create a signature by hashing the request body with the API secret
2. Add the signature to the `X-Bot-Signature` header
3. Set `Content-Type: application/json`

The client handles this automatically.

## Response Format

All API responses follow a consistent format:

```json
{
  "status": "success|error",
  "message": "Description of the response",
  "data": {...},
  "timestamp": 1234567890
}
```

Error responses include an `error` field with details.

## Files Included

1. **perfect_bot_api_client.py** - Main client implementation
2. **comprehensive_api_example.py** - Full demonstration of all features
3. **test_api_client.py** - Simple test script
4. **leech_specific_file.py** - Example for leeching the specific file mentioned

## Running Examples

```bash
# Test the client
python3 test_api_client.py

# Run comprehensive example
python3 comprehensive_api_example.py

# Leech the specific file
python3 leech_specific_file.py
```

## API Secret

The API secret must match the one configured in the bot:
```
wzmlx_bot_api_secret_2025
```

## Requirements

- Python 3.7+
- requests library
- Standard Python libraries (hmac, hashlib, json, etc.)

## Support

This client provides complete access to all bot functions via API with proper authentication and error handling.
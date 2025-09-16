# Perfect Bot API Client

This is a fully functional API client for your Telegram Mirror Bot. It provides complete access to all bot functions with proper authentication and error handling.

## Quick Start

1. **Test the API client:**
   ```bash
   python3 test_api_client.py
   ```

2. **Run comprehensive examples:**
   ```bash
   python3 comprehensive_api_example.py
   ```

3. **Leech the specific file you mentioned:**
   ```bash
   python3 leech_specific_file.py
   ```

## Key Features

✅ **Complete API Coverage** - All endpoints supported
✅ **Secure Authentication** - HMAC-SHA256 signatures
✅ **Real Task Execution** - Actual bot commands, not simulations
✅ **Error Handling** - Proper error responses and debugging
✅ **Task Management** - Built-in task tracking
✅ **Easy Integration** - Simple Python interface

## Usage Example

```python
from perfect_bot_api_client import PerfectBotAPIClient

# Initialize client
client = PerfectBotAPIClient(
    base_url="http://139.162.28.139:7392",
    api_secret="wzmlx_bot_api_secret_2025"
)

# Leech a Telegram file
result = client.start_leech(
    command="/leech https://t.me/c/3021633087/50",
    user_id="7859877609",
    chat_id="-1002934661749"
)

if result.get('status') == 'success':
    print("✅ File leech started successfully!")
    print(f"Task ID: {result.get('task_id')}")
```

## Files

- `perfect_bot_api_client.py` - Main client implementation
- `test_api_client.py` - Simple test script
- `comprehensive_api_example.py` - Full feature demonstration
- `leech_specific_file.py` - Example for your specific use case
- `API_CLIENT_PERFECT.md` - Detailed documentation

## Requirements

- Python 3.7+
- requests library (usually pre-installed)

The client handles all authentication automatically - just provide the correct API secret!

## Support

This client provides direct access to your bot's functions via HTTP API with the same functionality as Telegram commands.
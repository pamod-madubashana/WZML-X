# Simple Leech Client - Two-Parameter Interface

A simplified API client for leeching files with just two main parameters as requested.

## Overview

This client provides the simplest possible interface for leeching files:
- `file`: The file URL (Telegram link or HTTP URL)
- `command`: The leech command (optional, defaults to "/leech")

## Usage

### Basic Usage with Two Parameters

```python
from leech_client import LeechAPIClient

# Initialize client
client = LeechAPIClient(
    base_url="http://139.162.28.139:7392",
    api_secret="wzmlx_bot_api_secret_2025"
)

# Leech with just file parameter (uses default "/leech" command)
result = client.leech(file="https://t.me/c/3021633087/50")

# Leech with file and custom command
result = client.leech(
    file="https://t.me/c/3021633087/50",
    command="/leech1"
)
```

### Advanced Usage (Additional Parameters)

```python
# Specify user and chat IDs
result = client.leech(
    file="https://t.me/c/3021633087/50",
    command="/leech",
    user_id="7859877609",     # Pamod's ID
    chat_id="-1002934661749"  # Supergroup ID
)
```

## Methods

### `leech(file, command="/leech", user_id="7859877609", chat_id="-1002934661749")`

Leech a file with the specified parameters.

**Parameters:**
- `file` (str): File URL (Telegram link or HTTP URL)
- `command` (str, optional): Leech command (default: "/leech")
- `user_id` (str, optional): User ID (default: Pamod's ID)
- `chat_id` (str, optional): Chat ID (default: supergroup ID)

**Returns:**
- `dict`: API response with task information

### `get_task_status()`

Get current download tasks.

**Returns:**
- `dict`: Downloads information

### `get_bot_status()`

Get bot status information.

**Returns:**
- `dict`: Bot status information

### `is_bot_available()`

Check if bot is available.

**Returns:**
- `bool`: True if bot is available

## Examples

See the example files for usage:
- `simple_leech_example.py` - Basic two-parameter usage
- `test_leech_client.py` - Simple test script
- `leech_client.py` - Full client with main function

## Requirements

- Python 3.7+
- requests library
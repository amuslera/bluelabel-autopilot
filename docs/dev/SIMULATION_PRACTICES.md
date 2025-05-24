# Simulation Practices for WhatsApp Webhook Testing

This document outlines the practices for simulating WhatsApp webhook events for testing purposes.

## Overview

The `simulate_whatsapp.py` script allows you to test the WhatsApp webhook adapter by simulating incoming webhook events. It supports different types of payloads and provides options for customization.

## Supported Payload Types

The simulator currently supports the following payload types:

1. **URL Payload**
   ```json
   {
     "type": "url",
     "value": "https://example.com"
   }
   ```

2. **PDF Payload**
   ```json
   {
     "type": "pdf",
     "value": "/path/to/document.pdf"
   }
   ```

3. **Invalid Payload** (for testing error handling)
   ```json
   {
     "type": "invalid",
     "value": "should_fail"
   }
   ```

## Using the Simulator

### Basic Usage

```bash
# Simulate a URL webhook event
python runner/simulate_whatsapp.py --type url

# Simulate a PDF webhook event
python runner/simulate_whatsapp.py --type pdf
```

### Advanced Options

```bash
# Use a custom payload file
python runner/simulate_whatsapp.py --file path/to/payload.json

# Save the response to a file
python runner/simulate_whatsapp.py --type url --output response.json

# Use a custom payload directly from the command line
python runner/simulate_whatsapp.py --custom '{"type":"url","value":"https://example.com"}'
```

## Logging

All webhook events are logged to the following locations:

- **General Logs**: `data/whatsapp_logs/whatsapp_YYYYMMDD.log`
  - Contains all webhook events with timestamps and status

- **Individual Run Logs**: `data/whatsapp_logs/<run_id>.json`
  - Detailed logs for each webhook event
  - Includes input payload and processing status

### Example Log Entry

```json
{
  "timestamp": "2024-05-24T10:15:30.123456",
  "run_id": "550e8400-e29b-41d4-a716-446655440000",
  "workflow": "url_to_digest.yaml",
  "status": "completed",
  "input": {
    "type": "url",
    "value": "https://example.com"
  }
}
```

## Tips for Custom Test Runs

1. **Testing Error Cases**
   - Use the `invalid` payload type to test error handling
   - Test with missing or malformed fields

2. **Debugging**
   - Check the console output for immediate feedback
   - Review the log files in `data/whatsapp_logs/` for detailed information

3. **Custom Payloads**
   - Create custom payload files for complex test cases
   - Use the `--file` option to load them

4. **Automation**
   - The `--output` option allows saving responses for automated testing
   - The script returns a non-zero exit code on errors

## Future Improvements

- Add support for more payload types
- Include request/response timing information
- Add validation for input payloads
- Support for load testing with multiple concurrent requests

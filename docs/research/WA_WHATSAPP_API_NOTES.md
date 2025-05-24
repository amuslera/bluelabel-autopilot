# WhatsApp Business API Research

**Date**: 2024-05-24  
**Researcher**: WA (Windsurf AI)  
**Task ID**: TASK-161T  
**Version**: 1.0.0

## Table of Contents
1. [Overview](#overview)
2. [API Options](#api-options)
3. [Signup & Approval Process](#signup--approval-process)
4. [Sandbox Access](#sandbox-access)
5. [Webhook Structure](#webhook-structure)
6. [Message Types & Templates](#message-types--templates)
7. [Vendor Comparison](#vendor-comparison)
8. [Rate Limits](#rate-limits)
9. [Example Implementation](#example-implementation)
10. [Recommendations](#recommendations)
11. [Next Steps](#next-steps)

## Overview
This document outlines the research findings for integrating WhatsApp Business API into the Bluelabel Autopilot system. The focus is on understanding the requirements, limitations, and best practices for implementing WhatsApp messaging capabilities.

## API Options

### 1. Meta's Cloud API (Recommended)
- **Hosting**: Fully managed by Meta
- **Setup Time**: Faster implementation
- **Maintenance**: No server maintenance required
- **Scalability**: Handled automatically by Meta
- **Documentation**: [Meta Cloud API Docs](https://developers.facebook.com/docs/whatsapp/cloud-api/)

### 2. On-Premises API
- **Hosting**: Self-hosted solution
- **Setup Time**: Longer implementation (4-6 weeks)
- **Maintenance**: Requires dedicated DevOps
- **Control**: Full control over infrastructure
- **Documentation**: [On-Premises API Docs](https://developers.facebook.com/docs/whatsapp/on-premises/)

## Signup & Approval Process

### Direct with Meta
1. Create a Meta Developer Account
2. Submit business verification documents
3. Wait for approval (2-3 weeks)
4. Set up Business Manager
5. Create WhatsApp Business App
6. Get approved for production access

### Through Solution Providers
1. Sign up with a BSP (Business Solution Provider)
2. Complete business verification
3. Get access within 1-2 weeks
4. Start with sandbox immediately

## Sandbox Access

### Meta Cloud API Sandbox
- **Access**: Instant after app creation
- **Features**:
  - Test phone number provided
  - Limited to test numbers
  - Full API functionality
- **Limitations**:
  - Only works with registered test numbers
  - No production traffic allowed

### Testing Numbers
- Register up to 5 test numbers
- Must be real phone numbers that can receive SMS
- Verified via OTP

## Webhook Structure

### Required Endpoints
```
POST /webhooks/whatsapp
```

### Headers
```http
Content-Type: application/json
X-Hub-Signature-256: sha256=...
```

### Sample Payload (Message Received)
```json
{
  "object": "whatsapp_business_account",
  "entry": [{
    "id": "WHATSAPP_BUSINESS_ACCOUNT_ID",
    "changes": [{
      "value": {
        "messaging_product": "whatsapp",
        "metadata": {
          "display_phone_number": "1234567890",
          "phone_number_id": "PHONE_NUMBER_ID"
        },
        "contacts": [{
          "profile": {
            "name": "John Doe"
          },
          "wa_id": "1234567890"
        }],
        "messages": [{
          "from": "1234567890",
          "id": "wamid.abc123",
          "timestamp": "1234567890",
          "text": {
            "body": "Hello!"
          },
          "type": "text"
        }]
      },
      "field": "messages"
    }]
  }]
}
```

## Message Types & Templates

### Supported Message Types
1. **Text Messages**
2. **Media Messages** (Images, Documents, Audio, Video)
3. **Location Messages**
4. **Contacts**
5. **Interactive Messages**
   - List Messages
   - Reply Buttons
   - Product Messages

### Template Messages
- **Approval Required**: All templates must be approved
- **Categories**:
  - UTILITY
  - MARKETING
  - AUTHENTICATION
  - ALERT_UPDATE

#### Example Template Request
```http
POST /v17.0/PHONE_NUMBER_ID/messages
```

```json
{
  "messaging_product": "whatsapp",
  "to": "1234567890",
  "type": "template",
  "template": {
    "name": "hello_world",
    "language": {
      "code": "en_US"
    }
  }
}
```

## Vendor Comparison

| Feature | Meta Direct | Twilio | MessageBird | 360Dialog |
|---------|------------|--------|-------------|-----------|
| Setup Time | 2-3 weeks | 1-2 days | 1-2 days | 1-2 days |
| Monthly Cost | $0.005/message | $0.005/message | $0.005/message | $0.0045/message |
| Support | Limited | 24/7 | Business hours | 24/7 |
| Features | Full API | Full API + Extras | Full API + Extras | Full API + Extras |
| Scalability | High | Very High | High | High |
| Best For | Large volume | Global businesses | EU businesses | WhatsApp specialists |

## Rate Limits

### Cloud API
- 50 messages per second
- 1,000 unique contacts per 24 hours (tier 1)
- Higher tiers available upon request

### Business Management API
- 200 requests per hour per app
- 50 requests per hour per phone number

## Example Implementation

### Python Webhook Handler
```python
from fastapi import FastAPI, Request, HTTPException
import hmac
import hashlib
import json

app = FastAPI()

VERIFY_TOKEN = "YOUR_VERIFY_TOKEN"
APP_SECRET = "YOUR_APP_SECRET"

@app.get("/webhooks/whatsapp")
async def verify_webhook(
    request: Request,
    hub_mode: str = None,
    hub_verify_token: str = None,
    hub_challenge: str = None
):
    if hub_mode == "subscribe" and hub_verify_token == VERIFY_TOKEN:
        return int(hub_challenge)
    raise HTTPException(status_code=403, detail="Verification failed")

@app.post("/webhooks/whatsapp")
async def webhook(request: Request):
    # Verify signature
    signature = request.headers.get("X-Hub-Signature-256", "")
    body = await request.body()
    
    # Verify webhook signature
    expected_signature = hmac.new(
        APP_SECRET.encode(),
        body,
        hashlib.sha256
    ).hexdigest()
    
    if not hmac.compare_digest(f"sha256={expected_signature}", signature):
        raise HTTPException(status_code=401, detail="Invalid signature")
    
    # Process webhook
    data = await request.json()
    # Process the webhook data here
    
    return {"status": "success"}
```

## Recommendations

1. **Start with Meta's Cloud API** for faster implementation
2. **Use a Solution Provider** for faster approval and better support
3. **Implement Webhook Verification** properly
4. **Use Template Messages** for outbound communications
5. **Implement Rate Limiting** on your end
6. **Set Up Monitoring** for webhook delivery

## Next Steps

1. Create a Meta Developer Account
2. Set up a test app and get sandbox credentials
3. Implement webhook verification
4. Test with template messages
5. Apply for production access
6. Implement message handling logic
7. Set up monitoring and error handling

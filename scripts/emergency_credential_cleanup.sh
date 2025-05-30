#!/bin/bash
# Emergency Credential Cleanup Script for AIOS v2

echo "🚨 EMERGENCY CREDENTIAL CLEANUP FOR AIOS V2"
echo "=========================================="

AIOS_DIR="/Users/arielmuslera/Development/Projects/bluelabel-AIOS-V2"

# Check if we're in the right place
if [ ! -d "$AIOS_DIR" ]; then
    echo "❌ Error: AIOS v2 directory not found at $AIOS_DIR"
    exit 1
fi

cd "$AIOS_DIR"

echo ""
echo "1️⃣ Backing up current .env (without credentials)..."
# Create a clean backup without the exposed credentials
head -n 168 .env > .env.clean_backup
echo "✅ Clean backup created as .env.clean_backup"

echo ""
echo "2️⃣ Removing exposed credentials from .env..."
# Keep only the clean template part
head -n 168 .env > .env.tmp && mv .env.tmp .env
echo "✅ Cleaned .env file"

echo ""
echo "3️⃣ Removing dangerous backup files..."
# Remove files with exposed credentials
if [ -f ".env.backup" ]; then
    rm -f .env.backup
    echo "✅ Removed .env.backup"
fi

echo ""
echo "4️⃣ Cleaning up token files..."
# Remove OAuth tokens (they'll be regenerated)
rm -f data/gmail_token.json
rm -f data/gmail_credentials/token.json
rm -f data/mcp/gmail_token.json
echo "✅ Removed OAuth token files"

echo ""
echo "5️⃣ Checking git status..."
git status --porcelain | grep -E "\.env|token\.json"

echo ""
echo "6️⃣ Creating secure .env from template..."
echo "# Add your NEW credentials below this line" >> .env
echo "# DO NOT use the exposed keys!" >> .env

echo ""
echo "✅ CLEANUP COMPLETE!"
echo ""
echo "NEXT STEPS:"
echo "1. Add your NEW API keys to .env (not the exposed ones!)"
echo "2. Run: git add -A && git commit -m 'Remove exposed credentials'"
echo "3. Consider running BFG to clean git history"
echo ""
echo "⚠️  IMPORTANT: The old API keys are compromised and must be rotated!"
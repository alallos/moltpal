#!/bin/bash
# Test the live MoltPal deployment

# Set this to your Railway URL
API_URL="${1:-https://moltpal-production.up.railway.app}"

echo "🧪 Testing MoltPal at: $API_URL"
echo "=" | head -c 50; echo

# Test 1: Health check
echo "1️⃣  Health Check..."
curl -s "$API_URL/health" | python3 -m json.tool
echo -e "\n"

# Test 2: Create user
echo "2️⃣  Creating test user..."
USER_RESPONSE=$(curl -s -X POST "$API_URL/api/user/create" \
  -H "Content-Type: application/json" \
  -d '{"email":"demo@moltpal.dev"}')

echo "$USER_RESPONSE" | python3 -m json.tool

USER_ID=$(echo "$USER_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['user']['id'])" 2>/dev/null)

if [ -z "$USER_ID" ]; then
  echo "❌ Failed to create user"
  exit 1
fi

echo "✅ User created: $USER_ID"
echo

# Test 3: Add funds
echo "3️⃣  Adding funds ($1000.00)..."
curl -s -X POST "$API_URL/api/user/$USER_ID/balance" \
  -H "Content-Type: application/json" \
  -d '{"amount": 100000}' | python3 -m json.tool
echo -e "\n"

# Test 4: Create agent key
echo "4️⃣  Creating agent API key..."
KEY_RESPONSE=$(curl -s -X POST "$API_URL/api/agent/keys" \
  -H "Content-Type: application/json" \
  -d "{
    \"user_id\": \"$USER_ID\",
    \"name\": \"Test Agent\",
    \"limit_per_transaction\": 10000,
    \"limit_daily\": 50000,
    \"limit_monthly\": 200000
  }")

echo "$KEY_RESPONSE" | python3 -m json.tool

API_KEY=$(echo "$KEY_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['key']['api_key'])" 2>/dev/null)

if [ -z "$API_KEY" ]; then
  echo "❌ Failed to create API key"
  exit 1
fi

echo "✅ API Key: ${API_KEY:0:30}..."
echo

# Test 5: Make payment
echo "5️⃣  Making test payment ($50.00)..."
curl -s -X POST "$API_URL/api/payment/pay" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d '{
    "amount": 5000,
    "description": "Test payment - OpenAI API",
    "merchant": "OpenAI"
  }' | python3 -m json.tool
echo -e "\n"

# Test 6: Check balance
echo "6️⃣  Checking balance..."
curl -s "$API_URL/api/payment/balance" \
  -H "X-API-Key: $API_KEY" | python3 -m json.tool
echo -e "\n"

# Test 7: Get transactions
echo "7️⃣  Transaction history..."
curl -s "$API_URL/api/payment/transactions?limit=5" \
  -H "X-API-Key: $API_KEY" | python3 -m json.tool
echo -e "\n"

echo "🎉 All tests passed!"
echo
echo "Live API: $API_URL"
echo "Test User ID: $USER_ID"
echo "Test API Key: ${API_KEY:0:30}..."

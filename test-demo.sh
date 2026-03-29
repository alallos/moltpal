#!/bin/bash
# MoltPal Demo Test Script

API_URL="http://localhost:3000/api"

echo "🧪 MoltPal API Demo Test"
echo "========================"
echo ""

# Check if API is running
echo "📡 Checking if API is running..."
if ! curl -s "$API_URL/../health" > /dev/null; then
  echo "❌ API is not running. Start it with: docker-compose up -d"
  exit 1
fi
echo "✅ API is running"
echo ""

# 1. Create user
echo "1️⃣  Creating user..."
USER_RESPONSE=$(curl -s -X POST "$API_URL/user/create" \
  -H "Content-Type: application/json" \
  -d '{"email":"demo@moltpal.dev"}')

USER_ID=$(echo $USER_RESPONSE | grep -o '"id":"[^"]*' | cut -d'"' -f4)
echo "✅ User created: $USER_ID"
echo ""

# 2. Add funds
echo "2️⃣  Adding $1000.00 to balance..."
curl -s -X POST "$API_URL/user/$USER_ID/balance" \
  -H "Content-Type: application/json" \
  -d '{"amount": 100000}' > /dev/null
echo "✅ Funds added"
echo ""

# 3. Create agent key
echo "3️⃣  Creating agent API key..."
KEY_RESPONSE=$(curl -s -X POST "$API_URL/agent/keys" \
  -H "Content-Type: application/json" \
  -d "{
    \"user_id\": \"$USER_ID\",
    \"name\": \"Demo Agent\",
    \"limit_per_transaction\": 10000,
    \"limit_daily\": 50000,
    \"limit_monthly\": 200000
  }")

API_KEY=$(echo $KEY_RESPONSE | grep -o '"api_key":"[^"]*' | cut -d'"' -f4)
echo "✅ API Key created: ${API_KEY:0:20}..."
echo ""

# 4. Make payment
echo "4️⃣  Making payment as agent ($50.00)..."
PAYMENT_RESPONSE=$(curl -s -X POST "$API_URL/payment/pay" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d '{
    "amount": 5000,
    "description": "OpenAI GPT-4 API usage",
    "merchant": "OpenAI",
    "metadata": {
      "model": "gpt-4",
      "tokens": 10000
    }
  }')

echo "$PAYMENT_RESPONSE" | python3 -m json.tool
echo ""

# 5. Check balance
echo "5️⃣  Checking balance..."
BALANCE_RESPONSE=$(curl -s "$API_URL/payment/balance" \
  -H "X-API-Key: $API_KEY")

echo "$BALANCE_RESPONSE" | python3 -m json.tool
echo ""

# 6. Get transaction history
echo "6️⃣  Transaction history..."
TRANSACTIONS=$(curl -s "$API_URL/payment/transactions?limit=5" \
  -H "X-API-Key: $API_KEY")

echo "$TRANSACTIONS" | python3 -m json.tool
echo ""

# 7. Get user stats
echo "7️⃣  User statistics..."
STATS=$(curl -s "$API_URL/user/$USER_ID/stats")
echo "$STATS" | python3 -m json.tool
echo ""

echo "✨ Demo completed successfully!"
echo ""
echo "📝 Summary:"
echo "   User ID:  $USER_ID"
echo "   API Key:  ${API_KEY:0:30}..."
echo ""
echo "🔗 Try the API yourself:"
echo "   curl $API_URL/payment/balance -H 'X-API-Key: $API_KEY'"

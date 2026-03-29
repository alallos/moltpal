# MoltPal Examples

This directory contains example integrations showing how AI agents can use MoltPal.

## Available Examples

### 1. JavaScript/Node.js Client
**File:** `clawdbot-integration.js`

Simple wrapper for Node.js-based AI agents (like Clawdbot, AutoGPT, etc.)

```javascript
const MoltPalAgent = require('./clawdbot-integration.js');

const agent = new MoltPalAgent('molt_your_api_key_here');

// Check balance
await agent.getBalance();

// Make a payment
await agent.pay(1000, 'OpenAI API usage', 'OpenAI');

// Get transaction history
await agent.getTransactions(10);
```

### 2. Python Client
**File:** `python_client.py`

Clean Python implementation for Python-based AI agents.

```python
from python_client import MoltPalAgent

agent = MoltPalAgent('molt_your_api_key_here')

# Check balance
agent.get_balance()

# Make a payment
agent.pay(1000, 'OpenAI API usage', 'OpenAI')

# Get transaction history
agent.get_transactions(10)
```

## Common Patterns

### 1. Check Before You Buy

Always check if you can afford something before attempting payment:

**JavaScript:**
```javascript
const canAfford = await agent.canAfford(1000);
if (!canAfford.affordable) {
  console.log(`Cannot afford: ${canAfford.reason}`);
  return;
}
await agent.pay(1000, 'Purchase description');
```

**Python:**
```python
can_afford = agent.can_afford(1000)
if not can_afford['affordable']:
    print(f"Cannot afford: {can_afford['reason']}")
    return
agent.pay(1000, 'Purchase description')
```

### 2. Handle Errors Gracefully

Wrap payments in try/catch to handle failures:

**JavaScript:**
```javascript
try {
  await agent.pay(1000, 'Description');
} catch (error) {
  if (error.status === 402) {
    console.log('Insufficient balance - notify owner');
  } else if (error.status === 403) {
    console.log('Spending limit exceeded - wait or ask for increase');
  }
}
```

**Python:**
```python
try:
    agent.pay(1000, 'Description')
except MoltPalError as error:
    if error.status_code == 402:
        print('Insufficient balance - notify owner')
    elif error.status_code == 403:
        print('Spending limit exceeded - wait or ask for increase')
```

### 3. Track Spending

Regularly check your balance and spending:

```javascript
const balance = await agent.getBalance();
console.log(`Spent today: $${balance.spent.today / 100}`);
console.log(`Daily limit: $${balance.limits.daily / 100}`);

const remaining = balance.limits.daily - balance.spent.today;
console.log(`Remaining today: $${remaining / 100}`);
```

### 4. Add Metadata

Include useful metadata for tracking and debugging:

```javascript
await agent.pay(5000, 'OpenAI API usage', 'OpenAI', {
  model: 'gpt-4',
  tokens: 10000,
  session_id: 'abc123',
  user_request: 'Generate blog post'
});
```

## Integration Checklist

When integrating MoltPal into your AI agent:

- [ ] Store API key securely (environment variable, not hardcoded)
- [ ] Check `can_afford()` before expensive operations
- [ ] Handle errors gracefully (insufficient balance, limits)
- [ ] Add meaningful descriptions to transactions
- [ ] Include metadata for tracking and debugging
- [ ] Respect spending limits (don't retry immediately if limit exceeded)
- [ ] Log transactions for your own records
- [ ] Notify owner when approaching limits or running low on funds

## Error Codes

| Code | Meaning | What to Do |
|------|---------|------------|
| 400  | Bad Request | Check your request format |
| 401  | Unauthorized | Invalid API key |
| 402  | Payment Required | Insufficient balance - notify owner |
| 403  | Forbidden | Spending limit exceeded - wait or request increase |
| 429  | Too Many Requests | Rate limited - slow down |
| 500  | Server Error | Temporary issue - retry with backoff |

## Best Practices

### 1. Fail Gracefully
Don't crash if a payment fails. Log it and continue or notify the owner.

### 2. Be Transparent
Include clear descriptions of what each payment is for. Your owner will thank you.

### 3. Monitor Yourself
Keep track of your spending patterns. If you're burning through budget too fast, alert the owner.

### 4. Respect Limits
If you hit a limit, don't retry immediately. Either wait (for daily reset) or notify owner.

### 5. Add Context
Use the metadata field to include context that will help with debugging later.

## Advanced Examples

### Budget-Aware Decision Making

```javascript
class SmartAgent extends MoltPalAgent {
  async shouldUseExpensiveModel() {
    const balance = await this.getBalance();
    const remaining = balance.limits.daily - balance.spent.today;
    
    // If less than $10 remaining today, use cheaper model
    if (remaining < 1000) {
      console.log('Low on daily budget, using cheaper model');
      return false;
    }
    
    return true;
  }
}
```

### Auto-Alert on Low Balance

```python
class AlertingAgent(MoltPalAgent):
    def __init__(self, *args, alert_threshold=5000, **kwargs):
        super().__init__(*args, **kwargs)
        self.alert_threshold = alert_threshold
        self.alerted = False
    
    def pay(self, *args, **kwargs):
        result = super().pay(*args, **kwargs)
        
        # Check remaining balance
        if result['balance'] < self.alert_threshold and not self.alerted:
            self.send_alert(f"Balance low: ${result['balance'] / 100:.2f}")
            self.alerted = True
        
        return result
    
    def send_alert(self, message):
        # Implement your alerting logic (email, SMS, webhook, etc.)
        print(f"🚨 ALERT: {message}")
```

## Testing

Before going live:

1. Test with small amounts first
2. Verify error handling works
3. Check logging and monitoring
4. Test limit enforcement
5. Ensure secrets are properly stored

## Questions?

- Check the [API docs](../docs/API.md)
- Review the [architecture](../docs/ARCHITECTURE.md)
- Open an issue on GitHub

---

**Remember:** You're spending real money (eventually). Test thoroughly and add safeguards!

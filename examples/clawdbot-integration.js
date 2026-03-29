/**
 * Example: How an AI agent (like Clawdbot) would integrate with MoltPal
 * 
 * This shows a simple wrapper that agents can use to make payments
 * autonomously within their spending limits.
 */

const https = require('https');

class MoltPalAgent {
  constructor(apiKey, baseUrl = 'http://localhost:3000/api') {
    this.apiKey = apiKey;
    this.baseUrl = baseUrl;
  }

  /**
   * Make a payment
   * @param {number} amount - Amount in cents
   * @param {string} description - What the payment is for
   * @param {string} merchant - Who is being paid (optional)
   * @param {object} metadata - Additional data (optional)
   */
  async pay(amount, description, merchant = null, metadata = {}) {
    try {
      const response = await this._request('POST', '/payment/pay', {
        amount,
        description,
        merchant,
        metadata
      });

      console.log(`✅ Payment successful: $${(amount / 100).toFixed(2)}`);
      console.log(`   Balance remaining: $${(response.balance / 100).toFixed(2)}`);
      
      return response;
    } catch (error) {
      if (error.status === 402) {
        console.error('❌ Insufficient balance');
      } else if (error.status === 403) {
        console.error('❌ Spending limit exceeded:', error.message);
      } else {
        console.error('❌ Payment failed:', error.message);
      }
      throw error;
    }
  }

  /**
   * Check current balance and spending limits
   */
  async getBalance() {
    const response = await this._request('GET', '/payment/balance');
    
    console.log(`💰 Balance: $${(response.balance / 100).toFixed(2)}`);
    console.log(`📊 Limits:`);
    console.log(`   Per transaction: $${(response.limits.per_transaction / 100).toFixed(2)}`);
    console.log(`   Daily: $${(response.limits.daily / 100).toFixed(2)}`);
    console.log(`   Monthly: $${(response.limits.monthly / 100).toFixed(2)}`);
    console.log(`📈 Spent:`);
    console.log(`   Today: $${(response.spent.today / 100).toFixed(2)}`);
    console.log(`   This month: $${(response.spent.this_month / 100).toFixed(2)}`);
    
    return response;
  }

  /**
   * Get transaction history
   */
  async getTransactions(limit = 10) {
    const response = await this._request('GET', `/payment/transactions?limit=${limit}`);
    
    console.log(`📋 Recent transactions (${response.count}):`);
    response.transactions.forEach(tx => {
      const amount = (tx.amount_cents / 100).toFixed(2);
      const date = new Date(tx.created_at).toLocaleString();
      console.log(`   $${amount} - ${tx.description} (${date})`);
    });
    
    return response;
  }

  /**
   * Check if we can afford a payment before making it
   */
  async canAfford(amount) {
    const balance = await this.getBalance();
    
    // Check balance
    if (balance.balance < amount) {
      return {
        affordable: false,
        reason: 'insufficient_balance',
        available: balance.balance
      };
    }
    
    // Check per-transaction limit
    if (balance.limits.per_transaction && amount > balance.limits.per_transaction) {
      return {
        affordable: false,
        reason: 'per_transaction_limit',
        limit: balance.limits.per_transaction
      };
    }
    
    // Check daily limit
    if (balance.limits.daily && (balance.spent.today + amount) > balance.limits.daily) {
      return {
        affordable: false,
        reason: 'daily_limit',
        limit: balance.limits.daily,
        spent: balance.spent.today
      };
    }
    
    // Check monthly limit
    if (balance.limits.monthly && (balance.spent.this_month + amount) > balance.limits.monthly) {
      return {
        affordable: false,
        reason: 'monthly_limit',
        limit: balance.limits.monthly,
        spent: balance.spent.this_month
      };
    }
    
    return { affordable: true };
  }

  /**
   * Internal: Make HTTP request
   */
  async _request(method, endpoint, body = null) {
    const url = new URL(endpoint, this.baseUrl);
    
    return new Promise((resolve, reject) => {
      const options = {
        method,
        headers: {
          'Content-Type': 'application/json',
          'X-API-Key': this.apiKey
        }
      };

      const req = https.request(url.toString(), options, (res) => {
        let data = '';
        
        res.on('data', chunk => data += chunk);
        
        res.on('end', () => {
          try {
            const json = JSON.parse(data);
            
            if (res.statusCode >= 200 && res.statusCode < 300) {
              resolve(json);
            } else {
              reject({
                status: res.statusCode,
                message: json.error || 'Request failed',
                ...json
              });
            }
          } catch (err) {
            reject({ status: res.statusCode, message: 'Invalid response' });
          }
        });
      });

      req.on('error', reject);
      
      if (body) {
        req.write(JSON.stringify(body));
      }
      
      req.end();
    });
  }
}

// ============================================
// Example Usage
// ============================================

async function exampleUsage() {
  // Initialize the agent with API key
  const agent = new MoltPalAgent('molt_your_api_key_here');
  
  try {
    // Check balance first
    console.log('=== Checking Balance ===');
    await agent.getBalance();
    console.log('');
    
    // Check if we can afford something before buying
    console.log('=== Checking if we can afford OpenAI API call ===');
    const openaiCost = 1000; // $10.00
    const canAfford = await agent.canAfford(openaiCost);
    
    if (!canAfford.affordable) {
      console.log(`❌ Cannot afford: ${canAfford.reason}`);
      return;
    }
    
    console.log('✅ Can afford this purchase');
    console.log('');
    
    // Make the payment
    console.log('=== Making Payment ===');
    await agent.pay(
      1000, // $10.00
      'OpenAI GPT-4 API usage',
      'OpenAI',
      {
        model: 'gpt-4',
        tokens: 10000,
        session_id: 'abc123'
      }
    );
    console.log('');
    
    // Get transaction history
    console.log('=== Transaction History ===');
    await agent.getTransactions(5);
    
  } catch (error) {
    console.error('Error:', error);
  }
}

// Run example if executed directly
if (require.main === module) {
  exampleUsage();
}

module.exports = MoltPalAgent;

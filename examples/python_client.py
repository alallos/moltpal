"""
MoltPal Python Client

Example integration for AI agents written in Python.
Simple wrapper around the MoltPal API.

Usage:
    from moltpal import MoltPalAgent
    
    agent = MoltPalAgent('molt_your_api_key_here')
    agent.pay(1000, 'OpenAI API usage')
"""

import requests
from typing import Optional, Dict, Any
from datetime import datetime


class MoltPalAgent:
    """MoltPal API client for AI agents"""
    
    def __init__(self, api_key: str, base_url: str = 'http://localhost:3000/api'):
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'X-API-Key': api_key
        })
    
    def pay(
        self, 
        amount: int, 
        description: str, 
        merchant: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Make a payment
        
        Args:
            amount: Amount in cents
            description: What the payment is for
            merchant: Who is being paid (optional)
            metadata: Additional data (optional)
        
        Returns:
            Transaction details
        
        Raises:
            MoltPalError: If payment fails
        """
        try:
            response = self._request('POST', '/payment/pay', {
                'amount': amount,
                'description': description,
                'merchant': merchant,
                'metadata': metadata or {}
            })
            
            print(f"✅ Payment successful: ${amount / 100:.2f}")
            print(f"   Balance remaining: ${response['balance'] / 100:.2f}")
            
            return response
            
        except MoltPalError as e:
            if e.status_code == 402:
                print("❌ Insufficient balance")
            elif e.status_code == 403:
                print(f"❌ Spending limit exceeded: {e.message}")
            else:
                print(f"❌ Payment failed: {e.message}")
            raise
    
    def get_balance(self) -> Dict[str, Any]:
        """Get current balance and spending limits"""
        response = self._request('GET', '/payment/balance')
        
        print(f"💰 Balance: ${response['balance'] / 100:.2f}")
        print(f"📊 Limits:")
        print(f"   Per transaction: ${response['limits']['per_transaction'] / 100:.2f}")
        print(f"   Daily: ${response['limits']['daily'] / 100:.2f}")
        print(f"   Monthly: ${response['limits']['monthly'] / 100:.2f}")
        print(f"📈 Spent:")
        print(f"   Today: ${response['spent']['today'] / 100:.2f}")
        print(f"   This month: ${response['spent']['this_month'] / 100:.2f}")
        
        return response
    
    def get_transactions(self, limit: int = 10) -> Dict[str, Any]:
        """Get transaction history"""
        response = self._request('GET', f'/payment/transactions?limit={limit}')
        
        print(f"📋 Recent transactions ({response['count']}):")
        for tx in response['transactions']:
            amount = tx['amount_cents'] / 100
            date = datetime.fromisoformat(tx['created_at'].replace('Z', '+00:00'))
            print(f"   ${amount:.2f} - {tx['description']} ({date.strftime('%Y-%m-%d %H:%M')})")
        
        return response
    
    def can_afford(self, amount: int) -> Dict[str, Any]:
        """
        Check if we can afford a payment before making it
        
        Returns:
            {
                'affordable': bool,
                'reason': str (if not affordable),
                'available': int,
                'limit': int (if limit exceeded),
                'spent': int (if limit exceeded)
            }
        """
        balance = self.get_balance()
        
        # Check balance
        if balance['balance'] < amount:
            return {
                'affordable': False,
                'reason': 'insufficient_balance',
                'available': balance['balance']
            }
        
        # Check per-transaction limit
        if balance['limits']['per_transaction'] and amount > balance['limits']['per_transaction']:
            return {
                'affordable': False,
                'reason': 'per_transaction_limit',
                'limit': balance['limits']['per_transaction']
            }
        
        # Check daily limit
        if balance['limits']['daily'] and (balance['spent']['today'] + amount) > balance['limits']['daily']:
            return {
                'affordable': False,
                'reason': 'daily_limit',
                'limit': balance['limits']['daily'],
                'spent': balance['spent']['today']
            }
        
        # Check monthly limit
        if balance['limits']['monthly'] and (balance['spent']['this_month'] + amount) > balance['limits']['monthly']:
            return {
                'affordable': False,
                'reason': 'monthly_limit',
                'limit': balance['limits']['monthly'],
                'spent': balance['spent']['this_month']
            }
        
        return {'affordable': True}
    
    def _request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """Make HTTP request to MoltPal API"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method == 'GET':
                response = self.session.get(url)
            elif method == 'POST':
                response = self.session.post(url, json=data)
            elif method == 'DELETE':
                response = self.session.delete(url)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            # Parse response
            try:
                json_data = response.json()
            except ValueError:
                raise MoltPalError(response.status_code, "Invalid JSON response")
            
            # Check status
            if response.status_code >= 400:
                error_msg = json_data.get('error', 'Request failed')
                raise MoltPalError(response.status_code, error_msg, json_data)
            
            return json_data
            
        except requests.RequestException as e:
            raise MoltPalError(0, f"Network error: {str(e)}")


class MoltPalError(Exception):
    """MoltPal API error"""
    
    def __init__(self, status_code: int, message: str, data: Optional[Dict] = None):
        self.status_code = status_code
        self.message = message
        self.data = data or {}
        super().__init__(f"[{status_code}] {message}")


# ============================================
# Example Usage
# ============================================

def example_usage():
    """Example of how an AI agent would use MoltPal"""
    
    # Initialize the agent with API key
    agent = MoltPalAgent('molt_your_api_key_here')
    
    try:
        # Check balance first
        print('=== Checking Balance ===')
        agent.get_balance()
        print()
        
        # Check if we can afford something before buying
        print('=== Checking if we can afford OpenAI API call ===')
        openai_cost = 1000  # $10.00
        can_afford = agent.can_afford(openai_cost)
        
        if not can_afford['affordable']:
            print(f"❌ Cannot afford: {can_afford['reason']}")
            return
        
        print('✅ Can afford this purchase')
        print()
        
        # Make the payment
        print('=== Making Payment ===')
        agent.pay(
            1000,  # $10.00
            'OpenAI GPT-4 API usage',
            'OpenAI',
            {
                'model': 'gpt-4',
                'tokens': 10000,
                'session_id': 'abc123'
            }
        )
        print()
        
        # Get transaction history
        print('=== Transaction History ===')
        agent.get_transactions(5)
        
    except MoltPalError as error:
        print(f'Error: {error}')


if __name__ == '__main__':
    example_usage()

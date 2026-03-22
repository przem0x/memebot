import aiohttp
from datetime import datetime

class TelegramNotifier:
    def __init__(self, token: str, chat_id: str):
        self.token = token
        self.chat_id = chat_id
        self.base_url = f"https://api.telegram.org/bot{token}"
    
    async def send_test_message(self):
        payload = {
            "chat_id": self.chat_id,
            "text": "✅ Bot włączony i gotów do pracy!"
        }
        async with aiohttp.ClientSession() as session:
            await session.post(f"{self.base_url}/sendMessage", json=payload)
    
    async def send_signal(self, signal: dict):
        token = signal.get("token", "N/A")
        wallet = signal.get("wallet", "N/A")[:8]
        amount = signal.get("amount", 0)
        liquidity = signal.get("liquidity", 0)
        
        message = f"""
🚨 BUY SIGNAL

📍 Token: {token}
👤 Wallet: {wallet}...
💰 Amount: ${amount:.2f}
💧 Liquidity: ${liquidity:,.0f}

⏰ {datetime.now().strftime('%H:%M:%S')}
        """
        
        payload = {
            "chat_id": self.chat_id,
            "text": message.strip()
        }
        
        async with aiohttp.ClientSession() as session:
            await session.post(f"{self.base_url}/sendMessage", json=payload)

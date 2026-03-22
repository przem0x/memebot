import aiohttp
from datetime import datetime

class TelegramNotifier:
    def __init__(self, token: str, chat_id: str):
        self.token = token
        self.chat_id = chat_id
        self.base_url = f"https://api.telegram.org/bot{token}"
    
    async def send_test_message(self):
        await self.send_telegram("✅ Bot włączony i gotów do pracy!")
    
    async def send_telegram(self, message: str):
        payload = {
            "chat_id": self.chat_id,
            "text": message.strip()
        }
        try:
            async with aiohttp.ClientSession() as session:
                await session.post(f"{self.base_url}/sendMessage", json=payload)
        except:
            pass
    
    async def send_signal(self, signal: dict):
        token = signal.get("token", "N/A")
        wallet = signal.get("wallet", "N/A")[:8]
        amount = signal.get("amount", 0)
        
        message = f"""
🚨 TRADE ALERT

📍 Token: {token}
👤 Wallet: {wallet}...
💰 Amount: \${amount:.2f}
⏰ {datetime.now().strftime('%H:%M:%S')}
        """
        await self.send_telegram(message)

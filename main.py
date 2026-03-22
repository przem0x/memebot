import os
import asyncio
from dotenv import load_dotenv
from src.telegram_notifier import TelegramNotifier
from src.wallet_tracker import WalletTracker
from src.token_monitor import TokenMonitor

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
HELIUS_API_KEY = os.getenv("HELIUS_API_KEY")

async def main():
    print("🤖 Bot startuje...")
    
    notifier = TelegramNotifier(TELEGRAM_TOKEN, TELEGRAM_CHAT_ID)
    wallet_tracker = WalletTracker(HELIUS_API_KEY)
    token_monitor = TokenMonitor(HELIUS_API_KEY)
    
    # Test Telegram
    await notifier.send_test_message()
    
    while True:
        try:
            top_wallets = await wallet_tracker.get_top_wallets()
            signals = await token_monitor.monitor_wallets(top_wallets)
            
            for signal in signals:
                await notifier.send_signal(signal)
            
            await asyncio.sleep(10)
        except Exception as e:
            print(f"❌ Error: {e}")
            await asyncio.sleep(30)

if __name__ == "__main__":
    asyncio.run(main())

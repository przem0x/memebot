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
    
    await notifier.send_test_message()
    
    # Skanuj co 6 godzin
    scan_interval = 6 * 60 * 60
    
    while True:
        try:
            print("🔍 Skanowanie nowych traderów...")
            new_wallets = await wallet_tracker.scan_for_traders()
            
            if new_wallets:
                for wallet in new_wallets:
                    msg = f"""
🎯 NOWY TRADER ZNALEZIONY

👤 Wallet: {wallet['wallet'][:8]}...
🏆 Win Rate: {wallet['win_rate']:.1f}%
📊 Tradów (30d): {wallet['total_trades']}
💰 Token: {wallet['token']}
                    """
                    await notifier.send_telegram(msg)
            
            # Monitoruj śledzonych walletów
            tracked = await wallet_tracker.get_tracked_wallets()
            signals = await token_monitor.monitor_wallets(tracked)
            
            for signal in signals:
                await notifier.send_signal(signal)
            
            await asyncio.sleep(scan_interval)
        except Exception as e:
            print(f"❌ Error: {e}")
            await asyncio.sleep(300)

if __name__ == "__main__":
    asyncio.run(main())

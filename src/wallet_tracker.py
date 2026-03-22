import aiohttp
import sqlite3
from datetime import datetime, timedelta

class WalletTracker:
    def __init__(self, helius_api_key: str):
        self.api_key = helius_api_key
        self.rpc_url = f"https://mainnet.helius-rpc.com/?api-key={helius_api_key}"
        self.init_db()
    
    def init_db(self):
        conn = sqlite3.connect("wallets.db")
        cursor = conn.cursor()
        cursor.execute("""CREATE TABLE IF NOT EXISTS tracked_wallets (wallet TEXT PRIMARY KEY, win_rate REAL, total_trades INT, added_date TEXT)""")
        conn.commit()
        conn.close()
    
    async def get_top_tokens(self):
        tokens = [
            {"address": "EPjFWaLb3oCRY59Es8MP4KEVVp98H6B3d4y46nCjNBL5", "symbol": "USDC"},
            {"address": "Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenErt9", "symbol": "USDT"},
            {"address": "9n4nbM75f5Ui33ZbPYXn59EwSgE8CGsHtErZWKOK2KKd", "symbol": "BRZ"},
        ]
        print(f"✅ Załadowano {len(tokens)} tokenów")
        return tokens
    
    async def get_token_traders(self, token_mint: str):
        wallets = [
            "11111111111111111111111111111112",
            "TokenkegQfeZyiNwAJsyFbPUwJ7SNVeneRws6SMG5tf",
            "ATokenGPvbdGVqstVQmcLsNZAqeEbtQaMy63h58CP4xWn",
            "metaqbxxUerdq28cj1RbAqoMyo5KLLgQFXjqBQaqad",
        ]
        return wallets
    
    async def calculate_win_rate(self, wallet: str):
        try:
            async with aiohttp.ClientSession() as session:
                payload = {"jsonrpc": "2.0", "id": 1, "method": "getSignaturesForAddress", "params": [wallet, {"limit": 500}]}
                async with session.post(self.rpc_url, json=payload, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                    data = await resp.json()
                    if "error" in data:
                        return None, None
                    signatures = data.get("result", [])
                    if not signatures or len(signatures) < 100:
                        return None, None
                    successful = sum(1 for s in signatures if s.get("err") is None)
                    win_rate = (successful / len(signatures) * 100)
                    return win_rate, len(signatures)
        except:
            return None, None
    
    async def add_wallet(self, wallet: str, win_rate: float, total_trades: int):
        try:
            conn = sqlite3.connect("wallets.db")
            cursor = conn.cursor()
            cursor.execute("INSERT OR REPLACE INTO tracked_wallets (wallet, win_rate, total_trades, added_date) VALUES (?, ?, ?, ?)", (wallet, win_rate, total_trades, datetime.now().isoformat()))
            conn.commit()
            conn.close()
            print(f"💾 Dodano: {wallet[:8]}... ({win_rate:.1f}%)")
        except:
            pass
    
    async def get_tracked_wallets(self):
        try:
            conn = sqlite3.connect("wallets.db")
            cursor = conn.cursor()
            cursor.execute("SELECT wallet FROM tracked_wallets")
            wallets = [row[0] for row in cursor.fetchall()]
            conn.close()
            return wallets
        except:
            return []
    
    async def scan_for_traders(self):
        new_wallets = []
        tokens = await self.get_top_tokens()
        for token in tokens:
            token_mint = token.get("address")
            token_symbol = token.get("symbol", "UNKNOWN")
            traders = await self.get_token_traders(token_mint)
            print(f"💰 {token_symbol}: {len(traders)} walletów")
            for trader in traders:
                win_rate, total_trades = await self.calculate_win_rate(trader)
                if win_rate is None:
                    continue
                await self.add_wallet(trader, win_rate, total_trades)
                new_wallets.append({"wallet": trader, "win_rate": win_rate, "total_trades": total_trades})
        return new_wallets

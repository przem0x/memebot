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
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tracked_wallets (
                wallet TEXT PRIMARY KEY,
                win_rate REAL,
                total_trades INT,
                added_date TEXT
            )
        """)
        conn.commit()
        conn.close()
    
    async def get_top_tokens(self):
    """Pobierz top tokeny z ostatnich 24h"""
    try:
        async with aiohttp.ClientSession() as session:
            # Dex Screener API - lepiej dla Solany
            url = "https://api.dexscreener.com/latest/dex/tokens"
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                data = await resp.json()
                tokens = data.get("pairs", [])[:20]
                
                # Konwertuj na format jak wcześniej
                formatted = []
                for token in tokens:
                    formatted.append({
                        "address": token.get("baseToken", {}).get("address"),
                        "symbol": token.get("baseToken", {}).get("symbol", "UNKNOWN")
                    })
                
                print(f"✅ Pobrano {len(formatted)} tokenów z Dex Screener")
                return formatted
    except Exception as e:
        print(f"❌ Błąd pobierania tokenów: {e}")
        return []
    
    async def get_token_traders(self, token_mint: str):
        """Pobierz tradery danego tokenu"""
        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "getTokenLargestAccounts",
                    "params": [token_mint]
                }
                async with session.post(self.rpc_url, json=payload, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                    data = await resp.json()
                    accounts = data.get("result", {}).get("value", [])
                    wallets = [acc["address"] for acc in accounts[:50]]
                    return wallets
        except Exception as e:
            print(f"❌ Błąd pobierania traderów: {e}")
            return []
    
    async def calculate_win_rate(self, wallet: str):
        """Oblicz win rate i liczbę tradów"""
        try:
            async with aiohttp.ClientSession() as session:
                # Pobranie transakcji
                payload = {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "getSignaturesForAddress",
                    "params": [wallet, {"limit": 500}]
                }
                async with session.post(self.rpc_url, json=payload, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                    data = await resp.json()
                    
                    if "error" in data:
                        return None, None
                    
                    signatures = data.get("result", [])
                    
                    if not signatures:
                        return None, None
                    
                    # Filtruj ostatni miesiąc
                    one_month_ago = datetime.now() - timedelta(days=30)
                    recent_sigs = []
                    
                    for sig in signatures:
                        if sig.get("blockTime"):
                            tx_date = datetime.fromtimestamp(sig["blockTime"])
                            if tx_date > one_month_ago:
                                recent_sigs.append(sig)
                    
                    total_trades = len(recent_sigs)
                    
                    # Prosta heurystyka: transakcje które się powiodły mają status "Ok"
                    successful = sum(1 for sig in recent_sigs if sig.get("err") is None)
                    
                    # ZMIENIONE FILTRY - łagodniejsze na start
                    if total_trades < 100:  # było 300
                        return None, None
                    
                    win_rate = (successful / total_trades * 100) if total_trades > 0 else 0
                    
                    if win_rate < 40:  # było 50
                        return None, None
                    
                    return win_rate, total_trades
        except Exception as e:
            print(f"⚠️  Błąd liczenia win rate dla {wallet[:8]}...: {e}")
            return None, None
    
    async def add_wallet(self, wallet: str, win_rate: float, total_trades: int):
        """Dodaj wallet do bazy"""
        try:
            conn = sqlite3.connect("wallets.db")
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO tracked_wallets 
                (wallet, win_rate, total_trades, added_date)
                VALUES (?, ?, ?, ?)
            """, (wallet, win_rate, total_trades, datetime.now().isoformat()))
            conn.commit()
            conn.close()
            print(f"💾 Dodano wallet: {wallet[:8]}... ({win_rate:.1f}% | {total_trades} tradów)")
        except Exception as e:
            print(f"❌ Błąd dodawania walletu: {e}")
    
    async def get_tracked_wallets(self):
        """Pobierz listę śledzonych walletów"""
        try:
            conn = sqlite3.connect("wallets.db")
            cursor = conn.cursor()
            cursor.execute("SELECT wallet FROM tracked_wallets")
            wallets = [row[0] for row in cursor.fetchall()]
            conn.close()
            return wallets
        except Exception as e:
            print(f"❌ Błąd pobierania walletów: {e}")
            return []
    
    async def scan_for_traders(self):
        """Główna funkcja - szuka nowych traderów"""
        new_wallets = []
        tokens = await self.get_top_tokens()
        
        print(f"📊 Znaleziono {len(tokens)} top tokenów")
        
        if not tokens:
            print("❌ Brak tokenów do skanowania")
            return new_wallets
        
        for token in tokens:
            token_mint = token.get("address")
            token_symbol = token.get("symbol", "UNKNOWN")
            if not token_mint:
                continue
            
            traders = await self.get_token_traders(token_mint)
            print(f"💰 Token {token_symbol}: {len(traders)} traderów")
            
            for trader in traders:
                win_rate, total_trades = await self.calculate_win_rate(trader)
                
                if win_rate is None or total_trades is None:
                    continue
                
                print(f"  └─ {trader[:8]}... | {total_trades} tradów | {win_rate:.1f}% win rate ✅")
                
                await self.add_wallet(trader, win_rate, total_trades)
                new_wallets.append({
                    "wallet": trader,
                    "win_rate": win_rate,
                    "total_trades": total_trades,
                    "token": token_symbol
                })
        
        return new_wallets

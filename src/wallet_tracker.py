import aiohttp

class WalletTracker:
    def __init__(self, helius_api_key: str):
        self.api_key = helius_api_key
        self.rpc_url = f"https://mainnet.helius-rpc.com/?api-key={helius_api_key}"
    
    async def get_top_wallets(self):
        return ["98765432198765432198765432198765432198765432198"]

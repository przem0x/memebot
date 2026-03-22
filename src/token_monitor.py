class TokenMonitor:
    def __init__(self, helius_api_key: str):
        self.api_key = helius_api_key
    
    async def monitor_wallets(self, wallets):
        """Monitoruj transakcje śledzonych walletów"""
        signals = []
        
        # TODO: Jeśli śledzony wallet robi buy/sell
        # to wysyłaj sygnał
        
        return signals

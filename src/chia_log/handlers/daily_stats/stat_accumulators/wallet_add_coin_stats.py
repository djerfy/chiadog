# std
from datetime import datetime

# project
from .. import WalletAddCoinMessage, WalletAddCoinConsumer, StatAccumulator


class WalletAddCoinStats(WalletAddCoinConsumer, StatAccumulator):
    def __init__(self):
        self._last_reset_time = datetime.now()
        self._total_added_mojos = 0

    def reset(self):
        self._last_reset_time = datetime.now()
        self._total_added_mojos = 0

    def consume(self, obj: WalletAddCoinMessage):
        self._total_added_mojos += obj.amount_mojos

    def get_summary(self) -> str:
        chia_coins = self._total_added_mojos / 1e12
        xch_string = f"{chia_coins:.12f}".rstrip("0").rstrip(".")
        return f"Received 💰: {xch_string} XCH"

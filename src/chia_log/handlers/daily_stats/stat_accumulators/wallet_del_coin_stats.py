# std
from datetime import datetime

# project
from .. import WalletDelCoinMessage, WalletDelCoinConsumer, StatAccumulator


class WalletDelCoinStats(WalletDelCoinConsumer, StatAccumulator):
    def __init__(self):
        self._last_reset_time = datetime.now()
        self._total_deleted_mojos = 0

    def reset(self):
        self._last_reset_time = datetime.now()
        self._total_deleted_mojos = 0

    def consume(self, obj: WalletDelCoinMessage):
        self._total_deleted_mojos += obj.amount_mojos

    def get_summary(self) -> str:
        chia_coins = self._total_deleted_mojos / 1e12
        xch_string = f"{chia_coins:.12f}".rstrip("0").rstrip(".")
        return f"Sent 💸: {xch_string} XCH"

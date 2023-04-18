# std
import logging
from typing import List, Optional

# lib
from confuse import ConfigView

# project
from . import LogHandlerInterface
from ..parsers.wallet_del_coin_parser import WalletDelCoinParser
from .daily_stats.stats_manager import StatsManager
from src.notifier import Event, EventService, EventType, EventPriority


class WalletDelCoinHandler(LogHandlerInterface):
    """This handler parses all logs that report wallet
    receiving XCH and creates user notifications.
    """

    @staticmethod
    def config_name() -> str:
        return "wallet_del_coin_handler"

    def __init__(self, config: ConfigView):
        super().__init__(config)
        self._parser = WalletDelCoinParser()
        self.min_mojos_amount = config["min_mojos_amount"].get(int)
        logging.info(f"Filtering transaction with mojos less than {self.min_mojos_amount}")

    def handle(self, logs: str, stats_manager: Optional[StatsManager] = None) -> List[Event]:
        events = []
        deleted_coin_messages = self._parser.parse(logs)
        if stats_manager:
            stats_manager.consume_wallet_messages(deleted_coin_messages)

        total_mojos = 0
        for coin_msg in deleted_coin_messages:
            logging.info(f"Just sent {coin_msg.amount_mojos} mojos 💰")
            total_mojos += coin_msg.amount_mojos

        if total_mojos > self.min_mojos_amount:
            chia_coins = total_mojos / 1e12
            xch_string = f"{chia_coins:.12f}".rstrip("0").rstrip(".")
            events.append(
                Event(
                    type=EventType.USER,
                    priority=EventPriority.LOW,
                    service=EventService.WALLET,
                    message=f"Just sent {xch_string} XCH 💰",
                )
            )
        elif total_mojos != 0:
            logging.debug(
                f"Filtering out chia coin message since the amount ${total_mojos} sent is less than"
                f"the configured transaction_amount: ${self.min_mojos_amount}"
            )

        return events

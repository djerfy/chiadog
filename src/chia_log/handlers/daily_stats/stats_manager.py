# std
import logging
import re
from datetime import datetime, timedelta
from typing import cast, List, Union
from threading import Thread
from time import sleep

# lib
from confuse import ConfigView

# project
from . import (
    HarvesterActivityConsumer,
    PartialConsumer,
    BlockConsumer,
    WalletAddCoinConsumer,
    WalletDelCoinConsumer,
    FinishedSignageConsumer,
)
from .stat_accumulators.eligible_plots_stats import EligiblePlotsStats
from .stat_accumulators.wallet_add_coin_stats import WalletAddCoinStats
from .stat_accumulators.wallet_del_coin_stats import WalletDelCoinStats
from .stat_accumulators.search_time_stats import SearchTimeStats
from .stat_accumulators.signage_point_stats import SignagePointStats
from .stat_accumulators.found_proof_stats import FoundProofStats
from .stat_accumulators.number_plots_stats import NumberPlotsStats
from .stat_accumulators.found_partial_stats import FoundPartialStats
from .stat_accumulators.found_block_stats import FoundBlockStats
from src.chia_log.parsers.wallet_add_coin_parser import WalletAddCoinMessage
from src.chia_log.parsers.wallet_del_coin_parser import WalletDelCoinMessage
from src.chia_log.parsers.harvester_activity_parser import HarvesterActivityMessage
from src.chia_log.parsers.finished_signage_point_parser import FinishedSignagePointMessage
from src.chia_log.parsers.partial_parser import PartialMessage
from src.chia_log.parsers.block_parser import BlockMessage
from src.notifier.notify_manager import NotifyManager
from src.notifier import Event, EventType, EventPriority, EventService


class StatsManager:
    """Manage all stat accumulators and trigger daily notification to the user
    with a summary from all stats that have been collected for the past 24 hours.
    """

    def __init__(self, config: ConfigView, notify_manager: NotifyManager):
        self._enable = config["enable"].get(bool)
        self._notify_time = self._parse_notify_time(config["time_of_day"].get())
        self._frequency_hours = config["frequency_hours"].get(int)

        if not self._enable:
            logging.warning("Disabled stats and daily notifications")
            return

        logging.info("Enabled stats for daily notifications")
        self._notify_manager = notify_manager
        self._stat_accumulators = [
            WalletAddCoinStats(),
            WalletDelCoinStats(),
            FoundProofStats(),
            FoundPartialStats(),
            FoundBlockStats(),
            SearchTimeStats(),
            NumberPlotsStats(),
            EligiblePlotsStats(),
            SignagePointStats(),
        ]

        logging.info(
            f"Summary notifications will be sent out every {self._frequency_hours} "
            f"hours starting from {self._notify_time['hour']:02d}:{self._notify_time['minute']:02d}"
        )
        self._datetime_next_summary = datetime.now().replace(
            hour=self._notify_time["hour"], minute=self._notify_time["minute"], second=0, microsecond=0
        )
        while datetime.now() > self._datetime_next_summary:
            self._datetime_next_summary += timedelta(hours=self._frequency_hours)

        # Start thread
        self._is_running = True
        self._thread = Thread(target=self._run_loop)
        self._thread.start()

    def consume_wallet_messages(self, objects_added: List[WalletAddCoinMessage], objects_deleted: List[WalletDelCoinMessage]):
        if not self._enable:
            return
        for stat_acc in self._stat_accumulators:
            if isinstance(stat_acc, WalletAddCoinConsumer):
                for obj in objects_added:
                    stat_acc.consume(obj)
            if isinstance(stat_acc, WalletDelCoinConsumer):
                for obj in objects_deleted:
                    stat_acc.consume(obj)

    def consume_harvester_messages(self, objects: List[HarvesterActivityMessage]):
        if not self._enable:
            return
        for stat_acc in self._stat_accumulators:
            if isinstance(stat_acc, HarvesterActivityConsumer):
                for obj in objects:
                    stat_acc.consume(obj)

    def consume_partial_messages(self, objects: List[PartialMessage]):
        if not self._enable:
            return
        for stat_acc in self._stat_accumulators:
            if isinstance(stat_acc, PartialConsumer):
                for obj in objects:
                    stat_acc.consume(obj)

    def consume_block_messages(self, objects: List[BlockMessage]):
        if not self._enable:
            return
        for stat_acc in self._stat_accumulators:
            if isinstance(stat_acc, BlockConsumer):
                for obj in objects:
                    stat_acc.consume(obj)

    def consume_signage_point_messages(self, objects: List[FinishedSignagePointMessage]):
        if not self._enable:
            return
        for stat_acc in self._stat_accumulators:
            if isinstance(stat_acc, FinishedSignageConsumer):
                for obj in objects:
                    stat_acc.consume(obj)

    def _send_daily_notification(self):
        summary = f"Hi! 👋 Here's what happened in the last {self._frequency_hours} hours:\n"
        for stat_acc in self._stat_accumulators:
            summary += "\n" + stat_acc.get_summary()
            stat_acc.reset()

        self._notify_manager.process_events(
            [Event(type=EventType.DAILY_STATS, priority=EventPriority.LOW, service=EventService.DAILY, message=summary)]
        )

    def _run_loop(self):
        while self._is_running:
            if datetime.now() > self._datetime_next_summary:
                self._send_daily_notification()
                self._datetime_next_summary += timedelta(hours=self._frequency_hours)
            sleep(1)

    def stop(self):
        self._is_running = False

    def _parse_notify_time(self, value: Union[str, int], default: dict = {"hour": 21, "minute": 0}) -> dict:
        if type(value) == int:
            return {"hour": value, "minute": 0}

        value = cast(str, value)
        match = re.match(r"(?:[01]\d|2[0-3]):(?:[0-5]\d)", value)
        if match:
            return {"hour": int(value[:2]), "minute": int(value[-2:])}

        return default

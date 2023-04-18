import unittest
from pathlib import Path
import copy
import confuse
from src.chia_log.handlers.wallet_del_coin_handler import WalletDelCoinHandler
from src.notifier import EventType, EventService, EventPriority


class TestWalletDelCoinHandler(unittest.TestCase):
    def setUp(self) -> None:
        config_dir = Path(__file__).resolve().parents[3]
        self.config = confuse.Configuration("chiadog", __name__)
        self.config.set_file(config_dir / "src/default_config.yaml")
        self.handler_config = self.config["handlers"][WalletDelCoinHandler.config_name()]

        self.handler = WalletDelCoinHandler(config=self.handler_config)
        self.example_logs_path = Path(__file__).resolve().parents[1] / "logs/wallet_del_coin"

    def tearDown(self) -> None:
        self.config.clear()

    def testConfig(self):
        self.assertEqual(self.handler_config["min_mojos_amount"].get(int), 0)  # Dependent on default value being 0

    def testNominal(self):
        with open(self.example_logs_path / "nominal.txt", encoding="UTF-8") as f:
            logs = f.readlines()

        events = self.handler.handle("".join(logs))
        self.assertEqual(1, len(events))
        self.assertEqual(events[0].type, EventType.USER, "Unexpected event type")
        self.assertEqual(events[0].priority, EventPriority.LOW, "Unexpected priority")
        self.assertEqual(events[0].service, EventService.WALLET, "Unexpected service")
        self.assertEqual(events[0].message, "Just sent 1.75 XCH 💰")

    def testFloatPrecision(self):
        with open(self.example_logs_path / "small_values.txt", encoding="UTF-8") as f:
            logs = f.readlines()

        events = self.handler.handle("".join(logs))
        self.assertEqual(1, len(events))
        self.assertEqual(events[0].type, EventType.USER, "Unexpected event type")
        self.assertEqual(events[0].priority, EventPriority.LOW, "Unexpected priority")
        self.assertEqual(events[0].service, EventService.WALLET, "Unexpected service")
        self.assertEqual(events[0].message, "Just sent 0.004849173605 XCH 💰")

    def testTransactionAmountFilter(self):
        no_filter_config = self.handler_config
        filter_config = copy.deepcopy(self.handler_config)
        filter_config["min_mojos_amount"].set(500000000000)

        filter_handler = WalletDelCoinHandler(filter_config)
        no_filter_handler = WalletDelCoinHandler(no_filter_config)
        with open(self.example_logs_path / "small_values.txt", encoding="UTF-8") as f:
            logs = f.readlines()
        filter_events = filter_handler.handle("".join(logs))
        self.assertEqual(0, len(filter_events))
        no_filter_events = no_filter_handler.handle("".join(logs))
        self.assertEqual(1, len(no_filter_events))


if __name__ == "__main__":
    unittest.main()

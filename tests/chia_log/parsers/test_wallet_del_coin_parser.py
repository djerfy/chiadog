import unittest
from pathlib import Path
from src.chia_log.parsers.wallet_del_coin_parser import WalletDelCoinParser


class TestWalletDelCoinParser(unittest.TestCase):
    def setUp(self) -> None:
        self.parser = WalletDelCoinParser()
        self.example_logs_path = Path(__file__).resolve().parents[1] / "logs/wallet_del_coin"
        with open(self.example_logs_path / "nominal.txt", encoding="UTF-8") as f:
            self.logs_nominal = f.read()

    def testBasicParsing(self):
        added_coins = self.parser.parse(self.logs_nominal)
        total_mojos = 0
        for coin in added_coins:
            total_mojos += coin.amount_mojos

        chia = total_mojos / 1e12
        self.assertEqual(1.75, chia)


if __name__ == "__main__":
    unittest.main()

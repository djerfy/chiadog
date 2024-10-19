# std
import re
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import List

# lib
from dateutil import parser as dateutil_parser


@dataclass
class WalletDelCoinMessage:
    timestamp: datetime
    amount_mojos: int


class WalletDelCoinParser:
    """This class can parse info log messages from the chia wallet

    You need to have enabled "log_level: INFO" in your chia config.yaml
    The chia config.yaml is usually under ~/.chia/mainnet/config/config.yaml
    """

    def __init__(self):
        logging.debug("Enabled parser for wallet activity - deleted coins.")
        self._regex = re.compile(
            r"([0-9:.]*)(?:\s[0-9:.]*)? wallet (?:src|chia).wallet.wallet_node(?:\s*)?: "
            r"INFO\s*request coin: (?:.*)'?amount'?: ([0-9]*)(\s})?, "
            r"\s*spent_height: Some\((?:\d*)\), created_height: Some\((?:\d*)\)"
        )

    def parse(self, logs: str) -> List[WalletDelCoinMessage]:
        """Parses all harvester activity messages from a bunch of logs

        :param logs: String of logs - can be multi-line
        :returns: A list of parsed messages - can be empty
        """

        parsed_messages = []
        matches = self._regex.findall(logs)
        for match in matches:
            parsed_messages.append(
                WalletDelCoinMessage(
                    timestamp=dateutil_parser.parse(match[0]),
                    amount_mojos=int(match[1]),
                )
            )

        return parsed_messages

# std
from abc import ABC, abstractmethod

# project
from ...parsers.finished_signage_point_parser import FinishedSignagePointMessage
from ...parsers.harvester_activity_parser import HarvesterActivityMessage
from ...parsers.wallet_add_coin_parser import WalletAddCoinMessage
from ...parsers.wallet_del_coin_parser import WalletDelCoinMessage
from ...parsers.partial_parser import PartialMessage
from ...parsers.block_parser import BlockMessage


class FinishedSignageConsumer(ABC):
    @abstractmethod
    def consume(self, obj: FinishedSignagePointMessage):
        pass


class HarvesterActivityConsumer(ABC):
    @abstractmethod
    def consume(self, obj: HarvesterActivityMessage):
        pass


class PartialConsumer(ABC):
    @abstractmethod
    def consume(self, obj: PartialMessage):
        pass


class BlockConsumer(ABC):
    @abstractmethod
    def consume(self, obj: BlockMessage):
        pass


class WalletAddCoinConsumer(ABC):
    @abstractmethod
    def consume(self, obj: WalletAddCoinMessage):
        pass


class WalletDelCoinConsumer(ABC):
    @abstractmethod
    def consume(self, obj: WalletDelCoinMessage):
        pass


class StatAccumulator(ABC):
    @abstractmethod
    def get_summary(self) -> str:
        pass

    @abstractmethod
    def reset(self):
        pass

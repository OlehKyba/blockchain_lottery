from typing import cast

from brownie import Lottery, MockV3Aggregator
from brownie.network.contract import ContractContainer

Lottery = cast(ContractContainer, Lottery)
MockV3Aggregator = cast(ContractContainer, MockV3Aggregator)

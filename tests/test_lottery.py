import typing as t

import pytest
from brownie import network, web3

from bl.account import get_main_account
from bl.config_utils import get_dev_networks, get_price_feed_address
from bl.contracts import Lottery
from bl.deploy import deploy_lottery, deploy_price_feed_mock

if t.TYPE_CHECKING:
    from brownie.network.account import Account
    from brownie.network.contract import ProjectContract

DECIMALS: t.Final[int] = 8
INITIAL_VALUE: t.Final[int] = 259829000000  # 2598,29 usd
USD_ENTRANCE_FEE: t.Final[int] = 50


@pytest.fixture(scope="session")
def dev_networks() -> set[str]:
    return get_dev_networks()


@pytest.fixture(scope="session")
def main_account() -> "Account":
    return get_main_account()


@pytest.fixture(scope="session")
def price_feed_address(dev_networks: set[str], main_account: "Account") -> str:
    active_network = network.show_active()
    if active_network in dev_networks:
        price_feed = deploy_price_feed_mock(main_account, DECIMALS, INITIAL_VALUE)
        return price_feed.address
    return get_price_feed_address(active_network)


@pytest.fixture()
def lottery(
    main_account: "Account",
    price_feed_address: str,
) -> "ProjectContract":
    lottery = deploy_lottery(
        account=main_account,
        price_feed_address=price_feed_address,
        usd_entrance_fee=USD_ENTRANCE_FEE,
        is_publish_source=False,
    )
    yield lottery
    Lottery.remove(lottery)


def test_get_entrance_fee(lottery: "ProjectContract") -> None:
    entrance_fee = lottery.getEntranceFee()

    assert entrance_fee > web3.toWei(0.01923, "ether")
    assert entrance_fee < web3.toWei(0.01925, "ether")

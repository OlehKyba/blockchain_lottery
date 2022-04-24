import typing as t
from enum import Enum

import pytest
from brownie import network, web3
from brownie.exceptions import VirtualMachineError

from bl.account import get_main_account, get_secondary_account
from bl.config_utils import get_dev_networks, get_price_feed_address
from bl.contracts import Lottery
from bl.deploy import deploy_lottery, deploy_price_feed_mock

if t.TYPE_CHECKING:
    from brownie.network.account import Account
    from brownie.network.contract import ProjectContract

DECIMALS: t.Final[int] = 8
INITIAL_VALUE: t.Final[int] = 259829000000  # 2598,29 usd
USD_ENTRANCE_FEE: t.Final[int] = 50


class LotteryStates(Enum):
    START = 0
    CLOSED = 1
    CALCULATING = 2


@pytest.fixture(scope="session")
def dev_networks() -> set[str]:
    return get_dev_networks()


@pytest.fixture(scope="session")
def main_account() -> "Account":
    return get_main_account()


@pytest.fixture(scope="session")
def secondary_account() -> "Account":
    return get_secondary_account()


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


def test_enter_should_raise_err_when_lottery_not_started(
    lottery: "ProjectContract",
    secondary_account: "Account",
) -> None:
    with pytest.raises(VirtualMachineError) as err_info:
        lottery.enter(
            {
                "from": secondary_account,
                "value": web3.toWei(0.02, "ether"),
            }
        )

    assert err_info.match("Lottery state must be OPEN!")


def test_enter_should_raise_err_when_lottery_not_in_start_state(
    lottery: "ProjectContract",
    main_account: "Account",
    secondary_account: "Account",
) -> None:
    lottery.startLottery({"from": main_account})

    with pytest.raises(VirtualMachineError) as err_info:
        lottery.enter(
            {
                "from": secondary_account,
                "value": web3.toWei(0.018, "ether"),
            }
        )

    assert err_info.match("Not enough ETH!")


def test_enter_should_success(
    lottery: "ProjectContract",
    main_account: "Account",
    secondary_account: "Account",
) -> None:
    lottery.startLottery({"from": main_account})

    lottery.enter(
        {
            "from": secondary_account,
            "value": web3.toWei(0.02, "ether"),
        }
    )

    assert secondary_account.address == lottery.players(0)


def test_start_lottery_should_raise_err_when_not_owner_request(
    lottery: "ProjectContract",
    secondary_account: "Account",
) -> None:
    with pytest.raises(VirtualMachineError) as exe_info:
        lottery.startLottery({"from": secondary_account})

    assert exe_info.match("Ownable: caller is not the owner")


def test_start_lottery_should_raise_err_when_not_close_state(
    lottery: "ProjectContract",
    main_account: "Account",
) -> None:
    # set state in START!
    lottery.startLottery({"from": main_account})

    with pytest.raises(VirtualMachineError) as exe_info:
        lottery.startLottery({"from": main_account})

    assert exe_info.match("Lottery state must be CLOSED!")


def test_start_lottery_should_success(
    lottery: "ProjectContract",
    main_account: "Account",
) -> None:
    lottery.startLottery({"from": main_account})

    assert LotteryStates(lottery.state()) == LotteryStates.START


def test_end_lottery_should_raise_err_when_not_owner_request(
    lottery: "ProjectContract",
    secondary_account: "Account",
) -> None:
    with pytest.raises(VirtualMachineError) as exe_info:
        lottery.endLottery({"from": secondary_account})

    assert exe_info.match("Ownable: caller is not the owner")


def test_end_lottery_should_raise_err_when_not_open_state(
    lottery: "ProjectContract",
    main_account: "Account",
) -> None:
    with pytest.raises(VirtualMachineError) as exe_info:
        lottery.endLottery({"from": main_account})

    assert exe_info.match("Lottery state must be OPEN!")


def test_end_lottery_should_success(
    lottery: "ProjectContract",
    main_account: "Account",
) -> None:
    lottery.startLottery({"from": main_account})

    lottery.endLottery({"from": main_account})

    assert LotteryStates(lottery.state()) == LotteryStates.CALCULATING

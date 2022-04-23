import logging
import typing as t

from brownie import network

from bl.config_utils import (
    get_dev_networks,
    get_is_publish_source,
    get_price_feed_address,
    get_usd_entrance_fee,
)
from bl.contracts import Lottery, MockV3Aggregator

if t.TYPE_CHECKING:
    from brownie.network.account import Account
    from brownie.network.contract import ProjectContract

USD_ENTRANCE_FEE: t.Final[int] = 50
log = logging.getLogger(__name__)


def deploy_price_feed_mock(
    account: "Account",
    decimals: int = 8,
    init_value: int = 200000000000,
) -> "ProjectContract":
    log.info(
        f"[Deploy] Deploy MockV3Aggregator with: " f"{decimals=}, " f"{init_value=}"
    )
    price_feed = MockV3Aggregator.deploy(
        decimals,
        init_value,
        {"from": account},
    )

    log.info(f"[Deploy] Finish MockV3Aggregator deploy: {price_feed.address=}!")
    return price_feed


def deploy_lottery(
    account: "Account",
    price_feed_address: t.Optional[str] = None,
    usd_entrance_fee: t.Optional[int] = None,
    is_publish_source: t.Optional[bool] = None,
) -> "ProjectContract":
    active_network = network.show_active()
    dev_networks = get_dev_networks()

    if is_publish_source is None:
        is_publish_source = get_is_publish_source(active_network)

    if price_feed_address is None:
        price_feed_address = get_price_feed_address(active_network)

    if usd_entrance_fee is None:
        usd_entrance_fee = get_usd_entrance_fee(USD_ENTRANCE_FEE)

    log.info(
        f"[Deploy] Start Lottery "
        f"contract deploy with: "
        f"{account=}, "
        f"{price_feed_address=}, "
        f"{usd_entrance_fee=}, "
        f"{active_network=}, "
        f"{is_publish_source=}"
    )

    if not price_feed_address and active_network in dev_networks:
        log.warning(
            f"[Deploy] No price feed address and {active_network} "
            f"is development network: deploy price feed contract!"
        )
        price_feed = deploy_price_feed_mock(account)
        price_feed_address = price_feed.address

    lottery = Lottery.deploy(
        price_feed_address,
        usd_entrance_fee,
        {"from": account},
        publish_source=is_publish_source,
    )

    log.info(f"[Deploy] Finish Lottery deploy: {lottery.address=}!")
    return lottery

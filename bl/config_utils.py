from brownie import config


def get_dev_networks() -> set[str]:
    return config["networks"].get("dev_networks", set())


def get_is_publish_source(network: str) -> bool:
    return config["networks"][network].get("is_publish_source", False)


def get_price_feed_address(network: str) -> str:
    return config["networks"][network]["price_feed_address"]


def get_usd_entrance_fee(default: int = 50) -> int:
    return config["lottery"].get("usd_entrance_fee", default)

import typing as t

from brownie import accounts

if t.TYPE_CHECKING:
    from brownie.network.account import Account


def get_main_account() -> "Account":
    return accounts[0]


def get_secondary_account() -> "Account":
    return accounts[1]


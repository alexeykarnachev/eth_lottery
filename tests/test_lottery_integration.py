import time

import pytest
from brownie import exceptions
from scripts.deploy_lottery import deploy_lottery
from scripts.utils import fund_with_link, get_account, get_contract, is_local_network
from web3 import Web3


def test_can_pick_winner():
    if is_local_network():
        pytest.skip()

    lottery = deploy_lottery()
    account = get_account()
    lottery.startLottery({"from": account})
    lottery.enter({"from": account, "value": lottery.getEntranceFee()})
    lottery.enter({"from": account, "value": lottery.getEntranceFee()})
    lottery.enter({"from": account, "value": lottery.getEntranceFee()})

    fund_with_link(lottery)
    lottery.endLottery({"from": account})
    print("Sleeping for 3 minutes to wait lottery end...")
    time.sleep(180)

    assert lottery.recentWinner() == account
    assert lottery.balance() == 0

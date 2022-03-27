import pytest
from brownie import exceptions
from scripts.deploy_lottery import deploy_lottery
from scripts.utils import fund_with_link, get_account, get_contract, is_local_network
from web3 import Web3


def test_get_entrance_fee():
    if not is_local_network():
        pytest.skip()

    lottery = deploy_lottery()
    wei_fee = lottery.getEntranceFee()
    expected_wei_fee = Web3.toWei(0.025, "ether")
    assert expected_wei_fee == wei_fee


def test_cant_enter():
    if not is_local_network():
        pytest.skip()

    lottery = deploy_lottery()
    with pytest.raises(exceptions.VirtualMachineError):
        lottery.enter({"from": get_account(), "value": lottery.getEntranceFee()})


def test_can_enter():
    if not is_local_network():
        pytest.skip()

    lottery = deploy_lottery()
    account = get_account()
    lottery.startLottery({"from": account})
    lottery.enter({"from": account, "value": lottery.getEntranceFee()})

    assert lottery.players(0) == account


def test_can_end_lottery():
    if not is_local_network():
        pytest.skip()

    lottery = deploy_lottery()
    account = get_account()
    lottery.startLottery({"from": account})
    lottery.enter({"from": account, "value": lottery.getEntranceFee()})
    fund_with_link(lottery)
    lottery.endLottery({"from": account})
    assert lottery.lottery_state() == 2


def test_can_pick_winner_correctly():
    if not is_local_network():
        pytest.skip()

    lottery = deploy_lottery()
    account = get_account()
    lottery.startLottery({"from": account})
    lottery.enter({"from": account, "value": lottery.getEntranceFee()})
    lottery.enter({"from": get_account(idx=1), "value": lottery.getEntranceFee()})
    lottery.enter({"from": get_account(idx=2), "value": lottery.getEntranceFee()})
    fund_with_link(lottery)
    tx = lottery.endLottery({"from": account})

    mock_rnd = 777
    winner_idx = mock_rnd % 3
    winner = get_account(idx=winner_idx)
    winner_start_balance = winner.balance()
    lottery_start_balance = lottery.balance()

    request_id = tx.events["RequestedRandomness"]["requestId"]
    get_contract("vrf_coordinator").callBackWithRandomness(
        request_id, mock_rnd, lottery.address, {"from": account}
    )

    assert lottery.recentWinner() == winner
    assert lottery.balance() == 0
    assert winner.balance() == winner_start_balance + lottery_start_balance

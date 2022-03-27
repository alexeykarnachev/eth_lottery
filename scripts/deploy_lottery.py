from brownie import Lottery, config, network

from scripts.utils import fund_with_link, get_account, get_contract


def deploy_lottery():
    account = get_account()
    lottery = Lottery.deploy(
        get_contract("eth_usd_price_feed").address,
        get_contract("vrf_coordinator").address,
        get_contract("link_token").address,
        config["networks"][network.show_active()]["fee"],
        config["networks"][network.show_active()]["keyhash"],
        {"from": account},
        publish_source=config["networks"][network.show_active()].get("verify", False),
    )

    print("Lottery deployed")
    return lottery


def start_lottery():
    account = get_account()
    lottery = Lottery[-1]
    tx = lottery.startLottery({"from": account})
    tx.wait(1)
    print("Lottery started")


def enter_lottery():
    account = get_account()
    lottery = Lottery[-1]
    value = lottery.getEntranceFee() + 100000000
    tx = lottery.enter({"from": account, "value": value})
    tx.wait(1)
    print("Lottery entered")


def end_lottery():
    account = get_account()
    lottery = Lottery[-1]

    tx = fund_with_link(lottery.address)
    tx.wait(1)

    end_tx = lottery.endLottery({"from": account, "gas_limit": 20000000})
    end_tx.wait(1)
    # time.sleep(4)

    print(f"Winner: {lottery.recentWinner()}")


def main():
    deploy_lottery()
    start_lottery()
    enter_lottery()
    end_lottery()

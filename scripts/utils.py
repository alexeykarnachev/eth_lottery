from brownie import (
    Contract,
    LinkToken,
    MockV3Aggregator,
    VRFCoordinatorMock,
    accounts,
    config,
    network,
)

_FORKED_LOCAL_ENVIRONMENTS = {"mainnet-fork", "mainnet-fork-dev"}
_LOCAL_BLOCKCHAIN_ENVIRONMENTS = {"development", "ganache-local"}
_CONTRACT_TO_MOCK = {
    "eth_usd_price_feed": MockV3Aggregator,
    "vrf_coordinator": VRFCoordinatorMock,
    "link_token": LinkToken,
}


def is_local_network():
    return network.show_active() in _LOCAL_BLOCKCHAIN_ENVIRONMENTS


def get_account(idx=None, id_=None):
    active_network = network.show_active()
    if idx is not None:
        return accounts[idx]

    if id_:
        return accounts.load(id_)

    if (
        active_network in _LOCAL_BLOCKCHAIN_ENVIRONMENTS
        or active_network in _FORKED_LOCAL_ENVIRONMENTS
    ):
        return accounts[0]

    return accounts.add(config["wallets"]["from_key"])


def get_contract(contract_name):
    """Grabs the contract address from the brownie config if defined,
    otherwise, it will deploy a mock version of that contract, and
    return that mock contract.

    :param contract_name: Name of the contract

    :return: brownie.network.contract.ProjectContract: the most recently deployed
        version of this contract.
    """
    contract_type = _CONTRACT_TO_MOCK[contract_name]
    if network.show_active() in _LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        if len(contract_type) == 0:
            deploy_mocks()
        contract = contract_type[-1]
    else:
        contract_address = config["networks"][network.show_active()][contract_name]
        contract = Contract.from_abi(
            contract_type._name, contract_address, contract_type.abi
        )
    return contract


def deploy_mocks(decimals=8, initial_value=int(2000 * 1e8)):
    account = get_account()
    MockV3Aggregator.deploy(decimals, initial_value, {"from": account})
    link_token = LinkToken.deploy({"from": account})
    VRFCoordinatorMock.deploy(link_token.address, {"from": account})
    print("Mocks deployed")


def fund_with_link(contract_address, account=None, link_token=None, amount=int(2e17)):
    account = account or get_account()
    link_token = link_token or get_contract("link_token")
    tx = link_token.transfer(contract_address, amount, {"from": account})
    tx.wait(1)

    print(f"Fund contract: {tx}")
    return tx

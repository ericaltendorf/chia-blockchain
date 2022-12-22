import aiohttp

from pprint import pprint
from typing import Optional

from chia.cmds.cmds_util import get_wallet
from chia.rpc.full_node_rpc_client import FullNodeRpcClient
from chia.rpc.wallet_rpc_client import WalletRpcClient
from chia.util.config import load_config
from chia.util.default_root import DEFAULT_ROOT_PATH
from chia.util.ints import uint16


async def get_node_client(full_node_rpc_port: Optional[int]):
    try:
        config = load_config(DEFAULT_ROOT_PATH, "config.yaml")
        self_hostname = config["self_hostname"]
        if full_node_rpc_port is None:
            full_node_rpc_port = config["full_node"]["rpc_port"]
        full_node_client = await FullNodeRpcClient.create(
            self_hostname, uint16(full_node_rpc_port), DEFAULT_ROOT_PATH, config
        )
        return full_node_client
    except Exception as e:
        if isinstance(e, aiohttp.ClientConnectorError):
            pprint(f"Connection error. Check if full node is running at {full_node_rpc_port}")
        else:
            pprint(f"Exception from 'full node' {e}")
        return None


async def get_wallet_client(wallet_rpc_port: Optional[int]):
    try:
        config = load_config(DEFAULT_ROOT_PATH, "config.yaml")
        self_hostname = config["self_hostname"]
        if wallet_rpc_port is None:
            wallet_rpc_port = config["wallet"]["rpc_port"]
        wallet_client = await WalletRpcClient.create(self_hostname, uint16(wallet_rpc_port), DEFAULT_ROOT_PATH, config)
        return wallet_client
    except Exception as e:
        if isinstance(e, aiohttp.ClientConnectorError):
            pprint(f"Connection error. Check if wallet is running at {wallet_rpc_port}")
        else:
            pprint(f"Exception from 'wallet' {e}")
        return None


async def get_node_and_wallet_clients(
    full_node_rpc_port: Optional[int], wallet_rpc_port: Optional[int], fingerprint: Optional[int]
):
    try:
        full_node_client = await get_node_client(full_node_rpc_port)
        assert full_node_client is not None
        _wallet_client = await get_wallet_client(wallet_rpc_port)
        assert _wallet_client is not None
        # return full_node_client, _wallet_client # wjb how best to do get_wallet
        # wallet_client_f = await get_wallet(_wallet_client, fingerprint)
        # assert wallet_client_f is not None
        # wallet_client, _ = wallet_client_f
        wallet_client = await _wallet_client.log_in(fingerprint)
        return full_node_client, _wallet_client
    except Exception as e:
        if isinstance(e, aiohttp.ClientConnectorError):
            pprint("Connection error. Check if full node and wallet are running.")
        else:
            pprint(f"Exception from 'node or wallet' {e}")
        return None, None


def get_additional_data():
    config = load_config(DEFAULT_ROOT_PATH, "config.yaml")
    selected_network = config["farmer"]["selected_network"]
    return bytes.fromhex(config["farmer"]["network_overrides"]["constants"][selected_network]["GENESIS_CHALLENGE"])
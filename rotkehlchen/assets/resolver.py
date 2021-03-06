import json
import os
from typing import Any, Dict, List, Optional

from rotkehlchen.typing import AssetData, AssetType, ChecksumEthAddress, EthTokenInfo

asset_type_mapping = {
    'fiat': AssetType.FIAT,
    'own chain': AssetType.OWN_CHAIN,
    'ethereum token and own chain': AssetType.OWN_CHAIN,
    'ethereum token and more': AssetType.ETH_TOKEN_AND_MORE,
    'ethereum token': AssetType.ETH_TOKEN,
    'omni token': AssetType.OMNI_TOKEN,
    'neo token': AssetType.NEO_TOKEN,
    'counterparty token': AssetType.XCP_TOKEN,
    'bitshares token': AssetType.BTS_TOKEN,
    'ardor token': AssetType.ARDOR_TOKEN,
    'nxt token': AssetType.NXT_TOKEN,
    'Ubiq token': AssetType.UBIQ_TOKEN,
    'Nubits token': AssetType.NUBITS_TOKEN,
    'Burst token': AssetType.BURST_TOKEN,
    'waves token': AssetType.WAVES_TOKEN,
    'qtum token': AssetType.QTUM_TOKEN,
    'stellar token': AssetType.STELLAR_TOKEN,
    'tron token': AssetType.TRON_TOKEN,
    'ontology token': AssetType.ONTOLOGY_TOKEN,
    'exchange specific': AssetType.EXCHANGE_SPECIFIC,
    'vechain token': AssetType.VECHAIN_TOKEN,
    'binance token': AssetType.BINANCE_TOKEN,
    'eos token': AssetType.EOS_TOKEN,
}


class AssetResolver():
    __instance = None
    assets: Dict[str, Dict[str, Any]] = {}
    eth_token_info: Optional[List[EthTokenInfo]] = None

    def __new__(cls) -> 'AssetResolver':
        if AssetResolver.__instance is not None:
            return AssetResolver.__instance  # type: ignore

        AssetResolver.__instance = object.__new__(cls)

        dir_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
        with open(os.path.join(dir_path, 'data', 'all_assets.json'), 'r') as f:
            assets = json.loads(f.read())

        AssetResolver.__instance.assets = assets
        return AssetResolver.__instance

    @staticmethod
    def is_identifier_canonical(asset_identifier: str) -> bool:
        """Checks if an asset identifier is canonical"""
        return asset_identifier in AssetResolver().assets

    @staticmethod
    def get_asset_data(asset_identifier: str) -> AssetData:
        """Get all asset data from the known assets file for valid asset symbol"""
        data = AssetResolver().assets[asset_identifier]
        asset_type = asset_type_mapping[data['type']]
        result = AssetData(
            identifier=asset_identifier,
            symbol=data['symbol'],
            name=data['name'],
            # If active is in the data use it, else we assume it's true
            active=data.get('active', True),
            asset_type=asset_type,
            started=data.get('started', None),
            ended=data.get('ended', None),
            forked=data.get('forked', None),
            swapped_for=data.get('swapped_for', None),
            ethereum_address=data.get('ethereum_address', None),
            decimals=data.get('ethereum_token_decimals', None),
        )
        return result

    @staticmethod
    def get_all_eth_token_info() -> List[EthTokenInfo]:
        if AssetResolver().eth_token_info is not None:
            return AssetResolver().eth_token_info  # type: ignore
        all_tokens = []

        for identifier, asset_data in AssetResolver().assets.items():
            asset_type = asset_type_mapping[asset_data['type']]
            if asset_type not in (AssetType.ETH_TOKEN_AND_MORE, AssetType.ETH_TOKEN):
                continue

            all_tokens.append(EthTokenInfo(
                identifier=identifier,
                address=ChecksumEthAddress(asset_data['ethereum_address']),
                symbol=asset_data['symbol'],
                name=asset_data['name'],
                decimals=int(asset_data['ethereum_token_decimals']),
            ))

        AssetResolver().eth_token_info = all_tokens
        return all_tokens

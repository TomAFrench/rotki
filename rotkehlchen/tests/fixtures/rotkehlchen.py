import base64
from collections import namedtuple
from unittest.mock import patch

import pytest

import rotkehlchen.tests.utils.exchanges as exchange_tests
from rotkehlchen.db.settings import DBSettings
from rotkehlchen.history import PriceHistorian
from rotkehlchen.premium.premium import Premium, PremiumCredentials
from rotkehlchen.rotkehlchen import Rotkehlchen
from rotkehlchen.tests.utils.api import create_api_server
from rotkehlchen.tests.utils.database import (
    add_blockchain_accounts_to_db,
    add_manually_tracked_balances_to_test_db,
    add_settings_to_test_db,
    add_tags_to_test_db,
    maybe_include_cryptocompare_key,
    maybe_include_etherscan_key,
)
from rotkehlchen.tests.utils.factories import make_random_b64bytes
from rotkehlchen.tests.utils.history import maybe_mock_historical_price_queries
from rotkehlchen.tests.utils.zerion import create_zerion_patch, wait_until_zerion_is_initialized


@pytest.fixture
def start_with_logged_in_user():
    return True


@pytest.fixture(scope='session')
def session_start_with_logged_in_user():
    return True


@pytest.fixture
def start_with_valid_premium():
    return False


@pytest.fixture
def rotki_premium_credentials() -> PremiumCredentials:
    return PremiumCredentials(
        given_api_key=base64.b64encode(make_random_b64bytes(128)).decode(),
        given_api_secret=base64.b64encode(make_random_b64bytes(128)).decode(),
    )


@pytest.fixture()
def cli_args(data_dir):
    args = namedtuple('args', [
        'sleep_secs',
        'data_dir',
        'zerorpc_port',
        'ethrpc_endpoint',
        'logfile',
        'logtarget',
        'loglevel',
        'logfromothermodules',
    ])
    args.loglevel = 'debug'
    args.logfromothermodules = False
    args.sleep_secs = 60
    args.data_dir = data_dir
    return args


def initialize_mock_rotkehlchen_instance(
        rotki,
        start_with_logged_in_user,
        start_with_valid_premium,
        db_password,
        rotki_premium_credentials,
        username,
        blockchain_accounts,
        include_etherscan_key,
        include_cryptocompare_key,
        should_mock_price_queries,
        mocked_price_queries,
        ethereum_modules,
        db_settings,
        ignored_assets,
        tags,
        manually_tracked_balances,
        default_mock_price_value,
        ethereum_manager_connect_at_start,
):
    if not start_with_logged_in_user:
        return

    # Mock the initial get settings to include the specified ethereum modules
    def mock_get_settings() -> DBSettings:
        settings = DBSettings(active_modules=ethereum_modules)
        return settings
    settings_patch = patch.object(rotki, 'get_settings', side_effect=mock_get_settings)

    # Do not connect to the usual nodes at start by default. Do not want to spam
    # them during our tests. It's configurable per test, with the default being nothing
    rpcconnect_patch = patch(
        'rotkehlchen.rotkehlchen.ETHEREUM_NODES_TO_CONNECT_AT_START',
        new=ethereum_manager_connect_at_start,
    )
    zerion_patch = create_zerion_patch()

    with settings_patch, zerion_patch, rpcconnect_patch:
        rotki.unlock_user(
            user=username,
            password=db_password,
            create_new=True,
            sync_approval='no',
            premium_credentials=None,
        )
        wait_until_zerion_is_initialized(rotki.chain_manager)

    if start_with_valid_premium:
        rotki.premium = Premium(rotki_premium_credentials)
        rotki.premium_sync_manager.premium = rotki.premium

    # After unlocking when all objects are created we need to also include
    # customized fixtures that may have been set by the tests
    rotki.chain_manager.accounts = blockchain_accounts
    add_settings_to_test_db(rotki.data.db, db_settings, ignored_assets)
    maybe_include_etherscan_key(rotki.data.db, include_etherscan_key)
    maybe_include_cryptocompare_key(rotki.data.db, include_cryptocompare_key)
    add_blockchain_accounts_to_db(rotki.data.db, blockchain_accounts)
    add_tags_to_test_db(rotki.data.db, tags)
    add_manually_tracked_balances_to_test_db(rotki.data.db, manually_tracked_balances)
    maybe_mock_historical_price_queries(
        historian=PriceHistorian(),
        should_mock_price_queries=should_mock_price_queries,
        mocked_price_queries=mocked_price_queries,
        default_mock_value=default_mock_price_value,
    )


@pytest.fixture()
def uninitialized_rotkehlchen(cli_args, inquirer):  # pylint: disable=unused-argument
    """A rotkehlchen instance that has only had __init__ run but is not unlocked

    Adding the inquirer fixture as a requirement to make sure that any mocking that
    happens at the inquirer level is reflected in the tests.

    For this to happen inquirer fixture must be initialized before Rotkehlchen so
    that the inquirer initialization in Rotkehlchen's __init__ uses the fixture's instance
    """
    return Rotkehlchen(cli_args)


@pytest.fixture()
def rotkehlchen_api_server(
        uninitialized_rotkehlchen,
        api_port,
        start_with_logged_in_user,
        start_with_valid_premium,
        db_password,
        rotki_premium_credentials,
        username,
        blockchain_accounts,
        include_etherscan_key,
        include_cryptocompare_key,
        should_mock_price_queries,
        mocked_price_queries,
        ethereum_modules,
        db_settings,
        ignored_assets,
        tags,
        manually_tracked_balances,
        default_mock_price_value,
        ethereum_manager_connect_at_start,
):
    """A partially mocked rotkehlchen server instance"""

    api_server = create_api_server(rotki=uninitialized_rotkehlchen, port_number=api_port)

    initialize_mock_rotkehlchen_instance(
        rotki=api_server.rest_api.rotkehlchen,
        start_with_logged_in_user=start_with_logged_in_user,
        start_with_valid_premium=start_with_valid_premium,
        db_password=db_password,
        rotki_premium_credentials=rotki_premium_credentials,
        username=username,
        blockchain_accounts=blockchain_accounts,
        include_etherscan_key=include_etherscan_key,
        include_cryptocompare_key=include_cryptocompare_key,
        should_mock_price_queries=should_mock_price_queries,
        mocked_price_queries=mocked_price_queries,
        ethereum_modules=ethereum_modules,
        db_settings=db_settings,
        ignored_assets=ignored_assets,
        tags=tags,
        manually_tracked_balances=manually_tracked_balances,
        default_mock_price_value=default_mock_price_value,
        ethereum_manager_connect_at_start=ethereum_manager_connect_at_start,
    )
    return api_server


@pytest.fixture()
def rotkehlchen_instance(
        uninitialized_rotkehlchen,
        start_with_logged_in_user,
        start_with_valid_premium,
        db_password,
        rotki_premium_credentials,
        username,
        blockchain_accounts,
        include_etherscan_key,
        include_cryptocompare_key,
        should_mock_price_queries,
        mocked_price_queries,
        ethereum_modules,
        db_settings,
        ignored_assets,
        tags,
        manually_tracked_balances,
        default_mock_price_value,
        ethereum_manager_connect_at_start,
):
    """A partially mocked rotkehlchen instance"""

    initialize_mock_rotkehlchen_instance(
        rotki=uninitialized_rotkehlchen,
        start_with_logged_in_user=start_with_logged_in_user,
        start_with_valid_premium=start_with_valid_premium,
        db_password=db_password,
        rotki_premium_credentials=rotki_premium_credentials,
        username=username,
        blockchain_accounts=blockchain_accounts,
        include_etherscan_key=include_etherscan_key,
        include_cryptocompare_key=include_cryptocompare_key,
        should_mock_price_queries=should_mock_price_queries,
        mocked_price_queries=mocked_price_queries,
        ethereum_modules=ethereum_modules,
        db_settings=db_settings,
        ignored_assets=ignored_assets,
        tags=tags,
        manually_tracked_balances=manually_tracked_balances,
        default_mock_price_value=default_mock_price_value,
        ethereum_manager_connect_at_start=ethereum_manager_connect_at_start,
    )
    return uninitialized_rotkehlchen


@pytest.fixture()
def rotkehlchen_api_server_with_exchanges(
        rotkehlchen_api_server,
        added_exchanges,
):
    """Adds mock exchange objects to the rotkehlchen_server fixture"""
    exchanges = rotkehlchen_api_server.rest_api.rotkehlchen.exchange_manager.connected_exchanges
    rotki = rotkehlchen_api_server.rest_api.rotkehlchen
    for exchange_name in added_exchanges:

        if exchange_name in ('coinbasepro', 'coinbase', 'gemini'):
            # TODO: Add support for the above exchanges in tests too
            continue

        create_fn = getattr(exchange_tests, f'create_test_{exchange_name}')
        exchanges[exchange_name] = create_fn(
            database=rotki.data.db,
            msg_aggregator=rotki.msg_aggregator,
        )

    return rotkehlchen_api_server

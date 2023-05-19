"""
Bot Building - Structure and Helper Functions

- Built-in python data types where possible
- Python dictionaries over dataframes (for now)
- Bot naming: network + pair (ie., traderjoe_sspell_spell.py)
- Module imports: from brownie import *             allows calling functions directly network.connect() or accounts.load() instead of brownie.network.connect()

- Python-dotenv
- GLOBAL CONSTANTS python convention UPPERCASE
- Helper values for time
- Bot Options
- Swap Thresholds and Slippage
    • THRESHOLD_SPELL_TO_SSPELL: how close bot's threshold for swapping SPELL for sSPELL compared to base Abracadabra staking rate
    • THRESHOLD_SSPELL_TO_SPELL: how close bot's threshold for swapping sSPELL for SPELL compared to base Abracadabra staking rate

- Helper Functions (covered later)
    • account_get_balance(account)
    • contract_load(address, alias)
    • get_approval(token, router, user)
    • get_token_name(token)
    • get_token_symbol(token)
    • get_token_balance(token, user)
    • get_token_decimals(token)
    • get_swap_rate(token_in_quantity, token_in_address, token_out_address, router)
    • token_approve(token, router, value="unlimited")  -- default value unlimited, unless set otherwise * not safe
    • token_swap(token_in_quantity, token_in_address, token_out_quantity, token_out_address, router)

- Error Handling: try-except; The more failure methods you can address, the longer your bot will run without crashing.
- Function definition
"""

import sys
import time 
import datetime
import requests
import os
from brownie import *

# use python-dotenv to get API key
from dotenv import load_dotenv
load_dotenv()

os.environ.get('SNOWTRACE_TOKEN')

# conract addresses (verify on Snowtrace)
TRADERJOE_ROUTER_CONTRACT_ADDRESS = "0x60aE616a2155Ee3d9A68541Ba4544862310933d4"
SPELL_CONTRACT_ADDRESS = "0xce1bffbd5374dac86a2893119683f4911a2f7814"
SSPELL_CONTRACT_ADDRESS = "0x3ee97d514bbef95a2f110e6b9b73824719030f7a"

# Helper Values
SECOND = 1
MINUTE = 60 * SECOND
HOUR = 60 * MINUTE
DAY = 24 * HOUR
PERCENT = 0.01

# ---- BOT Options ----

# Simulate swaps and approvals
DRY_RUN = False

# Quite after first successful trade
ONE_SHOT = False

# How often to run the main loop (in seconds)
LOOP_TIME = 1.0

# ---- Swap Thresholds and Slippage ----

# SPELL -> sSPELL swap targets
# a zero value will trigger a swap when the ratio matches base_staking_rate EXACTLY
# a negative value will trigger a swap when the rate is BELOW base_staking_rate
# a positive value will trigger a swap when the rate is ABOVE base_staking_rate

THRESHOLD_SPELL_TO_SSPELL = 0.2 * PERCENT

# sSPELL -> SPELL swap targets
# a positive value will trigger a (sSPELL -> SPELL) swap when the ratio is above the base_staking_rate
THRESHOLD_SSPELL_TO_SPELL = 1.2 * PERCENT

# tolerated slippage in swap price (used to calculate amountOutMin) which is passed to swapExactTokensForTokens()
SLIPPAGE = 0.1 * PERCENT

# ----- Function Definitions -------

def account_get_balance(account):
    try:
        return account.balance()
    except Exception as e:
        print(f"Exception in account_get_balance: {e}")


def contract_load(address, alias):
    """
    Attempts to load the saved contract by alias.
    If not found, fetch from network explorer and set alias.
    """
    try:
        contract = Contract(alias)
    except ValueError:
        contract = Contract.from_explorer(address)
        contract.set_alias(alias)
    finally:
        print(f"• {alias}")
        return contract


def get_approval(token, router, user):
    try:
        return token.allowance.call(user, router.address)
    except Exception as e:
        print(f"Exception in get_approval: {e}")
        return False


def get_token_name(token):
    try:
        return token.name.call()
    except Exception as e:
        print(f"Exception in get_token_name: {e}")
        raise


def get_token_symbol(token):
    try:
        return token.symbol.call()
    except Exception as e:
        print(f"Exception in get_token_symbol: {e}")
        raise


def get_token_balance(token):
    try:
        return token.balanceOf.call(user)
    except Exception as e:
        print(f"Exception in get_token_balance: {e}")
        raise


def get_token_decimals(token):
    try:
        return token.decimals.call()
    except Exception as e:
        print(f"Exception in get_token_decimals: {e}")
        raise


def token_approve(token, router, value="unlimited"):
    if DRY_RUN:
        return True

    if value == "unlimited":
        try:
            token.approve(
                router,
                2 ** 256 - 1,
                {"from": user},
            )
            return True
        except Exception as e:
            print(f"Exception in token_approve: {e}")
            raise
    else:
        try:
            token.approve(
                router,
                value,
                {"from": user},
            )
            return True
        except Exception as e:
            print(f"Exception in token_approve: {e}")
            raise


def get_swap_rate(token_in_quantity, token_in_address, token_out_address, router):
    try:
        return router.getAmountsOut(
            token_in_quantity, [token_in_address, token_out_address]
        )
    except Exception as e:
        print(f"Exception in get_swap_rate: {e}")
        return False

def token_swap(
    token_in_quantity,
    token_in_address,
    token_out_quantity,
    token_out_address,
    router,
):
    if DRY_RUN:
        return True

    try:
        router.swapExactTokensForToken(
            token_in_quantity,
            int(token_out_quantity * (1 - SLIPPAGE)),
            [token_in_address, token_out_address],
            user.address,
            int(1000 * (time.time()) + 30 * SECOND),
            {"from": user},
        )
        return True
    except Exception as e:
        print(f"Exception: {e}")
        return False



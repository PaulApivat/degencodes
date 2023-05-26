"""
First post in Bot Building series: 
" Bot Building - Structure and Helper Functions "

Code Structure and Philosophy 
- OOP: interested in building a set of classes to represent tokens, token pairs, routers and swapping triggers, 
- but have not done that yet (will start with built-in data types as classes are 'fancy')
- instead of classes Python _dictionaries_ represent tokens inside the bot
- will do OOP-re-write later
"""

import sys 
import time 
import datetime 
import requests 
import os 
from brownie import *

"""
from brownie import *  
- allows to call Brownie functions directily, eg. network.connect() instead of brownie.network.connect()
"""

# Global Constants - UPPERCASE (verify on Snowtrace)
TRADERJOE_ROUTER_CONTRACT_ADDRESS = "0x60aE616a2155Ee3d9A68541Ba4544862310933d4"
SPELL_CONTRACT_ADDRESS = "0xce1bffbd5374dac86a2893119683f4911a2f7814"
SSPELL_CONTRACT_ADDRESS = "0x3ee97d514bbef95a2f110e6b9b73824719030f7a"

"""
Avoid exposing API key in main script
- equivalent to: export SNOWTRACE_TOKEN='alphanumericstring' in console
"""
# use python-dotenv to avoid exposing API key in main file
from dotenv import load_dotenv
load_dotenv()

os.environ.get('SNOWTRACE_TOKEN')

"""
Helper Values
- hard coded, but convenient
"""
SECOND = 1
MINUTE = 60 * SECOND
HOUR = 60 * MINUTE
DAY = 24 * HOUR
PERCENT = 0.01

"""
Bot Options 
- instead of setting options at runtime
- runtime is /Users/username/.pyenv/versions/3.10.4/envs/degencodes 
- the python executable that will translate this file into CPU-readable bytecode
- (context: you can assign one or more CPU to a VM); both CPU and VM translate code to bytecode
- EVM needs translating solidity code to bytecode
- so "runtime" involves an extra-step of translation to bytecode
"""
# Simulate swaps and approvals
DRY_RUN = False

# Quit after the first successful trade
ONE_SHOT = False

# How often to run the main loop (in seconds)
LOOP_TIME = 1.0

"""
Swap Thresholds and Slippage
- This is DeFi-related 
- Two swap thresholds are set, comparing "the inverse of base Abracadabra staking rate"
- Slippage variables is also set to calculate amountOutMin, which is passed to swapExactTokensForTokens()
"""
# SPELL -> sSPELL swap targets
# a zero value will trigger a swap when the ratio matches base_staking_rate exactly
# a negative value will trigger a swap when the rate is below base_staking_rate
# a positive value will trigger a swap when the rate is above base_staking_rate
THRESHOLD_SPELL_TO_SSPELL = 0.2 * PERCENT

# sSPELL -> SPELL swap targets
# a positive value will trigger a (sSPELL -> SPELL) swap when the ratio is above base_staking_rate
# 1.2 * PERCENT -> 0.5 * PERCENT
THRESHOLD_SSPELL_TO_SPELL = 0.5 * PERCENT

# tolerated slippage in swap price (used to calculate amountOutMin)
SLIPPAGE = 0.1 * PERCENT

"""
Helper Functions & Function Definitions
**** Everything wrapped in try-except for error handling ****

- account_get_balance(account) which retrieves the current balance of the account
- contract_load(address, alias) which first attempts to retrieve a saved contract by its alias. If it is not available, it retrieves it from the explorer and sets an alias for faster loading on next run.
- get_approval(token, router, user) which retrieves the token approval value for a given routing contract and user.
- get_token_name(token) which retrieves the token name such as “Wrapped FTM”
- get_token_symbol(token) which retrieves the shorthand symbol such as “WFTM”
- get_token_balance(token, user) which retrieves the balance associated with a given user at a token contract address.
- get_token_decimals(token) which retrieves the decimals variable for a given token contract address.
- get_swap_rate(token_in_quantity, token_in_address, token_out_address, router) which returns a two-value tuple with values for token quantity in and token quantity out for a given pair of token contract addresses and router contract address.
- token_approve(token, router, value="unlimited") which will set the token approval for a given router contract to spend tokens at a given token contract address on behalf of our user. Note this includes a default value that will set unlimited approval if not specified. I do this for my bot since it only holds tokens that I am actively swapping, and do not want to issue hundreds of approvals for partial balances.
- token_swap(token_in_quantity, token_in_address, token_out_quantity, token_out_address, router) which calls the router’s swapExactTokensForTokens() method for the given token quantities, addresses, and router contract.
"""

# account_get_balance(account) which retrieves the current balance of the account
# uses from brownie *
# raise Exception if unsuccessful
def account_get_balance(account):
    try:
        return account.balance()
    except Exception as e:
        print(f"Exception in account_get_balance: {e}")



# contract_load(address, alias) which first attempts to retrieve a saved contract by its alias. 
# If it is not available, it retrieves it from the explorer and sets an alias for faster loading on next run.
# ValueError is a _specific_ Exception 
# you generally use specific exceptions to trap only ones that are likely to occur
# StackOverflow: https://tinyurl.com/3fk5fa4a
def contract_load(address, alias):
    try:
        contract = Contract(alias)
    except ValueError:
        contract = Contract.from_explorer(address)
        contract.set_alias(alias)
    finally:
        print(f"• {alias}")
        return contract

# get_approval(token, router, user) which retrieves the token approval value for a given routing contract and user.
def get_approval(token, router, user):
    try:
        return token.allowance.call(user, router.address)
    except Exception as e:
        print(f"Exception in get_approval: {e}")
        return contract 

# get_token_name(token) which retrieves the token name such as “Wrapped FTM”
def get_token_name(token):
    try:
        return token.name.call()
    except Exception as e:
        print(f"Exception in get_token_name: {e}")
        raise 

# get_token_symbol(token) which retrieves the shorthand symbol such as “WFTM”
def get_token_symbol(token):
    try:
        return token.symbol.call()
    except Exception as e:
        print(f"Exception in get_token_symbol: {e}")
        raise 


# get_token_balance(token, user) which retrieves the balance associated with a given user at a token contract address.
def get_token_balance(token, user):
    try:
        return token.balanceOf.call(user)
    except Exception as e:
        print(f"Exception in get_token_balance: {e}")
        raise 


# get_token_decimals(token) which retrieves the decimals variable for a given token contract address.
def get_token_decimals(token):
    try:
        return token.decimals.call()
    except Exception as e:
        print(f"Exception in get_token_decimals: {e}")
        raise 


# token_approve(token, router, value="unlimited") which will set the token approval for a given router contract 
# to spend tokens at a given token contract address on behalf of our user. 
# Note this includes a default value that will set unlimited approval if not specified. 
# I do this for my bot since it only holds tokens that I am actively swapping, and do not want to issue hundreds of approvals for partial balances.

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



# get_swap_rate(token_in_quantity, token_in_address, token_out_address, router) 
# which returns a two-value tuple with values for token quantity in and token quantity out 
# for a given pair of token contract addresses and router contract address.
def get_swap_rate(token_in_quantity, token_in_address, token_out_address, router):
    try:
        return router.getAmountsOut(
            token_in_quantity, [token_in_address, token_out_address]
        )
    except Exception as e:
        print(f"Exception in get_swap_rate: {e}")
        return False 


# token_swap(token_in_quantity, token_in_address, token_out_quantity, token_out_address, router) which calls the router’s swapExactTokensForTokens() method
# for the given token quantities, addresses, and router contract.

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
        router.swapExactTokensForTokens(
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
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




THRESHOLD_SPELL_TO_SSPELL = 0.2 * PERCENT
THRESHOLD_SSPELL_TO_SPELL = 0.5 * PERCENT
SLIPPAGE = 0.1 * PERCENT

STAKING_RATE_FILENAME = '.abra_rate'


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


# ========== Function Definitions ===========
# ---- Setup - Global Variables, Network, Account -------
# ---- Setup - Contracts and Token Dictionaries ---------
# ---- Setup - Approvals and Staking Rate ---------------
# ---- Main Loop - Balance Refresh and Staking Updater --
# ---- Main Loop - Quotes, Swaps, and Timing ------------

# 
# Start main() arbitrage loop
#

"""
- the main() loop contains all setup and swapping logic
- 'global' variables allows _other_variables outside of main() to access to reduce variable count
- however, global variables are frowned upon because they cause bugs
        due to one functioning acting on the value of global variables 
        before another function has chance to set it to an appropriate value

- connect to avax-main network to set transaction priority fee and load "trade_account" 
- wrap in try-except to have program terminate if fail 
"""

def main():

    global spell_contract 
    global sspell_contract 
    global traderjoe_router_contract 
    global spell 
    global sspell 

    try:
        network.connect("avax-main")
        # Avalanche supports EIP-1559 transactions, so we set the priority fee
        # and allow the base fee to change as needed
        network.priority_fee('5 gwei')
        # Can set a limit on maximum fee, if desired
        #network.max_fee('200 gwei')
    except: 
        sys.exit(
            "Could not load account! Verify that your account is listed using 'brownie accounts list' and that you are using the correct password. If you have not added an account, run 'brownie accounts' now."
        )


    # Use contract_load helper function to create objects to interact with TraderJoe router
    print("\nContracts loaded:")
    spell_contract = contract_load(SPELL_CONTRACT_ADDRESS, "Avalanche Token: SPELL")
    sspell_contract = contract_load(SSPELL_CONTRACT_ADDRESS, "Avalance Token: sSPELL")
    router_contract = contract_load(TRADERJOE_ROUTER_CONTRACT_ADDRESS, "TraderJoe: Router")

    # create two dictionaries
    # 'None' values anticipate being over-written later
    spell = {
        "address": SPELL_CONTRACT_ADDRESS,
        "contract": spell_contract,
        "name": None,
        "symbol": None,
        "balance": None,
        "decimals": None,
    }

    sspell = {
        "address": SSPELL_CONTRACT_ADDRESS,
        "contract": sspell_contract,
        "name": None,
        "symbol": None,
        "balance": None,
        "decimals": None,
    }

    spell["symbol"] = get_token_symbol(spell["contract"])
    spell["name"] = get_token_name(spell["contract"])
    spell["balance"] = get_token_balance(spell_contract, user)
    spell["decimals"] = get_token_decimals(spell_contract)

    sspell["symbol"] = get_token_symbol(sspell["contract"])
    sspell["name"] = get_token_name(sspell["contract"])
    sspell["balance"] = get_token_balance(sspell_contract, user)
    sspell["decimals"] = get_token_decimals(sspell_contract)

    if (spell["balance"] == 0) and (sspell["balance"] == 0):
        sys.exit("No tokens found:")

    # Confirm approvals for tokens
    print("\nChecking Approvals:")

    if get_approval(spell["contract"], router_contract, user):
        print(f"• {spell['symbol']} OK")
    else:
        token_approve(spell["contract"], router_contract)

    if get_approval(sspell["contract"], router_contract, user):
        print(f"• {sspell['symbol']} OK")
    else:
        token_approve(sspell["contract"], router_contract)

    try:
        with open(STAKING_RATE_FILENAME, "r") as file:
            base_staking_rate = float(file.read().strip())
            print(f"\nEthereum L1 Staking Rate: {base_staking_rate}")
    except FileNotFoundError:
        sys.exit(
            "Cannot load the base Abracadabra SPELL/sSPELL staking rate. Run `python3 abra_rate.py` and try again."
        )

    balance_refresh = True

    # 
    # Start of arbitrage loop
    # 
    while True:

        loop_start = time.time()

        try:
            with open(STAKING_RATE_FILENAME, "r") as file:
                if (result := float(file.read().strip())) != base_staking_rate:
                    base_staking_rate = result
                    print(f"Updated staking rate: {base_staking_rate}")
        except FileNotFoundError:
            sys.exit(
                "Cannot load the base Abracadabra SPELL/sSPELL staking rate. Run `python3 abra_rate.py` and try again."
            )

        if balance_refresh:
            time.sleep(10)
            spell["balance"] = get_token_balance(spell_contract, user)
            sspell["balance"] = get_token_balance(sspell_contract, user)
            print("\nAccount Balance:")
            print(
                f"• Token #1: {int(spell['balance']/(10**spell['decimals']))} {spell['symbol']} ({spell['name']})"
            )
            print(
                f"• Token #2: {int(sspell['balance']/(10**sspell['decimals']))} {sspell['symbol']} ({sspell['name']})"
            )
            print()
            balance_refresh = False 
            last_ratio_spell_to_sspell = 0
            last_ratio_sspell_to_spell = 0

        if spell["balance"]:

            if result := get_swap_rate(
                token_in_quantity=spell["balance"],
                token_in_address=spell["address"],
                token_out_address=sspell["address"],
                router=router_contract,
            ):

                spell_in, sspell_out = result
                ratio_spell_to_sspell = round(sspell_out / spell_in, 4)

                # print and save any updated swap values since last loop 
                if ratio_spell_to_sspell != last_ratio_spell_to_sspell:
                    print(
                        f"{datetime.datetime.now().strftime('[%I:%M:%S %p]')} {spell['symbol']} → {sspell['symbol']}: ({ratio_spell_to_sspell:.4f}/{1 / (base_staking_rate * (1 + THRESHOLD_SPELL_TO_SSPELL)):.4f})"
                    )
                    last_ratio_spell_to_sspell = ratio_spell_to_sspell
                else:
                    # abandon the for loop to avoid re-using stale data 
                    break 

                # execute SPELL -> sSPELL arb if trigger is satisfied 
                if ratio_spell_to_sspell >= 1 / (
                    base_staking_rate * (1 + THRESHOLD_SPELL_TO_SSPELL)
                ):
                    print(
                        f"*** EXECUTING SWAP OF {int(spell_in / (10**spell['decimals']))} {spell['symbol']} AT BLOCK {chain.height} ***"
                    )
                    if token_swap(
                        token_in_quantity=spell_in,
                        token_in_address=spell["address"],
                        token_out_quantity=sspell_out,
                        token_out_address=sspell["address"],
                        router=router_contract,
                    ):
                        balance_refresh = True 
                        if ONE_SHOT:
                            sys.exit("single shot complete!")

        loop_end = time.time()

        # Control the loop timing more precisely by measuring start and end time and sleeping as needed
        if (loop_end - loop_start) >= LOOP_TIME:
            continue 
        else:
            time.sleep(LOOP_TIME - (loop_end - loop_start))
            continue 
            





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
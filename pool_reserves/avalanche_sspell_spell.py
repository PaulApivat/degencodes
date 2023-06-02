
import sys 
import time 
import datetime 
import requests 
import os 
import json 
from decimal import Decimal 
from brownie import * 

# Contract addresses (verify on Snowtrace)
TRADERJOE_ROUTER_CONTRACT_ADDRESS = "0x60aE616a2155Ee3d9A68541Ba4544862310933d4"
TRADERJOE_POOL_CONTRACT_ADDRESS = "0x033C3Fc1fC13F803A233D262e24d1ec3fd4EFB48"
SPELL_CONTRACT_ADDRESS = "0xce1bffbd5374dac86a2893119683f4911a2f7814"
SSPELL_CONTRACT_ADDRESS = "0x3ee97d514bbef95a2f110e6b9b73824719030f7a"

# use python-dotenv to get API key
os.environ.get('SNOWTRACE_TOKEN')

# Helper Values
SECOND = 1
MINUTE = 60 * SECOND
HOUR = 60 * MINUTE
DAY = 24 * HOUR
PERCENT = 0.01

# SPELL -> sSPELL swap targets
# a zero value will trigger a swap when the ratio matches base_staking_rate exactly
# a negative value will trigger a swap when the rate is below base_staking_rate
# a positive value will trigger a swap when the rate is above base_staking_rate
THRESHOLD_SPELL_TO_SSPELL = Decimal("0.02")

# sSPELL -> SPELL swap targets
# a positive value will trigger a (sSPELL -> SPELL) swap when the ratio is above base_staking_rate
THRESHOLD_SSPELL_TO_SPELL = Decimal("0.05")

SLIPPAGE = Decimal("0.001") # tolerated slippage in swap price (0.1%)

BASE_STAKING_RATE_FILENAME = ".abra_rate"

# Simulate swaps and approvals
DRY_RUN = True
# Quit after the first successful trade
ONE_SHOT = False
# How often to run the main loop (in seconds)
LOOP_TIME = 1.0

"""
[MAIN PROGRAM LOOP]

if token['balance']:
    get pool reserves 
    check maximum input using get_tokens_in_for_ratio_out()
    check maximum output using get_tokens_out_from_tokens_in()
    call token_swap() using input and output amounts from the two functions 
    refresh balances and restart loop
"""
def main():

    global traderjoe_router 
    global traderjoe_lp 
    global spell 
    global sspell 
    global user 

    try:
        network.connect("avax-main")
    except:
        sys.exit(
            "Could not connect to Avalanche! Verify that brownie lists the Avalanche Mainnet using 'brownie networks list'"
        )

    try: 
        user = accounts.load("trade_account")
    except:
        sys.exit(
            "Could not load account! Verify that your account is listed using 'brownie accounts list' and that you are using the correct password. If you have not added an account, run 'brownie accounts new' now."
        )


    print("\nContracts loaded:")
    spell_contract = contract_load(SPELL_CONTRACT_ADDRESS, "Avalanche Token: SPELL")
    sspell_contract = contract_load(SSPELL_CONTRACT_ADDRESS, "Avalanche Token: sSPELL")

    traderjoe_router = contract_load(
        TRADERJOE_ROUTER_CONTRACT_ADDRESS, "TraderJoe: Router"
    )

    traderjoe_lp = contract_load(
        TRADERJOE_POOL_CONTRACT_ADDRESS, "TraderJoe LP: SPELL-sSPELL"
    )

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
        sys.exit("No tokens found!")

    # Confirm approvals for tokens
    print("\nChecking Approvals:")

    if get_approval(spell["contract"], traderjoe_router, user):
        print(f"• {spell['symbol']} OK")
    else:
        token_approve(spell["contract"], traderjoe_router)

    if get_approval(sspell["contract"], traderjoe_router, user):
        print(f"• {sspell['symbol']} OK")
    else:
        token_approve(sspell["contract"], traderjoe_router)    
    
    try:
        with open(BASE_STAKING_RATE_FILENAME, "r") as file:
            base_staking_rate = Decimal(file.read().strip())
            print(f"\nEthereum L1 Staking Rate: {base_staking_rate}")
    except FileNotFoundError:
        sys.exit(
            "Cannot load the base Abracadabra SPELL/sSPELL staking rate. Run `python3 abra_rate.py` and try again."
        )

    network.priority_fee("5 gwei")
    balance_refresh = True

        # get quotes and execute SPELL -> sSPELL swaps only if we have a balance of SPELL

        if spell["balance"]:

            try:
                # token0 (x) is sSPELL
                # token1 (y) is SPELL
                x0, y0 = lp.getReserves.call()[0:2]
            except:
                # restarts loop if getReserves() fails
                continue 

            # find maximum SPELL input at desired sSPELL/SPELL ratio "C"
            if spell_in := get_tokens_in_for_ratio_out(
                pool_reserves_token0=x0,
                pool_reserves_token1=y0,
                # sSPELL (token0) out 
                token0_out=True,
                token0_per_token1=Decimal(
                    str(1 / (base_staking_rate * (1 + THRESHOLD_SPELL_TO_SSPELL)))
                ),
                fee=Decimal("0.003"),
            ):
                if spell_in > spell["balance"]:
                    spell_in = spell["balance"]

                # calculate sSPELL output from SPELL input calculated above (used by token_swap to get amountOutMin)
                sspell_out = get_tokens_out_for_tokens_in(
                    pool_reserves_token0=x0,
                    pool_reserves_token1=y0,
                    quantity_token1_in=spell_in,
                    fee=Decimal("0.003"),
                )

                print(
                    f"*** EXECUTING SWAP FOR {spell_in // (10 ** spell['decimals'])} SPELL ***"
                )
                if token_swap(
                    token_in_quantity=spell_in,
                    token_in_address=spell["address"],
                    token_out_quantity=sspell_out,
                    token_out_address=sspell["address"],
                    router=router,
                ):
                    balance_refresh = True 
                    if ONE_SHOT:
                        sys.exit("single shot complete!")
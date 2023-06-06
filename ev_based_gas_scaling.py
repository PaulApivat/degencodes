"""
---- Inputs to implement a gas scaling function ----

def get_scaled_priority_fee(
    base_fee,       --> fixed portion of gas fees
    swap_ev,        --> the expected value (EV) of the swap opportunity, denominated in some currency shared by the swap token and gas token
    gas_limit,      --> the estimated units of gas that the swap will consume
    price_of_wei,   --> the price of a single unit of the gas token (10**-18)
    fee_ratio       --> a user-defined upper limit of gas spent as a fraction of swap EV
):
    return swap_ev * fee_ratio // (gas_limit * price_of_wei) - base_fee

---- (Gas) Scaling Strategies -----

1. If you found an undisturbed pool, you don't have to compete for gas at all
2. If you're in a pool with unsophisticated bots that bid a fixed amount, just bid slightly more (1 gwei ok)
3. If you're in a pool with sophisticated bots that adjust their gas inputs, you need to make choices.

Question: Do we conservatively attempt to control our costs, or aggressively pursue swaps to grow the overall balance?
Ansers: Depends on your level conviction of the coin you're accumulating. 

"""

# original token_swap() function from Structure and Helper Functions 

# --- Extend in two ways: 1. add optional custom_priority function to override priority_fee (set to None) in swapExactTokensForTokens
# --- Extend in two ways: 2. add logic to do basic sanity check on priority_fee passed into the function

# modify the router function call to swapExactTokensForTokens() to include priority_fee

def token_swap(
    token_in_quantity,
    token_in_address,
    token_out_quantity,
    token_out_address,
    router,
    priority_fee=None
):
    if DRY_RUN:
        print("*** DRY RUN! SWAPPING IS DISABLED ***")
        return True 

    if priority_fee:
        assert priority_fee > 0, "priority_fee must be greater than zero!"
        assert type(priority_fee) is int, "priority_fee must be an integer (expressed in Wei)"
    else:
        priority_fee = 0

    try:
        router.swapExactTokensForTokens(
            token_in_quantity,
            int(token_out_quantity * (1 - SLIPPAGE)),
            [token_in_address, token_out_address],
            user.address,
            int(1000 * (time.time()) + 30 * SECOND),
            {
                "from": user,
                "priority_fee": priority_fee
            },
        )
        return True 
    except Exception as e:
        print(f"Exception: {e}")
        return False 

"""
Notes for use: 

The EV of any given swap is determined by the pool state, your available balance, and the swap thresholds you've chosen. 
The price of AVAX, SPELL and gas_limit fluctuates. If you have a small balance, you might pick a larger fixed gas fee.
If you have a large balance, the EV approach above that dynamically scales could be the approach for you. 
"""
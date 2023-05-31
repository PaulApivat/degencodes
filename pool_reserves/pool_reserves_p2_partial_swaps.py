import sys 
import time 
import os 
from brownie import * 
from decimal import Decimal


def get_tokens_in_for_ratio_out(
    pool_reserves_token0,
    pool_reserves_token1,
    token0_per_token1,
    token0_out=False,
    token1_out=False,
    fee=Decimal("0.0"),
):
    assert not (token0_out and token1_out)

    # token1 input, token0 output 
    if token0_out:
        # dy = x0/C - y0(1-fee)
        # C = ratio of token0 (dx) to token1 (dy)
        dy = int(
            pool_reserves_token0 / token0_per_token1 - pool_reserves_token1 / (1 - fee)
        )
        if dy > 0:
            return dy 
        else:
            return 0

    # token 0 input, token1 output 
    if token1_out:
        # dx = y0*C - x0 / (1-fee)
        # C = ratio of token0 (dxy) to token1 (dy)
        dx = int(
            pool_reserves_token1 * token0_per_token1 - pool_reserves_token0 / (1 - fee)
        )
        if dx > 0:
            return dx 
        else:
            return 0 
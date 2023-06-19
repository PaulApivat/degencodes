import sys, time, os
from decimal import Decimal
from fractions import Fraction
from brownie import accounts, network
from degenbot import *
from dotenv import dotenv_values

# Contract addresses (verify on Arbiscan)
SUSHISWAP_ROUTER_CONTRACT_ADDRESS = "0x1b02da8cb0d097eb8d57a175b88c7d8b47997506"
SUSHISWAP_POOL_CONTRACT_ADDRESS = "0xB7E50106A5bd3Cf21AF210A755F9C8740890A8c9"
WETH_CONTRACT_ADDRESS = "0x82aF49447D8a07e3bd95BD0d56f35241523fBab1"
MAGIC_CONTRACT_ADDRESS = "0x539bdE0d7Dbd336b79148AA742883198BBF60342"

SLIPPAGE = Decimal("0.001")  # tolerated slippage in swap price (0.1%)

# Simulate swaps and approvals
DRY_RUN = False
# Quit after the first successful trade
ONE_SHOT = False
# How often to run the main loop (in seconds)
LOOP_TIME = 0.25

#CONFIG_FILE = "limit_bot.env"
CONFIG_FILE = ".env"
BROWNIE_NETWORK = dotenv_values(CONFIG_FILE)["BROWNIE_NETWORK"]
BROWNIE_ACCOUNT = dotenv_values(CONFIG_FILE)["BROWNIE_ACCOUNT"]
os.environ["ARBISCAN_TOKEN"] = dotenv_values(CONFIG_FILE)["ARBISCAN_API_KEY"]

def main():

    try:
        network.connect(BROWNIE_NETWORK)
    except:
        sys.exit(
            "Could not connect! Verify your Brownie network settings using 'brownie networks list'"
        )

    try:
        degenbot = accounts.load(BROWNIE_ACCOUNT)
    except:
        sys.exit(
            "Could not load account! Verify your Brownie account settings using 'brownie accounts list'"
        )

    magic = Erc20Token(
        address=MAGIC_CONTRACT_ADDRESS,
        user=degenbot,
        # abi=ERC20
    )

    weth = Erc20Token(
        address=WETH_CONTRACT_ADDRESS,
        user=degenbot,
        # abi=ERC20
    )

    tokens = [
        magic,
        weth,
    ]

    sushiswap_router = Router(
        address=SUSHISWAP_ROUTER_CONTRACT_ADDRESS,
        name="SushiSwap Router",
        user=degenbot,
        abi=UNISWAPV2_ROUTER,
    )

    sushiswap_lp = LiquidityPool(
        address=SUSHISWAP_POOL_CONTRACT_ADDRESS,
        name="SushiSwap: MAGIC-WETH",
        router=sushiswap_router,
        abi=UNISWAPV2_LP_ABI,
        tokens=tokens,
        fee=Fraction(3, 1000),
    )

    lps = [
        sushiswap_lp,
    ]

    routers = [
        sushiswap_router,
    ]

    # Confirm approvals for all tokens on every router
    print()
    print("Approvals:")
    for router in routers:
        for token in tokens:
            if not token.get_approval(external_address=router.address) and not DRY_RUN:
                token.set_approval(external_address=router.address, value=-1)
            else:
                print(f"{token} on {router} OK")
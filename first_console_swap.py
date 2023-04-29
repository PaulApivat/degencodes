# Pre-requisites
# every transaction, approval(), requires gas

"""
Prerequisites:
Create new account on Brownie
- write name, password, seed phrase offline

Load new account into browser wallet using private keys
- to get private keys, load user in console and query user.private_key

In browser wallet, "import account"
- enter private_key

Fund new wallet

Bridge AVAX over to the Avalanche C-Chain 
- do a cross-chain swap ETH -> AVAX via rocketx.exchange 

Load Brownie console session
(brownie console --network avax-main)
Re-check user.balance() to confirm AVAX receipt
"""

# The Gameplan

"""
The Gameplan

Start up console:

% brownie console --network avax-main
>>> user = accounts.load('trade_account')
>>> user.balance() / (10**18)

(Trader Joe Router)

>>> router = Contract.from_explorer('0x60aE616a2155Ee3d9A68541Ba4544862310933d4')
>>> mim = Contract.from_explorer('0x130966628846bfd36ff31a822705796e8cb8c18d')
>>> dai = Contract.from_explorer('0xd586e7f844cea2f87f50152665bcbc2c279d8d70')

>>> mim.balanceOf(user.address)
>>> dai.balanceOf(user.address)

--- How many tokens can the router spent on the user's behalf?

>>> mim.allowance(user.address, router.address)
>>> dai.allowance(user.address, router.address)
"""

# Swap AVAX for MIM
# swapAVAXForExactTokens

"""
Swap AVAX for MIM

source: Uniswap V2 Router02 contract, Trader Joe forked Uni V2

>>> import time

--- since the Router contract can only swap ERC20, must change avax -> wavax

>>> wavax = Contract.from_explorer('0xB31f66AA3C1e785363F0875A1B74E27b85FD66c7')

--- change value from 5*(10**mim.decimals()) -> 0.5(10**mim.decimals())
--- due to AVAX losing 90% of price

--- Transactions actually went through after 'Waiting for confirmation...'

--- 5 cents of MIM
>>> router.swapAVAXForExactTokens(0.05*(10**mim.decimals()), [wavax.address, mim.address], user.address, 1000*int(time.time()+30), {'from': user.address, 'value':0.05*10**18})
--- 50 cents of MIM
>>> router.swapAVAXForExactTokens(0.5*(10**mim.decimals()), [wavax.address, mim.address], user.address, 1000*int(time.time()+30), {'from': user.address, 'value':0.05*10**18})
--- 5 dollars of MIM
>>> router.swapAVAXForExactTokens(5*(10**mim.decimals()), [wavax.address, mim.address], user.address, 1000*int(time.time()+30), {'from': user.address, 'value':0.5*10**18})

--- check user's MIM balance
>>> mim.balanceOf(user.address)/(10**mim.decimals())

"""

# Swap Avax for MIM cont.

"""
--- Breakdown swapAVAXForExactTokens
--- See the parameters in the console:

>>> router.swapAVAXForExactTokens(uint256 amountOut, address[] path, address to, uint256 deadline, {'from': Account, 'value': Wei})
>>> router.swapAVAXForExactTokens(5*(10**mim.decimals()), [wavax.address, mim.address], to user.address, 1000*int(time.time()+30), {'from': user.address, 'value': AVAX gas estimation})
>>> router.swapAVAXForExactTokens(MIM amountOut, swapping [wrapped AVAX address, for MIM address], to. user.address, deadline: time.time() returns current time in UNIX and set deadline to +30 seconds from now and multiply 1000 to get milliseconds, {'from': Account, 'value': amount of AVAX, gas, consumed by swap before reverint})

"""

# Set Approval for MIM
# Approval
# Allowance

"""
>>> mim.balanceOf(user.address)/(10**mim.decimals())

We have 5.55 MIM, we can set approval to spend a lower amount (2.5 MIM) to demonstrate how
approve() can be managed to reduce risk.

>>> mim.approve(router.address, 2.5*10**mim.decimals(), {'from': user.address})

--- confirm allowance set

>>> mim.allowance(user.address, router.address)/(10**mim.decimals())

"""

# Swap MIM for DAI
# swapExactTokensForTokens

"""
1. Show a reverted transaction 
- Do not expect MIM-to-DAI swap ratio to be 1.0
- note: swapExactTokensForTokens

>>> router.swapExactTokensForTokens(2.5*10**mim.decimals(), 2.5*10**dai.decimals(), [mim.address, dai.address], user.address, 1000*int(time.time()+30), {'from': user.address})

--- ValueError: Gas estimation failed: 'execution reverted: JoeRouter: INSUFFICIENT_OUTPUT_AMOUNT'
--- because we told TraderJoe's router to swap 2.5 MIM for a _minimum_ of 2.5 DAI


2. Show a successful transaction
--- Use more reasonable exchange rate (1 MIM = 0.95 DAI)

>>> router.swapExactTokensForTokens(2.5*10**mim.decimals(), 0.95*2.5*10**dai.decimals(), [mim.address, dai.address], user.address, 1000*int(time.time()+30), {'from': user.address})

--- Check MIM and DAI balance for user.address
--- example: 3.05 MIM, 2.468316876560881 DAI

>>> mim.balanceOf(user.address)/(10**mim.decimals())
>>> dai.balanceOf(user.address)/(10**dai.decimals())
"""


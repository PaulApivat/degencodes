"""
--- Integrating the Price Feed ---

Chainlink Price Feed: Avalanche Mainnet: https://data.chain.link/avalanche/mainnet
Chainlink Data Feeds API Reference: https://docs.chain.link/data-feeds/api-reference

- $ export SNOWTRACE_TOKEN
- $ brownie console --network avax-main 

>>> spell_price = Contract.from_explorer('0x4f3ddf9378a4865cf4f28be51e10aecb83b7daee')
>>> avax_price = Contract.from_explorer('0x0a77230d17318075983913bc2145db16c7366156')
>>> spell_price.latestRoundData()
>>> spell_price.decimals()
>>> spell_price.latestRoundData()[1]/(10**spell_price.decimals())
>>> avax_price.latestRoundData()[1]/(10**avax_price.decimals())

--- Calculating Expected Value (EV) ---

A swap requires the following:
- Input token quantity
- Output token quantity
- SPELL price
- AVAX price 

Standard formula for calculating Exepcted Value by compare swap rate vs base rate:
• EV = (rate - base_rate) * input_quantity * token_price

Example: What is the EV of swapping 100,000 sSPELL to SPELL at rate of 1.17, 
compare to base rate of 1.16. SPELL price at $0.015.

• EV = (1.17 SPELL/sSPELL - 1.16 SPELL/sSPELL) * 100000 sSPELL * $0.015/SPELL
• EV = $15 worth of SPELL in profits with this swap.

--- Fee as Percentage of EV ---

- How much gas should we bid for this opportunity?
- If willing to bid up 10% of EV in gas, how to calculate gas spend?

max_gas_spent = fee_ratio * swap_ev
max_gas_spent = 0.10 * $15
max_gas_spent = $1.50

>>> traderjoe_router = Contract.from_explorer('0x60aE616a2155Ee3d9A68541Ba4544862310933d4')
>>> user = accounts.load('trade_account')
(Enter password for "trade_account")

-- NOTE: This is hacky and for demo purposes only; missing 'time' parameter
>>> traderjoe_router.swapExactTokensForTokens.estimate_gas(120*10**18, 100*10**18, ['0xce1bffbd5374dac86a2893119683f4911a2f7814', '0x3ee97d514bbef95a2f110e6b9b73824719030f7a'], user.address, 1000*int(time.ti
me()+60), {'from':user.address})

(NameError: name 'time' is not defined)

- Because Avalanche supports EIP-1559 transactions, gas fees are made up to two parts:
- base fee & priority fee

>>> chain.base_fee

- Equation to solve for calculating priority gas fee:

max_gas_spent = gas_limit * (base_fee + priority_fee) * ($/Wei for AVAX)
max_fee = gas_limit * (base_fee + priority_fee) * ($/AVAX) / (10**18)

Solving algebraically for priority_fee:

priority_fee = max_fee / ( gas_limit * $AVAX / (10**18)) - base_fee
"""

def get_scaled_priority_fee(
    base_fee,
    swap_ev,
    gas_limit,
    price_of_wei,
    fee_ratio
):
    return swap_ev * fee_ratio // (gas_limit * price_of_wei) - base_fee
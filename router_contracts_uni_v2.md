# Router Contracts - Exploring getAmountsOut()

>>> Many DEXes are copy-paste clones of Uniswap

## Uniswap V2 Router contract

This session focuses on `getAmountsOut()`. We're going to query the Uni V2 Router contract to get fluctuating exchange rates. 

### Uniswap Documentation

>>> Given an input asset amount and an array of token addresses, calculates all subsequent maximum output token amounts by calling getReserves for each pair of token addresses in the path in turn, and using these to call getAmountOut.

>>> Useful for calculating optimal token amounts before calling swap.

**Note**: We'll be interacting with Avalanche (`avax-main` network within Brownie), TraderJoe Router contract which is a derivative of Sushiswap, which is a derivative of Uniswap V2. 

[TraderJoe contracts from their documentation.](https://help.traderjoexyz.com/en/security-and-contracts/contracts)

We'll use `JoeRouter` contract at [0x60aE616a2155Ee3d9A68541Ba4544862310933d4](https://snowtrace.io/address/0x60aE616a2155Ee3d9A68541Ba4544862310933d4).


JoeRouter: 0x60aE616a2155Ee3d9A68541Ba4544862310933d4

## Brownie Hands-On

Start a Brownie console session, load `test_account`, provide password and set the `JoeRouter` address.

```
>>> user = accounts.load('test_account')

Enter password for "test_account": 

>>> router_contract = Contract.from_explorer('0x60aE616a2155Ee3d9A68541Ba4544862310933d4')

>>> usdc_contract = Contract.from_explorer('0xb97ef9ef8734c71904d8002f8b6bc66dd9c48a6e')

>>> usdt_contract = Contract.from_explorer('0xc7198437980c041c805a1edcba50c1ce5db95118')

>>> wavax_contract = Contract.from_explorer('0xb31f66aa3c1e785363f0875a1b74e27b85fd66c7')

```

Now that we have **contract objects** loaded, use them as arguments to the `getAmountsOut()` function. A review of their docs shows, in Solidity not Python, what the parameters for `getAmountsOut()` function are:

>>> function getAmountsOut(uint amountIn, address[] memory path) internal view returns (uint[] memory amounts)

```
>>> router_contract.getAmountsOut(1*( 10**usdt_contract.decimals()), [usdt_contract.address, wavax_contract.address, usdc_contract.address ])

output: (1000000, 47308268829805666, 994687)

# prettier version if you only want USDC output
>>> router_contract.getAmountsOut(1*( 10**usdt_contract.decimals()), [usdt_contract.address, wavax_contract.address, usdc_contract.address ])[-1]/(10**usdc_contract.decimals())

output: 0.994476
```

**NOTE**:
1. Ethereum and its derivatives store balances as very high bit unsigned integers, so to descrbie a token quantity, always *convert it by the appropriate power of 10*. This is achieved here with `1 * (10**usdt_contract.decimals())`
2. Instead of writing out the full address, use "in-line" syntax (i.e., `usdt_contract.address`).
3. The output for this example, is a Python tuple: `(1000000, 47308268829805666, 994687)` containing the quantity of tokens output at *each stage* of the swap. 
4. In this case 1000000 USDT => 47308268829805666 WAVAX => 994687 USDC

```
Human readable form would be: 
1000000 / (10**6), 47308268829805666 / (10**18), 994687 / (10**6)

```

**Summary**: We enter load up contract objects:  `usdc_contract`, `wavax_contract`, and `usdt_contract`, then use them as inputs for `router_contract` and the `getAmountsOut()` function. This means to swap 1 USDT, we'd get 0.994476 USDC. We know how to query a Router contract for fluctuating exchange rates. 
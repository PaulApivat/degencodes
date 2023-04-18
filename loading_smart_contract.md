# Loading a Smart Contract

**Official Ethereum Definition**: A program that runs on the Ethereum blockchain. It's a collection of code (its functions) and data (its state) that resides at a **specific address** on the Ethereum blockchain. [source](https://ethereum.org/en/developers/docs/smart-contracts/)

### Interacting with Smart Contracts (Ethereum Network) without a Frontend

Smart contracts resides at a **specific address** so we can interact with them directly, without a frontend, via Brownie. Benefits include:

- interact with underlying smart contract directly
- access smart contract data not exposed via frontend
- transfer assets, make swaps, operate normally during web browser outages or where a frontend does not exist

### Block Explorers

Block explorers, like [Etherscan](https://etherscan.io/), allow smart contract authors to publish their smart contract to be **verified against the stored blockchain bytecode**. Anything can be published to a blockchain, but by default the *source code* is **NOT** published, only the *compiled bytecode*. 

An **unverified** smart contract is useless to anyone but the author who understands its inputs and outputs. 

**Implication**: Smart contracts **not** published or verified cannot be trusted. Reputable smart contract devs **all publish their source code to the appropriate block explorer**. 

**NOTE**: ONly after the author has submitted and verified their contract can we retrieve information from the block explorer and *interact with* that smart contract in Brownie withtout any need for the frontend. 

### Smart Contracts and Brownie

Start console. Using Avalanche to access their default open API.

% brownie console --network avax-main

*note*: 'test_account' was setup in [previous post](https://github.com/PaulApivat/degencodes/blob/main/intro_brownie.md).

>>> user = accounts.load('test_account')

(create `wavax_contract` object, use  `from_explorer()` method within `Contract` class.)

>>> wavax_contract = Contract.from_explorer('0xB31f66AA3C1e785363F0875A1B74E27b85FD66c7')

(ignore warning about Snowtrace API, will address later)

(list all associated variables and methods with `wavax_contract`)


```
>>> dir(wavax_contract)

[abi, address, alias, allowance, approve, balance, balanceOf, bytecode, decimals, decode_input, deposit, events, from_abi, from_ethpm, from_explorer, get_method, get_method_object, get_solc_version, info, name, remove_deployment, selectors, set_alias, signatures, symbol, topics, totalSupply, transfer, transferFrom, tx, withdraw]
```

Two ways access **address** variable and **balance()** method:

```
>>> wavax_contract.balanceOf(wavax_contract.address)
>>> wavax_contract.balanceOf('0xB31f66AA3C1e785363F0875A1B74E27b85FD66c7')
```

**NOTE**: Floating point numbers (any number with decimals) are *not* perfectly reproducible on all hardware, so a blockchain ledger uses high bit integers instead of floating point numbers with a *separate* `decimals()` value. This is why Ethereum offers 256 bit integer precision (18 decimal places) on all numbers.

There's a difference between `balance()` vs. `balanceOf()`. The former method is associated with the native gas token, Avalanche's AVAX. The latter is the method associated wtih an ERC-20 implementation that works *on top of* the base blockchain, Wrapped AVAX or WAVAX. 

```
# associated with native gas token, AVAX, of base chain
>>> wavax_contract.balance()

# associated with implementation of ERC-20 token, Wrapped AVAX or WAVAX, on top of base chain
>>> wavax_contract.balanceOf(wavax_contract.address) 
>>> wavax_contract.balanceOf('0xB31f66AA3C1e785363F0875A1B74E27b85FD66c7')

```

### Numbers and Decimals

Native token balances (ETH, AVAX, FTM) don't have a `decimals()` method associated with them, the **number is always 18 for any EVM-compatible blockchain**. 

To figure out the AVAX balance of `wavax_contract`:

```
>>> wavax_contract.balance() / (10 ** 18)
```
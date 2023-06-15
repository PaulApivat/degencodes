"""
- Ethereum does not return a value on state-changing transactions, it only returns the transaction hash.
- Brownie taks the transaction hash nd watches the blockchain for that hash to appear
- Only after the hash appears can we know (through Brownie) whether transaction was confirmed or reverted
- Nature of the blockchain: submitting a state-changing transaction guarantees neither success or timely execution

Events

- events are nice workaround
- an emitted event is a smart contract programmer signalling that some state change has taken place
- events emitted in **LOGS**, data is published to separate stream of **topics**
- events are _not_ recorded onchain, gas cost to emit are low

Sync (see event logs in: https://snowtrace.io/tx/0x17a56e20064cc4d7728b1c06e96d6a2ea7fe48f9b8fa6a54a3fb7fad6640d4d6#eventlog)

- gives you pool state without calling getReserves(), you can monitor (listen) to unlimited number of liquidity poos for updated reserve states

Watching Events with Brownie

-  Brownie is a "wrapper" for web3.py

"""
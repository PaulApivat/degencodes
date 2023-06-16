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

**Watching Events with Brownie**

-  Brownie is a "wrapper" for web3.py
- CRITICAL NOTE: event filter only works with a websocket connection (requires payment subscription from Ankr) ; Can also use Alchemy SDK

- WebSockets are bi-directional communication protocol that maintains a network connection between a server and client; 
unlike HTTP requests, WebSocket clients don't need to continuously make requests when they want information

Example ADD WebSocket connection on console (substitute with your own data):

devil@hades:~/degenbot$ brownie networks add Avalanche moralis-avax-main-websocket host=wss://speedy-nodes-nyc.moralis.io/[redacted]/avalanche/mainnet/ws explorer=https://api.snowtrace.io/api chainid=43114

** After add WebSocket connection **

SUCCESS: A new network 'ankr-avax-main-websocket' has been added
  └─ankr-avax-main-websocket
    ├─id: ankr-avax-main-websocket
    ├─chainid: 43114
    ├─explorer: https://api.snowtrace.io/api
    └─host: [fill in your WSS connection]

** Start Brownie Console **
0. export SNOWTRACE_TOKEN
1. start brownie
2. connect to Avalanche network using Ankr WebSocket RPC
3. set up filter to monitor USDC-WAVAX pool

$ brownie console --network ankr-avax-main-websocket
>>> lp = Contract.from_explorer('0xA389f9430876455C36478DeEa9769B7Ca4E3DDB1')



ValueError: {'code': -32601, 'message': 'the method eth_newFilter does not exist/is not available'}

This works: filter = web3.eth.contract(address=lp.address, abi=lp.abi).events.Sync.createFilter()
Isolate issue: .createFilter(fromBlock='latest')

>>> filter = web3.eth.contract(address=lp.address, abi=lp.abi).events.Sync.createFilter(fromBlock='latest')
"""
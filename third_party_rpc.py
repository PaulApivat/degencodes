"""
Add Private RPC from Ankr

(article recommended Moralis, which no longer offers "Speedy Nodes")

$ brownie networks add Avalanche moralis-avax-main host=https://speedy-nodes-nyc.moralis.io/[your_special_api_key_here]/avalanche/mainnet explorer=https://api.snowtrace.io/api chainid=43114 name=Mainnet

-- switching from Moralis to Ankr HTTPS Endpoint
-- (see environment variable)

$ brownie networks add Avalanche ankr-avax-main host=ANRK_ENDPOINT_HTTPS explorer=https://api.snowtrace.io/api chainid=43114 name=Mainnet
$ export SNOWTRACE_TOKEN
$ brownie console --network ankr-avax-main

-- testing Ankr HTTPS Endpoint

>>> spell_price = Contract.from_explorer('0x4f3ddf9378a4865cf4f28be51e10aecb83b7daee')
>>> spell_price.latestRoundData()
>>> spell_price.decimals()
>>> spell_price.latestRoundData()[1]/(10**spell_price.decimals())

"""
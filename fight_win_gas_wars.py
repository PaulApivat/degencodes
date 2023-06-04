"""
Premise: To make a profitable trade and not get rekt due to high gas fees, 
we need to calculate and ensure gas is roughly 5-10% of expected value (EV),

In the case of swapping SPELL <-> sSPELL, we need to make two swaps to actually make a profit:
1. SPELL -> sSPELL (capture premium)
2. sSPELL -> SPELL (lock-in premium)

To control gas fees to be 5-10% of potential profit, we must know at minimum:
1. Current price of SPELL (to calculate profit)
2. Current price of AVAX (to calculate fee per gas on avalanche)
3. Current base fee of the network (assuming 1559 is implemented)
4. EV of swap opportunity (how much profit can be locked-in)

Next:
- how to query blockchain for prices using Chainlink data feeds
- how to query blockchain for current base fee
- how to calculate and scale gas fees automatically

Bid more big opportunities, less for small ones

Review: setting up brownie in console
- exporting API keys
$ export WEB3_INFURA_PROJECT_ID="somealphanumeric"
$ export SNOWTRACE_TOKEN="somealphanumeric"
- initializing brownie console specific-network
$ brownie console --network avax-main

"""


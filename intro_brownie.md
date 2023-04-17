# Introduction to Brownie

## Create a User

**Context**: activate `pyenv virtualenv degencodes`, create a COMPROMISED and INSECURE account with user, private keys, and wallet address

% brownie accounts generate test_account

(write down 12-word seed phrase privately)
(give this account a password)

### Degen Code example:
```
Generating a new private key...
mnemonic: 'start ecology client situate rib ecology rare gaze festival leave view upper'
Enter the password to encrypt this account with: 
SUCCESS: A new account '0xC763A439754eEB4e9D55dE9E264668272CCbE126' has been generated with the id 'test_account'
```

(use password generated to access this 'test_account' next time in the console using `accounts.load()`)


## Use the Console

**Context**: Start a Python console with all of the default Brownie modules pre-loaded, plus tab-completion commands and helper functions.

(start w Avalanche Network as it provides public API w no need for authentication)
(connect to EVM later) 

% brownie networks modify avax-main

('modify' does nothing, only prints current settings)

(start Brownie console with following command)

% brownie console --network avax-main

>>> user = accounts.load('test_account')

(Enter password for "test_account": )

(explore 'user' object)

>>> dir(user)

[address*, balance, deploy, estimate_gas, gas_used*, get_deployment_address, nonce*, private_key*, public_key*, 
save, sign_defunct_message, sign_message, transfer]

* variables, everything else is a method()

>>> user.address

>>> user.balance()

>>> user.private_key 

>>> user.public_key

#### check the balance of an actual account to see that Brownie is working correctly

(address for Wrapped AVAX contract)

>>> someone_else = network.account.PublicKeyAccount('0xB31f66AA3C1e785363F0875A1B74E27b85FD66c7')

>>> someone_else.balance()

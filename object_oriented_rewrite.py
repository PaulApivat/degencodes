"""
ERC20 Token Class
"""

class Erc20Token:
    """
    Represents an ERC-20 token. Must be initialized with an address. 
    Brownie will load the Contract object from the supplied ABI (if given),
    then attempt to load the verified ABI from the block explorer.
    If both methods fail, it will attempt to use a supplied ERC-20 ABI
    """
    def __init__(
        self, 
        address: str, 
        user: network.account.LocalAccount, 
        abi: list = None, 
        oraacle_address: str = None,
        ) -> None:
        self.address = address 
        self._user = user 
        if abi:
            try:
                self._brownie_contract = Contract.from_abi(
                    name="", 
                    address=self.address, 
                    abi=abi
                )
            except:
                raise 
        else:
            try:
                self._brownie_contract = Contract.from_explorer(
                    self.address
                )
            except:
                self._brownie_contract = Contract.from_abi(
                    name="",
                    address=self.address,
                    abi=ERC20
                )
        self.name = self._brownie_contract.name.call()
        self.symbol = self._brownie_contract.symbol.call()
        self.decimals = self._brownie_contract.decimals.call()
        self.balance = self._brownie_contract.balanceOf.call(self._user)
        self.normalized_balance = self.balance / (10 ** self.decimals)
        if oraacle_address:
            self._price_oracle = ChainlinkPriceContract(
                address=oraacle_address
            )
            self.price = self._price_oracle.price 
        print(f"• {self.symbol} ({self.name})")
        
    def _str__(self):
        return self.symbol

    def get_approval(self, external_address: str):
        return self._brownie_contract.allowance.call(self._user.address, external_address)

    def set_approval(self, external_address: str, value: int):
        if value == "unlimited":
            value = 2 ** 256 - 1

        try:
            self._brownie_contract.approve(
                external_address,
                value,
                {"from": self._user.address},
            )
        except Exception as e:
            print(f"Exception in token_approve: {e}")
            raise

    def update_balance(self):
        self.balance = self._brownie_contract.balanceOf.call(self._user)
        self.normalized_balance = self.balance / (10 ** self.decimals)


    def update_price(self):
        self.price = self._price_oracle.update_price()

        
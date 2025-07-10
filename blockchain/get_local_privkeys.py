from bip_utils import Bip39SeedGenerator, Bip44, Bip44Coins, Bip44Changes
from eth_account import Account


MNEMONIC = "test test test test test test test test test test test junk"

seed_bytes = Bip39SeedGenerator(MNEMONIC).Generate()

wallet = Bip44.FromSeed(seed_bytes, Bip44Coins.ETHEREUM)

for i in range(5):
    account = wallet.Purpose().Coin().Account(0).Change(Bip44Changes.CHAIN_EXT).AddressIndex(i)
    private_key = account.PrivateKey().Raw().ToHex()
    address = Account.from_key(private_key).address

    print(f"[{i}] Address: {address}")
    print(f"    Private Key: {private_key}")

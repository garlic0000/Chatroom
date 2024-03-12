from client.settings.others import long_to_bytes
import hashlib
from client.settings.secure import get_prikey_pubkey, get_kG

# A用户获取公私钥对
prikey = get_prikey_pubkey.PrivateKey()
pubkey = prikey.publicKey()
prikey_str16 = prikey.toString()
pubkey_str16 = pubkey.toString(compressed=False)
prikey = int(prikey_str16, base=16)
pubkey = int(pubkey_str16, base=16)


def get_shared_secret(toward_pubkey):
    c = get_kG.CryptSM2(prikey_str16, pubkey_str16)
    toward_pubkey = hex(toward_pubkey)[2:]
    share_key = c.kg(prikey, toward_pubkey)
    share_key = int(share_key, base=16)
    return hashlib.sha256(long_to_bytes(share_key)).digest()

from hashlib import sha256

from ventoy_ng_cpio.schemas.sources import SourceInfo


def verify_source(this: SourceInfo, data: bytes):
    xhash = this.xhash
    assert xhash is not None
    sxhash = xhash.split(":")
    hash_kind = sxhash[0]
    assert hash_kind == "sha256"
    valid_hash_value = sxhash[1]
    hash_value = sha256(data)
    if hash_value.hexdigest() != valid_hash_value:
        raise ValueError

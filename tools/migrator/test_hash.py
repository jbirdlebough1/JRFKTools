import hashlib
import string
import random
import os

# Official Raspberry Pi OS userconf encryption
# RPi OS userconf accepts openssl/glibc sha512 crypt.
# We can also generate it using Python passlib if installed,
# or a standard glibc sha512-crypt algorithm, or openssl/powershell.

def test_hash():
    salt = "".join(random.choice(string.ascii_letters + string.digits) for _ in range(8))
    # We can also check if openssl or python has a hasher
    print("Salt generated:", salt)

test_hash()

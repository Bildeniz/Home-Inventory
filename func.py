from string import hexdigits
from random import choice

# Generating secret key
def secretKey():
    key = ""
    for i in range(15):
        key = key + choice(hexdigits)
    return key

#!/usr/bin/env python3
#
# NOT USED - scraps to hold onto
#

import hashlib

"""
https://docs.python.org/3.8/library/functions.html#hash
"""

"""
https://docs.python.org/3/library/hashlib.html
"""
m = hashlib.sha256()
m.update(b"Nobody inspects")
m.update(b" the spammish repetition")
m.digest()

"""
https://grabthiscode.com/python/how-to-convert-hash-to-string-in-python
"""

str = "alecramsay@comcast.net"
  
hashed = hashlib.md5(str.encode()) 
   
print("The hexadecimal equivalent of hash is : ", end ="") 
print(hashed.hexdigest()) 


import hashlib

def getPass(s):
    return hashlib.md5(s.encode('utf-8')).hexdigest()

def getEncryptedUname(s):
    return s
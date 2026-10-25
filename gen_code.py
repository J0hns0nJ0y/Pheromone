import secrets, hashlib, string

alphabet = string.ascii_lowercase + string.digits
code = "".join(secrets.choice(alphabet) for _ in range(12))
print("Give recipient :", code)
print("Put in file    :", hashlib.sha256(code.encode()).hexdigest())
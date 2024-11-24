import random

def generate_secret_key(length=50, exclude="#&"):
    allowed_chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@%^*-_"
    allowed_chars = ''.join(c for c in allowed_chars if c not in exclude)
    return ''.join(random.choice(allowed_chars) for _ in range(length))

print(generate_secret_key(50))

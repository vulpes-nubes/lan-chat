import hashlib

# Generate a SHA-256 key
key = "super_secret_key"  # This is your shared secret; change this to something secure
key_hash = hashlib.sha256(key.encode()).hexdigest()

# Save the key hash to a file
with open("client_key.txt", "w") as key_file:
    key_file.write(key_hash)

print("SHA-256 key saved to client_key.txt")

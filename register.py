import json
import sys
import client

try:
    with open("profile.json") as f:
        profile = json.load(f)
except FileNotFoundError:
    sys.exit("Create profile.json.")

try:
    print(json.dumps(client.post("register", profile, auth=False), indent=2))
except client.ApiError as e:
    sys.exit(f"Registration failed: {e}")
print("Check your email for the ec2_ key and put it in .env")


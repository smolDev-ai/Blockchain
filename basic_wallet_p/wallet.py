import hashlib
import requests

import sys

# get the server address
if __name__ == '__main__':
    if len(sys.argv) > 1:
        node = sys.argv[1]
    else:
        node = "http://localhost:5000"


f = open("my_id.txt", "r")
id = f.read()
print("ID is", id)
f.close()


r = requests.get(url=f'{node}/wallet/{id}')

data = r.json()

if data['user'] == id:
    print(f"\n{data}")
else:
    print(f"This wallet doesn't belong to you!")

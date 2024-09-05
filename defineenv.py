import sys
import json

secret_username=sys.argv[1]
secret_password=sys.argv[2]

arr = [secret_username, secret_password]

f = open("credentials.json", "wt")

f.write(json.dumps(arr))

f.close()



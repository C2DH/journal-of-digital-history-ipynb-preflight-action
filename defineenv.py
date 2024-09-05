import sys
import json

secret_username=sys.argv[1]
secret_password=sys.argv[2]
secret_api_key = sys.argv[3]

arr = [secret_username, secret_password, secret_api_key]

f = open("credentials.json", "wt")

f.write(json.dumps(arr))

f.close()



def getCredentials():
    import json
    f = open("credentials.json", "r")

    credentials=json.loads(f.read())
    f.close()
    return credentials
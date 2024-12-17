import json

appid = 730590

with open(f"appcache/{appid}.json", "r") as appfile:
    app_json = json.load(appfile)

    depots = app_json["data"][f"{appid}"]["depots"]
print(depots)
import requests 
import argparse
import xmltodict
import json
import os

def dump_appinfo(appid):
    response = requests.get(f"https://api.steamcmd.net/v1/info/{appid}") 
    
    app_json = response.json() 

    os.makedirs("appcache", exist_ok=True)
    with open(f"appcache/{appid}.json", "w") as appfile:
        json.dump(app_json, appfile)


def get_app_maxsize(appid):
    
    response = requests.get(f"https://api.steamcmd.net/v1/info/{appid}") 
    
    app_json = response.json() 
    try:
        depots = app_json["data"][f"{appid}"]["depots"]
    except: 
        print(appid)
        exit()
    sizes = []

    for depot_id, depot_data in depots.items():
        if isinstance(depot_data, dict):  # ensure depot_data is a dictionary
            manifests = depot_data.get("manifests")
            if manifests and "public" in manifests:
                size = manifests["public"].get("size")
                if size is not None:  # check if size exists
                    sizes.append((depot_id, size))
            else:
                pass
                #print(f"depot {depot_id} skipped: 'manifests' or 'public' key missing.")
        else:
            pass
            #print(f"depot {depot_id} skipped: data is not a dictionary.")

    sizenums = []
    for depot_id, size in sizes:
        sizenums.append(int(size))
    #    print(size)
    #print("Biggest: ",max(sizenums))
    return max(sizenums, default=0)

### cli argument parser
cliparser = argparse.ArgumentParser(description="Alternative options.")
cliparser.add_argument("-u", "--url", type=str, help="Provide full URL of a Profile")


# parse arguments
args = cliparser.parse_args()

if args.url:
    steamurl = args.url.rstrip('/')
    url = f"{steamurl}/games?tab=all&xml=1"
    print("calling Steam about provided profile's games...")
else:
    print("\nNo 64 IDs here! use -u [link] to provide a full profile url instead; --help for a list of additional arguments.\n")
    steamurl = input("Please Provide a Steam Custom URL: ")
    if not steamurl == "":
        print(f"calling Steam about {steamurl}'s games...")
        url = f"https://steamcommunity.com/id/{steamurl}/games?tab=all&xml=1"
    else:
        exit()

response = requests.get(url)
lib_data = xmltodict.parse(response.content)

###local testing
#with open("flumandashort_lib.json","r") as inputfile:
#    lib_data = json.load(inputfile)
#if "gamesList" in lib_data and "games" in lib_data["gamesList"]: # check if the response makes sense, if yes: store the important stuff
if (                                            # improved response check. specifically for public profiles with private games.
    "gamesList" in lib_data
    and isinstance(lib_data["gamesList"], dict)
    and "games" in lib_data["gamesList"]
    and lib_data["gamesList"]["games"] is not None
    and "game" in lib_data["gamesList"]["games"]
):
    gamedetails = lib_data["gamesList"]["games"]["game"]
    app_ids = [game["appID"] for game in gamedetails]
    #print(app_ids)
    #print(type(app_ids))
else:
    print(f"couldn't fetch {steamurl}'s apps. perhaps they're private or Steam is unresponsive.")
    exit()




app_sizes = []
for appid in app_ids:
    if dump_appinfo(appid) is not None:
        dump_appinfo(appid)
        #get_app_bytesize = get_app_maxsize(appid)
        #print(get_app_bytesize)
        #app_sizes.append(get_app_bytesize)

print(f":::::::::::::::::::::\nResults for: {steamurl}")
max_size_gib = int(sum(app_sizes)) / (1024 ** 3)
max_size_gb = int(sum(app_sizes)) / (1000 ** 3)
print(f"::: {max_size_gb:.2f} GB")
print(f"or: {max_size_gib:.2f} GiB")
print(f"for {len(app_sizes)} apps steam provided sizes of.")
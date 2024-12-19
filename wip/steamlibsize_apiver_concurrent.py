import requests 
import argparse
import xmltodict
import shutil
import json
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

os.chdir(os.path.dirname(os.path.abspath(__file__)))

def autodelete_useless(nosizeapp):
    os.remove(f"appcache/{nosizeapp}.json")

def delete_cache():
    really = input("delete cache? (y/N) ")
    if not really == "y":
        exit()
    else:
        print(f"deleting cache...")
        shutil.rmtree("appcache/")


def dump_appinfo(appid):
    try:
        response = requests.get(f"https://api.steamcmd.net/v1/info/{appid}") 
        
        app_json = response.json() 
    except:
        print(f"Error: Received status code {response.status_code}")

    os.makedirs("appcache", exist_ok=True)
    with open(f"appcache/{appid}.json", "w") as appfile:
        json.dump(app_json, appfile, indent=4)
    print(f"app dump written: {appid}")

#broken_files = []
nosize = 0
def get_app_maxsize(appid):
    global nosize
    #global broken_files
    #response = requests.get(f"https://api.steamcmd.net/v1/info/{appid}") 
    #app_json = response.json() 
    with open(f"appcache/{appid}.json", "r") as appfile:
        app_json = json.load(appfile)
    try:
        depots = app_json["data"][f"{appid}"]["depots"]
    except: 
        print("Couldn't get size data of", appid)
        nosize += 1
        #broken_files.append(appid)
        return 0
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
cliparser.add_argument("-d", "--delete-cache", action="store_true", help="Delete Cache")


# parse arguments
args = cliparser.parse_args()

if args.delete_cache:
    delete_cache()
    print("done.")
    exit()

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

#######################CONCURRENCY#############################
nosize_files = []
app_sizes = []

#function to handle the data fetching and processing for an individual appid
def process_appid(appid):
    if not os.path.isfile(f"appcache/{appid}.vdf"):
        dump_appinfo(appid)
    if get_app_maxsize(appid) is not None:
        return int(get_app_maxsize(appid))  #return the int of size if it's available
    return None

# concurrent.futures's ThreadPoolExecutor to multithread process_appid
with ThreadPoolExecutor(max_workers=16) as executor:  # max_workers= max numer of threads
    # submit tasks for each appid
    future_to_appid = {executor.submit(process_appid, appid): appid for appid in app_ids}
    
    for future in as_completed(future_to_appid): # process the completed size values provided by the workers
        try:                            # has 'future' placeholder been replaced by completed size value?
            result = future.result()  # retrieve result of processing
            if result is not None:
                app_sizes.append(result)  
            elif result == 0:
                nosize_files.append(future_to_appid[future])
        except Exception as e:
            appid = future_to_appid[future]
            print(f"Error processing appid {appid}: {e}")
###############################################################
#######################ORIGINAL################################
# nosize_files = []
# app_sizes = []
# for appid in app_ids:
#     if not os.path.isfile(f"appcache/{appid}.json"):
#         dump_appinfo(appid)
    
#     get_app_bytesize = int(get_app_maxsize(appid))
#     if get_app_bytesize == 0:
#         nosize_files.append(appid)
#     else:
#         #print(get_app_bytesize)
#         app_sizes.append(get_app_bytesize)
################################################################

print(f":::::::::::::::::::::\nResults for: {steamurl}")
max_size_gib = int(sum(app_sizes)) / (1024 ** 3)
max_size_gb = int(sum(app_sizes)) / (1000 ** 3)
print(f"::: {max_size_gb:.2f} GB")
print(f"or: {max_size_gib:.2f} GiB")
print(f"for {len(app_sizes)} apps steam provided sizes of.")
if nosize > 0:
    print(nosize, " returned no size.")
    print(f"Specifically: {nosize_files}")
    for nosizeapp in nosize_files:
        autodelete_useless(nosizeapp)
    print("removed them from cache.")
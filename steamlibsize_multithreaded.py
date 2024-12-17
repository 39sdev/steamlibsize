import requests
import xmltodict
import json
import subprocess
import vdf
import steamcmd_output_parse as mikus
import sys
import pprint as p
import os
import shutil
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import tarfile
import urllib.request
import time
import warnings

os.chdir(os.path.dirname(os.path.abspath(__file__))) # make script path agnostic
warnings.filterwarnings("ignore", category=DeprecationWarning) # we'll bother with this later
###start of onboarding handler
steamcmd_dir = "steamcmd"
steamcmd_sh = os.path.join(steamcmd_dir, "steamcmd.sh")
steamcmd_url = "https://steamcdn-a.akamaihd.net/client/installer/steamcmd_linux.tar.gz"

if not os.path.exists(steamcmd_sh):
    os.makedirs(steamcmd_dir, exist_ok=True)

    print("\ndownloading and setting up steamcmd...\n")
    with urllib.request.urlopen(steamcmd_url) as response:
        with tarfile.open(fileobj=response, mode="r:gz") as tar:
            tar.extractall(path=steamcmd_dir)
    time.sleep(3.9)
    subprocess.run(["steamcmd/steamcmd.sh", "+quit"])
    print("\ndone.\n")
###end of onboarding handler

def list_empty_vdfs(): #I'm lazy and tried okay, this is for debug purposes 
    cachedir = "vdfcache/"
    empty_file_count = 0
    for filename in os.listdir(cachedir):
        file_path = os.path.join(cachedir, filename)
        
        if os.path.isfile(file_path) and 0 <= os.path.getsize(file_path) <= 25:
            empty_file_count += 1
            print(f"{file_path}")
    print(f"{empty_file_count} empty vdf's. steamcmd ftw.")

def delete_cache():
    really = input("delete cache? (y/N) ")
    if not really == "y":
        exit()
    else:
        cachedir = "vdfcache/"
        print(f"deleting cache...")
        shutil.rmtree(cachedir)

def delete_empty_vdfs():
    cachedir = "vdfcache/"

    # iterate through all files in the directory
    for filename in os.listdir(cachedir):
        file_path = os.path.join(cachedir, filename)
        
        # check if it's a file and if its size is 0 bytes
        if os.path.isfile(file_path) and 0 <= os.path.getsize(file_path) <= 25:
            print(f"deleting empty vdf so it can be reaquired later: {file_path}")
            os.remove(file_path)  # delete the empty file


def get_app_maxsize(appid):
    with open(f"vdfcache/{appid}.vdf","r") as VDFile:
        game_metadata = vdf.load(VDFile)
    #gamesize = game_metadata["2835570"]["depots"]["2835572"]["manifests"]["public"]["size"]
    #print(gamesize)
    if str(appid) in game_metadata and "depots" in game_metadata[str(appid)]:
        depots = game_metadata[f"{appid}"]["depots"]
        #print(depots.keys())

        ###godless shit incoming. 
        # the fact you have to filter the path this way is just :skullemoji:
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
        


    ### ^ in the next session, make this stuff dynamic (Buckshot Roulette appid 2835570) 
    # still hardcoded. 
    # P.S. I really hope every depot has their main under manifest > public, otherwise I kms.   
                        # I assumed it correctly. done.



    # for app_id in app_ids:
    #     print(app_id)

#sys.exit()
###unused
#dirty_app_vdf_content = subprocess.check_output(['steamcmd', '+app_info_print 220', '+quit'])
###
error_dumping = False
def get_vdf_data(appid):
    def loggedin_get_vdf_data(appid): # some appids require a login -.-
        global error_dumping
        ln_dirty_vdf_data = subprocess.run(["steamcmd/steamcmd.sh", "+login anonymous", f"+app_info_request {appid}", "+login anonymous", f"+app_info_print {appid}", "+quit"], stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout.decode()
        
        ln_cleaned_vdf_data = mikus.extract_vdf(ln_dirty_vdf_data)

        with open(f"vdfcache/{appid}.vdf", "w") as output_vdf_file:
            if isinstance(ln_cleaned_vdf_data, str) and len(ln_cleaned_vdf_data) > 39:
                output_vdf_file.write(ln_cleaned_vdf_data)
                print(f"vdf dumper: called nested login function for {appid}")
            else:
                error_dumping = True
                print(f"vdf dumper: Fuck! Error dumping {appid}. written empty vdf file for it.")

    #appid = input("Enter AppID to get vdf of: ")

    ###unused
    #writing dirty vdf from steamcmd to a file
    #with open(f"{appid}_dirty.vdf","w") as dirty_vdf_file:
    #    subprocess.run(["steamcmd", "+app_info_print {appid}", "+quit"], stdout=dirty_vdf_file, stderr=subprocess.STDOUT)
    ###

    #### explanation for future self:
    #       subsubprocess.PIPE is used to redirect all of steamcmd's output into our variable 
    #       & .stdout.decode() is appended cuz the output gets originally stored in some unparsable shitty encoded format I have no clue about yet.
    dirty_vdf_data = subprocess.run(["steamcmd/steamcmd.sh", f"+app_info_print {appid}", "+quit"], stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout.decode()
    #print("-------------------------------------------------!")
    #print(appid)

    cleaned_vdf_data = mikus.extract_vdf(dirty_vdf_data)
    
    #we write our clean vdf app info here atm. will be unused later when the loop works.
                                #okay, I changed my mind, steamcmd is so utterly slow, building a local cache is basically mendatory.
    os.makedirs("vdfcache", exist_ok=True)
    with open(f"vdfcache/{appid}.vdf", "w") as output_vdf_file:
        if isinstance(cleaned_vdf_data, str) and len(cleaned_vdf_data) > 39:
            output_vdf_file.write(cleaned_vdf_data)
            print(f"vdf dumper: written {appid}")
        else:
            loggedin_get_vdf_data(appid)


### cli argument parser
cliparser = argparse.ArgumentParser(description="Manage VDF cache files.")
cliparser.add_argument("-r", "--remove-empty", action="store_true", help="Remove empty files in vdfcache/")
cliparser.add_argument("-l", "--list-empty", action="store_true", help="List empty files in vdfcache/")
cliparser.add_argument("-u", "--url", type=str, help="Provide full URL of a Profile")
cliparser.add_argument("-d", "--delete-cache", action="store_true", help="Delete Cache")


# parse arguments
args = cliparser.parse_args()

# if -r is provided, execute the function
if args.remove_empty:
    delete_empty_vdfs()
    os.remove(os.path.expanduser("~/.local/share/Steam/appcache/appinfo.vdf"))
    
if args.list_empty:
    list_empty_vdfs()
    exit()
if args.delete_cache:
    delete_cache()
    print("done.")
    exit()
###
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


#testinput #app_ids = [304050, 535930, 2085920, 1024010, 1290490, 470220, 1431050, 760160, 1794680, 951440]
app_sizes = []

#function to handle the data fetching and processing for an individual appid
def process_appid(appid):
    if not os.path.isfile(f"vdfcache/{appid}.vdf"):
        get_vdf_data(appid)
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
        except Exception as e:
            appid = future_to_appid[future]
            print(f"Error processing appid {appid}: {e}")


print(f":::::::::::::::::::::\nResults for: {steamurl}")
max_size_gib = int(sum(app_sizes)) / (1024 ** 3)
max_size_gb = int(sum(app_sizes)) / (1000 ** 3)
print(f"::: {max_size_gb:.2f} GB")
print(f"or: {max_size_gib:.2f} GiB")
print(f"for {len(app_sizes)} apps steam provided sizes of.")
if error_dumping:
    print("some apps failed to provide data. run with flag -r to request them again if needed.\notherwise those apps will return with a size of 0.")

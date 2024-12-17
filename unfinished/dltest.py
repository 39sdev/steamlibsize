import os
import subprocess
import tarfile
import urllib.request
import time
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

os.chdir(os.path.dirname(os.path.abspath(__file__)))

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

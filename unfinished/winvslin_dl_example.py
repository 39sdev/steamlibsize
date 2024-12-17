import os
import sys
import tarfile
import zipfile
import urllib.request
import shutil

def download_and_extract_linux():
    url = "https://steamcdn-a.akamaihd.net/client/installer/steamcmd_linux.tar.gz"
    steamcmd_dir = "steamcmd"
    # Create steamcmd directory if it doesn't exist
    if not os.path.exists(steamcmd_dir):
        os.makedirs(steamcmd_dir)

    # Download the file
    print("Downloading steamcmd for Linux...")
    with urllib.request.urlopen(url) as response, open("steamcmd_linux.tar.gz", "wb") as out_file:
        out_file.write(response.read())

    # Extract the tar.gz file
    print("Extracting steamcmd...")
    with tarfile.open("steamcmd_linux.tar.gz", "r:gz") as tar_ref:
        tar_ref.extractall(steamcmd_dir)

    # Clean up the tar.gz file
    os.remove("steamcmd_linux.tar.gz")
    print("Linux steamcmd setup complete.")

def download_and_extract_windows():
    url = "https://steamcdn-a.akamaihd.net/client/installer/steamcmd.zip"
    steamcmd_dir = "steamcmd"
    # Create steamcmd directory if it doesn't exist
    if not os.path.exists(steamcmd_dir):
        os.makedirs(steamcmd_dir)

    # Download the file
    print("Downloading steamcmd for Windows...")
    with urllib.request.urlopen(url) as response, open("steamcmd_windows.zip", "wb") as out_file:
        out_file.write(response.read())

    # Extract the zip file
    print("Extracting steamcmd...")
    with zipfile.ZipFile("steamcmd_windows.zip", 'r') as zip_ref:
        zip_ref.extractall(steamcmd_dir)

    # Clean up the zip file
    os.remove("steamcmd_windows.zip")
    print("Windows steamcmd setup complete.")

def main():
    steamcmd_dir = "steamcmd"

    # Check for existing steamcmd.sh (Linux) or steamcmd.exe (Windows)
    if sys.platform.startswith('linux'):
        if os.path.exists(os.path.join(steamcmd_dir, "steamcmd.sh")):
            print("steamcmd.sh already exists. No action needed.")
            return
        download_and_extract_linux()

    elif sys.platform.startswith('win'):
        if os.path.exists(os.path.join(steamcmd_dir, "steamcmd.exe")):
            print("steamcmd.exe already exists. No action needed.")
            return
        download_and_extract_windows()

    else:
        print("Unsupported OS. This script only works on Linux and Windows.")

if __name__ == "__main__":
    main()

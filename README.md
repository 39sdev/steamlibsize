# SteamLibSize
a Steam library install size calculator.

Created as a python learning experience \
 & because SteamGauge was down and I couldn't find any other tool for this.
 
 ### Only usable in Linux Environments atm. 
 Note: Seems like SteamCMD is currently pretty broken on Windows. \
 &ensp;&ensp;&ensp;&ensp;&ensp;&ensp;Having symptoms simmilar to this [Issue](https://github.com/ValveSoftware/steam-for-linux/issues/9683) just way less predictable \
&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;and no workaround; at least none that I could find during testing. \
&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;The Script should technically work. Let's hope Valve fixes it one day. \
&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;Either that or I'll come up with a better solution till then.
 
 ## Usage

 Don't forget to `pip install -r requirements.txt` \
 Start `steamlibsize_multithreaded.py` from the command line with the `-u [profileurl]` argument. \
When no argument is provided, the script will ask you for a Steam Custom URL ID.
 
 Use `--help` to get a list of arguments to manage the local app cache with.
 
 If the repo's been freshly cloned, the script will automatically download & setup [steamcmd](https://developer.valvesoftware.com/wiki/SteamCMD) in a subdirectory.
 
### Why SteamCMD?
tldr; Because I managed to get more consistent results with it.

There is a Community made api at [steamcmd.net](https://www.steamcmd.net) but it failed to provide information most of the time \
& creating this workaround solution was more fun and rewarding.
##
![demo](https://github.com/39sdev/steamlibsize/blob/main/demo.png?raw=true)

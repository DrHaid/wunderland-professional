# Wunderland Professional

Impress your colleagues, friends and family with this edition of the "Wunderland" wallpaper. With the nostalgic feel of the original [LiveWallpaper - Wunderland](https://github.com/DrHaid/LiveWallpaper-Wunderland) and new climate changing additions.

## Features
- Customize your Wunderland with:
    - expertly handdrawn cows
    - custom community drawings
    - changing weather
- Desktop wallpaper
- Animated Wunderland background for Microsoft Teams

| Desktop wallpaper | MS Teams background |
|-|-|
| ![Desktop](/docs/desktop.png) | ![Teams](/docs/teams.png) |

<sup>* results and reactions may deviate from demonstration</sup>



# How 2 use

1. Download the latest release from the [Releases](https://github.com/DrHaid/wunderland-professional/releases) page
2. Unpack the ZIP file
3. Run the executable

❗Your Anti-Virus may (falsely (trust me bro)) detect the program as malicious. It's not a virus - pinky promise... Anyway, if you don't want to take the risk you can...

#### ...alternatively

1. Clone the repository
2. Make sure you have **Python 3.10** & **pipenv** installed
3. Setup pipenv by running `pipenv install --dev` in the repository directory
4. Run `pipenv run python .\wunderland_wallpaper.py`
5. (Or build the EXE yourself by running `pipenv run pyinstaller build-win.spec`) 

## User Interface
![UI-Screenshot](/docs/ui.png)  

## Run on command line
You can also run the program on the command line (e.g. to use in a scheduled task).
```
> wunderland-generator.exe [-h] [-t] [-d] [-o] [-c Drawing count] [-a] [-w Weather overwrite] [-p Target directory]
```
| Parameter                               | Description                                                           |
|-----------------------------------------|-----------------------------------------------------------------------|
| -t, --teams                             | Saves Wunderland as Microsoft Teams background                        |
| -d, --desktop                           | Sets Wunderland as Desktop wallpaper                                  |
| -o, --online                            | Use custom drawings from API                                          |
| -c Drawing count, --count Drawing count | Define how many drawings populate the Wunderland                      |
| -a, --animated                          | Generates an animated Wunderland                                      |
| -w Weather overwrite                    | Set custom weather instead of current location (check UI for options) |
| -p Target directory                     | Save the Wunderland in a specified directory                          |
 
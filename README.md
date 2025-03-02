# Wunderland Professional
![](https://github.com/DrHaid/wunderland-professional/actions/workflows/release-win.yml/badge.svg)  

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
| Parameter                               | Description                                                                                                                                 |
|-----------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------|
| -d, --desktop                           | Sets Wunderland as Desktop wallpaper                                                                                                        |
| -o, --online                            | Use custom drawings from API                                                                                                                |
| -c Drawing count, --count Drawing count | Define how many drawings populate the Wunderland                                                                                            |
| -w Weather overwrite                    | Set custom weather instead of current location (check UI for options)                                                                       |
| -p File path, --out-path File path      | Save the Wunderland image as a PNG file                                                                                                     |
| -a File path, --animated-path File path | Save the Wunderland animated image as a GIF file                                                                                            |
| -t, --teams                             | Makes the output image suitable to use in MS Teams. Saves a low-res "_thumb.png" copy. Renames the animated GIF to PNG so Teams can load it |


## How to use the Teams background
1. Find the directory where Microsoft Teams saves the backgrounds.
    - old Teams: `C:/Users/<windows_user_name>/AppData/Roaming/Microsoft/Teams/Backgrounds/Uploads`
    - new Teams: `C:/Users/<windows_user_name>/AppData/Local/Packages/MSTeams_8wekyb3d8bbwe/LocalCache/Microsoft/MSTeams/Backgrounds/Uploads`
2. Run `wunderland_generator.exe` with the `--teams` option and save the image in the backgrounds directory
    - ❗If the background is not showing up in Teams: You may have to overwrite an existing background that was added previously using the Teams app

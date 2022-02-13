# Wunderland Professional

Impress your colleagues, friends and family with this edition of the "Wunderland" wallpaper. With the nostalgic feel of the original [LiveWallpaper - Wunderland](https://github.com/DrHaid/LiveWallpaper-Wunderland) and new climate changing additions.

## Features
- Photoreal Cows
- Changing weather
- Wunderland as Teams Background
- Wunderland as desktop wallpaper
- Live Wunderland as webcam background

![Desktop](https://i.imgur.com/YyKADej.png)
![Teams](https://i.imgur.com/c1jdoYM.png)
<sup>* actual results may deviate from demonstration</sup>

# How 2 use
## Requirements
- Python ~3.8 
- Installed requirements using `pip install -r requirements.txt`
## Usage
### Wunderland Wallpaper
Run `wunderland_wallpaper.py` with one or both of the following parameters:
- `-d` to set as Desktop wallpaper
- `-t` to save as Microsoft Teams background

You can also place the `run_wunderland_generator.bat` file in the Windows Startup folder to run on startup (Windows+R, enter `shell:startup`).
<br>
Or you can create a Task in the Windows Task Scheduler to update regularly. When creating a Task set the Action to **Start a Program** and select the `run_wunderland_generator.bat` as target. Choose parameters and enter the directory containing the target in the **Start in (optional)** box:
![Task Scheduler](https://i.imgur.com/JZ0bXgs.png)

### Wunderland Webcam
Install a virtual camera for your operating system. For details read the **Supported virtual cameras** section here https://pypi.org/project/pyvirtualcam/.
<br>
Run `wunderland_webcam.py` with or without the following parameters:
- `-c <camera-index>` to choose which camera to use. Default is 0.
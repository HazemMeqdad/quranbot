<h1 align="center"> fdrbot - بوت فاذكروني</h1>
<p align="center">
بوت فاذكروني لإحياء سنة ذكر الله
</p>

<p align="center">
<a href="https://discord.gg/VX5F54YNuy">
    <img alt="Discord" src="https://img.shields.io/discord/729526735749513267" />
</a> 
<img alt="PyPI - Python Version" src="https://img.shields.io/pypi/pyversions/hikari" />
<img alt="GitHub top language" src="https://img.shields.io/github/languages/top/DwcTeam/fdrbot" /> 
<a href="https://fdrbot.com">
    <img alt="Website" src="https://img.shields.io/website?down_color=red&down_message=offline&up_color=green&up_message=online&url=https%3A%2F%2Ffdrbot.com" />
</a>
</p>

## About

The bot is a bot that helps your server to remember for allah. its send azkar for every 30 minutes or some other times. 

## Features

- Send Azkar for every 30 minutes or some other times.
- Play quran with radio or any other audio source.
- Got prayer times for every city.
- Got all quran holy pages with custom fast cdn.

## How bot works
bot work on python and use a [hikari](https://github.com/hikari-py/hikari) library to connect to the discord gateway & rest discord api, it use a [mongodb](https://www.mongodb.com/) database to store all data, and we use a [lavaplayer](https://github.com/hazemmeqdad/lavaplayer) library to play quran (made by [hazemmeqdad](https://github.com/hazemmeqdad)).

## Setup

### Clone the repository. (required)
```bash
git clone https://github.com/DwcTeam/fdrbot.git  # required git
```
if you hava a problem or not donwload git tool then you can download it from [here](https://git-scm.com/downloads), or you can download repository from [here](https://github.com/DwcTeam/fdrbot/archive/refs/heads/main.zip)

### Install python 3.8 or higher. (required)
Go to [python.org](https://www.python.org/downloads/) and download the python 3.10 version.

### Install reuqired modules. (required)
```bash
pip install -r requirements.txt  # Windows
pip3 install -r requirements.txt  # Unix
```

### Configure the bot. (required)
Rename the file `configuration.example.yml` to `configuration.yml` and edit it. also the (mongo_url & token) is required, any other config is optional. 

### Create a error file. (optional)
Create a `errors.json` file in the same directory as the bot.

### Run the bot.
```bash
python -OO run.py  # Windows
python3 -OO run.py  # Unix
```

## How to use

You can find all commands in [here](https://fdrbot.com/commands)



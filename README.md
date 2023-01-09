<h1 align="center"> fdrbot - بوت فاذكروني</h1>
<p align="center">
بوت فاذكروني لإحياء سنة ذكر الله
</p>

<p align="center">
<a href="https://discord.gg/VX5F54YNuy">
    <img alt="Discord" src="https://img.shields.io/discord/729526735749513267" />
</a> 
<img alt="PyPI - Python Version" src="https://img.shields.io/pypi/pyversions/hikari" />
<img alt="GitHub top language" src="https://img.shields.io/github/languages/top/HazemMeqdad/fdrbot" /> 
</p>

## About

The bot is a bot that helps your server to remember for allah. its send azkar for every 30 minutes or some other times. 

## Features

- Send Azkar for every 30 minutes or some other times.
- Play quran with radio or any other audio source.
- Got prayer times for every city.
- Got all quran holy pages with custom fast cdn.

## How bot works
bot work on python and use a [discord.py](https://github.com/Rapptz/discord.py) library to connect to the discord gateway & rest discord api, it use a [mongodb](https://www.mongodb.com/) database to store all data, and we use a [lavalink](https://github.com/freyacodes/Lavalink) library to play quran audio.

## Setup steps

### Clone the repository. (required)
```bash
git clone https://github.com/DwcTeam/fdrbot.git  # required git
```
if you hava a problem or not donwload git tool then you can download it from [here](https://git-scm.com/downloads), or you can download repository from [here](https://github.com/HazemMeqdad/fdrbot/archive/refs/heads/master.zip)

* This steps to install in linux vps 
### Install docker latest version. (required)
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
DRY_RUN=1 sudo sh ./get-docker.sh
```

### Install docker-compose latest version. (required)
```bash
sudo apt-get update
sudo apt-get install docker-compose-plugin
sudo yum update
sudo yum install docker-compose-plugin
```

### Configure the bot. (required)
create the `.env` file and use the config template from example file `example.env` and edit it. example:
```env
TOKEN="OTg3NTM5NjEw..."
MONGO_URL="mongodb://localhost:27017"
OWNER_IDS="670993199011201025"

# If you went to create slash command on once guild
# DEBUG_GUILD="843710915861545000"

# Just password required
LAVALINK_NODE_PASSWORD="youshallnotpass"  # lavalink password
```

### Create a docker container
Open the folder of your clone
```bash
docker-compose up -d
```

### Other commands
```bash
docker-compose stop  # to stop the bot
```

## How to use

You can find all commands in on use the help command <br />
![image](https://user-images.githubusercontent.com/66125469/211267488-ecba2b2b-46bb-40c8-a833-6d25696f2ea3.png)
# Some screenshots of commands
![image](https://user-images.githubusercontent.com/66125469/211267581-8431805b-313c-45e2-abf2-af185aa8ddef.png) <br />
![image](https://user-images.githubusercontent.com/66125469/211267730-b4621960-d45b-499e-b77e-8c560e11b528.png) <br />
![image](https://user-images.githubusercontent.com/66125469/211267827-82280fb0-2b11-442a-844d-eeb1c780a8cc.png)




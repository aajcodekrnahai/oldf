#Join me at telegram @dev_gagan

from pyrogram import Client

from telethon.sessions import StringSession
from telethon.sync import TelegramClient

from decouple import config
import logging, time, sys

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logging.getLogger("pyrogram").setLevel(logging.WARNING)
logging.getLogger("telethon").setLevel(logging.WARNING)


# variables
API_ID = "27945805"
API_HASH = "ddc35a5f93c79c257d3cceafd3d97d2f"
BOT_TOKEN = "7003513788:AAGcKClYLeU_E3Xekm2AmHGjFpaXi9AtE88"
SESSION = "BQGqa00AFfzR9_NvtxJWXHDSpN7PAqZTxTAnPdDsr9y41pg_nB1U1QGymFEAL6g3y6FEatD8xsMcyEMjNOMEe7sSTISweLZIMfnjl88rBer9-2YOcs8A7Gk8-eBaic8167ccjerPAWwP9zlBd5e4qB2HtY_uiaCOF66SnyX3UbOkYTV632pVKMPQAdMfk88_wHPrZqJAMzxOgZ74DUxiXs-OWgN4dZ_RHwHkwNeHO8AldRFkcYXcoMw6kg6wViekwi42mIU79Vyc8XzRisVFBb-ZiTCQXYUbDpEuZgXubVbpCytYHo-d8m3NAhqg8i0e4dkX5E_xcQslevQMlSWer5Y605vpVgAAAAFpU1rjAA"
FORCESUB = "noobankitcoder"
AUTH = "6441456023"
SUDO_USERS = []

if len(AUTH) != 0:
    SUDO_USERS = {int(AUTH.strip()) for AUTH in AUTH.split()}
else:
    SUDO_USERS = set()

bot = TelegramClient('bot', API_ID, API_HASH).start(bot_token=BOT_TOKEN) 

userbot = Client("myacc",api_id=API_ID,api_hash=API_HASH,session_string=SESSION)

try:
    userbot.start()
except BaseException:
    print("Your session expired please re add that... thanks @dev_gagan.")
    sys.exit(1)

Bot = Client(
    "SaveRestricted",
    bot_token=BOT_TOKEN,
    api_id=int(API_ID),
    api_hash=API_HASH
)    

try:
    Bot.start()
except Exception as e:
    #print(e)
    logger.info(e)
    sys.exit(1)

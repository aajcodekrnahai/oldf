
# Join t.me/dev_gagan
import re
import asyncio, time, os
import pymongo
from pyrogram.enums import ParseMode , MessageMediaType
from .. import Bot, bot
from main.plugins.progress import progress_for_pyrogram
from main.plugins.helpers import screenshot
from pyrogram import Client, filters
from pyrogram.errors import ChannelBanned, ChannelInvalid, ChannelPrivate, ChatIdInvalid, ChatInvalid, FloodWait

from main.plugins.helpers import video_metadata
from telethon import events
import logging
logging.basicConfig(level=logging.debug,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
logging.getLogger("pyrogram").setLevel(logging.INFO)
logging.getLogger("telethon").setLevel(logging.INFO)

# MongoDB connection string
MONGODB_CONNECTION_STRING = 

# MongoDB database name and collection name
DB_NAME = "renameauth_users"
COLLECTION_NAME = "authorized_users_collections"

OWNER_ID = 

# Establish a connection to MongoDB
mongo_client = pymongo.MongoClient(MONGODB_CONNECTION_STRING)
db = mongo_client[DB_NAME]
collection = db[COLLECTION_NAME]

# Define a dictionary to store user chat IDs
user_chat_ids = {}

async def copy_message_with_chat_id(client, sender, chat_id, message_id):
    # Get the user's set chat ID, if available; otherwise, use the original sender ID
    target_chat_id = user_chat_ids.get(sender, sender)
    try:
        await client.copy_message(target_chat_id, chat_id, message_id)
    except Exception as e:
        error_message = f"Error occurred while sending message to chat ID {target_chat_id}: {str(e)}"
        await client.send_message(sender, error_message)
        await client.send_message(sender, f"Make Bot admin in your Channel - {target_chat_id} and restart the process after /cancel")

async def send_message_with_chat_id(client, sender, message, parse_mode=None):
    # Get the user's set chat ID, if available; otherwise, use the original sender ID
    chat_id = user_chat_ids.get(sender, sender)
    try:
        await client.send_message(chat_id, message, parse_mode=parse_mode)
    except Exception as e:
        error_message = f"Error occurred while sending message to chat ID {chat_id}: {str(e)}"
        await client.send_message(sender, error_message)
        await client.send_message(sender, f"Make Bot admin in your Channel - {chat_id} and restart the process after /cancel")

async def send_video_with_chat_id(client, sender, path, caption, duration, hi, wi, thumb_path, upm):
    # Get the user's set chat ID, if available; otherwise, use the original sender ID
    chat_id = user_chat_ids.get(sender, sender)
    try:
        await client.send_video(
            chat_id=chat_id,
            video=path,
            caption=caption,
            supports_streaming=True,
            duration=duration,
            height=hi,
            width=wi,
            thumb=thumb_path,
            progress=progress_for_pyrogram,
            progress_args=(
                client,
                '**__Uploading: [Team SPY](https://t.me/devggn)__**\n ',
                upm,
                time.time()
            )
        )
    except Exception as e:
        error_message = f"Error occurred while sending video to chat ID {chat_id}: {str(e)}"
        await client.send_message(sender, error_message)
        await client.send_message(sender, f"Make Bot admin in your Channel - {chat_id} and restart the process after /cancel")


async def send_document_with_chat_id(client, sender, path, caption, thumb_path, upm):
    # Get the user's set chat ID, if available; otherwise, use the original sender ID
    chat_id = user_chat_ids.get(sender, sender)
    try:
        await client.send_document(
            chat_id=chat_id,
            document=path,
            caption=caption,
            thumb=thumb_path,
            progress=progress_for_pyrogram,
            progress_args=(
                client,
                '**__Uploading:__**\n**__Bot made by [Team SPY](https://t.me/devggn)__**',
                upm,
                time.time()
            )
        )
    except Exception as e:
        error_message = f"Error occurred while sending document to chat ID {chat_id}: {str(e)}"
        await client.send_message(sender, error_message)
        await client.send_message(sender, f"Make Bot admin in your Channel - {chat_id} and restart the process after /cancel")

def load_authorized_users():
    """
    Load authorized user IDs from the MongoDB collection
    """
    authorized_users = set()
    for user_doc in collection.find():
        if 'user_id' in user_doc:
            authorized_users.add(user_doc["user_id"])
    return authorized_users

def save_authorized_users(authorized_users):
    """
    Save authorized user IDs to the MongoDB collection
    """
    collection.delete_many({})
    for user_id in authorized_users:
        collection.insert_one({"user_id": user_id})

def load_delete_words():
    """
    Load delete words from MongoDB
    """
    try:
        words_data = collection.find_one({"_id": "delete_words"})
        if words_data:
            return set(words_data["words"])
        else:
            return set()
    except Exception as e:
        print(f"Error loading delete words: {e}")
        return set()

def save_delete_words(delete_words):
    """
    Save delete words to MongoDB
    """
    try:
        collection.update_one(
            {"_id": "delete_words"},
            {"$set": {"words": list(delete_words)}},
            upsert=True
        )
    except Exception as e:
        print(f"Error saving delete words: {e}")

AUTHORIZED = load_authorized_users()
DELETE_WORDS = load_delete_words()
# Add after load_delete_words and save_delete_words around line 76

def load_replacement_words():
    """
    Load replacement words from MongoDB
    """
    try:
        words_data = collection.find_one({"_id": "replacement_words"})
        if words_data:
            return words_data["words"]
        else:
            return {}
    except Exception as e:
        print(f"Error loading replacement words: {e}")
        return {}

def save_replacement_words(replacement_words):
    """
    Save replacement words to MongoDB
    """
    try:
        collection.update_one(
            {"_id": "replacement_words"},
            {"$set": {"words": replacement_words}},
            upsert=True
        )
    except Exception as e:
        print(f"Error saving replacement words: {e}")


# Command to add a word to the list of words to delete
@bot.on(events.NewMessage(incoming=True, pattern='/delete'))
async def delete_word_command_handler(event):
    """
    Command to add a word to the list of words to delete
    """
    # Check if the command is used by an authorized user
    user_id = event.sender_id
    # if user_id not in AUTHORIZED:
    #     return await event.respond("This command is available to paid plan users! Send /plan to know more.")
    
    # Parse the words from the command
    words_to_delete = event.text.split()[1:]
    if not words_to_delete:
        await event.respond("Please provide word(s) to delete!")
        return
    
    # Add the word(s) to the list of words to delete
    for word in words_to_delete:
        DELETE_WORDS.add(word)
    save_delete_words(DELETE_WORDS)
    await event.respond(f"Word(s) added to the list of words to delete: {', '.join(words_to_delete)}")


def thumbnail(sender):
    return f'{sender}.jpg' if os.path.exists(f'{sender}.jpg') else f'thumb.jpg'

# Initialize the dictionary to store user preferences for renaming
user_rename_preferences = {}

# Initialize the dictionary to store user caption
user_caption_preferences = {}

# Function to handle the /setrename command
async def set_rename_command(user_id, custom_rename_tag):
    # Update the user_rename_preferences dictionary
    user_rename_preferences[str(user_id)] = custom_rename_tag

# Function to get the user's custom renaming preference
def get_user_rename_preference(user_id):
    # Retrieve the user's custom renaming tag if set, or default to '@dev_gagan'
    return user_rename_preferences.get(str(user_id), '@dev_gagan')

# Function to set custom caption preference
async def set_caption_command(user_id, custom_caption):
    # Update the user_caption_preferences dictionary
    user_caption_preferences[str(user_id)] = custom_caption

# Function to get the user's custom caption preference
def get_user_caption_preference(user_id):
    # Retrieve the user's custom caption if set, or default to an empty string
    return user_caption_preferences.get(str(user_id), '')

# Add this around line 127, after the /delete command

@bot.on(events.NewMessage(incoming=True, pattern='/addreplacement'))
async def add_replacement_command_handler(event):
    # Command format: /addreplacement <word_to_replace> <replacement>
    try:
        _, word, replacement = event.text.split(' ', 2)
        replacement_words = load_replacement_words()
        replacement_words[word] = replacement
        save_replacement_words(replacement_words)
        await event.respond(f"Replacement added: {word} -> {replacement}")
    except ValueError:
        await event.respond("Usage: /addreplacement <word_to_replace> <replacement>")

@bot.on(events.NewMessage(incoming=True, pattern='/removereplacement'))
async def remove_replacement_command_handler(event):
    # Command format: /removereplacement <word>
    try:
        word = event.text.split(' ')[1]
        replacement_words = load_replacement_words()
        if word in replacement_words:
            del replacement_words[word]
            save_replacement_words(replacement_words)
            await event.respond(f"Replacement removed: {word}")
        else:
            await event.respond(f"No replacement found for: {word}")
    except IndexError:
        await event.respond("Usage: /removereplacement <word>")




@bot.on(events.NewMessage(incoming=True, pattern='/setchat'))
async def set_chat_id(event):
    # Check if the command is used by an authorized user
    user_id = event.sender_id
    #if user_id not in AUTHORIZED:
        #return await event.respond("This command is available to authorized users only.")
    
    # Extract chat ID from the message
    try:
        chat_id = int(event.raw_text.split(" ", 1)[1])
        # Store user's chat ID
        user_chat_ids[event.sender_id] = chat_id
        await event.reply("Chat ID set successfully!")
    except ValueError:
        await event.reply("Invalid chat ID!")



@bot.on(events.NewMessage(incoming=True, pattern='/setcaption'))
async def set_caption_command_handler(event):
    # Check if the command is used by an authorized user
    #if event.sender_id not in AUTHORIZED:
        #return await event.respond("This command is available to paid plan users! Send /plan to know more.")

    # Parse the custom caption from the command
    custom_caption = ' '.join(event.message.text.split(' ')[1:])
    if not custom_caption:
        return await event.respond("Please provide a custom caption!")

    # Call the function to set the custom caption
    await set_caption_command(event.sender_id, custom_caption)
    await event.respond(f"Custom caption set to: {custom_caption}")

async def check(userbot, client, link):
    logging.info(link)
    msg_id = 0
    try:
        msg_id = int(link.split("/")[-1])
    except ValueError:
        if '?single' not in link:
            return False, "**Invalid Link!**"
        link_ = link.split("?single")[0]
        msg_id = int(link_.split("/")[-1])
    if 't.me/c/' in link:
        try:
            chat = int('-100' + str(link.split("/")[-2]))
            await userbot.get_messages(chat, msg_id)
            return True, None
        except ValueError:
            return False, "**Invalid Link!**"
        except Exception as e:
            logging.info(e)
            return False, "Have you joined the channel?"
    else:
        try:
            chat = str(link.split("/")[-2])
            await client.get_messages(chat, msg_id)
            return True, None
        except Exception as e:
            logging.info(e)
            return False, "Maybe bot is banned from the chat, or your link is invalid!"

async def get_msg(userbot, client, sender, edit_id, msg_link, i, file_n):
    edit = ""
    chat = ""
    msg_id = int(i)
    if msg_id == -1:
        await client.edit_message_text(sender, edit_id, "**Invalid Link!**")
        return None
    if 't.me/c/'  in msg_link or 't.me/b/' in msg_link:
        if "t.me/b" not in msg_link:    
            chat = int('-100' + str(msg_link.split("/")[-2]))
        else:
            chat = msg_link.split("/")[-2]
        file = ""
        try:
            msg = await userbot.get_messages(chat_id=chat, message_ids=msg_id)
            logging.info(msg)
            if msg.service is not None:
                await client.delete_messages(chat_id=sender, message_ids=edit_id)
                return None
            if msg.empty is not None:
                await client.delete_messages(chat_id=sender, message_ids=edit_id)
                return None            
            if msg.media and msg.media == MessageMediaType.WEB_PAGE:
                a = b = True
                edit = await client.edit_message_text(sender, edit_id, "Cloning.")
                if '--'  in msg.text.html or '**' in msg.text.html or '__' in msg.text.html or '~~' in msg.text.html or '||' in msg.text.html or '```' in msg.text.html or '`' in msg.text.html:
                    await send_message_with_chat_id(client, sender, msg.text.html, parse_mode=ParseMode.HTML)
                    a = False
                if '<b>' in msg.text.markdown or '<i>' in msg.text.markdown or '<em>' in msg.text.markdown  or '<u>' in msg.text.markdown or '<s>' in msg.text.markdown or '<spoiler>' in msg.text.markdown or '<a href=>' in msg.text.markdown or '<pre' in msg.text.markdown or '<code>' in msg.text.markdown or '<emoji' in msg.text.markdown:
                    await send_message_with_chat_id(client, sender, msg.text.markdown, parse_mode=ParseMode.MARKDOWN)
                    b = False
                if a and b:
                    await send_message_with_chat_id(client, sender, msg.text.markdown, parse_mode=ParseMode.MARKDOWN)
                await edit.delete()
                return None
            if not msg.media and msg.text:
                a = b = True
                edit = await client.edit_message_text(sender, edit_id, "Cloning.")
                if '--'  in msg.text.html or '**' in msg.text.html or '__' in msg.text.html or '~~' in msg.text.html or '||' in msg.text.html or '```' in msg.text.html or '`' in msg.text.html:
                    await send_message_with_chat_id(client, sender, msg.text.html, parse_mode=ParseMode.HTML)
                    a = False
                if '<b>' in msg.text.markdown or '<i>' in msg.text.markdown or '<em>' in msg.text.markdown  or '<u>' in msg.text.markdown or '<s>' in msg.text.markdown or '<spoiler>' in msg.text.markdown or '<a href=>' in msg.text.markdown or '<pre' in msg.text.markdown or '<code>' in msg.text.markdown or '<emoji' in msg.text.markdown:
                    await send_message_with_chat_id(client, sender, msg.text.markdown, parse_mode=ParseMode.MARKDOWN)
                    b = False
                if a and b:
                    await send_message_with_chat_id(client, sender, msg.text.markdown, parse_mode=ParseMode.MARKDOWN)
                await edit.delete()
                return None
            if msg.media == MessageMediaType.POLL:
                await client.edit_message_text(sender, edit_id, 'poll media cant be saved')
                return 
            edit = await client.edit_message_text(sender, edit_id, "Trying to Download.")
            file = await userbot.download_media(msg, progress=progress_for_pyrogram, progress_args=(client, "**__Unrestricting__: __[Team SPY](https://t.me/devggn)__**\n ", edit, time.time()))
            
            # Retrieve user's custom renaming preference if set, default to '@dev_gagan' otherwise
            custom_rename_tag = get_user_rename_preference(sender)
            # retriving name 
            last_dot_index = str(file).rfind('.')
            if last_dot_index != -1 and last_dot_index != 0:
              original_file_name = str(file)[:last_dot_index]
              file_extension = str(file)[last_dot_index + 1:]
            else:
              original_file_name = str(file)
              file_extension = 'mp4'
            
            #Removing Words
            delete_words = load_delete_words()
            for word in delete_words:
              original_file_name = original_file_name.replace(word, "")
            
            # Rename the file with the updated file name and custom renaming tag
            video_file_name = original_file_name + " " + custom_rename_tag
            new_file_name = original_file_name + " " + custom_rename_tag + "." + file_extension
            os.rename(file, new_file_name)
            file = new_file_name   
          
            path = file
            await edit.delete()
            upm = await client.send_message(sender, 'Preparing to Upload!')
            
            caption = str(file)
            if msg.caption is not None:
                caption = msg.caption
            if file_extension in ['mkv', 'mp4', 'webm', 'mpe4', 'mpeg', 'ts', 'avi', 'flv', 'org', 'm4v', " Economy by Vivek Singh"]:
                if file_extension in ['webm', 'mkv', 'mpe4', 'mpeg', 'ts', 'avi', 'flv', 'org', 'm4v', " Economy by Vivek Singh"]:
                    path = video_file_name + ".mp4"
                    os.rename(file, path) 
                    file = path
                data = video_metadata(file)
                duration = data["duration"]
                wi = data["width"]
                hi = data["height"]
                logging.info(data)

                if file_n != '':
                    if '.' in file_n:
                        path = f'/app/downloads/{file_n}'
                    else:
                        path = f'/app/downloads/{file_n}.' + str(file).split(".")[-1]

                    os.rename(file, path)
                    file = path
                try:
                    thumb_path = thumbnail(sender)
                except Exception as e:
                    logging.info(e)
                    thumb_path = None

                # Modify the caption based on user's custom caption preference
                # Add this after word deletion around line 372

                # Load replacement words
                replacement_words = load_replacement_words()

                # Apply word replacements
                for word, replace_word in replacement_words.items():
                 final_caption = final_caption.replace(word, replace_word)

                #   final_caption = final_caption.replace(word, '  ')
                # final_caption = re.sub(r'\s{2,}', ' ', final_caption.strip())
                # final_caption = re.sub(r'\n{2,}', '\n', final_caption)
                caption = f"`{final_caption}`\n\n`{custom_caption}`" if custom_caption else f"`{final_caption}`\n\n__**[Team SPY](https://t.me/devggn)**__"
                await send_video_with_chat_id(client, sender, path, caption, duration, hi, wi, thumb_path, upm)
            elif file_extension in ['jpg', 'jpeg', 'png', 'webp']:
                if file_n != '':
                    if '.' in file_n:
                        path = f'/app/downloads/{file_n}'
                    else:
                        path = f'/app/downloads/{file_n}.' + str(file).split(".")[-1]
                    os.rename(file, path)
                    file = path       
                # Modify the caption based on user's custom caption preference
                custom_caption = get_user_caption_preference(sender)
                original_caption = msg.caption if msg.caption else ''
                final_caption = f"{original_caption}" if custom_caption else f"{original_caption}"
                delete_words = load_delete_words()
                for word in delete_words:
                   final_caption = final_caption.replace(word, '  ')
                # final_caption = re.sub(r'\s{2,}', ' ', final_caption.strip())
                # final_caption = re.sub(r'\n{2,}', '\n', final_caption)
                caption = f"`{final_caption}`\n\n`{custom_caption}`" if custom_caption else f"`{final_caption}`\n\n__**[Team SPY](https://t.me/devggn)**__"
                await upm.edit("Uploading photo.")
                await bot.send_file(sender, path, caption=caption)
            else:
                if file_n != '':
                    if '.' in file_n:
                        path = f'/app/downloads/{file_n}'
                    else:
                        path = f'/app/downloads/{file_n}.' + str(file).split(".")[-1]
                    os.rename(file, path)
                    file = path
                thumb_path = thumbnail(sender)
                # Modify the caption based on user's custom caption preference
                custom_caption = get_user_caption_preference(sender)
                original_caption = msg.caption if msg.caption else ''
                final_caption = f"{original_caption}" if custom_caption else f"{original_caption}"
                delete_words = load_delete_words()
                for word in delete_words:
                  final_caption = final_caption.replace(word, '  ')
                # final_caption = re.sub(r'\s{2,}', ' ', final_caption.strip())
                # final_caption = re.sub(r'\n{2,}', '\n', final_caption)
                caption = f"`{final_caption}`\n\n`{custom_caption}`" if custom_caption else f"`{final_caption}`\n\n__**[Team SPY](https://t.me/devggn)**__"
                await send_document_with_chat_id(client, sender, path, caption, thumb_path, upm)
                    
            os.remove(file)
            await upm.delete()
            return None
        except (ChannelBanned, ChannelInvalid, ChannelPrivate, ChatIdInvalid, ChatInvalid):
            await client.edit_message_text(sender, edit_id, "Bot is not in that channel/ group \n send the invite link so that bot can join the channel ")
            return None
    else:
        edit = await client.edit_message_text(sender, edit_id, "Cloning.")
        chat =  msg_link.split("/")[-2]
        await copy_message_with_chat_id(client, sender, chat, msg_id)
        await edit.delete()
        return None   
    
async def get_bulk_msg(userbot, client, sender, msg_link, i):
    x = await client.send_message(sender, "Processing!")
    file_name = ''
    await get_msg(userbot, client, sender, x.id, msg_link, i, file_name) 

import asyncio
import discord
import json
import requests
import re
import time
import threading
from random import choice
from pyfp import Pipe, Match
from doughbot.bot_helpers import command_prefix, restrict_to, get_role

MUTE_REGEX = re.compile(r"^mute <@!\d+> \d+[s,m,h,d,w]")

class Bot(discord.Client):
    def run(self, config_path):
        with open(config_path, "r") as config_file:
            config = json.load(config_file)

            if "token" not in config:
                raise IOError("Config does not contain bot token.")

            if "pixbay-key" not in config:
                raise IOError("Config does not contain pixbay key.")
            
            self._token = config["token"]
            self._pixbay_key = config["pixbay-key"]
        
        super().run(self._token)

    async def on_ready(self):
        print("Logged in")

    @command_prefix(">")
    async def on_message(self, message):
        await Match(message.content) \
        .branch("doughnut", lambda: self.respond_with_doughnut(message)) \
        .branch(lambda x: MUTE_REGEX.match(x), lambda: self.mute_user(message)) \
        .default(lambda: self.ignore_message()) \
        .get()
    
    async def on_raw_reaction_add(self, payload):
        print("reaction")

    async def ignore_message(self):
        pass
    
    def get_doughnut_url(self):
        params = {
            "key": self._pixbay_key,
            "q": "doughnut",
            "image_type": "illustration",
            "per_page": 200
        }

        picture_url = Pipe(params) \
            .to(requests.get, "https://pixabay.com/api/") \
            .to(lambda x: x.content) \
            .to(json.loads) \
            .to(lambda x: x.get("hits")) \
            .to(choice) \
            .to(lambda x: x.get("webformatURL")) \
            .get()
        
        return picture_url

    async def respond_with_doughnut(self, message):
            doughnut_embed = discord.Embed().set_image(url=self.get_doughnut_url())
            channel = message.channel

            await channel.send(f"{message.author.mention} Order up!", embed=doughnut_embed)
    
    @staticmethod
    def unmute_user(member, mute_role, duration, loop):
        time.sleep(duration)
        future = asyncio.run_coroutine_threadsafe(member.remove_roles(mute_role), loop)
        
        try_count = 0
        while not future.done():
            if try_count > 5:
                break

            time.sleep(0.5)
            count += 1
        else:
            pass

    @restrict_to("Admin")
    async def mute_user(self, message):
        duration = message.content.split(" ")[2]
        print(duration)
        mute_role = get_role(message.guild, "Muted")
        if mute_role.is_empty():
            print("No mute role")
            return
        else:
            mute_role = mute_role.unwrap()

        muted_member = message.mentions[0]
        await muted_member.add_roles(mute_role)
        await message.channel.send(f"Muting {muted_member}")

        event_loop = asyncio.get_event_loop()
        unmute_thread = threading.Thread(target=Bot.unmute_user, args=(muted_member, mute_role, 100, event_loop))
        unmute_thread.start()


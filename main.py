# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import json
import os
import time
from typing import Mapping, Tuple
import discord
import random
import requests
from discord.abc import Messageable
from discord.ext.commands import Bot, Context

IMAGES = [
    'https://imgur.com/a/p2aceSH',
    'https://imgur.com/a/dhwhYGl',
    'https://imgur.com/a/PJqGQ11',
    'https://imgur.com/a/F4coyqe',
    'https://imgur.com/a/72uEfym',
    'https://imgur.com/a/imb9wH6',
    'https://imgur.com/a/FcRIdQO',
    'https://imgur.com/a/PmkqIJF',
    'https://imgur.com/a/FsUuSVM',
    'https://imgur.com/a/ZcClOeq',
    'https://imgur.com/a/XgckFOK',
    'https://imgur.com/a/yCwvmN7',
    'https://imgur.com/a/csfU6vJ',
    'https://imgur.com/a/NE4EeNd',
    'https://imgur.com/a/OThWL8t',
    'https://imgur.com/a/LbloDmH',
    'https://imgur.com/a/kkUa4tH',
    'https://imgur.com/a/EAAAvKZ',
    'https://imgur.com/a/8mXks5v',
    'https://imgur.com/a/51AgiNL',
    'https://imgur.com/a/KfGhe1t',
    'https://imgur.com/a/bw4X7NK',
    'https://imgur.com/a/V8q6hYU',
    'https://imgur.com/a/mx5PyeY',
    'https://imgur.com/a/ZFAF7Kw',
    'https://imgur.com/a/NYASpE3',
    'https://imgur.com/a/4i6CTc5',
    'https://imgur.com/a/0s4nnGA',
    'https://imgur.com/a/N5BtSbh' # Rare Ed Pretzel
]

WIKI_HEADERS = {
    'User-Agent': 'ShadesBot'
}

client = Bot(command_prefix="!")
price_cache: Mapping[int, Tuple[int, int, int, int]] = {}

with open("mappings.json") as f:
    raw_mappings = json.load(f)
    mappings = {
        m['name'].lower(): m['id'] for m in raw_mappings
    }

print(f"Loaded {len(mappings)} mappings")

def get_choice() -> int:
    c = random.randint(0, len(IMAGES) - 1)
    if IMAGES[c] == IMAGES[-1]:
        j = random.randint(0, 100)
        if j == 0:
            return c
        else:
            return get_choice()
    else:
        return c

@client.command()
async def mm(ctx: Context):
    c = get_choice()
    print(f"Sending image {IMAGES[c]} ({c})")
    image = IMAGES[c]
    if not isinstance(ctx.channel, discord.VoiceChannel):
        channel: Messageable = ctx.channel
        msg = await channel.send(f"{image} <@742858582281945220>")
        await msg.add_reaction("<a:Sensei:918707966184677378>")


def refresh_cache(item_id: int) -> None:
    item_price_resp = requests.get(f'https://prices.runescape.wiki/api/v1/osrs/latest?id={item_id}', headers=WIKI_HEADERS).json()
    data = item_price_resp['data'][str(item_id)]
    price_cache[item_id] = (data['high'], data['highTime'], data['low'], data['lowTime'])


@client.command()
async def price(ctx: Context, *item_args):
    item_name = ' '.join(item_args)
    print(f"Looking up price for {item_name}")
    item_id = mappings.get(item_name)
    if item_id:
        # Check if it's in cache to avoid hitting wiki a bunch
        cache_entry = price_cache.get(item_id)
        if cache_entry:
            cache_time_stamp = max(cache_entry[1], cache_entry[3])
            curr_time_stamp = round(time.time())
            # Cache price for 5 minutes
            if curr_time_stamp - cache_time_stamp > 300:
                refresh_cache(item_id)
        else:
            refresh_cache(item_id)
        cache_entry = price_cache.get(item_id)
        if not isinstance(ctx.channel, discord.VoiceChannel):
            await ctx.channel.send(f"{item_name} hi: {cache_entry[0]:,}, lo: {cache_entry[2]:,}")
    else:
        print(f"No item_id found for {item_name}")
        await ctx.message.add_reaction('❌')


print("Running")
client.run(os.environ.get('DISCORD_SECRET'))
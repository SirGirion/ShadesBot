# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import json
import os
import time
import sys
import discord
import logging
import random
from discord.flags import Intents
from discord.message import Message
import requests
from typing import Mapping, Tuple
from discord.abc import Messageable
from discord.ext.commands import Bot, check, Context


discord_logger = logging.getLogger('discord')
discord_logger.setLevel(logging.DEBUG)
discord_handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='a')
discord_handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
discord_logger.addHandler(discord_handler)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

seven_logger = logging.getLogger('__seven__')
seven_logger.setLevel(logging.DEBUG)
seven_handler = logging.FileHandler(filename='seven.log', encoding='utf-8', mode='a')
seven_handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
seven_logger.addHandler(seven_handler)


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
    'https://imgur.com/a/0s4nnGA'
]

RARE_EDS = [
    'https://imgur.com/a/N5BtSbh', # Rare Ed Pretzel, 0-3
    'https://imgur.com/a/J70RMjb', # Mega Ed Pretzel, 4-7
    'https://imgur.com/a/PwRTrUE',  # Nega Ed Pretzel, 8-9
    'https://imgur.com/a/ujj7Uj2' # Stoner matt, 10
]

HONKS = [
    'Burn the churches\nHang the christfags in the street',
    'Shut your mouth cat!'
]

GIRION_ID = 235181847770824707
CJ_ID = 378992331782619137
SEVEN_ID = 287003884889833472
GOOSE_ID = 264822497206206468


def is_owner():
    async def predicate(ctx):
        return ctx.author.id == GIRION_ID
    return check(predicate)

WIKI_HEADERS = {
    'User-Agent': 'ShadesBot'
}

client = Bot(command_prefix="!", intents=Intents.all())
price_cache: Mapping[int, Tuple[int, int, int, int]] = {}
mappings = {}


def load_mappings():
    with open("mappings.json") as f:
        raw_mappings = json.load(f)
        for m in raw_mappings:
            mappings[m['name'].lower()] = (m['id'], m['icon'])

    logger.info(f"Loaded {len(mappings)} mappings")


@client.command()
@is_owner()
async def reload_mappings(ctx: Context) -> None:
    logger.info('Reloading mappings')
    mapping_resp = requests.get('https://prices.runescape.wiki/api/v1/osrs/mapping', headers=WIKI_HEADERS).json()
    with open('mappings.json', 'w') as f:
        json.dump(mapping_resp, f)


def get_choice() -> Tuple[int, bool]:
    # Roll for regular or rare pretzel
    roll = random.randint(0, len(IMAGES))
    if roll < len(IMAGES):
        return (roll, False)
    else:
        # On the rare pretzel drop table
        # roll a d30 to see if actually getting a rare ed
        roll2 = random.randint(0, 29)
        if roll2 == 0:
            # Actually on the pretzel table, roll a d11 to determine which pretzel
            roll3 = random.randint(0, 10)
            if roll3 >=0 and roll3 <= 3:
                return (0, True)
            elif roll3 >= 4 and roll3 <= 7:
                return (1, True)
            elif roll3 >= 8 and roll3 <= 9:
                return (2, True)
            else:
                return (3, True)
        else:
            # Re-roll
            return get_choice()


@client.command()
@is_owner()
async def pretzel(ctx: Context, choice: int) -> None:
    channel: Messageable = ctx.channel
    image = RARE_EDS[choice]
    msg = await channel.send(f"{image} <@{SEVEN_ID}>")
    await msg.add_reaction("<a:Sensei:918707966184677378>")


@client.command()
async def mm(ctx: Context):
    if ctx.message.author.id == CJ_ID:
        await ctx.message.add_reaction('🖕')
        return
    c, rare_ed = get_choice()
    img = IMAGES[c] if not rare_ed else RARE_EDS[rare_ed]
    if not isinstance(ctx.channel, discord.VoiceChannel):
        print(f"Sending image {img} ({c})")
        channel: Messageable = ctx.channel
        msg = await channel.send(f"{img} <@{SEVEN_ID}>")
        await msg.add_reaction("<a:Sensei:918707966184677378>")


def refresh_cache(item_id: int) -> None:
    item_price_resp = requests.get(f'https://prices.runescape.wiki/api/v1/osrs/latest?id={item_id}', headers=WIKI_HEADERS).json()
    data = item_price_resp['data'][str(item_id)]
    price_cache[item_id] = (data['high'], data['highTime'], data['low'], data['lowTime'])


@client.listen()
async def on_message(message: Message):
    if message.author.id == SEVEN_ID:
        if random.randint(0, 4) == 0:
            await message.add_reaction("<a:Sensei:918707966184677378>")
        seven_logger.info(f'channel({message.channel}): {message.content}')
    if message.author.id == 434975622586957824 and '<:FeelsAnnoyedMan:722224702415962243>' in message.content:
        print('Trolling mystic')
        await message.add_reaction('🌳')


@client.command()
async def price(ctx: Context, *item_args):
    if ctx.message.author.id == CJ_ID:
        await ctx.message.add_reaction('🖕')
        return
    
    item_name = ' '.join(item_args)
    item_name = item_name.lower()
    print(f"Looking up price for {item_name}")
    item_id, icon = mappings.get(item_name, (None, None))
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
            icon = icon.replace(' ', '_')
            embed = discord.Embed()
            embed.title = item_name
            embed.color = 52224
            embed.set_thumbnail(url=f"https://raw.githubusercontent.com/runelite/static.runelite.net/gh-pages/cache/item/icon/{item_id}.png")
            embed.description = f"hi: {cache_entry[0]:,}, lo: {cache_entry[2]:,}"
            await ctx.channel.send(embed=embed)
    else:
        print(f"No item_id found for {item_name}")
        await ctx.message.add_reaction('❌')


@client.command()
async def apple(ctx: Context):
    if not isinstance(ctx.channel, discord.VoiceChannel):
        channel: Messageable = ctx.channel
        await channel.send(f"Apple phones are better on account of Girion posting 1 graph and then battering me by calling me a retard and then shoving semantics up my ass until I lost the will to argue")


@client.command()
async def honk(ctx: Context):
    if not isinstance(ctx.channel, discord.VoiceChannel):
        channel: Messageable = ctx.channel
        honk_string = random.choice(HONKS)
        await channel.send(honk_string)


load_mappings()
print("Running")
client.run(os.environ.get('DISCORD_SECRET'))
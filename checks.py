from discord.ext import commands
from main import GIRION_ID


def is_owner():
    async def predicate(ctx):
        return ctx.author.id == GIRION_ID
    return commands.check(predicate)
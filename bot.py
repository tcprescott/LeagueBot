import asyncio

import discord
from discord.ext import commands

import logging
import logging.handlers as handlers

import leaguebot.config as cfg
config = cfg.get_config()

discordbot = commands.Bot(
    command_prefix='$',
)
discordbot.load_extension("leaguebot.admin")
discordbot.load_extension("leaguebot.mods")
discordbot.load_extension("leaguebot.racers")

logger = logging.getLogger('discord')
logger.setLevel(logging.INFO)
handler = handlers.TimedRotatingFileHandler(filename='logs/discord.log', encoding='utf-8', when='D', interval=1, backupCount=30)
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

@discordbot.event
async def on_ready():
    try:
        await discordbot.change_presence(activity=discord.Game(name='$help for available cmds'))
        logger.info('discord - {username} - {userid}'.format(
            username=discordbot.user.name,
            userid=discordbot.user.id
            ))

    except Exception as e:
        print(e)

    @discordbot.event
    async def on_command_error(ctx, error):
        if isinstance(error, commands.CheckFailure):
            await ctx.message.add_reaction('🚫')
            return
        elif isinstance(error, commands.CommandNotFound):
            pass
        elif isinstance(error, commands.errors.MissingRequiredArgument):
            await ctx.send(error)
            await ctx.message.add_reaction('👎')
        else:
            await ctx.send(error)
            await ctx.message.add_reaction('👎')
        await ctx.message.remove_reaction('⌚',ctx.bot.user)

@discordbot.check
async def globally_block_dms(ctx):
    if ctx.guild is None:
        return False
    else:
        return True



if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(discordbot.start(config['discord_bot_token']))
    loop.run_forever()
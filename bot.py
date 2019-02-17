import asyncio

import discord
from discord.ext import commands

import logging
import logging.handlers as handlers

import pyz3r_asyncio

import leaguebot.database as db
import leaguebot.alttpr as alttpr

import leaguebot.config as cfg
config = cfg.get_config()

discordbot = commands.Bot(
    command_prefix='$',
)

logger = logging.getLogger('spoilerbot')
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

# generate a seed
@discordbot.command()
async def genseed(ctx):
    await ctx.message.add_reaction('⌚')
    lbdb = db.LeagueBotDatabase(loop)

    await lbdb.connect()
    settings = await lbdb.get_seed_settings(ctx.guild.id)
    seed = await alttpr.generate_game(
        randomizer=settings['randomizer'],
        difficulty=settings['difficulty'],
        goal=settings['goal'],
        logic=settings['logic'],
        state=settings['state'],
        shuffle=settings['shuffle'],
        swords=settings['swords'],
        variation=settings['variation'],
    )

    await ctx.send(
        '------------------------\n'
        'Requested seed for {user}:\n\n'
        'Permalink: {permalink}\n'
        'File select code: [{fscode}]\n'.format(
            user=ctx.author.name,
            fscode=' | '.join(await seed.code()),
            permalink=await seed.url()
        )
    )

    result = await lbdb.get_config(ctx.guild.id, 'logchannel')
    try:
        logchannel = discord.utils.get(ctx.guild.text_channels, name=result['value'])
        await logchannel.send(
            '------------------------\n'
            'Requested seed for {user}:\n\n'
            'Permalink: {permalink}\n'
            'File select code: [{fscode}]\n'.format(
                user=ctx.author.name + '#' + ctx.author.discriminator,
                fscode=' | '.join(await seed.code()),
                permalink=await seed.url()
            )
        )
    except KeyError:
        pass

    await lbdb.close()

    await ctx.message.add_reaction('👍')
    await ctx.message.remove_reaction('⌚',ctx.bot.user)

@discordbot.command()
async def week(ctx):
    await ctx.message.add_reaction('⌚')
    lbdb = db.LeagueBotDatabase(loop)
    await lbdb.connect()
    settings = await lbdb.get_seed_settings(ctx.guild.id)

    await ctx.send(msg_settings(settings))

    await lbdb.close()
    await ctx.message.add_reaction('👍')
    await ctx.message.remove_reaction('⌚',ctx.bot.user)

# configure the seed for the week and store it in the database
@discordbot.group()
@commands.has_any_role('admin','mods')
async def setseed(ctx):
    pass

@setseed.command()
async def item(ctx, difficulty, goal, logic, mode, weapons, variation):
    await ctx.message.add_reaction('⌚')

    verify = await alttpr.verify_game_settings('item',
        state = mode,
        logic = logic,
        swords = weapons,
        goal = goal,
        difficulty = difficulty,
        variation = variation
    )

    if not verify == None:
        await ctx.send('Invalid settings: {settings}'.format(
            settings=', '.join(verify)
        ))
        return

    lbdb = db.LeagueBotDatabase(loop)
    await lbdb.connect()
    await lbdb.set_seed_settings(
            randomizer = 'item',
            guild = ctx.guild.id,
            state = mode,
            logic = logic,
            swords = weapons,
            shuffle = None,
            goal = goal,
            difficulty = difficulty,
            variation = variation
        )

    settings = await lbdb.get_seed_settings(ctx.guild.id)

    result = await lbdb.get_config(ctx.guild.id, 'logchannel')
    try:
        logchannel = discord.utils.get(ctx.guild.text_channels, name=result['value'])
        await logchannel.send(
            '------------------------\n'
            'Seed settings changed!\n'
            'Initiated by {user}:\n{msg}'.format(
                    user=ctx.author.name + "#" + ctx.author.discriminator,
                    msg=msg_settings(settings)
                )
        )
    except KeyError:
        pass

    await lbdb.close()

    await ctx.message.add_reaction('👍')
    await ctx.message.remove_reaction('⌚',ctx.bot.user)

@setseed.command()
async def entrance(ctx, difficulty, goal, logic, mode, shuffle, variation):
    await ctx.message.add_reaction('⌚')

    verify = await alttpr.verify_game_settings('entrance',
        state = mode,
        logic = logic,
        shuffle = shuffle,
        goal = goal,
        difficulty = difficulty,
        variation = variation
    )

    if not verify == None:
        await ctx.send('Invalid settings: {settings}'.format(
            settings=', '.join(verify)
        ))
        return

    lbdb = db.LeagueBotDatabase(loop)
    await lbdb.connect()
    await lbdb.set_seed_settings(
            randomizer = 'entrance',
            guild = ctx.guild.id, 
            state = mode,
            logic = logic,
            swords = None,
            shuffle = shuffle,
            goal = goal,
            difficulty = difficulty,
            variation = variation
        )
    await lbdb.close()
    await ctx.message.add_reaction('👍')
    await ctx.message.remove_reaction('⌚',ctx.bot.user)

# get the available seed settings
@discordbot.command()
@commands.has_any_role('admin','mods')
async def modes(ctx, randomizer):
    await ctx.message.add_reaction('⌚')

    settings = await alttpr.list_game_settings(randomizer)

    try: 
        del settings['difficulty_adjustments']
    except KeyError:
        pass

    msg = "Available settings for randomizer: {randomizer}\n".format(
        randomizer=randomizer,
    )
    msg = msg + '```\n'
    for setting in settings:
        msg = msg + '{setting}:\n    {options}\n\n'.format(
            setting=setting,
            options='\n    '.join(settings[setting].keys())
        )
    msg = msg + '```'
    await ctx.send(msg)

    await ctx.message.add_reaction('👍')
    await ctx.message.remove_reaction('⌚',ctx.bot.user)


# get/set configuration values, only the server administrator should be able to set these
@discordbot.group(name='config')
@commands.has_permissions(administrator=True)
async def config_func(ctx):
    pass

@config_func.command()
async def set(ctx, parameter, value):
    await ctx.message.add_reaction('⌚')

    lbdb = db.LeagueBotDatabase(loop)
    await lbdb.connect()
    await lbdb.set_config(ctx.guild.id, parameter, value)
    await lbdb.close()

    await ctx.message.add_reaction('👍')
    await ctx.message.remove_reaction('⌚',ctx.bot.user)

@config_func.command()
async def get(ctx, parameter):
    await ctx.message.add_reaction('⌚')

    lbdb = db.LeagueBotDatabase(loop)
    await lbdb.connect()
    result = await lbdb.get_config(ctx.guild.id, parameter)
    await ctx.send(result['value'])
    await lbdb.close()

    await ctx.message.add_reaction('👍')
    await ctx.message.remove_reaction('⌚',ctx.bot.user)

# @discordbot.event
# async def on_command_error(ctx, error):
#     if isinstance(error, commands.CheckFailure):
#         # await ctx.message.add_reaction('🚫')
#         return
#     if isinstance(error, commands.CommandNotFound):
#         return
#     await ctx.message.add_reaction('👎')
#     await ctx.message.remove_reaction('⌚',ctx.bot.user)

@discordbot.check
async def globally_block_dms(ctx):
    if ctx.guild is None:
        return False
    else:
        return True

def msg_settings(settings):
    if settings['randomizer'] == 'item':
         msg = 'This week\'s settings:\n\n' \
            '```\n' \
            'Randomizer: {randomizer}\n\n' \
            'Difficulty: {difficulty}\n' \
            'Goal: {goal}\n' \
            'Logic: {logic}\n' \
            'State: {state}\n' \
            'Swords: {swords}\n' \
            'Variation: {variation}\n' \
            '```'.format(
                randomizer=settings['randomizer'],
                difficulty=settings['difficulty'],
                goal=settings['goal'],
                logic=settings['logic'],
                state=settings['state'],
                shuffle=settings['shuffle'],
                swords=settings['swords'],
                variation=settings['variation'],
            )
    elif settings['randomizer'] == 'entrance':
        msg = 'This week\'s settings:\n\n' \
            '```\n' \
            'Randomizer: {randomizer}\n\n' \
            'Difficulty: {difficulty}\n' \
            'Goal: {goal}\n' \
            'Logic: {logic}\n' \
            'State: {state}\n' \
            'Shuffle: {shuffle}\n' \
            'Variation: {variation}\n' \
            '```'.format(
                randomizer=settings['randomizer'],
                difficulty=settings['difficulty'],
                goal=settings['goal'],
                logic=settings['logic'],
                state=settings['state'],
                shuffle=settings['shuffle'],
                swords=settings['swords'],
                variation=settings['variation'],
            )
    return msg

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(discordbot.start(config['discord_bot_token']))
    loop.run_forever()
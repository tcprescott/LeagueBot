import asyncio
from discord.ext import commands
import leaguebot.database as db

def has_any_role_fromdb(configkey):
    async def predicate(ctx):
        loop = asyncio.get_event_loop()
        lbdb = db.LeagueBotDatabase(loop)
        await lbdb.connect()
        result = await lbdb.get_config(ctx.guild.id, configkey)
        if not result == None:
            roles = result['value'].split(',')
            await lbdb.close()
            for role in ctx.author.roles:
                if role.name in roles:
                    return True
        return False
    return commands.check(predicate)

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
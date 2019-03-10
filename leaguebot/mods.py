from discord.ext import commands

import discord
import asyncio

import leaguebot.database as db
import leaguebot.alttpr as alttpr
import leaguebot.common as c

class Moderators:
    def __init__(self, bot):
        self.bot = bot

    # configure the seed for the week and store it in the database
    @commands.group()
    @c.has_any_role_fromdb('adminroles')
    async def setseed(self, ctx):
        pass

    @setseed.command()
    async def item(self, ctx, difficulty, goal, logic, mode, weapons, variation):
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

        loop = asyncio.get_event_loop()
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
                        msg=c.msg_settings(settings)
                    )
            )
        except KeyError:
            pass

        await lbdb.close()

        await ctx.message.add_reaction('👍')
        await ctx.message.remove_reaction('⌚',ctx.bot.user)

    @setseed.command()
    async def entrance(self, ctx, difficulty, goal, logic, mode, shuffle, variation):
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

        loop = asyncio.get_event_loop()
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
    @commands.command()
    @c.has_any_role_fromdb('adminroles')
    async def modes(self, ctx, randomizer):
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

def setup(bot):
    bot.add_cog(Moderators(bot))
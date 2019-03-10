from discord.ext import commands

import discord
import re

import leaguebot.database as db
import leaguebot.alttpr as alttpr
import leaguebot.common as c
import leaguebot.sg as sg

import asyncio

class Racers:
    def __init__(self, bot):
        self.bot = bot

    # generate a seed
    @commands.command()
    @c.has_any_role_fromdb('racersroles')
    async def genseed(self, ctx, episodeid):
        await ctx.message.add_reaction('⌚')

        sge = await sg.find_episode(episodeid)
        participants = await sge.get_player_discords()
        players = await sge.get_player_names()

        if participants == False:
            await ctx.message.add_reaction('👎')
            await ctx.send('{author}, that episode doesn\'t appear to exist.'.format(
                author=ctx.author.mention
            ))
            return

        participants.append(ctx.author.name + '#' + ctx.author.discriminator)
        participants = list(set(participants))

        for user in participants:
            u = ctx.guild.get_member_named(user)
            
            dm = u.dm_channel
            if dm == None:
                dm = await u.create_dm()
            await dm.send( 'Preparing game, please standy')

        loop = asyncio.get_event_loop()

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

        for user in participants:
            u = ctx.guild.get_member_named(user)
            dm = u.dm_channel
            if dm == None:
                dm = await u.create_dm()
            await dm.send(
                'Requested seed for {players}:\n\n'
                'Permalink: {permalink}\n'
                'File select code: [{fscode}]\n'.format(
                    players=' vs. '.join(players),
                    fscode=' | '.join(await seed.code()),
                    permalink=await seed.url()
                )
            )

        result = await lbdb.get_config(ctx.guild.id, 'logchannel')
        try:
            logchannel = discord.utils.get(ctx.guild.text_channels, name=result['value'])
            await logchannel.send(
                '------------------------\n'
                'Requested seed for {players}:\n\n'
                'Permalink: {permalink}\n'
                'File select code: [{fscode}]\n'.format(
                    players=' vs. '.join(players),
                    fscode=' | '.join(await seed.code()),
                    permalink=await seed.url()
                )
            )
        except KeyError:
            pass

        await lbdb.close()

        await ctx.message.add_reaction('👍')
        await ctx.message.remove_reaction('⌚',ctx.bot.user)

    @commands.command()
    @c.has_any_role_fromdb('racersroles')
    async def week(self, ctx):
        await ctx.message.add_reaction('⌚')
        loop = asyncio.get_event_loop()
        lbdb = db.LeagueBotDatabase(loop)
        await lbdb.connect()
        settings = await lbdb.get_seed_settings(ctx.guild.id)

        await ctx.send(c.msg_settings(settings))

        await lbdb.close()
        await ctx.message.add_reaction('👍')
        await ctx.message.remove_reaction('⌚',ctx.bot.user)

def setup(bot):
    bot.add_cog(Racers(bot))
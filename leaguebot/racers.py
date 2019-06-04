from discord.ext import commands

import discord
import re

import leaguebot.database as db
import leaguebot.alttpr as alttpr
import leaguebot.common as c
import leaguebot.sg as sg

import asyncio

class Racers(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        help='Generate a seed for an SG race.\n\n'
            'episodeid = speedgaming episode id',
        brief='Generate a seed for an SG race.'
    )
    @c.has_any_role_fromdb('mtplayers')
    async def mtgen(self, ctx, player1: discord.Member, player2: discord.Member):
        await ctx.message.add_reaction('⌚')

        for member in [player1, player2]:

            dm = member.dm_channel
            if dm == None:
                dm = await member.create_dm()
            await dm.send( 'Preparing game, please standby...')

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

        code = await seed.code()

        for member in [player1, player2]:
            dm = member.dm_channel
            if dm == None:
                dm = await member.create_dm()
            await dm.send(
                'Requested seed for {player1} vs. {player2}:\n\n'
                'Permalink: {permalink}\n'
                'File select code: [{fscode}]\n'.format(
                    player1=player1.name,
                    player2=player2.name,
                    fscode=' | '.join(code),
                    permalink=await seed.url()
                )
            )

        result = await lbdb.get_config(ctx.guild.id, 'logchannel')
        try:
            logchannel = discord.utils.get(ctx.guild.text_channels, name=result['value'])
            await logchannel.send(
                '------------------------\n'
                'Requested seed for {player1} vs. {player2}:\n\n'
                'Permalink: {permalink}\n'
                'File select code: [{fscode}]\n'.format(
                    player1=player1.name,
                    player2=player2.name,
                    fscode=' | '.join(code),
                    permalink=await seed.url()
                )
            )
        except KeyError:
            pass

        await lbdb.close()

        await ctx.message.add_reaction('👍')
        await ctx.message.remove_reaction('⌚',ctx.bot.user)

    # generate a seed
    @commands.command(
        help='Generate a seed for an SG race.\n\n'
            'episodeid = speedgaming episode id',
        brief='Generate a seed for an SG race.'
    )
    @c.has_any_role_fromdb('racersroles')
    async def genseed(self, ctx, episodeid, settingsid=None):
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
            await dm.send( 'Preparing game, please standby...')

        loop = asyncio.get_event_loop()

        lbdb = db.LeagueBotDatabase(loop)

        await lbdb.connect()
        if settingsid==None:
            settings = await lbdb.get_seed_settings(ctx.guild.id)
        else:
            settings = await lbdb.get_seed_settings_by_id(ctx.guild.id, int(settingsid))

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
                'SRL Goal: {srlgoal}\n'
                'File select code: [{fscode}]\n'.format(
                    players=', '.join(players),
                    fscode=' | '.join(await seed.code()),
                    permalink=await seed.url(),
                    srlgoal='`.setgoal ALTTPR League: {players} - Week #`'.format(
                        players=', '.join(players),
                    )
                )
            )

        result = await lbdb.get_config(ctx.guild.id, 'logchannel')
        try:
            logchannel = discord.utils.get(ctx.guild.text_channels, name=result['value'])
            await logchannel.send(
                '------------------------\n'
                'Requested seed for {players}:\n\n'
                'Permalink: {permalink}\n'
                'SRL Goal: {srlgoal}\n'
                'File select code: [{fscode}]\n'.format(
                    players=', '.join(players),
                    fscode=' | '.join(await seed.code()),
                    permalink=await seed.url(),
                    srlgoal='`.setgoal ALTTPR League: {players} - Week #`'.format(
                        players=', '.join(players),
                    )
                )
            )
        except KeyError:
            pass

        await lbdb.close()

        await ctx.message.add_reaction('👍')
        await ctx.message.remove_reaction('⌚',ctx.bot.user)


    # generate a seed
    @commands.command(
        help='Generate a playoff game for an SG race.'
    )
    @c.has_any_role_fromdb('playoffroles')
    async def playoffrace(self, ctx, episodeid, gamenum, hash=None):
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
            await dm.send( 'Preparing game, please standby...')

        loop = asyncio.get_event_loop()

        lbdb = db.LeagueBotDatabase(loop)
        await lbdb.connect()
        if gamenum == '1':
            seed = await alttpr.generate_game(
                randomizer='item',
                difficulty='normal',
                goal='ganon',
                logic='NoGlitches',
                state='open',
                swords='randomized',
                variation='none',
            )
        elif gamenum == '2':
            seed = await alttpr.generate_game(
                randomizer='item',
                difficulty='normal',
                goal='ganon',
                logic='NoGlitches',
                state='standard',
                swords='randomized',
                variation='none',
            )
        elif gamenum in ['3','4','5']:
            seed = await alttpr.retrieve_game(
                hash=hash
            )
            if not seed.patchdata['spoiler']['meta']['tournament'] == True:
                await ctx.send('That is not a Race Rom.  Please generate a new game.')
                await ctx.message.add_reaction('👎')
                return
        else:
            await ctx.send('Specify a game number (1 to 5)')
            await ctx.message.add_reaction('👎')
            return

        for user in participants:
            u = ctx.guild.get_member_named(user)
            dm = u.dm_channel
            if dm == None:
                dm = await u.create_dm()
            await dm.send(
                'Requested seed for {players}:\n\n'
                'Permalink: {permalink}\n'
                'SRL Goal: {srlgoal}\n'
                'File select code: [{fscode}]\n'.format(
                    players=', '.join(players),
                    fscode=' | '.join(await seed.code()),
                    permalink=await seed.url(),
                    srlgoal='`.setgoal ALTTPR League: {players} - Game {gamenum}`'.format(
                        players=', '.join(players),
                        gamenum=gamenum
                    )
                )
            )

        result = await lbdb.get_config(ctx.guild.id, 'logchannel')
        try:
            logchannel = discord.utils.get(ctx.guild.text_channels, name=result['value'])
            await logchannel.send(
                '------------------------\n'
                'Requested seed for {players}:\n\n'
                'Permalink: {permalink}\n'
                'SRL Goal: {srlgoal}\n'
                'File select code: [{fscode}]\n'.format(
                    players=', '.join(players),
                    fscode=' | '.join(await seed.code()),
                    permalink=await seed.url(),
                    srlgoal='`.setgoal ALTTPR League: {players} - Game {gamenum}`'.format(
                        players=', '.join(players),
                        gamenum=gamenum
                    )
                )
            )
        except KeyError:
            pass

        await lbdb.close()

        await ctx.message.add_reaction('👍')
        await ctx.message.remove_reaction('⌚',ctx.bot.user)

    @commands.command(
        help='Get this week\'s seed settings.'
    )
    @c.has_any_role_fromdb('racersroles')
    async def week(self, ctx, settingsid=None):
        await ctx.message.add_reaction('⌚')
        loop = asyncio.get_event_loop()
        lbdb = db.LeagueBotDatabase(loop)
        await lbdb.connect()
        if settingsid==None:
            settings = await lbdb.get_seed_settings(ctx.guild.id)
        else:
            settings = await lbdb.get_seed_settings_by_id(ctx.guild.id, int(settingsid))

        await ctx.send(c.msg_settings(settings))

        await lbdb.close()
        await ctx.message.add_reaction('👍')
        await ctx.message.remove_reaction('⌚',ctx.bot.user)

def setup(bot):
    bot.add_cog(Racers(bot))
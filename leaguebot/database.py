import asyncio
import aiomysql

import leaguebot.config as cfg
config = cfg.get_config()

class LeagueBotDatabase():
    def __init__(self, loop):
        self.loop = loop

    async def connect(self):
        conn = await aiomysql.connect(
            user=config['leaguebot_db']['username'],
            db=config['leaguebot_db']['database'],
            host=config['leaguebot_db']['hostname'],
            password=config['leaguebot_db']['password'],
            loop=self.loop
        )
        self.conn = conn

    async def close(self):
        conn = self.conn.close()

    async def get_config(self, guild, parameter):
        cursor = await self.conn.cursor(aiomysql.DictCursor)
        sql = 'SELECT id, guild, parameter, value FROM config where guild=%s AND parameter=%s'
        result = await cursor.execute(sql, (guild, parameter))
        return await cursor.fetchone()

    async def set_config(self, guild, parameter, value):
        cursor = await self.conn.cursor()
        sql = 'DELETE FROM config where guild=%s AND parameter=%s'
        await cursor.execute(sql, (guild, parameter))

        cursor = await self.conn.cursor()
        sql = "INSERT INTO config (guild, parameter, value) VALUES (%s, %s, %s)"
        await cursor.execute(sql, (guild, parameter, value))
        await self.conn.commit()

    async def get_seed_settings(self, guild):
        cursor = await self.conn.cursor(aiomysql.DictCursor)
        sql = 'SELECT * FROM seed_settings WHERE guild=%s ORDER BY id DESC LIMIT 1'
        result = await cursor.execute(sql, (guild))
        return await cursor.fetchone()

    async def set_seed_settings(self, guild, randomizer, state, logic, swords, shuffle, goal, difficulty, variation):
        cursor = await self.conn.cursor()
        sql = "INSERT INTO seed_settings (guild, randomizer, state, logic, swords, shuffle, goal, difficulty, variation) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
        await cursor.execute(sql, (guild, randomizer, state, logic, swords, shuffle, goal, difficulty, variation))
        await self.conn.commit()
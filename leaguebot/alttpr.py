import pyz3r_asyncio

async def set_game():
    pass

async def generate_game(randomizer, state, logic, goal, difficulty, variation, swords=False, shuffle=False, enemizer=False):
    if enemizer:
        raise Exception('enemizer not supported yet')
    
    if randomizer == 'item':
        seed = await pyz3r_asyncio.create_seed(
            randomizer=randomizer, # optional, defaults to item
            settings={
                "logic": logic,
                "difficulty": difficulty,
                "mode": state,
                "variation": variation,
                "weapons": swords,
                "goal": goal,
                "enemizer": False,
                "tournament": True,
                "lang": "en"
            }
        )
    elif randomizer == 'entrance':
        seed = await pyz3r_asyncio.create_seed(
            randomizer=randomizer, # optional, defaults to item
            settings={
                "logic": logic,
                "difficulty": difficulty,
                "mode": state,
                "variation": variation,
                "shuffle": shuffle,
                "goal": goal,
                "enemizer": False,
                "tournament": True,
                "lang": "en"
            }
        )
    return seed

async def list_game_settings(randomizer):
    seed = await pyz3r_asyncio.create_seed(randomizer=randomizer)
    settings = await seed.list_settings()
    return settings

async def verify_game_settings(randomizer, state, logic, goal, difficulty, variation, swords=None, shuffle=None):
    settings = await list_game_settings(randomizer)
    non_existant_settings = []

    try: settings['difficulties'][difficulty]
    except KeyError: non_existant_settings.append('difficulty')
    
    try: settings['goals'][goal]
    except KeyError: non_existant_settings.append('goal')
    
    try: settings['logics'][logic]
    except KeyError: non_existant_settings.append('logic')
    
    try: settings['modes'][state]
    except KeyError: non_existant_settings.append('state')

    try: settings['variations'][variation]
    except KeyError: non_existant_settings.append('variations')
    
    if randomizer=='item':
        try: settings['weapons'][swords]
        except KeyError: non_existant_settings.append('swords')
    elif randomizer=='entrance':
        try: settings['shuffles'][shuffle]
        except KeyError: non_existant_settings.append('shuffle')

    if len(non_existant_settings) > 0:
        return non_existant_settings
    else:
        return None
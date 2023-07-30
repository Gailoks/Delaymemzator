import json
import abstractions
import bots.vk.vkinteraction as vk
import bots.vk.dbcontext as vkdb
import asyncio
import dev

async def main():
    with open("config.json", 'r', encoding = "utf-8") as config:
        config = json.load(config)

    vkdb_context = vkdb.SQLiteDBContext()
    await vkdb_context.connect(**config["vk-source"]["database"]["sqlite"])

    bot = vk.VkSourceBot(**config["vk-source"]["bot"])
    sources: list[abstractions.MemeSource] = [
        bot
    ]
 
    intakes: dict[str, abstractions.MemeIntake] = {
        "vk": dev.DevIntake('pseudo-vk', 'ok'),
        "tg": dev.DevIntake('pseudo-tg', 'fail'),
        "ds": dev.DevIntake('pseudo-ds', 'fail'),
        "dev": dev.DevIntake('dev', 'invalid')
    }

    main_router = abstractions.MemeRouter(sources, intakes)
    main_router.initialize()

    bot.initialize()
    await bot.run()


loop = asyncio.get_event_loop()
loop.create_task(main())
loop.run_forever()
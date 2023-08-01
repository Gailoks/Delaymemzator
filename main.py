import json
import models
import abstractions
import router
import bots.vk.vkinteraction as vk
import bots.vk.dbcontext as vkdb
import asyncio
import dev
import bots.telegram.telegraminteractions as tg
import bots.telegram.dbcontext as tgdb
import logtools
import dateparser

async def main():
    with open("config.json", 'r', encoding = "utf-8") as config:
        config = json.load(config)

    logger_factory = logtools.LoggerFactory(logtools.LogLevel.TRACE)
    logger_factory.add_logger(logtools.ConsoleLoggerProvider())


    vk_source_bot = vk.VkSourceBot(**config["vk-source"]["bot"])
    sources: list[abstractions.MemeSource] = [
        vk_source_bot
    ]

    vkdb_context = vkdb.SQLiteDBContext()
    await vkdb_context.connect(**config["vk-intake"]["database"]["sqlite"])
    vk_intake_bot = vk.VkIntakeBot(**config["vk-intake"]["bot"], db = vkdb_context)

    # tgdb_context = tgdb.SQLiteDBContext()
    # await tgdb_context.connect(**config["telegram-intake"]["database"]["sqlite"])
    # telegam_intake_bot = tg.TelegramIntakeBot(**config["telegram-intake"]["bot"], db = tgdb_context)

    intakes: dict[str, abstractions.MemeIntake] = {
        "вк": vk_intake_bot,
        "vk": vk_intake_bot,
        # "tg": telegam_intake_bot,
        # "тг": telegam_intake_bot
    }

    main_router = router.MemeRouter(sources, intakes, logger_factory.create_logger("router.MemeRouter"))
    main_router.initialize()

    await vk_source_bot.run()

loop = asyncio.get_event_loop()
loop.create_task(main())
loop.run_forever()

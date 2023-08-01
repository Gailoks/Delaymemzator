from abstractions import *

class MemeRouter(AbstractMemeRouter):
    def __init__(self, sources: list[MemeSource], intakes: dict[str, MemeIntake], logger: Logger):
        self.__sources = sources
        self.__intakes = intakes
        self.__logger = logger
        pass

    def initialize(self):
        for source in self.__sources:
            source.set_router(self)

    async def route_memes(self, sender_id: int, addresses: list[str], memes: list[models.Meme]) -> Awaitable[str]:
        routing_result = await self.__route_meme_internal(sender_id, addresses, memes)
        self.__logger.log(LogLevel.INFORMATION, LogEvent(11, "MemeRouted"),
            "Memes from {SenderId} that contains {MemeCount} memes routed to {Addresses} with result {RoutingResult}",
            [sender_id, len(memes), addresses, routing_result])


    async def __route_meme_internal(self, sender_id: int, addresses: list[str], memes: list[models.Meme]) -> Awaitable[str]:
        try:
            for address in addresses:
                if address not in self.__intakes:
                    return f"Unknown address {address}"

            targets = list(map(lambda x: (self.__intakes[x], x), addresses))

            for intake in targets:
                validation_result = await intake[0].validate_user(sender_id)
                if validation_result:
                    return f"You cannot send meme to {intake[1]}, reason: {validation_result}"

            meme_codes = []

            for meme_id, meme in enumerate(memes):
                meme_id += 1 # start from 1

                for intake in targets:
                    validation_result = await intake[0].validate_upload(sender_id, meme)
                    if validation_result:
                        return f"Enable to send meme #{meme_id}, reason {validation_result}"

                coroutines: list = [intake[0].upload_meme(sender_id, meme) for intake in targets]
                errors: list[Exception] = []

                for coroutine in coroutines:
                    try:
                        await coroutine
                    except Exception as ex:
                        errors.append(ex)

                if errors:
                    meme_codes.append("\n\t" + "\n\t".join(map(str, errors)))
                else:
                    meme_codes.append("Successful")


            return '\n'.join(map(lambda x: f"[{x[0]}]: {x[1]}", enumerate(meme_codes)))
        
        except Exception as ex:
            return f"Fatal exception in meme routing process, please contact with developers to fix it error. Error text:\n{ex}"
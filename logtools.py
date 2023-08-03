from abc import ABC, abstractmethod
from enum import Enum
from termcolor import colored
import re
from dataclasses import dataclass

# Models ------------------------

class LogLevel(Enum):
    TRACE = 0,
    DEBUG = 1,
    INFORMATION = 2,
    WARNING = 3,
    ERROR = 4,
    FATAL = 5,

@dataclass
class LogEvent:
    id: int
    title: str

# Abstractions ------------------------

class Logger(ABC):
    @abstractmethod
    def log(self, log_level: LogLevel, event: LogEvent, message_template: str, log_parameters: list[any], exception: Exception | None = None) -> None:
        raise NotImplementedError()

class LoggerProvider(ABC):
    @abstractmethod
    def create_logger(self, category: str) -> Logger:
        raise NotImplementedError()

# Logger factory ------------------------

class LoggerFactory(LoggerProvider):
    def __init__(self, min_log_level: LogLevel):
        self.__min_log_level = min_log_level
        self.logger_providers: list[LoggerProvider] = []

    def create_logger(self, category: str) -> Logger:
        loggers = [provider.create_logger(category) for provider in self.logger_providers]
        return CompositeLogger(loggers, self.__min_log_level)

    def add_logger(self, provider: LoggerProvider) -> None:
        self.logger_providers.append(provider)

class CompositeLogger(Logger):
    def __init__(self, loggers: list[Logger], min_log_level: LogLevel):
        self.__loggers = loggers
        self.__min_log_level = min_log_level

    def log(self, log_level: LogLevel, event: LogEvent, message_template: str, log_parameters: list[any], exception: Exception | None = None) -> None:
        if log_level.value >= self.__min_log_level.value:
            for logger in self.__loggers:
                logger.log(log_level, event, message_template, log_parameters, exception)


# Console logging ------------------------

class ConsoleLoggerProvider(LoggerProvider):
    def create_logger(self, category: str) -> Logger:
        return ConsoleLogger(category)

class ConsoleLogger(Logger):
    def __init__(self, category: str):
        self.__category = category

    def log(self, log_level: LogLevel, event: LogEvent, message_template: str, log_parameters: list[any], exception: Exception | None = None) -> None:
        message = "["

        message += colored(self.__category, 'magenta')
        message += ":"

        match log_level:
            case LogLevel.TRACE: message += colored('TRACE', 'dark_grey', 'on_light_grey')
            case LogLevel.DEBUG: message += colored('DEBUG', 'dark_grey', 'on_light_grey')
            case LogLevel.INFORMATION: message += colored('INFORMATION', 'light_cyan', 'on_light_grey')
            case LogLevel.WARNING: message += colored('WARNING', 'yellow', 'on_light_grey')
            case LogLevel.ERROR: message += colored('ERROR', 'red', 'on_light_grey')
            case LogLevel.FATAL: message += colored('FATAL', 'red', 'on_light_grey')
            case _: message += colored(f'NOTSUP {log_level}', 'white', 'on_light_grey')

        message += f"({event.title}:{event.id})"

        message += "]: "

        segments = re.split(r"{[^}]+}", message_template)

        if len(segments) - 1 != len(log_parameters):
            raise Exception("Recived log parameters and message template parameters size mismatch")
        
        for i, parameter in enumerate(log_parameters):
            message += segments[i]
            message += colored(str(parameter), 'light_magenta')

        message += segments[-1]

        if exception:
            message += f"\n\t\tException recived: {exception}"

        print(message)
        
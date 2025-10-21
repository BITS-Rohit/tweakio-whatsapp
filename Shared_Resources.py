"""
Shared Resources Module for tweakio-whatsapp library
"""
import logging
import threading
from logging.handlers import RotatingFileHandler

from colorlog import ColoredFormatter

import directory as dirs

# ------ Logger Configs ---------
logger = logging.getLogger("tweakio")
logger.setLevel(logging.INFO)

# -------------------------------
# Console handler
# -------------------------------

console_formatter = ColoredFormatter(
    "%(log_color)s%(asctime)s | %(levelname)s | %(message)s",
    log_colors={
        'DEBUG': 'cyan',
        'INFO': 'green',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'bold_red'
    }
)

console_handler = logging.StreamHandler()
console_handler.setFormatter(console_formatter)
logger.addHandler(console_handler)

console_formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
console_handler.setFormatter(console_formatter)
logger.addHandler(console_handler)

# -------------------------------
# File handler with rotation
# -------------------------------
file_handler = RotatingFileHandler(
    dirs.ErrorTrace_file,  # file path
    maxBytes=20 * 1024 * 1024,  # 20 MB per file
    backupCount=3  # keep last 3 files
)
file_formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)

# -------------------------------
# General settings
# -------------------------------
logger.propagate = False


# ---------------- Shared Resource class ----------------
class SharedResource:
    """
    Shared Resource that will be used by other function.
    It contains credentials.
    TODO : Will be added a exception and decryption for API Keys
    """
    _lock = threading.Lock()
    _data = {"number": None, "country": None}

    @classmethod
    def set_or_add(cls, key, value):
        """ Set the key with value if exists else add the key with value"""
        with cls._lock:
            cls._data[key] = value

    @classmethod
    def get(cls, key):
        """

        :param key:
        :return:
        """
        with cls._lock:
            return cls._data.get(key)

    @classmethod
    def clean_res(cls, res: str, type_res: str) -> str:
        """

        :param res:
        :param type_res:
        :return:
        """
        with cls._lock:
            if type_res == "number":
                n = ""
                for x in res:
                    if x.isnumeric(): n += x
                return n
            elif type_res == "country":
                c = ""
                for x in res:
                    if x.isalpha(): c += x
                return c
            return ""

    # ___________________________Typed wrappers_______________________
    @classmethod
    def set_number(cls, number: str):
        """

        :param number:
        """
        with cls._lock:
            number = cls.clean_res(number, "number")
            cls.set_or_add("number", number)

    @classmethod
    def get_number(cls) -> str | None:
        """

        :return:
        """
        return cls.get("number")

    @classmethod
    def set_country(cls, country: str):
        """

        :param country:
        """
        with cls._lock:
            country = cls.clean_res(country, "country")
            cls.set_or_add("country", country)

    @classmethod
    def get_country(cls) -> str | None:
        """
        for other modules to have it saved once for all the operations.
        :return:
        """
        return cls.get("country")

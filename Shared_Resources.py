import logging
import threading

# ------ Logger Configs ---------
logger = logging.getLogger("tweakio")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.propagate = False

# ---------------- Shared Resource class ----------------
class SharedResource:
    _lock = threading.Lock()
    _data = {"number": None, "country": None}

    @classmethod
    def set_or_add(cls, key, value):
        """ Set the key with value if exists else add the key with value"""
        with cls._lock:
            cls._data[key] = value

    @classmethod
    def get(cls, key):
        with cls._lock:
            return cls._data.get(key)

    @classmethod
    def clean_res(cls, res: str, type_res: str) -> str:
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
        with cls._lock:
            number = cls.clean_res(number, "number")
            cls.set_or_add("number", number)

    @classmethod
    def get_number(cls) -> str | None:
        return cls.get("number")

    @classmethod
    def set_country(cls, country: str):
        with cls._lock:
            country = cls.clean_res(country, "country")
            cls.set_or_add("country", country)

    @classmethod
    def get_country(cls) -> str | None:
        return cls.get("country")

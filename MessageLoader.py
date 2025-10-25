"""
Message Class for whatsapp chats
"""
import asyncio
from typing import Union

from playwright.async_api import Page, Locator, ElementHandle

import Extra as ex
import directory as dirs
import selector_config as sc
from Errors import MessageNotFound
from Extra import TracerOBJ
from Shared_Resources import logger


class MessageLoader:
    """
    This class will contain :
    - Message Fetching - Full / Live Fetching
    - Tracer

    -- So Message Fetching means :
    ==== Full :
    You will get all the messages of the page currently visible in the dom
    - can select incoming / outgoing messages / Both
    default : both
    ==== Live :
    You will get all messages + Bot will wait for the current new messages if received while processing the old ones.
    If it comes then we can track it with limit upto how many times we need to check.
    This is efficient for live + Heavy chatting areas but need manual intervention for stopping from abusive nature to stop Number ban.
    Default : 5 times

    ---- So Unread / Read marking :
    === Unread :
    This will check or make it unread from read.
    Read is always on as this is prime feature and essential for whatsapp
    we won't break this using websocket as main purpose of this lib is to protect from ban while being able to automate task

    ----- Tracer :
    Tracer has its own coverage for every message it processes.
    It will dump all messages to a dict and can be invoked into a json file with path and name defined
    It will contain :
    -Chat Name : str
    -Community name : str
    -preview Image url : str [ Note - May get removed in future ]
    -JID : Internal ID : str
    -Message : str
    -Type of Message : str [ can throw errors , check tracer logs for errors to report to developers(on GitHub repo) ]
    -time : Message Time on the message it arrived : str
    -SysTime : when the system saw it [ For deep debugging ] : str
    -Direction : Incoming/Outgoing message direction : str


    ----- Some Extra Functions :
    """

    def __init__(self, page: Page, trace_path: str = str(dirs.MessageTrace_file)) -> None:
        self.outgoing: bool
        self.incoming: bool
        self.default: bool
        self.page: Page = page
        self.trace_path = trace_path
        self.TracerDICT: dict = {}  # Temporary Based Running

    async def _GetScopedMessages(self, incoming: bool, outgoing: bool) -> Locator:
        self.incoming = incoming
        self.outgoing = outgoing

        self.default = self.incoming & self.outgoing  # Both true == default

        if self.default:
            messages: Locator = await sc.messages(self.page)
        elif self.incoming:
            messages: Locator = await sc.messages_incoming(page=self.page)
        else:
            messages: Locator = await sc.messages_outgoing(page=self.page)
        return messages

    async def LiveMessages(
            self,
            chat_id: Union[Locator, ElementHandle],
            cycle: int = 5,
            incoming: bool = True,
            outgoing: bool = True,
            pollingTime: float = 5.0):
        """
        This will have the default both true for both messages.
        For specific type you need, make the other false.
        Messages will fetch in sequential order as they came.
        For single Set of Fetching , give cycle = 0 else default is 5.
        pollingTime is the waiting time for next fetch of new Messages.
        """

        try:
            await chat_id.click(timeout=3000)
            messages: Locator = await self._GetScopedMessages(incoming, outgoing)
            count: int = await messages.count()

            if count == 0:
                raise MessageNotFound()

            for i in range(count):
                msg = messages.nth(i)  # Msg Element
                txt : str = await sc.get_message_text(msg)  # Text Message of the Msg

                data_id: str = await sc.get_dataID(msg)
                if not data_id:
                    raise Exception("Data ID null in the Live Messages")

                if data_id not in self.TracerDICT:
                    tracing: bool = await ex.trace_message(
                        seen_messages=self.TracerDICT,
                        message=msg,
                        chat=chat_id,
                        data_id=data_id)  # Tracing Automatically

                    # Yielding 4 params msg locator , txt str , tracing bool , tracer dict if tracing else {}
                    yield msg, txt, tracing, TracerOBJ(self.TracerDICT[data_id]) if tracing else TracerOBJ()

            if cycle == 0: return

            await asyncio.sleep(pollingTime)
            async for m in self.LiveMessages(chat_id, cycle - 1, incoming, outgoing, pollingTime):
                yield m


        except Exception as e:
            logger.error(f" -- Error in LiveMessages -- {e}", exc_info=True)

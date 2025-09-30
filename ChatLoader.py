import asyncio
import random
import re
from typing import Dict, Union, Optional

from playwright.async_api import Page, Locator, ElementHandle

import selector_config as sc
from Errors import ChatsNotFound
from Shared_Resources import logger


async def _is_Unread(chat: Union[ElementHandle, Locator]) -> int:
    """
    Returns:
      1 → chat has actual unread messages (numeric badge),
      0 → manually marked as unread (no numeric badge) or none,
     -1 → error occurred
    """
    try:
        if isinstance(chat, Locator):
            chat = await chat.element_handle(timeout=1000)
        if not chat:
            return 0

        unread_badge = await chat.query_selector("[aria-label*='unread']")
        if unread_badge:
            number_span = await unread_badge.query_selector("span")
            if number_span:
                text = (await number_span.inner_text()).strip()
                return 1 if text.isdigit() else 0
        return 0
    except Exception as e:
        logger.error(f"[is_unread] Error: {e}")
        return -1





class ChatLoader:
    """
    This class will contain :
    -- Chats Handling
    -- Unread / Read Markings

    """

    def __init__(self):
        # self.chats = {}
        self.page = None
        self.totalChats = 0
        self.ChatMap: Dict[str, Locator] = {}
        self.ID = 1

    async def _GetChat_ID(self) -> str:
        ChatID = f"M{self.ID}"
        self.ID += 1
        return ChatID

    async def ChatRoller(
            self,
            cycle: int,
            page: Page,
            MaxChat: int = 5,
            PollingTime: float = 1.0):
        """
        This edit the ChatMap

        :param MaxChat:
        :param cycle:
        :param page:
        :param PollingTime:
        :return:
        """
        try :
            TotalChats = await sc.total_chats(page)
            if not TotalChats: self.totalChats = TotalChats

            count = 0
            while True:
                chats = sc.chat_items(page)
                if not chats or await chats.count() == 0:
                    raise ChatsNotFound()
                n = min(await chats.count(), MaxChat)
                for i in range(n):
                    chat = chats.nth(i)
                    name = sc.getChatName(chat)
                    # self.ChatMap[self._GetChat_ID()]=chat
                    yield chat, name

                count += 1
                if cycle != 0 and count >= cycle:
                    break
                await asyncio.sleep(PollingTime)
        except Exception as e:
            logger.error(f"[ChatLoader] Error: {e}")

    @staticmethod
    async def isUnread(chat: ElementHandle) -> Optional[bool]:
        i = _is_Unread(chat=chat) == 1
        if i == 1:
            return True
        elif i == 0:
            return None
        else:
            return False

    @staticmethod
    async def ChatClicker(chat: Union[ElementHandle, Locator])-> None:
        await chat.click(timeout=3500)

    async def Do_Unread(self ,  chat: Union[ElementHandle, Locator]) -> None:
        """
        Marks the given chat as unread by simulating right-click and selecting 'Mark as unread'.
        If already unread, logs info instead of failing.
        """
        try:
            if isinstance(chat, Locator):
                chat = await chat.element_handle(timeout=1000)
            if not chat:
                print("[do_unread] Chat handle not found")
                return
            page = self.page
            # Right-click chat
            await chat.click(button="right")
            await page.wait_for_timeout(random.randint(1300, 2500))

            # Try to find unread option
            unread_option = page.locator("li span").filter(has_text=re.compile('mark*as*unread', re.I))
            if await unread_option.count() > 0:
                await unread_option.first.click(timeout=random.randint(1701, 2001))
                print("[do_unread] Marked as unread ✅")
            else:
                read_option = page.locator("li span").filter(has_text=re.compile('mark*as*read', re.I))
                if await read_option.count() > 0:
                    print("[do_unread] Chat already unread")
                else:
                    print("[do_unread] Context menu option not found ❌")

        except Exception as e:
            print(f"[do_unread] Error marking unread: {e}")

            # Reset by clicking WA icon if available
            try:
                wa_icon = sc.wa_icon(self.page)
                if await wa_icon.count() > 0:
                    await wa_icon.first.click()
            except:
                pass


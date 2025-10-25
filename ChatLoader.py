"""
Chat Class for the whatsapp module
"""
import asyncio
import random
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
        logger.error(f"[is_unread] Error: {e}", exc_info=True)
        return -1


class ChatLoader:
    """
    This class will contain :
    -- Chats Handling
    -- Unread / Read Markings

    """

    def __init__(self, page: Page):
        # self.chats = {}
        self.page = page
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
            MaxChat: int = 5,
            PollingTime: float = 1.0):
        """
        Generator that yields chat elements and names.

        :param MaxChat: Max number of chats to process per iteration.
        :param cycle: Number of cycles to run (0 = infinite)
        :param PollingTime: Wait time between cycles
        """
        page = self.page
        try:
            count = 0
            while True:

                chats = sc.chat_items(page)
                n_chats = await chats.count()

                if n_chats == 0:
                    await page.wait_for_timeout(1000)
                    n_chats = await chats.count()
                    if n_chats == 0:
                        raise ChatsNotFound("No chats found in chat list during iteration")

                n = min(n_chats, MaxChat)
                for i in range(n):
                    chat = chats.nth(i)
                    name = await sc.getChatName(chat)
                    yield chat, name

                count += 1
                if cycle != 0 and count >= cycle:
                    break
                await asyncio.sleep(PollingTime)

        except Exception as e:
            logger.critical(f"[ChatLoader] Error: {e}", exc_info=True)

    @staticmethod
    async def isUnread(chat: ElementHandle) -> Optional[bool]:
        """
        Checks if the chat is unread or not.
        :param chat:
        :return:
        """
        i = await _is_Unread(chat=chat) == 1
        if i == 1:
            return True
        elif i == 0:
            return None
        else:
            return False

    @staticmethod
    async def ChatClicker(chat: Union[ElementHandle, Locator]) -> None:
        """
        clicks the chats with the correct timeout
        :param chat:
        """
        await chat.click(timeout=3500)

    async def Do_Unread(self, chat: Union[ElementHandle, Locator]) -> None:
        """
        Marks the given chat as unread by simulating right-click and selecting 'Mark as unread'.
        If already unread, logs info instead of failing.
        """
        try:
            page : Page = self.page

            if isinstance(chat, Locator):
                chat = await chat.element_handle(timeout=1000)
            if not chat:
                print("[do_unread] Chat handle not found")
                return

            # Right-click on chat
            await chat.click(button="right")
            await page.wait_for_timeout(random.uniform(1.3, 2.5))

            # Get the application menu as ElementHandle
            menu = await page.query_selector("role=application")
            if not menu:
                raise Exception("App Menu not found")

            # Look for 'Mark as unread' option inside menu
            unread_option = await menu.query_selector("li >> text=/mark.*as.*unread/i")
            if unread_option:
                await unread_option.click(timeout=random.randint(1701, 2001))
                logger.info("[do_unread] Marked as unread ✅")
            else:
                # Check if already unread
                read_option = await menu.query_selector("li >> text=/mark.*as.*read/i")
                if read_option:
                    logger.info("[do_unread] Chat already unread")
                else:
                    logger.info("[do_unread] Context menu option not found ❌")

        except Exception as e:
            logger.error(f"[do_unread] Error marking unread: {e}", exc_info=True)
            # Reset by clicking WA icon if available
            try:
                wa_icon = sc.wa_icon(page= self.page)
                if await wa_icon.count() > 0:
                    await wa_icon.first.click()
            except Exception as e:
                logger.warning(f"WA Icon Error : {e}")

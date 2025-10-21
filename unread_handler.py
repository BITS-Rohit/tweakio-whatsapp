"""
Unread Handler Doc
"""
import asyncio
import random
from typing import Union

from playwright.async_api import Page, ElementHandle, Locator

import selector_config as sc
from Shared_Resources import logger


# --- ---- Unread Handle ---- ---
async def is_unread(chat: Union[ElementHandle, Locator]) -> int:
    """
    Return 1 if the chat has actual unread messages (with a numeric count),
    else 0 if only marked as unread manually (no numeric badge).
    """
    if isinstance(chat, Locator):
        chat = await chat.element_handle(timeout=1001)

    try:
        unread_badge = await chat.query_selector("[aria-label*='unread']")
        if unread_badge:
            number_span = await unread_badge.query_selector("span")
            if number_span:
                text = (await number_span.inner_text()).strip()
                return 1 if text.isdigit() else 0
        return 0
    except Exception as e:
        logger.error(f"[is_unread] Error {e}", exc_info=True)
        return 0


async def do_unread(page: Page, chat: Union[ElementHandle, Locator]) -> None:
    """
    Marks the given chat as unread by simulating right-click and selecting 'Mark as unread'.
    """
    if isinstance(chat, Locator):
        chat = await chat.element_handle(timeout=1001)

    try:
        await chat.click(button="right")
        await asyncio.sleep(random.uniform(1.3, 2.5))

        app_menu = await page.query_selector("role=application")  # top-level menu
        if not app_menu:
            raise Exception("Application menu not found")

        unread_option = await app_menu.query_selector(
            "li span:text-matches('mark as unread', 'i')"
        )
        if unread_option:
            await unread_option.click(timeout=random.randint(1701, 2001))
        else:
            raise Exception("'Mark as unread' option not found or not visible")

    except Exception:
        try:
            read_option = await (await page.query_selector("role=application")).query_selector(
                "li span:text-matches('mark as read', 'i')"
            )
            if read_option:
                logger.info(f"Chat is already unread — [{await sc.getChatName(chat)}]")
            else:
                raise
        except Exception as e:
            logger.error(f"[do_unread] Error marking unread {e}", exc_info=True)

        # Reset state by clicking outside (WA icon)
        wa_icon = sc.wa_icon(page)
        await wa_icon.click()

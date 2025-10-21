import random
from typing import Union

from playwright.async_api import Page, ElementHandle, Locator

import _Humanize as ha
import _Media as med
import selector_config as sc
from Shared_Resources import logger


async def double_edge_click(page: Page, message: Union[ElementHandle, Locator]) -> bool:
    """
    Performs a precise double click at the edge of a message element.

    This is typically used to trigger context menus or special message interactions.
    Handles scrolling if the element is out of viewport.

    Args:
        page (Page): Playwright page object.
        message (ElementHandle | Locator): Message element or locator to click.

    Returns:
        bool: True if the click succeeded, False otherwise.
    """
    try:
        if isinstance(message, Locator):
            message = await message.element_handle()

        attempts = 0
        while not await message.bounding_box() and attempts < 20:
            await page.mouse.wheel(0, -random.randint(150, 250))
            await page.wait_for_timeout(random.randint(768, 1302))
            attempts += 1
            logger.info(f"Scrolling to message: attempt {attempts}")

        condition = sc.is_message_out(message)  # True = outgoing, False = incoming
        box = await message.bounding_box()
        if not box:
            logger.warning("[double_edge_click] Element bounding box not found after scrolling")
            return False

        # Compute click coordinates relative to element
        rel_x = box["width"] * (0.2 if condition else 0.8)
        rel_y = box["height"] / 2

        await page.mouse.move(rel_x, rel_y)
        await message.click(
            position={"x": rel_x, "y": rel_y},  # Relative click
            click_count=2,
            delay=random.randint(38, 69),
            timeout=3000
        )

        await page.wait_for_timeout(500)  # Small pause for UI reaction
        return True

    except Exception as e:
        logger.error(f"[double_edge_click] Error: {e}")
        return False


async def _reply_(page: Page, message: Union[ElementHandle, Locator], text: str, retry: int = 0) -> bool:
    """
    Core async function to type a reply into the message box without sending.

    Handles retries automatically on failure.

    Args:
        page (Page): Playwright page object.
        message (ElementHandle | Locator): Message element to reply to.
        text (str): Message text to type.
        retry (int): Current retry count.

    Returns:
        bool: True if typing succeeded, False otherwise.
    """
    try:
        await double_edge_click(page, message)

        inBox = sc.message_box(page)
        await inBox.click(timeout=3000)

        await ha.human_send(page, element=await inBox.element_handle(timeout=1000), text=text)
        return True

    except Exception:
        if retry < 1:
            return await _reply_(page, message, text, retry + 1)
        logger.error(f"[_reply_] Failed after retry", exc_info=True)
        return False


async def reply(
        page: Page,
        element: Union[ElementHandle, Locator],
        text: str) -> None:
    """
    Async function to reply to a message and automatically press Enter.

    Args:
        page (Page): Playwright page object.
        element (ElementHandle | Locator): Message element to reply to.
        text (str): Message text to send.
    """
    success = await _reply_(page, element, text)
    if success:
        await page.keyboard.press("Enter")
    else:
        logger.error("[reply] Failed to reply, Enter not pressed.", exc_info=True)


async def reply_media(
        page: Page,
        message: ElementHandle,
        text: str,
        file: list[str],
        mediatype: str = "doc",
        send_type: str = "add") -> None:
    """
    Sends a reply message with optional media attachment.

    Types the text first, then attaches media, and finally sends the message.
    Supports two sending types:
        - 'add': normal file attach via AddMedia
        - 'inject': direct file injection via InjectMedia

    Args:
        page (Page): Playwright page object.
        message (ElementHandle): Message element to reply to.
        text (str): Text to type before sending media.
        file (list[str]): List of file paths to attach.
        mediatype (str): Type of media ('doc', 'image', 'audio', etc.).
        send_type (str): 'add' or 'inject' for different media injection methods.
    """
    success = await _reply_(page, message, text)
    if success:
        if send_type == "inject":
            await med.InjectMedia(page=page, files=file, mediatype=mediatype)
        else:
            await med.AddMedia(page=page, file=file[0], mediatype=mediatype)

        await page.wait_for_timeout(random.randint(1123, 1491))
        await page.keyboard.press("Enter")
    else:
        await page.keyboard.press("Escape", delay=random.randint(701, 893))
        await page.keyboard.press("Escape", delay=random.randint(701, 893))
        logger.warning("[reply_media] Failed to reply with media, Escaped out.", exc_info=True)

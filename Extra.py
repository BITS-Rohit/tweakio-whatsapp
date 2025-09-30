import asyncio
import pathlib as pa
import random
import shutil
import time
from typing import Union, Optional

from playwright.async_api import Page, ElementHandle, Locator

import selector_config as sc
from Shared_Resources import logger


# ----------------------
# Message to any Chat
# ----------------------
async def MessageToChat(page: Page, text: str) -> bool:
    """
    Send message to any chat
    Steps:
    1. Locate and use the search box in the chat list panel.
    2. Type the owner’s number and pick the first chat result.
    3. Focus the message box, clear it, and type the login success message.
    4. Send the message and return to the main WhatsApp screen.
    """

    try:
        logger.info("Messaging to owner...")

        searchBox = sc.searchBox_chatList_panel(page)
        if not searchBox:
            logger.error("Search box is None.")
            return
        else:
            logger.debug("Search box found.")

        await searchBox.click()
        await searchBox.fill("")
        await searchBox.fill("7678686855")
        await asyncio.sleep(random.uniform(1.0, 2.0))

        firstPick = page.locator("div[role='listitem'] >> div[role='button']").first
        if not firstPick:
            logger.error("Failed to locate first chat result in chat list.")
            return

        await firstPick.hover()
        await firstPick.click()

        mess = sc.message_box(page)
        if not mess:
            logger.error("Message box locator is None.")
            return

        await mess.click()
        await mess.fill("")
        await mess.fill(text)
        await mess.press("Enter")

        await page.keyboard.press("Escape")
        await sc.wa_icon(page).click()

        logger.info("Messaged: Logged in, Success. Tweakio: Hi ! ✅ Messaging Done.")
    except Exception as e:
        logger.error(f"Failed to Message to Chat with error {e}")


# ----------------------
# Message ID
# ----------------------
async def getJID_mess(message: Union[ElementHandle, Locator]) -> str:
    """
    Extract the JID (WhatsApp ID) of a message.

    Example:
        "7678xxxxxx@c.us"

    Args:
        message (Union[ElementHandle, Locator]): The message element.

    Returns:
        str: The extracted JID string or "" if not found.
    """
    if isinstance(message, Locator):
        message = await message.element_handle(timeout=1001)

    data_id = await sc.get_dataID(message)
    if not data_id or "_" not in data_id:
        return ""

    parts = data_id.split("_")
    return parts[1] if len(parts) > 1 else ""


# ----------------------
# Sender ID
# ----------------------
async def getSenderID(message: Union[ElementHandle, Locator]) -> str:
    """
    Extract the sender’s identifier from a message.

    - If from a group: returns the sender's display name or number.
    - If from direct chat: returns the number.
    - Handles both @c.us (contacts) and @g.us (groups).

    Args:
        message (Union[ElementHandle, Locator]): The message element.

    Returns:
        str: Sender identifier (name or number), or "" if extraction fails.
    """
    if isinstance(message, Locator):
        message = await message.element_handle(timeout=1001)

    raw = await sc.get_dataID(message)

    async def get_from_lid() -> str:
        """Extract sender info for LinkedIn IDs (@lid)."""
        try:
            div = await message.query_selector("div.copyable-text[data-pre-plain-text]")
            if not div:
                return ""

            attr = await div.get_attribute("data-pre-plain-text")
            if not attr or "]" not in attr:
                logger.warning("[data-pre-plain-text] content is malformed.")
                return ""

            parts = attr.split("]", 1)
            return parts[1].strip()[:-1] if len(parts) > 1 else ""
        except Exception as e:
            logger.error(f"Error extracting sender: {e}")
            return ""

    if "@lid" in raw:
        return await get_from_lid()
    elif "@c.us" in raw and "@g.us" in raw:
        return raw.split("_", 3)[3].replace("@c.us", "")
    elif "@c.us" in raw:
        return raw.split("_", 2)[1].replace("@c.us", "")
    else:
        return ""


# ----------------------
# Group ID | Chat ID
# ----------------------
async def getGID_CID(message: Union[ElementHandle, Locator]) -> str:
    """
    Extract the Group ID (@g.us) for groups or Chat ID (@c.us) for single chats.

    Args:
        message (Union[ElementHandle, Locator]): The message element.

    Returns:
        str: Group/Chat ID string or "" if extraction fails.
    """
    if isinstance(message, Locator):
        message = await message.element_handle(timeout=1001)

    try:
        raw = await sc.get_dataID(message)
        logger.debug(f"Raw data-id: {raw}")

        if "g.cus" not in raw and "@c.us" in raw:
            return raw.split("_")[1]
        elif "@g.us" in raw:
            return raw.split("_", 2)[1]
        else:
            return ""
    except Exception as e:
        logger.error(f"Error in getGID_CID: {e}")
        return ""


# ----------------------
# Direction
# ----------------------
async def getDirection(message: Union[ElementHandle, Locator]) -> str:
    """Returns a direction [out: bot | in: other]."""
    return "out" if await sc.is_message_out(message) else "in"


# ----------------------
# Message type
# ----------------------
async def GetMessType(message: Union[ElementHandle, Locator]) -> str:
    """Returns the specific type of message: image, video, audio, gif, sticker, quoted, text"""
    if isinstance(message, Locator):
        message = await message.element_handle(timeout=1001)

    try:
        if await sc.isVideo(message):
            return "video Message"

        if await sc.pic_handle(message):
            return "image Message"

        if await sc.is_Voice_Message(message):
            return "Voice Message"

        q = sc.isQuotedText(message)
        if q and await q.is_visible():
            return "quoted"
        return "text"

    except Exception as e:
        logger.error(f"Unexpected error in GetMessType: {e}")
        return "unknown"


# ----------------------
# Timestamp
# ----------------------
async def get_Timestamp(message: Union[ElementHandle, Locator]) -> str:
    """Returns TimeStamp of the WhatsApp stored Time of the message.
    if error occurred returns Empty string"""
    if isinstance(message, Locator):
        message = await message.element_handle(timeout=1001)

    try:
        element = await message.query_selector("div[data-pre-plain-text]")
        if element:
            data = await element.get_attribute("data-pre-plain-text")
            if data:
                # WhatsApp format: [4:25 PM, 7/26/2025] Time: Sender
                return data.split("]")[0].strip("[")
        return ""
    except Exception as e:
        logger.error(f"Error in get_Timestamp : [{e}]")
        return ""


# ----------------------
# Trace message
# ----------------------
async def trace_message(
        seen_messages: dict,
        chat: Union[ElementHandle, Locator],
        message: Union[ElementHandle, Locator]) -> Optional[bool]:
    """Tracks a unique message and stores its details if not already seen.
    :return true if success in tracing message else false and None on error.
    """
    try:
        data_id = await sc.get_dataID(message)
        if not data_id:
            logger.error("data id is empty in trace_message")
            return None

        if data_id not in seen_messages:
            seen_messages[data_id] = {
                "chat": await sc.getChatName(chat),
                "community": await sc.is_community(chat),
                # "preview_url": await sc.getChat_low_Quality_Img(chat),
                "jid": await getJID_mess(message),
                "message": await sc.get_message_text(message),
                "sender": await getSenderID(message),
                "time": await get_Timestamp(message),
                "systime": time.time(),
                "direction": await getDirection(message),
                "type": await GetMessType(message),
            }
            return True
        return False
    except Exception as e:
        logger.error(f"Error in trace_message : {e}")
        return None


def cleanFolder(folder: pa.Path) -> None:
    """This one stays sync — it's just filesystem operations."""
    if folder.exists():
        for item in folder.iterdir():
            try:
                if item.is_file():
                    item.unlink()
                elif item.is_dir():
                    shutil.rmtree(item)
            except Exception as e:
                print(f"⚠️ Could not delete {item}: {e}")

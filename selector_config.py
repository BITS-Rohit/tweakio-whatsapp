"""
Helper functions to interact with various WhatsApp Web UI components using Playwright.

Conventions:
- `page`: refers to `playwright.sync_api.Page` instance.
- All other elements returned are of the type `Locator`.
- Utility functions are written to extract attributes or recognize content like images, videos, or quoted messages.
"""
import re
from typing import Union, Optional

from playwright.async_api import ElementHandle, Locator, Page


def chat_list(page: Page) -> Locator:
    """Returns the chat list grid locator on the main UI."""
    return page.get_by_role("grid", name=re.compile("chat list", re.I))


def message_chat_panel(page: Page) -> Locator:
    """ Gives the message container panel"""
    return page.locator("div[id='main']").get_by_role("application").first


def new_chat_chat_list_panel(page: Page) -> Locator:
    """ Return the locator for the new chat on the chat list upper panel"""
    return page.get_by_role("button", name=re.compile("new chat", re.I)).first


def searchBox_chatList_panel(page: Page) -> Locator:
    """Returns the search box on the chat list panel"""
    return page.get_by_role("textbox", name=re.compile("search input textbox", re.I)).first


def message_box(page: Page) -> Locator:
    """Message Input box on the message panel"""
    return page.locator("footer").get_by_role("textbox").first


def wa_icon(page: Page) -> Locator:
    """WhatsApp icon locator"""
    return page.get_by_role("heading", name="WhatsApp").first


def chat_list_filters_ALL(page: Page) -> Locator:
    """Return the chat list filter : ALL """
    return page.locator("#all-filter")


def chat_list_filters_Unread(page: Page) -> Locator:
    """Return the chat list filter : Unread"""
    return page.locator("#unread-filter")


def chat_list_filters_favorites(page: Page) -> Locator:
    """Return the chat list filter : Favorites"""
    return page.locator("#favorites-filter")


def chat_list_filters_groups(page: Page) -> Locator:
    """Return the chat list filter : Groups"""
    return page.locator("#group-filter")


async def total_chats(page: Page) -> int:
    """Returns the total number of chats visible in the chat list."""
    element = chat_list(page)  # await if chat_list is async
    attr = await element.get_attribute("aria-rowcount")
    return int(attr) if attr else 0


def chat_items(page: Page) -> Optional[Locator]:
    """Returns a locator for all individual chat items (buttons) in the list."""
    row_locator = chat_list(page).get_by_role("row")
    list_locator = chat_list(page).get_by_role("listitem")
    if row_locator:
        return row_locator
    elif list_locator:
        return list_locator
    return None


async def getChat_low_Quality_Img(chat: Union[ElementHandle, Locator]) -> str:
    """Extracts the low-quality image (thumbnail) from a chat preview item."""
    if isinstance(chat, Locator):
        chat = await chat.element_handle(timeout=1001)
        if chat is None:
            return ""

    imgs = await chat.query_selector_all("img[src]")
    if imgs:
        img_el = imgs[0]
        if await img_el.is_visible():
            src = await img_el.get_attribute("src")
            return src or ""
    return ""


async def getChatName(chat: Union[ElementHandle, Locator]) -> str:
    """Returns the primary chat name (first span[title]) or empty string."""
    if isinstance(chat, Locator):
        chat = await chat.element_handle(timeout=1001)
        if chat is None:
            return ""

    if await is_community(chat):
        spans = await chat.query_selector_all("span[title]")
        if len(spans) > 1:
            return await spans[1].get_attribute("title") or ""
        return ""

    span = await chat.query_selector("span[title]")
    if span:
        return await span.get_attribute("title") or ""
    return ""


async def is_community(chat: Union[ElementHandle, Locator]) -> bool:
    """
    If this chat item has the 'default-community-refreshed' icon,
    return True.
    """
    if isinstance(chat, Locator):
        chat = await chat.element_handle(timeout=1001)
        if chat is None:
            return False

    icon = await chat.query_selector("span[data-icon='default-community-refreshed']")
    if icon and await icon.is_visible():
        return True
    return False


def Profile_header(page: Page) -> Locator:
    """
    Returns the profile header button locator used to open contact details.
    Used when a chat is opened and the top bar includes profile/name/media access.
    """
    return page.locator("header").get_by_role("button", name=re.compile("profile details", re.I))


def qr_canvas(page: Page) -> Locator:
    """Returns the QR canvas image for login."""
    return page.get_by_role("img", name=re.compile(r"scan.*qr", re.I))


# -------------------- Sidebar Navigation -------------------- #

def _side_Bar_chats(page: Page) -> Locator:
    """Returns the sidebar button locator for 'Chats'."""
    return page.locator("header").first.get_by_role("button", name=re.compile("chats", re.I))


def _side_Bar_status(page: Page) -> Locator:
    """Returns the sidebar button locator for 'Status Updates'."""
    return page.locator("header").first.get_by_role("button", name=re.compile("updates in status", re.I))


def _side_Bar_channels(page: Page) -> Locator:
    """Returns the sidebar button locator for 'Channels'."""
    return page.locator("header").first.get_by_role("button", name=re.compile("channels", re.I))


def _side_Bar_Communities(page: Page) -> Locator:
    """Returns the sidebar button locator for 'Communities'."""
    return page.locator("header").first.get_by_role("button", name=re.compile("communities", re.I))


# -------------------- Messages Section -------------------- #

def messages(page: Page) -> Locator:
    """
    Returns a locator for all messages in the current open chat.
    Each message element has a unique `data-id` and role "row".
    """
    return page.locator('[role="row"] div[data-id]')


def messages_incoming(page: Page) -> Locator:
    """Filter for the personal | group chat incoming messages"""
    return page.locator('[role="row"] div[data-id] .message-in')


def messages_outgoing(page: Page) -> Locator:
    """Filter for the personal | group chat outgoing messages"""
    return page.locator('[role="row"] div[data-id] .message-out')


async def get_message_text(message_element: Union[ElementHandle, Locator]) -> str:
    """Returns the text content of a message if visible."""
    if isinstance(message_element, Locator):
        message_element = await message_element.element_handle()
        if message_element is None:
            return ""

    span = await message_element.query_selector("span.selectable-text.copyable-text")
    if span and await span.is_visible():
        text = await span.text_content()
        return text or ""
    return ""


# def get_message_text(element: Locator | ElementHandle) -> str:
#     return element.inner_text().strip()


async def is_message_out(message: Union[ElementHandle, Locator]) -> bool:
    """Returns True if the message is outgoing (sent by bot)."""
    if isinstance(message, ElementHandle):
        element = await message.query_selector(".message-out")
    else:
        element = message.locator(".message-out")

    if isinstance(element, Locator):
        return await element.is_visible()
    return element is not None and await element.is_visible()


async def get_dataID(message: Union[ElementHandle, Locator]) -> str:
    """Returns the unique data-id attribute of a message."""
    return await message.get_attribute("data-id") or ""


# -------------------- Media Send  -------------------- #
def plus_rounded_icon(page: Page) -> Locator:
    """
    It is a locator for the plus icon in the message box for opening menu with options like : image , videos ,documents to send
    :param page:
    :return:
    """
    return page.get_by_role("button").locator("span[data-icon]").filter(has_text=re.compile("plus-rounded", re.I)).first


def document(page: Page) -> Locator:
    """Safely locates the 'Document' upload option in the menu"""
    return page.get_by_role("button", name="Document").first


def photos_videos(page: Page) -> Locator:
    """Safely locates the 'Photos & videos' upload option in the menu"""
    return page.get_by_role("button", name="Photos & videos").first


def camera(page: Page) -> Locator:
    """Safely locates the 'Camera' upload option in the menu"""
    return page.get_by_role("button", name="Camera").first


def audio(page: Page) -> Locator:
    """Safely locates the 'Audio' upload option in the menu"""
    return page.get_by_role("button", name="Audio").first


def contact(page: Page) -> Locator:
    """Safely locates the 'Contact' upload option in the menu"""
    return page.get_by_role("button", name="Contact").first


def poll(page: Page) -> Locator:
    """Safely locates the 'Poll' upload option in the menu"""
    return page.get_by_role("button", name="Poll").first


def event(page: Page) -> Locator:
    """Safely locates the 'Event' upload option in the menu"""
    return page.get_by_role("button", name="Event").first


def new_sticker(page: Page) -> Locator:
    """Safely locates the 'New sticker' upload option in the menu"""
    return page.get_by_role("button", name="New sticker")


# -------------------- Message Type Checkers -------------------- #

async def get_mess_pic_url(message: ElementHandle) -> str:
    """Extracts the image URL from an incoming picture message if visible."""
    img_el = await message.query_selector("img")
    if img_el:
        return await img_el.get_attribute("src") or ""
    return ""


async def isReacted(message: Union[ElementHandle, Locator]) -> bool:
    """Check if the message is reacted or not"""
    try:
        if isinstance(message, Locator):
            message = await message.element_handle(timeout=1001)
        btn = await message.query_selector("button[aria-label*='reaction 👍']")
        return await btn.is_visible() if btn else False
    except:
        return False


async def pic_handle(message: ElementHandle) -> bool:
    pic = await message.query_selector(
        "xpath=.//div[@role='button' and "
        "translate(@aria-label, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz')='open picture']//img"
    )
    if pic and await pic.is_visible():
        return True
    pic2 = await message.query_selector("xpath=.//img[contains(@src,'data:image/')]")
    return await pic2.is_visible() if pic2 else False


async def isVideo(message: ElementHandle) -> bool:
    """
    Checks if current message is of type : video
    :param message: ElementHandle
    :return: bool
    """
    video = await message.query_selector(
        "xpath=.//span[@data-icon='media-play' or @data-icon='msg-video']"
    )
    return await video.is_visible() if video else False


async def is_Voice_Message(message: ElementHandle) -> bool:
    voice = await message.query_selector(
        "xpath=.//button[contains(translate(@aria-label,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'voice message')]"
    )
    if voice and await voice.is_visible():
        return True
    voice2 = await message.query_selector(
        "xpath=.//span[contains(translate(@data-icon,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'audio-play')]"
    )
    return await voice2.is_visible() if voice2 else False


async def is_gif(message: ElementHandle) -> bool:
    gif_btn = await message.query_selector(
        "xpath=.//div[@role='button' and "
        "contains(translate(@aria-label,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'play gif')]"
    )
    if gif_btn and await gif_btn.is_visible():
        return True
    gif2 = await message.query_selector(
        "xpath=.//span[contains(translate(@data-icon,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'media-gif')]"
    )
    return await gif2.is_visible() if gif2 else False


async def is_animated_sticker(message: ElementHandle) -> bool:
    sticker = await message.query_selector(
        "xpath=.//img[contains(translate(@alt,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'animated sticker')]"
    )
    return await sticker.is_visible() if sticker else False


async def is_plain_sticker(message: ElementHandle) -> bool:
    sticker = await message.query_selector(
        "xpath=.//img[contains(translate(@alt,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'sticker with no label')]"
    )
    return await sticker.is_visible() if sticker else False


async def is_lottie_animation_sticker(message: ElementHandle) -> bool:
    el = await message.query_selector(
        "xpath=.//button[contains(translate(@aria-label,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'sticker')]//img[contains(@src,'blob:')]"
    )
    return await el.is_visible() if el else False


async def isSticker(message: ElementHandle) -> bool:
    """Returns True if any sticker type is detected using XPath."""
    return (
            await is_animated_sticker(message)
            or await is_plain_sticker(message)
            or await is_lottie_animation_sticker(message)
    )


# -------------------- Quoted Message Utilities -------------------- #

async def isQuotedText(message: ElementHandle) -> Optional[ElementHandle]:
    """
    Checks if a message is quoting another and returns the quoted-message handle.
    """
    return await message.query_selector("span.quoted-mention")


def get_QuotedText_handle(message: ElementHandle) -> str:
    """Returns the handle for the quoted-mention span inside a quoted message."""
    return isQuotedText(message).is_visible() or ""


# -- System -- #

def startup_popup_locator(page: Page) -> Locator:
    """Returns the startup continue popup button locator."""
    return page.get_by_role("button", name=re.compile("continue", re.I))


async def popup2(page: Page):
    """
    2nd Pop up of WhatsApp with message:
    "Your chats and calls are private"
    """
    button = await page.query_selector("div[data-animate-model-popup] button:text-is('OK')")
    if button:
        try:
            if await button.is_visible():
                await button.click()
        except Exception as e:
            print(f"[popup2] Click failed: {e}")


# ---------------------------- Message Other Option ------------------------------ #
"""
Options :
--Group info 
--select messages
--Mute notifications
--Disappearing messages
--Add to favourite
--close chat 
--clear chat 
--Exit group
"""


async def group_info(page: Page) -> Optional[ElementHandle]:
    dialog = await page.query_selector("div[role='dialog']")
    return await dialog.query_selector("li:has-text('group info')") if dialog else None


async def select_messages(page: Page) -> Optional[ElementHandle]:
    dialog = await page.query_selector("div[role='dialog']")
    return await dialog.query_selector("li:has-text('select messages')") if dialog else None


async def mute_notifications(page: Page) -> Optional[ElementHandle]:
    dialog = await page.query_selector("div[role='dialog']")
    return await dialog.query_selector("li:has-text('mute notifications')") if dialog else None


async def disappearing_messages(page: Page) -> Optional[ElementHandle]:
    dialog = await page.query_selector("div[role='dialog']")
    return await dialog.query_selector("li:has-text('disappearing messages')") if dialog else None


async def add_to_fav(page: Page) -> Optional[ElementHandle]:
    dialog = await page.query_selector("div[role='dialog']")
    return await dialog.query_selector("li:has-text('add to favourites')") if dialog else None


async def close_chat(page: Page) -> Optional[ElementHandle]:
    dialog = await page.query_selector("div[role='dialog']")
    return await dialog.query_selector("li:has-text('close chat')") if dialog else None


async def clear_chat(page: Page) -> Optional[ElementHandle]:
    dialog = await page.query_selector("div[role='dialog']")
    return await dialog.query_selector("li:has-text('clear chat')") if dialog else None

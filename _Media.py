"""Media private Methods"""
import asyncio
import random
from pathlib import Path

from playwright.async_api import Page, Locator, FileChooser

import selector_config as sc


# ----------------------------------------------------------------  #

async def getMediaOptionLocator(page: Page, mediatype: str) -> Locator:
    """
    Returns the visible <li> or <button> you need to click
    to open the Photos & videos / Document / Audio chooser.
    """
    mt = mediatype.lower().strip()
    if mt in ("img", "image", "vid", "video"):
        return sc.photos_videos(page)
    if mt == "audio":
        return sc.audio(page)
    # fallback to document
    return sc.document(page)


async def getMediaInputLocator(page: Page, mediatype: str) -> Locator:
    """
    Returns the hidden <input type=file> inside that menu item,
    for direct .set_input_files() injection.
    """
    l = await  getMediaOptionLocator(page, mediatype)
    return l.locator("input[type=file]")


async def menu_icon_click(page: Page):
    try:
        menu_icon = await sc.plus_rounded_icon(page=page).element_handle()

        if not menu_icon:
            print("Menu Icon not found")
            return

        # ha.move_mouse_to_locator(page, menu_icon)
        await menu_icon.click(timeout=2000)
        await asyncio.sleep(random.uniform(1.0, 1.5))
    except Exception as e:
        print(f"Menu Icon not found : {e}")
        await page.keyboard.press("Escape", delay=0.5)
        await page.keyboard.press("Escape", delay=0.5)


async def InjectMedia(page: Page, files: list[str], mediatype: str = "doc") -> None:
    """
    Add the Media to the message box but don't send. Just adds the Media.
    :param mediatype:  type of the file to add
    :param files: list of type str [give the list of the files path as str]
    :param page:page
    :return:None
    """

    try:
        await menu_icon_click(page)
        media_input = await getMediaInputLocator(page, mediatype)
        if not media_input:
            print(f"❌ Media type button not visible for: {mediatype}")
            return

        if not media_input:
            print(f"Media input for type [ {mediatype} ] not found")
            return

        await media_input.set_input_files(files)
    except Exception as e:
        print(f" Error occurred in InjectMedia : {e}")
        await page.keyboard.press("Escape", delay=0.5)
        await page.keyboard.press("Escape", delay=0.5)


async def AddMedia(page: Page, file: str, mediatype: str = "doc") -> None:
    """
    this adds an image to the message box , only images
    :param page:
    :param file:
    :param mediatype:
    :return:
    """
    try:
        await menu_icon_click(page)
        target = await getMediaOptionLocator(page, mediatype)
        target = await target.element_handle()
        if not await target.is_visible():
            print(f"❌ Attach option for '{mediatype}' not visible.")
            return

        with page.expect_file_chooser() as fc:
            await target.click(timeout=2000)
        chooser: FileChooser = fc.value

        p = Path(file)
        if not p.exists():
            print(f"❌ File not found: {file}")
            return

        await chooser.set_files(str(p.resolve()))

        print(f"✅ Sent {mediatype}: {file}")

    except Exception as e:
        print(f"Error in AddMedia: {e}")
        await page.keyboard.press("Escape", delay=0.5)
        await page.keyboard.press("Escape", delay=0.5)

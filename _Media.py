"""Media private Methods"""
import asyncio
import random
from pathlib import Path

from playwright.async_api import Page, Locator, FileChooser

import selector_config as sc
from Shared_Resources import logger


# ----------------------------------------------------------------  #

async def _getMediaOptionLocator(page: Page, mediatype: str) -> Locator:
    """
    Returns the visible <li> or <button> you need to click
    to open the Photos & videos / Document / Audio chooser.
    :param page: Page
    :param mediatype: Media type
    :return: Locator
    """
    mt = mediatype.lower().strip()
    if mt in ("img", "image", "vid", "video"):
        return sc.photos_videos(page)
    if mt == "audio":
        return sc.audio(page)
    # fallback to document
    return sc.document(page)


async def _getMediaInputLocator(page: Page, mediatype: str) -> Locator:
    """
    Returns the hidden <input type=file> inside that menu item,
    for direct .set_input_files() injection.
    :param page: Page
    :param mediatype: Media type
    :return: Locator
    """
    l = await  _getMediaOptionLocator(page, mediatype)
    return l.locator("input[type=file]")


async def MenuClicker(page: Page) -> None:
    """
    This is a Menu Clicker ( Plus rounded icon on message bar left side )
    :param page: page
    :return: None
    """
    try:
        menu_icon = await sc.plus_rounded_icon(page=page).element_handle()
        if not menu_icon:
            logger.error("Menu Icon not found", exc_info=True)
            return

        await menu_icon.click(timeout=2000)
        await asyncio.sleep(random.uniform(1.0, 1.5))
    except Exception as e:
        logger.error(f"Menu Icon not found: {e}", exc_info=True)
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
        await MenuClicker(page)
        media_input = await _getMediaInputLocator(page, mediatype)
        if not media_input:
            logger.info(f"❌ Media type button not visible for: {mediatype}")
            return

        if not media_input:
            logger.info(f"Media input for type [ {mediatype} ] not found")
            return

        await media_input.set_input_files(files)
    except Exception as e:
        logger.error(f" Error occurred in InjectMedia: {e} ", exc_info=True)
        await page.keyboard.press("Escape", delay=0.5)
        await page.keyboard.press("Escape", delay=0.5)


async def AddMedia(page: Page, file: str, mediatype: str = "doc") -> None:
    """
    this adds an image to the message box , only images
    :param page:
    :param file: string path
    :param mediatype:
    :return:
    """
    try:
        await MenuClicker(page)
        target = await _getMediaOptionLocator(page, mediatype)
        target = await target.element_handle()
        if not await target.is_visible():
            logger.error(f"❌ Attach option for '{mediatype}' not visible.", exc_info=True)
            return

        with page.expect_file_chooser() as fc:
            await target.click(timeout=2000)
        chooser: FileChooser = fc.value

        p = Path(file)
        if not p.exists():
            logger.error(f"❌ File not found: {file}", exc_info=True)
            return

        await chooser.set_files(str(p.resolve()))
        logger.info(f"✅ Sent {mediatype}: {file}")

    except Exception as e:
        logger.error(f"Error in AddMedia: {e}", exc_info=True)
        await page.keyboard.press("Escape", delay=0.5)
        await page.keyboard.press("Escape", delay=0.5)

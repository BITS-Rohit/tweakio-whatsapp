import random

import pyperclip
from playwright.async_api import Page, ElementHandle

from Shared_Resources import logger


async def human_send(page: Page, element: ElementHandle, text: str):
    """
    Types text into a message input field in a human-like manner.

    - Clicks into the input field and clears previous text.
    - Handles multi-line input using Shift+Enter for newline characters.
    - Falls back to element.fill() for large text if typing fails.
    - Uses clipboard paste if individual lines are very long (>100 characters).

    Args:
        page (Page): Playwright page object.
        element (ElementHandle): The input element to type into.
        text (str): The message text to send.
    """
    try:
        await element.click(timeout=2000)

        # Clear previous content
        await element.press("Control+A")
        await element.press("Backspace")
        logger.info("Cleared previous text in input box")

        lines = text.split("\n")

        # If short text with no newline, type normally
        if len(text) <= 50 and len(lines) == 1:
            await page.keyboard.type(text, delay=random.randint(76, 98))
        else:
            for i, line in enumerate(lines):
                if len(line) > 100:
                    pyperclip.copy(line)
                    await page.keyboard.press("Control+V")
                else:
                    await page.keyboard.type(line, delay=random.randint(47, 98))

                if i < len(lines) - 1:
                    await page.keyboard.press("Shift+Enter")

    except Exception as e:
        logger.warning(f"[human_send fallback] Typing failed: {e}",exc_info=True)
        try:
            await element.fill(text)
            await page.keyboard.press("Enter")
        except Exception as e:
            logger.error(f"[human_send fallback] Fill and Enter also failed: {e}",exc_info=True)
            await page.keyboard.press("Escape", delay=0.5)
            await page.keyboard.press("Escape", delay=0.5)

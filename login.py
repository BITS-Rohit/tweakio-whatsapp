import asyncio
import random
import re
from pathlib import Path
from typing import Optional

from playwright.async_api import Page

import selector_config as sc
from Errors import NumberNotFound, CountryNotFound, QRNotScanned, PageNotFound, LoginError

class whatsapp_login:
    """
            _____Number_______
            Number is for the bot number u want it to be working on  , Ex : 387343xxxx
            country is the country of which the number that is India , india , Japan etc.
            Login prefer : 0 or 1 :
                0 means QR based Login ( u would need a device to scan the QR)
                1 means Code Based Login ( Default is 1 )
            :param number: 983283xxxx
            :param country: India or india
            :param login_prefer: 0 or 1
            :param page : get page from the Browser Driver first
            :param storage_file_path : It is the Browser's storage path where it will save the cookies
            """

    def __init__(self, number, country, page, storage_file_path, login_prefer="1"):
        self.number = number
        self.country = country
        self.page = page
        self.storage_file_path = storage_file_path
        self.login_prefer = login_prefer

    async def login(self, login_wait_time: int = 180_000, link: str = "https://web.whatsapp.com") -> bool:
        if not self.number:
            raise NumberNotFound()
        if not self.country:
            raise CountryNotFound()

        await self.page.goto(link, timeout=60_000)
        await self.page.wait_for_load_state("networkidle", timeout=50_000)

        # Use self.page, self.storage_file_path
        if self.login_prefer == "1":
            await self._code_login()
        else:
            await self._scanner_login(login_wait_time)
        return True

    async def _scanner_login(self, LOGIN_WAIT_TIME: int) -> Optional[bool]:
        if self.page is None: raise PageNotFound

        canvas = sc.qr_canvas(self.page)
        print("⏳ Waiting for QR scan…")

        t = LOGIN_WAIT_TIME / 2
        await sc.chat_list(self.page).wait_for(timeout=t, state="visible")

        if await canvas.is_visible():
            raise QRNotScanned(f"⚠️ QR not scanned within {t} ms")

        # Todo for Screenshot for the QR

        print("✅ QR scan succeeded")
        await self.page.context.storage_state(path=self.storage_file_path)
        return True

    async def _code_login(self, page: Page) -> Optional[bool]:
        print("🔑 Starting code-based login…")

        # Click “Login with phone number”
        try:
            btn = page.get_by_role("button", name=re.compile("log.*in.*phone number", re.I))
            await btn.click(timeout=3000)
            await page.wait_for_load_state("networkidle")
        except:
            print("⚠️ ‘Login with phone number’ button not found.")
            return False

        # Select country
        try:
            ctl = page.locator("button:has(span[data-icon='chevron'])")
            await ctl.click(timeout=3000)
            await page.keyboard.type(self.country, delay=random.randint(100, 200))
            await asyncio.sleep(0.5)

            # Todo make the country select more precise

            await page.keyboard.press("ArrowDown")
            await page.keyboard.press("ArrowDown")
            await page.keyboard.press("Enter")
        except Exception as e:
            print("⚠️ Country selection failed:", e)
            return False

        # Enter phone number
        try:
            inp = page.locator("form >> input")
            await inp.click(timeout=3000)
            await inp.type(self.number, delay=random.randint(100, 200))
            await page.keyboard.press("Enter")
        except Exception as e:
            print("⚠️ Phone number input failed:", e)
            return False

        # Retrieve login code
        try:
            code_elem = page.locator("div[data-link-code]")
            await code_elem.wait_for(timeout=10_000)
            code = code_elem.get_attribute("data-link-code")
            print(f"🔢 Received login code: {code}")
        except Exception as e:
            print("⚠️ Could not retrieve login code:", e)
            return False

        # Wait for chats to load
        try:
            print("Waiting 3 mins for chat load")
            await sc.chat_list(page).wait_for(timeout=180_000, state="visible")
            print("✅ Chats loaded via code login")
            await self.page.context.storage_state(path=str(self.storage_file_path))
            return True
        except:
            raise LoginError()


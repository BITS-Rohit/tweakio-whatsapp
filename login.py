"""
This is Login File for Whatsapp.
"""
import asyncio
import os
import random
import re
from typing import Optional

from playwright.async_api import Locator
from playwright.async_api import Page

import directory as dirs
import selector_config as sc
from Errors import NumberNotFound, CountryNotFound, QRNotScanned, PageNotFound
from Shared_Resources import logger


class WhatsappLogin:
    """Login to Whatsapp Web
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

    def __init__(self, number, country, page, storage_file_path=dirs.storage_state_file, login_prefer="1",
                 override_login: bool = False):
        self.number = number
        self.country = country
        self.page = page
        self.storage_file_path = storage_file_path
        self.login_prefer = login_prefer
        self.override_login = override_login

    async def login(self, login_wait_time: int = 180_000, link: str = "https://web.whatsapp.com") -> bool:
        """
        Do the login of whatsapp , Has 2 routes : 1st is QR-Based ( login prefer : 0 ) , 2nd is Code-Based ( login prefer : 1 )
        :param login_wait_time:
        :param link:
        :return: True if login successful else if  False on specified modules else raise Error LoginError() on any other Exception
        """
        if not self.number:
            raise NumberNotFound()
        if not self.country:
            raise CountryNotFound()

        await self.page.goto(link, timeout=60_000)
        await self.page.wait_for_load_state("networkidle", timeout=50_000)

        if self.override_login is False and os.path.exists(self.storage_file_path):
            logger.info("✅ Using saved storage state")
            return True

        # ------- Override ---------
        if self.override_login:
            logger.info("Overriding login to Whatsapp Web")
            if self.storage_file_path.exists():
                shutil.rmtree(self.storage_file_path)
                os.makedirs(self.storage_file_path)

        if self.page is None: raise PageNotFound()
        if self.login_prefer == "1":
            await self._code_login()
        else:
            await self._scanner_login(login_wait_time)
        return True

    async def _scanner_login(self, LOGIN_WAIT_TIME: int) -> Optional[bool]:

        canvas = sc.qr_canvas(self.page)
        logger.info("⏳ Waiting for QR scan…")

        t = LOGIN_WAIT_TIME / 2
        await sc.chat_list(self.page).wait_for(timeout=t, state="visible")

        if await canvas.is_visible():
            raise QRNotScanned(f"⚠️ QR not scanned within {t} ms")

        # Todo for Screenshot for the QR, Future release

        logger.info("✅ QR scan succeeded")
        if not os.path.exists(self.storage_file_path):
            await self.page.context.storage_state(path=self.storage_file_path)
            logger.info(f"Storage state saved to {self.storage_file_path}")
        else:
            logger.info(f"Storage state already exists at {self.storage_file_path}, skipping save.")

        return True

    async def _code_login(self) -> Optional[bool]:
        page: Page = self.page
        logger.info("🔑 Starting code-based login…")

        try:
            # Click "Login with phone number" button
            btn = page.get_by_role("button", name=re.compile("log.*in.*phone number", re.I))
            if await btn.count() == 0:
                await page.wait_for_timeout(3000)
            await btn.click(timeout=3000)
            await page.wait_for_load_state("networkidle")
        except PlaywrightTimeoutError:
            logger.warning("⏰ Timeout waiting for login button.")
            return False
        except Exception as e:
            logger.error(f"⚠️ Error clicking login button: {e}", exc_info=True)
            return False

        # Select country
        try:
            ctl = page.locator("button:has(span[data-icon='chevron'])")
            if await ctl.count() == 0:
                await page.wait_for_timeout(3000)
            await ctl.click(timeout=3000)
            await page.keyboard.type(self.country, delay=random.randint(100, 200))
            await asyncio.sleep(1.0)

            countries: Locator = page.get_by_role("listitem").locator("button")
            count_of_countries = await countries.count()
            if count_of_countries == 0:
                raise CountryNotFound(f"⚠️ Country '{self.country}' not found in the Whatsapp website List")

            for i in range(count_of_countries):
                element = countries.nth(i)
                country_name =await element.inner_text()

                def process(name: str) -> str:
                    """
                    Refine String for Words & in-between spaces
                    :param name:
                    :return:
                    """
                    return ''.join(ch for ch in name if ch.isalpha() or ch.isspace()).strip()

                country_name = process(country_name)
                print(f"name : {country_name}")

                if country_name.lower() == self.country.lower():
                    await element.click(timeout=3000)
        except Exception as e:
            logger.error(f"⚠️ Country selection failed: {e}", exc_info=True)
            return False

        # Enter phone number
        try:
            inp = page.locator("form >> input")
            await inp.click(timeout=3000)
            await inp.type(self.number, delay=random.randint(100, 200))
            await page.keyboard.press("Enter")
        except Exception as e:
            logger.error(f"⚠️ Phone number input failed: {e}", exc_info=True)
            return False

        # Retrieve login code
        try:
            code_elem = page.locator("div[data-link-code]")
            await code_elem.wait_for(timeout=10_000)
            code = await code_elem.get_attribute("data-link-code")
            logger.info(f"🔢 Received login code: {code}")
        except Exception as e:
            logger.error(f"⚠️ Could not retrieve login code: {e}", exc_info=True)
            return False

        # Wait for chats to load
        try:
            logger.info("⏳ Waiting for chats to load…")
            await sc.chat_list(page).wait_for(timeout=180_000, state="visible")
            logger.info("✅ Chats loaded via code login")

            # Save storage state
            await self.page.context.storage_state(path=self.storage_file_path)
            logger.info(f"💾 Storage state saved to {self.storage_file_path}")

            return True
        except Exception as e:
            logger.error(f"❌ Error waiting for chats: {e}", exc_info=True)
            return False

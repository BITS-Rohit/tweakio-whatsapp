"""
Browser Manager Class for whatsapp Module
"""
import os
import pickle
import shutil
from dataclasses import asdict
from pathlib import Path
from typing import Optional, Tuple

import camoufox.exceptions
from browserforge.fingerprints import FingerprintGenerator
from camoufox.async_api import launch_options, AsyncCamoufox
from playwright.async_api import BrowserContext, Page

import directory as dirs
from Shared_Resources import logger


class BrowserManager:
    """
    Manages a Playwright BrowserContext instance integrated with Camoufox and BrowserForge fingerprints.

    This class ensures that the browser fingerprint matches the system's actual screen dimensions,
    and provides optional parameters to customize browser launch behavior such as locale, cache,
    headless mode, and add-ons.

    Attributes
    ----------
    fingerprint : dict, optional
        A specific BrowserForge-style fingerprint to use.
        If None, a valid fingerprint will be automatically generated or loaded from cache.
        Reference format: https://camoufox.com/

    override_fingerprint : bool, default=False
        If True, any existing stored fingerprint will be replaced with a newly generated one.

    addons : list[str], optional
        A list of paths to browser extensions (add-ons) to be installed in the browser instance.
        Also give the path to the add-ons to a list of str

    locale : str, default="en-US"
        The locale setting for the browser.

    enable_cache : bool, default=True
        Enables or disables browser caching(going forward to backward in pages).

    cache_dir : pathlib.Path, optional
        The directory used for storing browser cache and session data.
        If not provided, the default application cache directory will be used.

    headless : bool, default=True
        Runs the browser in headless (non-UI) mode if True, or with visible UI if False.

    debug_fingerprint : bool, default=False
        It saves the fingerprint to a json file for debugging

    debug_fingerprint_json_path : Path
        It saves the json to this location

    Notes
    -----
    - If no arguments are provided, the browser instance will still initialize with default settings.
    - Fingerprints are automatically validated against system screen dimensions for realism.
    - Uses Camoufox’s internal `AsyncCamoufox` launcher under the hood.

    Example
    -------
    python
    from tweakio.browser import BrowserManager

    manager = BrowserManager()
    browser = await manager.getInstance()

    page = await browser.new_page()
    await page.goto("https://example.com")
    """

    def __init__(
            self,
            addons=None,
            cache_dir_path: Path = dirs.cache_dir,
            override_cookies: bool = False,
            headless: bool = False,
            locale: str = "en-US",
            enable_cache: bool = True,
            fingerprint=None,
            override_fingerprint: bool = False,
            debug_fingerprint: bool = False,
            debug_fingerprint_json_path: Path = dirs.fingerprint_debug_json,
    ):

        if override_cookies:
            shutil.rmtree(cache_dir_path) if os.path.exists(cache_dir_path) else None

        self.debug_fingerprint_json_path = debug_fingerprint_json_path
        self.debug_fingerprint = debug_fingerprint
        self.cache_dir_path = cache_dir_path
        if addons is None:
            addons = []
        self.enable_cache = enable_cache
        self.locale = locale
        self.headless = headless
        self.addons = addons
        self.browser: Optional[BrowserContext] = None
        self.override_fingerprint = override_fingerprint
        self.fg = fingerprint

    async def getInstance(self) -> BrowserContext:
        """Provides the Instance of the BrowserContext."""
        if self.browser is None:
            self.browser = await self.__GetBrowser__()
        return self.browser

    async def __GetBrowser__(self, tries : int  = 1) -> BrowserContext:
        Browser = self.browser

        def fingerprintFile():
            """
            Generates or loads a BrowserForge Fingerprint object for the current system.

            Behavior:
                - If override_fingerprint=True → always generate a new fingerprint.
                - If fingerprint.pkl exists and override=False → loads from file.
                - Ensures screen dimensions match real display size within tolerance.
            """
            path = dirs.fingerprint_file
            fg = self.fg

            # Force new fingerprint if override is enabled
            if self.override_fingerprint:
                logger.info("♻️ Override enabled. Generating a fresh fingerprint...")
                fg = None

            # Try loading existing fingerprint if override not set
            if fg is None and not self.override_fingerprint and path.exists():
                logger.info("📦 Loading existing fingerprint from file...")
                with open(path, 'rb') as fh:
                    fg = pickle.load(fh)

            # Generate new fingerprint if none found or override=True
            if fg is None:
                logger.info("🧬 Generating new fingerprint...")
                gen = FingerprintGenerator()
                real_w, real_h = get_screen_size()
                tolerance = 0.1  # 10% tolerance
                attempt = 0

                while True:
                    fg = gen.generate()
                    w, h = fg.screen.width, fg.screen.height
                    attempt += 1

                    if abs(w - real_w) / real_w < tolerance and abs(h - real_h) / real_h < tolerance:
                        logger.info(f"✅ Fingerprint screen OK: {w}x{h}")
                        break

                    logger.warning(
                        f"🔁 Invalid fingerprint screen ({w}x{h}) vs real ({real_w}x{real_h}). Regenerating... ({attempt})"
                    )
                    if attempt >= 10:
                        logger.error("⚠️ Could not get matching fingerprint after 10 attempts. Using last one.")
                        break

                with open(path, 'wb') as fh:
                    pickle.dump(fg, fh)
                logger.info("💾 New fingerprint saved successfully.")

            if self.debug_fingerprint:
                try:
                    with open(self.debug_fingerprint_json_path, "w", encoding="utf-8") as f:
                        json.dump(asdict(fg), f, indent=2)
                    logger.info(f"🪶 Fingerprint debug JSON saved at: {self.debug_fingerprint_json_path}")
                except Exception as e:
                    logger.error(f"⚠️ Failed to save fingerprint debug JSON: {e}")

            return fg

        self.fg = fingerprintFile()

        try :
            if Browser is None:
                Browser = await AsyncCamoufox(
                    **launch_options(
                        locale=self.locale,
                        headless=self.headless,
                        humanize=True,
                        geoip=True,
                        fingerprint=self.fg,
                        enable_cache=self.enable_cache,
                        i_know_what_im_doing=True,
                        firefox_user_prefs={
                            "dom.event.clipboardevents.enabled": True,
                            "dom.allow_cut_copy": True,
                            "dom.allow_copy": True,
                            "dom.allow_paste": True,
                            "dom.events.testing.asyncClipboard": True,
                        },
                        main_world_eval=True),
                    persistent_context=True,
                    user_data_dir=self.cache_dir_path
                ).__aenter__()
        except camoufox.exceptions.InvalidIP:
            logger.info(f"Camoufox IP failed ,Trials: {tries} retrying...")
            await self.__GetBrowser__(tries=tries+1)

        return Browser

    async def CloseBrowser(self):
        """
        To close the current Browser, Invoke this for no-resource leak
        """
        if self.browser:
            try:
                for page in self.browser.pages:
                    await page.close()
                await self.browser.__aexit__(None, None, None)
            except Exception as e:
                logger.error(f"Error while closing browser: {e}", exc_info=True)

    async def getPage(self) -> Page:
        """
        Returns an available blank page if it exists, otherwise creates a new page.
        Automatically initializes the browser if not already initialized.
        """
        Browser = self.browser
        if Browser is None:
            Browser = await self.getInstance()

        for page in Browser.pages:
            try:
                if page.url == "about:blank":
                    return page
            except Exception as e:
                logger.warning(f"⚠️ Error checking page URL: {e}")

        try:
            new_page = await Browser.new_page()
            return new_page
        except Exception as e:
            logger.error(f"❌ Failed to create new page: {e}", exc_info=True)
            raise


def get_screen_size() -> Tuple[int, int]:
    """
    Returns the width and height of the primary display in pixels.
    Works on Windows, Linux, and macOS.
    """
    try:
        import platform
        system = platform.system()

        # ---------------- Windows ----------------
        if system == "Windows":
            import ctypes
            user32 = ctypes.windll.user32
            user32.SetProcessDPIAware()  # High-DPI aware
            width = user32.GetSystemMetrics(0)
            height = user32.GetSystemMetrics(1)
            return width, height

        # ---------------- Linux ----------------
        elif system == "Linux":
            try:
                import subprocess
                out = subprocess.check_output("xdpyinfo | grep dimensions", shell=True).decode()
                dims = out.split()[1].split("x")
                return int(dims[0]), int(dims[1])
            except Exception:
                pass  # fallback to Tkinter below

        # ---------------- macOS ----------------
        elif system == "Darwin":
            try:
                import Quartz
                main_display = Quartz.CGMainDisplayID()
                width = Quartz.CGDisplayPixelsWide(main_display)
                height = Quartz.CGDisplayPixelsHigh(main_display)
                return width, height
            except Exception:
                pass  # fallback to Tkinter below

    except Exception:
        pass

    # --------------- Fallback (Tkinter) ----------------
    try:
        import tkinter as tk
        root = tk.Tk()
        root.withdraw()  # hide window
        width = root.winfo_screenwidth()
        height = root.winfo_screenheight()
        root.destroy()
        return width, height
    except Exception:
        # Default fallback if everything fails
        return 1920, 1080

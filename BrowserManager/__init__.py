from typing import Optional

from browserforge.fingerprints import Fingerprint
from camoufox.async_api import launch_options, AsyncCamoufox
from playwright.async_api import BrowserContext, Page

from Shared_Resources import logger
import directory as dirs

class BrowserManager:
    """
    You can import your own BrowserForge Fingerprint
    Or let the browser itself take care of it.
    """
    def __init__(self, fingerprint: Fingerprint = None):
        self.browser: BrowserContext = None
        self.fg = fingerprint

    async def getInstance(self) -> Optional[BrowserContext]:
        """
        Gets Instance of BrowserContext
        """
        if self.browser is None:
            self.browser = await self.__GetBrowser__()
            return self.browser
        return None

    # @staticmethod
    async def __GetBrowser__(self) -> BrowserContext:
        """
        Initialises the internal BrowserContext.
        """
        Browser = self.browser

        def fingerprintFile():
            import pickle
            fg = self.fg
            if fg is None:
                path = dirs.fingerprintDir
                if path.exists():
                    print("Loading existing fingerprint from file...")
                    with open(path, 'rb') as file_handle:
                        fg = pickle.load(file_handle)
                else:
                    print("Generating and saving new fingerprint...")
                    fg = FingerprintGenerator().generate()
                    with open(path, 'wb') as file_handle:
                        pickle.dump(fg, file_handle)
        fingerprintFile()

        if Browser is None:
            Browser = await AsyncCamoufox(
                **launch_options(
                    locale="en-US",
                    headless=False,
                    humanize=True,
                    geoip=True,
                    fingerprint=fg,
                    enable_cache=True,
                    i_know_what_im_doing=True,
                    firefox_user_prefs=
                    {
                        "dom.event.clipboardevents.enabled": True,
                        "dom.allow_cut_copy": True,
                        "dom.allow_copy": True,
                        "dom.allow_paste": True,
                        "dom.events.testing.asyncClipboard": True,
                    },
                    main_world_eval=True),
                persistent_context=True,
                user_data_dir=dirs.cache_dir
            ).__aenter__()

        return Browser

    async def CloseBrowser(self):
        Browser = self.browser
        if Browser:
            try:
                for page in Browser.pages:
                    await page.close()
                await Browser.__aexit__(None, None, None)
            except Exception as e:
                logger.error(f"Error while closing browser: {e}")

    async def getPage(self)-> Page:
        Browser = self.browser
        if Browser is None: Browser = await getInstance()
        pg = Browser.pages[0]
        if pg and pg.url == "about:blank":
            pg = Browser.pages[0]
        else:
            pg = await Browser.new_page()
        pageManager.append(pg)
        return pg

from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Self
import undetected_chromedriver as uc
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from icecream import ic

BraveOptions = uc.ChromeOptions
BraveDriver = uc.Chrome

ChromeOptions = Options
ChromeDriver = webdriver.Chrome

BrowserOptions = BraveOptions | ChromeOptions   #ignore
BrowserDriver = BraveDriver | ChromeDriver  #ignore

def check_if_directory(value: str | Path) -> Path:
    """Utility function to validate and create directory"""
    if not isinstance(value, Path):
        value = Path(value)

    if not value.is_dir():
        value.mkdir(parents=True)
    return value

def check_if_brave_installed() -> Optional[Path]:
    brave = Path.home() / 'Applications/Brave Browser.app/Contents/MacOS/Brave Browser'
    if brave.exists():
        return brave
    
def driver_wait_until(wait_obj: WebDriverWait, by: By, value: str) -> None:
        return wait_obj.until(EC.element_to_be_clickable((by, value))).click()

@dataclass
class CreateWebDriver:
    download_folder: str | Path
    _headless: bool = True
    options: Optional[BrowserOptions] = None
    chrome_driver: Optional[BrowserDriver] = None
    wait: Optional[WebDriverWait] = None
    _brave: Optional[Path] = None

    def __post_init__(self):
        self.download_folder = check_if_directory(self.download_folder)
        self._brave = check_if_brave_installed()

    @property
    def headless(self) -> bool:
        return self._headless

    @headless.setter
    def headless(self, value: bool) -> None:
        self._headless = value
        self._set_options()

    def _set_options(self) -> Self:
        options = BraveOptions() if self._brave else ChromeOptions()

        if self._brave:
            ic("Brave Browser detected...")
            options.binary_location = self._brave

        if self.headless:
            options.add_argument("--headless=True")  # hide GUI
        if self.download_folder:
            _prefs = {
                'download.default_directory': str(self.download_folder),
                "download.prompt_for_download": False,
            }
            # _prefs = {'download.default_directory': str(self.download_folder)}
            options.add_experimental_option('prefs', _prefs)
        options.add_argument("--window-size=1920,1080")  # set window size to native GUI size
        options.add_argument("start-maximized")  # ensure window is full-screen
        options.page_load_strategy = "none"  # Load the page as soon as possible
        self.options = options
        return self

    def create_driver(self) -> webdriver.Chrome:
        self._set_options()
        self.chrome_driver = BraveDriver(options=self.options) if self._brave else ChromeDriver(options=self.options)
        self.wait = WebDriverWait(self.chrome_driver, 10)
        return self.chrome_driver

    def wait_until_clickable(self, by: By, value: str) -> WebDriverWait:
        driver_wait_until(self.wait, by, value)
        return self.chrome_driver

        
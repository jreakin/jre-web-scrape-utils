from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Self, Protocol
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
        wait_obj.until(EC.element_to_be_clickable((by, value))).click()

@dataclass
class BrowserConfig:
    download_folder: str | Path
    headless: bool = True
    window_size: tuple[int, int] = (1920, 1080)
    page_load_strategy: str = "none"


class Browser(Protocol):
    def create_driver(self, options, BrowserOptions) -> BrowserDriver:
        ...


class ChromeBroswer:
    def create_driver(self, options: BrowserOptions) -> ChromeDriver:
        return ChromeDriver(options=options)
    
class BraveBrowser:
    binary_location: Path = Path.home() / 'Applications/Brave Browser.app/Contents/MacOS/Brave Browser'
    def create_driver(self, options: BrowserOptions) -> BraveDriver:
        return BraveDriver(options=options)
    

@dataclass
class WebDriverBuilder:
    config: BrowserConfig
    options: BrowserOptions = field(default_factory=ChromeOptions)
    _browser: BrowserDriver = field(default_factory=ChromeDriver)

    def with_brave(self) -> Self:
        self.options = BraveOptions()
        self._browser = BraveBrowser()
        return self

    def build_options(self):
        if self.config.headless:
            self.options.add_argument("--headless=new")
        
        self.options.add_experimental_option('prefs', {
            'download.default_directory': str(self.config.download_folder),
            "download.prompt_for_download": False,
        })

        self.options.add_argument(f"--window-size={self.config.window_size[0]},{self.config.window_size[1]}")
        self.options.add_argument("start-maximized")
        self.options.page_load_strategy = self.config.page_load_strategy
        return self.options
    

@dataclass
class CreateWebDriver:
    def __init__(self, config: BrowserConfig):
        self.config = config
        self._builder = WebDriverBuilder(config)
        self.driver: Optional[BrowserDriver] = None
        self.wait: Optional[WebDriverWait] = None

    @property
    def download_folder(self) -> Path:
        return self.config.download_folder
    
    @download_folder.setter
    def download_folder(self, value: str | Path) -> None:
        self.config.download_folder = check_if_directory(value)
    
    @property
    def headless(self) -> bool:
        return self.config.headless
    
    @headless.setter
    def headless(self, value: bool) -> None:
        self.config.headless = value


    def use_brave(self) -> Self:
        self._builder.with_brave()
        return self
    
    def create(self) -> BrowserDriver:
        self._builder.build_options()
        self.driver = self._builder._browser.create_driver(self._builder.options)
        self.wait = WebDriverWait(self.driver, 10)
        return self.driver
    
    def __enter__(self) -> BrowserDriver:
        return self.create()
    
    def __exit__(self, *args) -> None:
        if self.driver:
            self.driver.quit()
    
    def wait_for_clickable(self, by: By, value: str) -> None:
        if not self.wait
            raise ValueError("WebDriverWait object not initialized")
        self.wait.until(EC.element_to_be_clickable((by, value)))

    def find_element(self, by: By, value: str) -> BrowserDriver.find_element:
        return self.driver.find_element(by, value)
    
    
        
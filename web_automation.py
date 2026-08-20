import datetime
from datetime import datetime  # Import the CLASS from the module
import os
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import WebDriverException

class WebAutomator:
    def __init__(self):
        self.driver = None
        self.wait = None

    def _ensure_driver(self):
        """Checks if the browser is open/responsive; if not, launches a new one."""
        try:
            # Check if driver exists and is responsive by requesting the current URL
            if self.driver is not None:
                _ = self.driver.current_url 
        except (WebDriverException, Exception):
            # If the browser was closed manually or crashed, reset the variable
            self.driver = None

        if self.driver is None:
            chrome_options = Options()
            chrome_options.add_experimental_option("detach", True)
            chrome_options.add_argument("--start-maximized")
            chrome_options.add_argument("--disable-notifications")
            
            # This hides the "Chrome is being controlled by automated software" bar
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)

            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.wait = WebDriverWait(self.driver, 15)

    def open_website(self, url: str):
        self._ensure_driver()
        if not url.startswith("http"):
            url = "https://" + url
        try:
            self.driver.get(url)
            return f"Opening {url}, sir."
        except Exception as e:
            return f"I could not reach the site, sir. {str(e)}"

    def google_search(self, query: str):
        self._ensure_driver()
        try:
            self.driver.get("https://www.google.com")
            search_bar = self.wait.until(EC.element_to_be_clickable((By.NAME, "q")))
            search_bar.clear()
            search_bar.send_keys(query + Keys.RETURN)
            return f"Searching Google for {query}."
        except Exception as e:
            return f"Search failed, sir. {str(e)}"

    def youtube_play(self, video_name: str):
        self._ensure_driver()
        try:
            self.driver.get(f"https://www.youtube.com/results?search_query={video_name}")
            # Target the first video link specifically
            video = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "ytd-video-renderer a#video-title")))
            video.click()
            return f"Playing {video_name} on YouTube."
        except Exception:
            return "I've navigated to YouTube, but I encountered an issue starting the video."


    def close_browser(self):
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
            self.driver = None
            return "Browser session terminated."
        return "There is no active browser to close, sir."

# Instance for brain.py
automator = WebAutomator()
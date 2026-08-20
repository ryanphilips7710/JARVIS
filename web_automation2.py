import webbrowser
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service


# ---------------- SIMPLE (webbrowser) ---------------- #

def open_url(url):
    webbrowser.open(url)


def search_youtube_simple(query):
    url = f"https://www.youtube.com/results?search_query={query}"
    webbrowser.open(url)


# ---------------- ADVANCED (selenium) ---------------- #

def start_browser():
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    driver.maximize_window()
    return driver


def search_youtube_selenium(query):
    driver = start_browser()
    driver.get("https://www.youtube.com")

    time.sleep(2)

    search_box = driver.find_element(By.NAME, "search_query")
    search_box.send_keys(query)
    search_box.send_keys(Keys.RETURN)


def open_google_meet(meet_link):
    driver = start_browser()
    driver.get(meet_link)


def fill_google_form(form_url, answers):
    """
    answers = list of answers in order of fields
    (Works for basic text fields only)
    """
    driver = start_browser()
    driver.get(form_url)

    time.sleep(3)

    inputs = driver.find_elements(By.XPATH, "//input[@type='text']")

    for i, ans in enumerate(answers):
        try:
            inputs[i].send_keys(ans)
        except:
            pass


# ---------------- EXAMPLES ---------------- #

if __name__ == "__main__":
    
    # 1. Open a website
    open_url("https://google.com")

    # 2. Search YouTube (simple)
    search_youtube_simple("spiderman movie trailer")

    # 3. Search YouTube (advanced)
    search_youtube_selenium("AI tutorials")

    # 4. Open Google Meet
    # open_google_meet("https://meet.google.com/abc-defg-hij")

    # 5. Fill Google Form
    # fill_google_form("FORM_LINK_HERE", ["Ryan", "22"])
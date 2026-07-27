import time
from datetime import date
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager


chrome_options = Options()
chrome_options.add_argument("--headless=new")
chrome_options.add_experimental_option("detach", True)
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
driver.get("https://creditcards.chase.com/rewards-credit-cards/sapphire/preferred?CELL=6TKX")


title = driver.find_element(By.XPATH, '//*[@id="sapphire-preferred"]/div/div[2]/div/div[1]/div/div[2]/h1').text
print(title)
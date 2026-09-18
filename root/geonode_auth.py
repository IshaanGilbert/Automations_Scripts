# # -*- coding: utf-8 -*-
# """
# Created on Wed Jun  4 18:08:52 2025

# @author: yoges
# """

# import time
# import random
# import json
# import multiprocessing
# from gologin import GoLogin
# from selenium import webdriver
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.common.action_chains import ActionChains
# from selenium.webdriver.common.by import By

# # Load tokens from file or hardcoded list
# try:
#     with open("config.json") as f:
#         TOKENS = json.load(f)["tokens"]
# except Exception:
#     TOKENS = [
#         "CHANGE_ME_JWT_TOKEN",
#      "CHANGE_ME_JWT_TOKEN",
#  ]

# CHROMEDRIVER_PATH = "chromedriver.exe"

# PROXY_TEMPLATE = {
#     "mode": "socks5",
#     "host": "92.204.164.15",
#     "port": 11000,
#     "username": "geonode_xvmYN44Bvz",
#     "password": "CHANGE_ME_PASSWORD"
# }

# total_runs = 10000
# batch_size = 5


# def run_profile(run_index, token):
#     print(f"\n--- Starting profile #{run_index+1} ---")

#     gl = GoLogin({"token": token})
#     try:
#         profile_id = gl.createProfileWithCustomParams({
#             "name": f"auto-profile-{run_index+1}",
#             "os": "win",
#             "navigator": {
#                 "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.5993.90 Safari/537.36",
#                 "resolution": "1920x1080",
#                 "language": "en-US",
#                 "platform": "Win64"
#             },
#             "proxyEnabled": True,
#             "proxy": PROXY_TEMPLATE
#         })

#         gl.setProfileId(profile_id)
#         debugger_address = gl.start()

#         service = Service(CHROMEDRIVER_PATH)
#         chrome_options = webdriver.ChromeOptions()
#         chrome_options.add_experimental_option("debuggerAddress", debugger_address)
#         driver = webdriver.Chrome(service=service, options=chrome_options)

#         driver.execute_script("window.open('');")
#         driver.switch_to.window(driver.window_handles[-1])
#         driver.get("https://partners.streakads.com/click?aid=27&oid=388")

#         time.sleep(5)
#         driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
#         time.sleep(2)

#         buttons = driver.find_elements(By.XPATH, "//div[@class='hmvrCard']//a[contains(text(), 'Apply Now')]")
#         if buttons:
#             chosen_button = random.choice(buttons)
#             ActionChains(driver).move_to_element(chosen_button).perform()
#             time.sleep(1)
#             chosen_button.click()
#             print("Clicked a random Apply Now button.")
#         else:
#             print("No 'Apply Now' buttons found.")

#         time.sleep(5)
#         driver.quit()

#     except Exception as e:
#         print(f"[ERROR #{run_index+1}]:", e)
#     finally:
#         try:
#             gl.stop()
#         except:
#             pass
#         print(f"Stopped profile #{run_index+1}")


# def run_batch(batch_index):
#     processes = []
#     for i in range(batch_size):
#         run_index = batch_index * batch_size + i
#         token_index = run_index // 1000 % len(TOKENS)
#         token = TOKENS[token_index]
#         p = multiprocessing.Process(target=run_profile, args=(run_index, token))
#         processes.append(p)
#         p.start()

#     for p in processes:
#         p.join()


# if __name__ == '__main__':
#     total_batches = total_runs // batch_size
#     for batch_index in range(total_batches):
#         print(f"\n=== Running Batch {batch_index+1}/{total_batches} ===")
#         run_batch(batch_index)

#     print("\n✅ All profile runs completed.")



# -*- coding: utf-8 -*-
"""
Created on Wed Jun  4 18:08:52 2025

@author: yoges
"""

import time
import random
import json
import multiprocessing
import requests
from gologin import GoLogin
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By

# Load tokens from file or hardcoded list
try:
    with open("config.json") as f:
        TOKENS = json.load(f)["tokens"]
except Exception:
    TOKENS = [
        "your_new_token_here"
    ]

CHROMEDRIVER_PATH = "D:\\streakads\\chromedriver.exe"

PROXY_TEMPLATE = {
    "mode": "socks5",
    "host": "92.204.164.15",
    "port": 11000,
    "username": "geonode_xvmYN44Bvz",
    "password": "CHANGE_ME_PASSWORD"
}

total_runs = 10000
batch_size = 2  # Reduced batch size

def test_proxy(proxy):
    try:
        proxies = {
            "http": f"socks5://{proxy['username']}:{proxy['password']}@{proxy['host']}:{proxy['port']}",
            "https": f"socks5://{proxy['username']}:{proxy['password']}@{proxy['host']}:{proxy['port']}"
        }
        response = requests.get("http://ip-api.com/json", proxies=proxies, timeout=10)
        if response.status_code == 200 and response.json().get("countryCode") == "IN":
            print("Proxy working, IP is Indian.")
            return True
        else:
            print("Proxy not working or not Indian IP.")
            return False
    except Exception as e:
        print(f"Proxy test failed: {e}")
        return False

def run_profile(run_index, token):
    print(f"\n--- Starting profile #{run_index+1} ---")
    gl = GoLogin({
        "token": token,
        "port": random.randint(10000, 20000)
    })
    try:
        if not test_proxy(PROXY_TEMPLATE):
            print("Proxy failed, skipping profile.")
            return

        profile_id = gl.createProfileWithCustomParams({
            "name": f"auto-profile-{run_index+1}",
            "os": "android",
            "navigator": {
                "userAgent": "Mozilla/5.0 (Linux; Android 10; SM-G960F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.5993.90 Mobile Safari/537.36",
                "resolution": "360x640",
                "language": "en-US",
                "platform": "Linux armv8l"
            },
            "proxyEnabled": True,
            "proxy": PROXY_TEMPLATE
        })

        gl.setProfileId(profile_id)
        debugger_address = gl.start()

        service = Service(CHROMEDRIVER_PATH)
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_experimental_option("debuggerAddress", debugger_address)
        driver = webdriver.Chrome(service=service, options=chrome_options)

        driver.execute_script("window.open('');")
        driver.switch_to.window(driver.window_handles[-1])
        driver.get("https://partners.streakads.com/click?aid=27&oid=388")

        time.sleep(5)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)

        buttons = driver.find_elements(By.XPATH, "//div[@class='hmvrCard']//a[contains(text(), 'Apply Now')]")
        if buttons:
            chosen_button = random.choice(buttons)
            ActionChains(driver).move_to_element(chosen_button).perform()
            time.sleep(1)
            chosen_button.click()
            print("Clicked a random Apply Now button.")
        else:
            print("No 'Apply Now' buttons found.")

        time.sleep(5)
        driver.quit()

    except Exception as e:
        print(f"[ERROR #{run_index+1}]: {e}")
    finally:
        try:
            gl.stop()
        except:
            pass
        print(f"Stopped profile #{run_index+1}")

def run_batch(batch_index):
    processes = []
    for i in range(batch_size):
        run_index = batch_index * batch_size + i
        token_index = run_index // 1000 % len(TOKENS)
        token = TOKENS[token_index]
        p = multiprocessing.Process(target=run_profile, args=(run_index, token))
        processes.append(p)
        p.start()

    for p in processes:
        p.join()

if __name__ == '__main__':
    total_batches = total_runs // batch_size
    for batch_index in range(total_batches):
        print(f"\n=== Running Batch {batch_index+1}/{total_batches} ===")
        run_batch(batch_index)

    print("\n✅ All profile runs completed.")
import time
import random
import json
import multiprocessing
from gologin import GoLogin
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Load tokens from file or fallback
try:
    with open("config.json") as f:
        TOKENS = json.load(f)["tokens"]
except Exception:
    TOKENS = [
        "CHANGE_ME_JWT_TOKEN"
    ]

CHROMEDRIVER_PATH = "chromedriver.exe"

PROXY_TEMPLATE = {
    "mode": "socks5",
    "host": "sg.proxy.geonode.io",
    "port": 11000,
    "username": "geonode_xvmYN44Bvz-type-residential-country-in",
    "password": "CHANGE_ME_PASSWORD"
}

# Total profiles to run
total_runs = 1 # <-- change this number as needed
batch_size = 1   # number of processes to run in parallel


def run_profile(run_index, token):
    print(f"\n--- Starting profile #{run_index+1} ---")

    gl = GoLogin({"token": token})
    try:
        profile_id = gl.createProfileWithCustomParams({
            "name": f"auto-shweta-{run_index+1}",
            "os": "android",
            "navigator": {
                "userAgent": "Mozilla/5.0 (Linux; Android 13; Pixel 7 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.5993.90 Mobile Safari/537.36",
                "resolution": "412x915",
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

        # Open target URL
        driver.get("https://bigbillionwall.com/")
        time.sleep(10)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)

        # Click "Start Searching" button
        try:
            wait = WebDriverWait(driver, 30)
            start_btn = wait.until(
                EC.element_to_be_clickable((By.XPATH, '//a[@class="btn-main" and .//span[text()="Start Searching"]]'))
            )
            start_btn.click()
            print("[+] Clicked 'Start Searching' button.")
        except Exception as e:
            print("[!] Start Searching button not found or not clickable:", e)

        # Wait 60 seconds before closing
        time.sleep(10)
        driver.quit()

    except Exception as e:
        print(f"[ERROR #{run_index+1}]:", e)
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
        if run_index >= total_runs:
            break
        token_index = run_index // 1000 % len(TOKENS)
        token = TOKENS[token_index]
        p = multiprocessing.Process(target=run_profile, args=(run_index, token))
        processes.append(p)
        p.start()

    for p in processes:
        p.join()


if __name__ == '__main__':
    total_batches = (total_runs + batch_size - 1) // batch_size
    for batch_index in range(total_batches):
        print(f"\n=== Running Batch {batch_index+1}/{total_batches} ===")
        run_batch(batch_index)

    print("\n✅ All profile runs completed.")
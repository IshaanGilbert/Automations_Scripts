import os
import json
import time
import random
import hashlib
import datetime
import  logging
import requests
import threading
import tkinter as tk
from queue import Queue
from tkinter import messagebox
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException, TimeoutException
from selenium.common.exceptions import WebDriverException, TimeoutException



logging.basicConfig(
    filename="error_log.txt",  
    level=logging.ERROR,  
    format="%(asctime)s - %(levelname)s - %(message)s",  
    datefmt="%Y-%m-%d %H:%M:%S",  
)
with open('config.json', 'r') as config_file:
    config = json.load(config_file)

TARGET_URL = config.get('target_urls')
# IFRAME_XPATH = config.get('iframe_xpath')
BUTTON_XPATH = config.get('button_xpath')
visits = 0
app_start_time = time.time()
task_queue = Queue()
allow_task_run = False
task_lock = threading.Lock()
visit_times = []

def scheduler(start_times, end_times):

    global allow_task_run
    while True:
        now = datetime.datetime.now().time()
        with task_lock:
            allow_task_run = any(start <= now < end for start, end in zip(start_times, end_times))
        time.sleep(5)

class WebTaskGUI:

    def __init__(self, root):
        self.root = root
        self.root.title("Web Task Automation")
        self.root.geometry("500x400")
        padding = {'padx': 10, 'pady': 5}

        self.start_times = []
        self.end_times = []

        for i in range(3):
            start_label = tk.Label(root, text=f"Start Time {i+1} (HH:MM):")
            start_label.grid(row=i, column=0, sticky="w", **padding)
            start_entry = tk.Entry(root, width=10)
            start_entry.grid(row=i, column=1, **padding)
            self.start_times.append(start_entry)

            end_label = tk.Label(root, text=f"End Time {i+1} (HH:MM):")
            end_label.grid(row=i, column=2, sticky="w", **padding)
            end_entry = tk.Entry(root, width=10)
            end_entry.grid(row=i, column=3, **padding)
            self.end_times.append(end_entry)

        self.min_delay_label = tk.Label(root, text="Min Delay (seconds):")
        self.min_delay_label.grid(row=6, column=0, sticky="w", **padding)
        self.min_delay_entry = tk.Entry(root, width=10)
        self.min_delay_entry.grid(row=6, column=1, **padding)
        self.min_delay_entry.insert(0, "45")

        self.max_delay_label = tk.Label(root, text="Max Delay (seconds):")
        self.max_delay_label.grid(row=6, column=2, sticky="w", **padding)
        self.max_delay_entry = tk.Entry(root, width=10)
        self.max_delay_entry.grid(row=6, column=3, **padding)
        self.max_delay_entry.insert(0, "60")

        self.num_browsers_label = tk.Label(root, text="Number of Browsers:")
        self.num_browsers_label.grid(row=7, column=0, sticky="w", **padding)
        self.num_browsers_entry = tk.Entry(root, width=10)
        self.num_browsers_entry.grid(row=7, column=1, **padding)
        self.num_browsers_entry.insert(0, "1")

        self.status_label = tk.Label(root, text="Status: Ready", fg="blue")
        self.status_label.grid(row=10, columnspan=4, pady=5)

        self.run_button = tk.Button(root, text="Run Task", command=self.run_task)
        self.run_button.grid(row=11, columnspan=4, pady=10)

    def update_status(self, status):
        self.status_label.config(text=f"Status: {status}")

    def update_task_count(self, visit_count):
        self.status_label.config(text=f"Visit Count: {visit_count}")

    def run_task(self):

        try:
            start_times = []
            end_times = []
            for i in range(3):
                start_time_str = self.start_times[i].get()
                end_time_str = self.end_times[i].get()
                if start_time_str and end_time_str:
                    start_time = datetime.datetime.strptime(start_time_str, "%H:%M").time()
                    end_time = datetime.datetime.strptime(end_time_str, "%H:%M").time()
                    start_times.append(start_time)
                    end_times.append(end_time)
                elif not start_time_str and not end_time_str:
                    continue
                else:
                    raise ValueError("Both start and end times must be provided or left empty.")

            if not start_times or not end_times:
                raise ValueError("At least one set of start and end times must be provided.")

            min_delay = int(self.min_delay_entry.get()) if self.min_delay_entry.get() else 45
            max_delay = int(self.max_delay_entry.get()) if self.max_delay_entry.get() else 60
            if min_delay <= 0 or max_delay <= 0:
                raise ValueError("Delay values must be greater than zero.")
            if min_delay > max_delay:
                raise ValueError("Max Delay value must be greater than Min Delay.")

            num_browsers = int(self.num_browsers_entry.get())

            if num_browsers <= 0:
                raise ValueError("Number of browsers must be at least 1.")
           
            scheduler_thread = threading.Thread(target=scheduler, args=(start_times, end_times), daemon=True)
            scheduler_thread.start()

            def web_task_thread(browser_id):

                global allow_task_run
                while True:
                    if allow_task_run:
                        self.update_status(f"Running browser {browser_id}...")
                        # change_ip()
                        driver = init_browser()
                        navigate_and_click(driver, task_queue)
                        driver.quit()

                    else:
                        self.update_status(f"Paused browser {browser_id}...")
                    time.sleep(5)

            threads = []
            for i in range(num_browsers):
                t = threading.Thread(target=web_task_thread, args=(i + 1,))
                threads.append(t)
                t.start()

        except ValueError as e:
            messagebox.showerror("Input Error", f"Invalid input values: {str(e)}")


def generate_fingerprinting():

    device_os_mapping = {
    "desktop": ["Windows", "macOS", "Linux", "Fedora"],
    "laptop": ["Windows", "macOS", "Linux", "ChromeOS", "Fedora"],
    "ultrabook": ["Windows", "macOS", "Linux", "Fedora"],
    "macbook": ["macOS"],
    "chromebook": ["ChromeOS"],
    "smartphone": ["Windows", "Android", "iOS"],
    "android_phone": ["Android"],
    "iphone": ["iOS"],
    "tablet": ["Android", "iOS"],
    "ipad": ["iPadOS"],
    "android_tablet": ["Android"],
    "smart_tv": ["Android TV", "Tizen", "WebOS"],
    }

    user_agents = {
    "Windows": [
        "Mozilla/5.0 (Windows NT {0}.{1}; Win64; x64) AppleWebKit/{2}.36 (KHTML, like Gecko) Chrome/{3}.0.{4}.0 Safari/{2}.36",
        "Mozilla/5.0 (Windows NT {0}.{1}; Win64; x64) AppleWebKit/{2}.36 (KHTML, like Gecko) Edg/{3}.0.{4}.0 Safari/{2}.36",
        "Mozilla/5.0 (Windows NT {0}.{1}; Win64; x64) AppleWebKit/{2}.36 (KHTML, like Gecko) OPR/{3}.0.{4}.0 Safari/{2}.36",
        "Mozilla/5.0 (Windows NT {0}.{1}; Win64; x64) AppleWebKit/{2}.36 (KHTML, like Gecko) Brave/{3}.0.{4}.0 Safari/{2}.36",
        "Mozilla/5.0 (Windows NT {0}.{1}; Win64; x64) AppleWebKit/{2}.36 (KHTML, like Gecko) Vivaldi/{3}.0.{4}.0 Safari/{2}.36",
        "Mozilla/5.0 (Windows NT {0}.{1}; Win64; x64) AppleWebKit/{2}.36 (KHTML, like Gecko) Edge/{3}.0.{4}.0 Safari/{2}.36",
        "Mozilla/5.0 (Windows NT {0}.{1}; Win64; x64) AppleWebKit/{2}.36 (KHTML, like Gecko) FxiOS/{3}.0.{4}.0 Safari/{2}.36",
        "Mozilla/5.0 (Windows NT {0}.{1}; Win64; x64) AppleWebKit/{2}.36 (KHTML, like Gecko) Midori/{3}.0.{4}.0 Safari/{2}.36",
        "Mozilla/5.0 (Windows NT {0}.{1}; Win64; x64) AppleWebKit/{2}.36 (KHTML, like Gecko) Falkon/{3}.0.{4}.0 Safari/{2}.36",
        "Mozilla/5.0 (Windows NT {0}.{1}; Win64; x64) AppleWebKit/{2}.36 (KHTML, like Gecko) Opera/{3}.0.{4}.0 Safari/{2}.36",
        "Mozilla/5.0 (Windows NT {0}.{1}; Win64; x64) AppleWebKit/{2}.36 (KHTML, like Gecko) Safari/{3}.0.0.0",
        "Mozilla/5.0 (Windows NT {0}.{1}; Win64; x64) AppleWebKit/{2}.36 (KHTML, like Gecko) Chrome/{3}.0.{4}.0 Safari/{2}.36"
    ],
    "Fedora": [
        "Mozilla/5.0 (X11; Fedora; Linux x86_64) AppleWebKit/{2}.36 (KHTML, like Gecko) Chrome/{3}.0.{4}.0 Safari/{2}.36",
        "Mozilla/5.0 (X11; Fedora; Linux x86_64) AppleWebKit/{2}.36 (KHTML, like Gecko) Edge/{3}.0.{4}.0 Safari/{2}.36",
        "Mozilla/5.0 (X11; Fedora; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36",
        "Mozilla/5.0 (X11; Fedora; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/89.0",
        "Mozilla/5.0 (X11; Fedora; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Opera/76.0.4017.154 Safari/537.36",
        "Mozilla/5.0 (X11; Fedora; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Brave/1.26.74 Safari/537.36",
        "Mozilla/5.0 (X11; Fedora; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Vivaldi/4.2.2406.44 Safari/537.36",
        "Mozilla/5.0 (X11; Fedora; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Konqueror/5.0.97 Safari/537.36",
        "Mozilla/5.0 (X11; Fedora; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Epiphany/40.1 Safari/537.36"
    ],
    "iPadOS": [
        "Mozilla/5.0 (iPad; CPU OS {0}_{1} like Mac OS X) AppleWebKit/{2}.36 (KHTML, like Gecko) CriOS/{3}.0.{4}.0 Mobile/{4} Safari/{2}.36",
        "Mozilla/5.0 (iPad; CPU OS {0}_{1} like Mac OS X) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36",
        "Mozilla/5.0 (iPad; CPU OS {0}_{1} like Mac OS X) AppleWebKit/537.36 (KHTML, like Gecko) Safari/537.36",
        "Mozilla/5.0 (iPad; CPU OS {0}_{1} like Mac OS X) AppleWebKit/537.36 (KHTML, like Gecko) Edge/91.0.864.59 Safari/537.36",
        "Mozilla/5.0 (iPad; CPU OS {0}_{1} like Mac OS X) AppleWebKit/537.36 (KHTML, like Gecko) Opera/73.0.3856.257 Safari/537.36",
        "Mozilla/5.0 (iPad; CPU OS {0}_{1} like Mac OS X) AppleWebKit/537.36 (KHTML, like Gecko) Vivaldi/4.2.2406.44 Safari/537.36",
        "Mozilla/5.0 (iPad; CPU OS {0}_{1} like Mac OS X) AppleWebKit/537.36 (KHTML, like Gecko) Brave/1.31.87 Safari/537.36",
        "Mozilla/5.0 (iPad; CPU OS {0}_{1} like Mac OS X) AppleWebKit/537.36 (KHTML, like Gecko) UC Browser/13.4.0.1307 Safari/537.36"
    ],
    "macOS": [
        "Mozilla/5.0 (Macintosh; Intel Mac OS X {0}_{1}) AppleWebKit/{2}.36 (KHTML, like Gecko) Chrome/{3}.0.{4}.0 Safari/{2}.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X {0}_{1}) AppleWebKit/{2}.36 (KHTML, like Gecko) Edg/{3}.0.{4}.0 Safari/{2}.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X {0}_{1}) AppleWebKit/{2}.36 (KHTML, like Gecko) OPR/{3}.0.{4}.0 Safari/{2}.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X {0}_{1}) AppleWebKit/{2}.36 (KHTML, like Gecko) Brave/{3}.0.{4}.0 Safari/{2}.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X {0}_{1}) AppleWebKit/{2}.36 (KHTML, like Gecko) Vivaldi/{3}.0.{4}.0 Safari/{2}.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X {0}_{1}) AppleWebKit/{2}.36 (KHTML, like Gecko) Safari/{3}.0.0.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X {0}_{1}) AppleWebKit/{2}.36 (KHTML, like Gecko) FxiOS/{3}.0.{4}.0 Safari/{2}.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X {0}_{1}) AppleWebKit/{2}.36 (KHTML, like Gecko) Chrome/{3}.0.{4}.0 Safari/{2}.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X {0}_{1}) AppleWebKit/{2}.36 (KHTML, like Gecko) Microsoft Edge/{3}.0.{4}.0 Safari/{2}.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X {0}_{1}) AppleWebKit/{2}.36 (KHTML, like Gecko) FxiOS/{3}.0.{4}.0 Safari/{2}.36"
    ],
    "Linux": [ 
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/{2}.36 (KHTML, like Gecko) Chrome/{3}.0.{4}.0 Safari/{2}.36",
        "Mozilla/5.0 (X11; Ubuntu; Linux x86_64) AppleWebKit/{2}.36 (KHTML, like Gecko) Chrome/{3}.0.{4}.0 Safari/{2}.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/{2}.36 (KHTML, like Gecko) OPR/{3}.0.{4}.0 Safari/{2}.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/{2}.36 (KHTML, like Gecko) Edg/{3}.0.{4}.0 Safari/{2}.36",
        "Mozilla/5.0 (X11; Ubuntu; Linux x86_64) AppleWebKit/{2}.36 (KHTML, like Gecko) Brave/{3}.0.{4}.0 Safari/{2}.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/{2}.36 (KHTML, like Gecko) Vivaldi/{3}.0.{4}.0 Safari/{2}.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/{2}.36 (KHTML, like Gecko) Falkon/{3}.0.{4}.0 Safari/{2}.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/{2}.36 (KHTML, like Gecko) Midori/{3}.0.{4}.0 Safari/{2}.36",
        "Mozilla/5.0 (X11; Fedora; Linux x86_64) AppleWebKit/{2}.36 (KHTML, like Gecko) Chrome/{3}.0.{4}.0 Safari/{2}.36",
        "Mozilla/5.0 (X11; Arch Linux x86_64) AppleWebKit/{2}.36 (KHTML, like Gecko) Chrome/{3}.0.{4}.0 Safari/{2}.36",
        "Mozilla/5.0 (X11; Manjaro Linux x86_64) AppleWebKit/{2}.36 (KHTML, like Gecko) Chrome/{3}.0.{4}.0 Safari/{2}.36"
    ],
    "Android": [
        "Mozilla/5.0 (Linux; Android {0}.{1}) AppleWebKit/{2}.36 (KHTML, like Gecko) Chrome/{3}.0.{4}.0 Mobile Safari/{2}.36",
        "Mozilla/5.0 (Linux; Android {0}.{1}) AppleWebKit/{2}.36 (KHTML, like Gecko) OPR/{3}.0.{4}.0 Mobile Safari/{2}.36",
        "Mozilla/5.0 (Linux; Android {0}.{1}) AppleWebKit/{2}.36 (KHTML, like Gecko) EdgA/{3}.0.{4}.0 Mobile Safari/{2}.36",
        "Mozilla/5.0 (Linux; Android {0}.{1}) AppleWebKit/{2}.36 (KHTML, like Gecko) FxiOS/{3}.0.{4}.0 Mobile Safari/{2}.36",
        "Mozilla/5.0 (Linux; Android {0}.{1}) AppleWebKit/{2}.36 (KHTML, like Gecko) SamsungBrowser/{3}.0.{4}.0 Mobile Safari/{2}.36",
        "Mozilla/5.0 (Linux; Android {0}.{1}) AppleWebKit/{2}.36 (KHTML, like Gecko) DuckDuckGo/{3}.0.{4}.0 Mobile Safari/{2}.36",
        "Mozilla/5.0 (Linux; Android {0}.{1}) AppleWebKit/{2}.36 (KHTML, like Gecko) Brave/{3}.0.{4}.0 Mobile Safari/{2}.36"
    ],
    "iOS": [
        "Mozilla/5.0 (iPhone; CPU iPhone OS {0}_{1} like Mac OS X) AppleWebKit/{2}.36 (KHTML, like Gecko) CriOS/{3}.0.{4}.0 Mobile/{4} Safari/{2}.36",
        "Mozilla/5.0 (iPhone; CPU iPhone OS {0}_{1} like Mac OS X) AppleWebKit/{2}.36 (KHTML, like Gecko) OPR/{3}.0.{4}.0 Mobile/{4} Safari/{2}.36",
        "Mozilla/5.0 (iPhone; CPU iPhone OS {0}_{1} like Mac OS X) AppleWebKit/{2}.36 (KHTML, like Gecko) EdgiOS/{3}.0.{4}.0 Mobile/{4} Safari/{2}.36",
        "Mozilla/5.0 (iPhone; CPU iPhone OS {0}_{1} like Mac OS X) AppleWebKit/{2}.36 (KHTML, like Gecko) Brave/{3}.0.{4}.0 Mobile/{4} Safari/{2}.36",
        "Mozilla/5.0 (iPhone; CPU iPhone OS {0}_{1} like Mac OS X) AppleWebKit/{2}.36 (KHTML, like Gecko) DuckDuckGo/{3}.0.{4}.0 Mobile/{4} Safari/{2}.36",
        "Mozilla/5.0 (iPhone; CPU iPhone OS {0}_{1} like Mac OS X) AppleWebKit/{2}.36 (KHTML, like Gecko) SamsungBrowser/{3}.0.{4}.0 Mobile/{4} Safari/{2}.36",
        "Mozilla/5.0 (iPad; CPU OS {0}_{1} like Mac OS X) AppleWebKit/{2}.36 (KHTML, like Gecko) CriOS/{3}.0.{4}.0 Mobile/{4} Safari/{2}.36",
        "Mozilla/5.0 (iPad; CPU OS {0}_{1} like Mac OS X) AppleWebKit/{2}.36 (KHTML, like Gecko) OPR/{3}.0.{4}.0 Mobile/{4} Safari/{2}.36",
        "Mozilla/5.0 (iPad; CPU OS {0}_{1} like Mac OS X) AppleWebKit/{2}.36 (KHTML, like Gecko) EdgiOS/{3}.0.{4}.0 Mobile/{4} Safari/{2}.36"
    ],
    "ChromeOS": [
        "Mozilla/5.0 (X11; CrOS x86_64 {0}.{1}) AppleWebKit/{2}.36 (KHTML, like Gecko) Chrome/{3}.0.{4}.0 Safari/{2}.36",
        "Mozilla/5.0 (X11; CrOS x86_64 {0}.{1}) AppleWebKit/{2}.36 (KHTML, like Gecko) Edg/{3}.0.{4}.0 Safari/{2}.36",
        "Mozilla/5.0 (X11; CrOS x86_64 {0}.{1}) AppleWebKit/{2}.36 (KHTML, like Gecko) OPR/{3}.0.{4}.0 Safari/{2}.36",
        "Mozilla/5.0 (X11; CrOS x86_64 {0}.{1}) AppleWebKit/{2}.36 (KHTML, like Gecko) SamsungBrowser/{3}.0.{4}.0 Safari/{2}.36",
        "Mozilla/5.0 (X11; CrOS x86_64 {0}.{1}) AppleWebKit/{2}.36 (KHTML, like Gecko) Brave/{3}.0.{4}.0 Safari/{2}.36",
        "Mozilla/5.0 (X11; CrOS armv7l {0}.{1}) AppleWebKit/{2}.36 (KHTML, like Gecko) Chrome/{3}.0.{4}.0 Safari/{2}.36",
        "Mozilla/5.0 (X11; CrOS x86_64 {0}.{1}; Google Pixelbook) AppleWebKit/{2}.36 (KHTML, like Gecko) Chrome/{3}.0.{4}.0 Safari/{2}.36",
        "Mozilla/5.0 (X11; CrOS x86_64 {0}.{1}; ASUS Chromebook) AppleWebKit/{2}.36 (KHTML, like Gecko) Chrome/{3}.0.{4}.0 Safari/{2}.36",
        "Mozilla/5.0 (X11; CrOS x86_64 {0}.{1}; Acer Chromebook Spin) AppleWebKit/{2}.36 (KHTML, like Gecko) Chrome/{3}.0.{4}.0 Safari/{2}.36",
        "Mozilla/5.0 (X11; CrOS x86_64 {0}.{1}; Samsung Chromebook) AppleWebKit/{2}.36 (KHTML, like Gecko) Chrome/{3}.0.{4}.0 Safari/{2}.36"
    ],
    "Tizen": [
        "Mozilla/5.0 (SMART-TV; Linux; Tizen {0}.{1}) AppleWebKit/{2}.36 (KHTML, like Gecko) Chrome/{3}.0.{4}.0 Safari/{2}.36",
        "Mozilla/5.0 (SMART-TV; Tizen {0}.{1}) AppleWebKit/{2}.36 (KHTML, like Gecko) SamsungBrowser/{3}.0.{4}.0 Safari/{2}.36",
        "Mozilla/5.0 (SMART-TV; Linux; Tizen {0}.{1}) AppleWebKit/{2}.36 (KHTML, like Gecko) Edg/{3}.0.{4}.0 Safari/{2}.36",
        "Mozilla/5.0 (SMART-TV; Linux; Tizen {0}.{1}) AppleWebKit/{2}.36 (KHTML, like Gecko) OPR/{3}.0.{4}.0 Safari/{2}.36",
        "Mozilla/5.0 (SMART-TV; Linux; Tizen {0}.{1}) AppleWebKit/{2}.36 (KHTML, like Gecko) FxiOS/{3}.0.{4}.0 Safari/{2}.36",
        "Mozilla/5.0 (SMART-TV; Linux; Tizen {0}.{1}; Samsung SmartTV) AppleWebKit/{2}.36 (KHTML, like Gecko) Chrome/{3}.0.{4}.0 Safari/{2}.36",
        "Mozilla/5.0 (SMART-TV; Linux; Tizen {0}.{1}; Samsung 4K UHD) AppleWebKit/{2}.36 (KHTML, like Gecko) SamsungBrowser/{3}.0.{4}.0 Safari/{2}.36",
    ],    
    "Android TV": [
                "Mozilla/5.0 (Linux; Android {0}.{1}; Android TV) AppleWebKit/{2}.36 (KHTML, like Gecko) Chrome/{3}.0.0.0 Safari/{2}.36",
                "Mozilla/5.0 (Linux; Android {0}.{1}; Nexus Player) AppleWebKit/{2}.36 (KHTML, like Gecko) Chrome/{3}.0.0.0 Safari/{2}.36",
                "Mozilla/5.0 (Linux; Android {0}.{1}; MiTV) AppleWebKit/{2}.36 (KHTML, like Gecko) Chrome/{3}.0.0.0 Safari/{2}.36",
                "Mozilla/5.0 (Linux; Android {0}.{1}; SHIELD Android TV) AppleWebKit/{2}.36 (KHTML, like Gecko) Chrome/{3}.0.0.0 Safari/{2}.36",
                "Mozilla/5.0 (Linux; Android {0}.{1}; Sony BRAVIA 4K GB) AppleWebKit/{2}.36 (KHTML, like Gecko) Chrome/{3}.0.0.0 Safari/{2}.36",
                "Mozilla/5.0 (Linux; Android {0}.{1}; Samsung SmartTV) AppleWebKit/{2}.36 (KHTML, like Gecko) Chrome/{3}.0.0.0 Safari/{2}.36",
                "Mozilla/5.0 (Linux; Android {0}.{1}; Android TV) AppleWebKit/{2}.36 (KHTML, like Gecko) Edg/{3}.0.0.0 Safari/{2}.36",
                "Mozilla/5.0 (Linux; Android {0}.{1}; Android TV) AppleWebKit/{2}.36 (KHTML, like Gecko) OPR/{3}.0.0.0 Safari/{2}.36",
                "Mozilla/5.0 (Linux; Android {0}.{1}; Android TV) AppleWebKit/{2}.36 (KHTML, like Gecko) FxiOS/{3}.0.0.0 Safari/{2}.36",
                "Mozilla/5.0 (Linux; Android {0}.{1}; Android TV) AppleWebKit/{2}.36 (KHTML, like Gecko) SamsungBrowser/{3}.0.0.0 Safari/{2}.36"
    ],
    "WebOS": [  
        "Mozilla/5.0 (Linux; WebOS/{0}.{1}) AppleWebKit/{2}.36 (KHTML, like Gecko) Chrome/{3}.0.{4}.0 Safari/{2}.36",
        "Mozilla/5.0 (Linux; WebOS/{0}.{1}) AppleWebKit/{2}.36 (KHTML, like Gecko) Firefox/{3}.0.{4}.0 Safari/{2}.36",
        "Mozilla/5.0 (Linux; WebOS/{0}.{1}) AppleWebKit/{2}.36 (KHTML, like Gecko) Version/{3}.1 Safari/{2}.36",
        "Mozilla/5.0 (Linux; WebOS/{0}.{1}) AppleWebKit/{2}.36 (KHTML, like Gecko) WebView/{3}.0 Safari/{2}.36",
        "Mozilla/5.0 (Linux; WebOS/{0}.{1}) AppleWebKit/{2}.36 (KHTML, like Gecko) Opera/{3}.0.{4}.0 Safari/{2}.36",
        "Mozilla/5.0 (Linux; WebOS/{0}.{1}) AppleWebKit/{2}.36 (KHTML, like Gecko) Edge/{3}.0.{4}.0 Safari/{2}.36",
        "Mozilla/5.0 (Linux; WebOS/{0}.{1}) AppleWebKit/{2}.36 (KHTML, like Gecko) Brave/{3}.0.{4}.0 Safari/{2}.36",
        "Mozilla/5.0 (Linux; WebOS/{0}.{1}) AppleWebKit/{2}.36 (KHTML, like Gecko) Vivaldi/{3}.0.{4}.0 Safari/{2}.36",
        "Mozilla/5.0 (Linux; WebOS/{0}.{1}) AppleWebKit/{2}.36 (KHTML, like Gecko) SamsungBrowser/{3}.0 Safari/{2}.36",
        "Mozilla/5.0 (Linux; WebOS/{0}.{1}) AppleWebKit/{2}.36 (KHTML, like Gecko) Midori/{3}.0.{4}.0 Safari/{2}.36",
        "Mozilla/5.0 (Linux; WebOS/{0}.{1}) AppleWebKit/{2}.36 (KHTML, like Gecko) Falkon/{3}.0.{4}.0 Safari/{2}.36",
        "Mozilla/5.0 (Linux; WebOS/{0}.{1}) AppleWebKit/{2}.36 (KHTML, like Gecko) FxiOS/{3}.0 Safari/{2}.36",
    ],      
        }

    
    device_type = random.choice(list(device_os_mapping.keys()))
    os = random.choice(device_os_mapping[device_type]) 
    version_main = random.randint(8, 14)
    version_minor = random.randint(0, 3)
    webkit_version = random.randint(500, 600)
    chrome_version = random.randint(90, 120)
    firefox_version = random.randint(10, 90)
    build_version = random.randint(1000, 5000)
    user_agent = random.choice(user_agents[os]).format(
    version_main, version_minor, webkit_version, chrome_version, firefox_version, build_version
    )
    screen_widths = [1024, 1366, 1920, 2560, 3840]
    screen_heights = [768, 800, 1080, 1200, 1600]
    device_pixel_ratio = [1, 1.25, 1.5, 2, 2.5, 3]
    webgl_renderer = ["ANGLE (NVIDIA)", "Intel(R) UHD Graphics", "AMD Radeon RX"]
    webgl_vendor = ["Google Inc.", "Intel Inc.", "NVIDIA Corporation"]
    timezone = ["UTC", "America/New_York", "Europe/Berlin", "Asia/Tokyo"]
    plugin_list = [
        ["Chrome PDF Viewer", "Widevine Content Decryption Module"],
        ["PDF.js", "Shockwave Flash"],
        ["Java", "Silverlight"]
    ]
    installed_fonts = [
        ["Arial", "Verdana", "Times New Roman"],
        ["Roboto", "Lato", "Montserrat"],
        ["Comic Sans MS", "Courier New"]
    ]
    accept_language = [
        "en-US,en;q=0.9", "fr-FR,fr;q=0.8", "de-DE,de;q=0.9", "es-ES,es;q=0.8"
    ]
    navigator_platform = ["Win32", "Linux x86_64", "MacIntel"]
    speech_synthesis_voices = [
        ["Google UK English Male", "Microsoft Zira"],
        ["Google Deutsch", "Apple Samantha"],
        ["Google Español", "Microsoft David"]
    ]
    def generate_random_webgl():
        random_string = "".join(random.choices("abcdef0123456789", k=32))
        return hashlib.sha256(random_string.encode()).hexdigest()[:32]  
    def generate_random_canvas():
        random_string = "".join(random.choices("abcdef0123456789", k=32))
        return hashlib.sha256(random_string.encode()).hexdigest()[:32]  

    return {
        "device_type": device_type,
        "os": os,
        "user_agent": user_agent,
        "screen_width": random.choice(screen_widths),
        "screen_height": random.choice(screen_heights),
        "device_pixel_ratio": random.choice(device_pixel_ratio),
        "webgl_disabled": random.choice([True, False]),
        "webgl_renderer": random.choice(webgl_renderer),
        "webgl_vendor": random.choice(webgl_vendor),
        "peer_connection_disabled": random.choice([True, False]),
        "resist_fingerprinting": random.choice([True, False]),
        "language": random.choice(["en-US", "en-GB", "es-ES", "fr-FR", "de-DE", "it-IT", "pt-PT", "ru-RU", "zh-CN", "ja-JP", "ko-KR", "ar-SA"]),
        "timezone_offset": random.choice([0, -180, -240, 180, 360]),
        "timezone": random.choice(timezone),
        "plugins": random.choice([True, False]),
        "plugin_list": random.choice(plugin_list),
        "fonts": random.choice([True, False]),
        "installed_fonts": random.choice(installed_fonts),
        "hardware_concurrency": random.choice([2, 4, 8, 12, 16]),
        "device_memory": random.choice([2, 4, 8, 16, 32]),
        "screen_orientation": random.choice(["portrait", "landscape"]),
        "accept_language": random.choice(accept_language),
        "audio_fingerprint": random.choice(["audio1", "audio2", "audio3"]),
        "gpu_fingerprint": random.choice(["gpu1", "gpu2", "gpu3"]),
        "navigator_platform": random.choice(navigator_platform),
        "do_not_track": random.choice(["1", "0", None]),
        "math_tan_pi": random.choice([3.14159265358979, 3.0000000000000000]),
        "speech_synthesis_voices": random.choice(speech_synthesis_voices),
        "canvas":generate_random_canvas(),
        "networkType": random.choice(["4g", "5g", "wifi"]),
        "cookieEnabled": random.choice([True, False]),
        "display": f"{random.randint(20, 50)}|{random.randint(300, 600)}|{random.randint(400, 800)}|{random.randint(300, 600)}|{random.randint(400, 800)}",
        "platform": random.choice(["MacIntel", "Win32", "Linux x86_64"]),
        "java": random.choice(["true", "false"]),
        "webgl":  generate_random_webgl(),
        "silverlight": "NA",
        "touchSupport": random.choice([True, False]),
        "errorProperty": "${flash,http-accept-headers,audio}"
}


def init_browser():
    try:
        options = Options()
        fingerprinting = generate_fingerprinting()
        print(fingerprinting)

        if not fingerprinting:
            print("Fingerprinting data is missing or invalid.")
            return None

        options.add_argument(f"--user-agent={fingerprinting['user_agent']}")

        options.add_argument("--disable-gpu")  
        options.add_argument("--disable-software-rasterizer") 
        options.add_argument("--enable-unsafe-webgl")
        options.add_argument("--use-gl=swiftshader")
        options.add_argument("--enable-webgl")

        options.add_argument("--log-level=3") 
        options.add_argument("--disable-logging") 
        options.add_argument("--no-sandbox") 
        options.add_argument("--disable-dev-shm-usage")  
        options.add_argument("--disable-popup-blocking")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-infobars")
        options.add_experimental_option("excludeSwitches", ["enable-logging"])  
        options.add_argument("--disable-blink-features=AutomationControlled")

        options.add_argument("--force-timezone=UTC")

        project_dir = os.getcwd()
        chrome_binary_path = os.path.join(project_dir, "Chrome", "chrome.exe")
        driver_path = os.path.join(project_dir, "chromedriver", "chromedriver.exe")

        options.binary_location = chrome_binary_path
        service = Service(executable_path=driver_path)
        driver = webdriver.Chrome(service=service, options=options)

        if not os.path.exists(chrome_binary_path):
            print(f"Chrome binary not found at {chrome_binary_path}. Check the path!")
            return None

        if not os.path.exists(driver_path):
            print(f"ChromeDriver not found at {driver_path}. Check the path!")
            return None
        
        device_type = fingerprinting['device_type']
        device_resolutions = {
            "android_phone": (360, 640),
            "iphone": (360, 640),
            "tablet": (768, 1024),
            "ipad": (768, 1024),
            "android_tablet": (768, 1024),
            "smart_tv": (1920, 1080),
            "car_browser": (1280, 720),
        }
        driver.set_window_size(*device_resolutions.get(device_type, (1366, 768)))

        js_script = f"""
        Object.defineProperty(navigator, 'platform', {{ get: () => '{fingerprinting["navigator_platform"]}' }});
        Object.defineProperty(navigator, 'doNotTrack', {{ get: () => '{fingerprinting["do_not_track"]}' }});
        Object.defineProperty(navigator, 'webdriver', {{ get: () => false }});

        // Modify WebGL Renderer & Vendor
        const getParameterProxy = WebGLRenderingContext.prototype.getParameter;
        WebGLRenderingContext.prototype.getParameter = function(param) {{
            if (param === 37445) return '{fingerprinting["webgl_vendor"]}'; // Fake WebGL Vendor
            if (param === 37446) return '{fingerprinting["webgl_renderer"]}'; // Fake WebGL Renderer
            return getParameterProxy.call(this, param);
        }};

        // Modify Canvas Fingerprint
        const originalToDataURL = HTMLCanvasElement.prototype.toDataURL;
        HTMLCanvasElement.prototype.toDataURL = function() {{
            return "data:image/png;base64," + btoa("fakecanvasdata");
        }};

        // Modify Audio Fingerprint
        const audioContext = window.AudioContext || window.webkitAudioContext;
        if (audioContext) {{
            const originalCreateOscillator = audioContext.prototype.createOscillator;
            audioContext.prototype.createOscillator = function() {{
                const oscillator = originalCreateOscillator.call(this);
                oscillator.frequency.value = 1000; 
                return oscillator;
            }};
        }}

        // Disable WebRTC (Prevent IP Leaks)
        Object.defineProperty(navigator, 'mediaDevices', {{
            get: () => undefined
        }});

        // Modify Timezone
        Intl.DateTimeFormat.prototype.resolvedOptions = function() {{
            return {{ timeZone: '{fingerprinting["timezone"]}' }};
        }};
        """

        driver.execute_script(js_script)

        return driver

    except Exception as e:
        print("Failed to initialize browser")
        error_message = f"Failed to initialize browser: {e}"
        logging.error(error_message) 
        return None



def random_delay(min_delay, max_delay):
    delay = random.randint(min_delay, max_delay)
    return delay  

def clear_cookies(driver):
    try:
        print("Clearing all cookies...")
        driver.delete_all_cookies()
        print("All cookies cleared.")
       
    except Exception as e:
        error_message = f"Failed to clear cookie: {e}"
        print("Failed to clear cookies")
        logging.error(error_message) 
        return
    
def write_to_file(file_path, visit_data):
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
            if not isinstance(data, list):
                data = []
        data.append(visit_data)
        with open(file_path, 'w') as file:
            json.dump(data, file, indent=4)
        print(f"  Visit data successfully written to {file_path}")
    except (FileNotFoundError, json.JSONDecodeError):
        with open(file_path, 'w') as file:
            json.dump([visit_data], file, indent=4)
        print(f"  New visit data file created: {file_path}")
    except Exception as e:
        error_message = f"Error writing file: {e}"
        print("Error writing file")
        logging.error(error_message) 
        return
    
import asyncio 

def navigate_and_click(driver, task_queue):
    global visits
    max_retries = 10
    retry_delay = 15
    visits += 1
    print("Visit:", visits)
    gui.update_task_count(visits)

    for attempt in range(max_retries):
        try:
            print(f"Attempt {attempt + 1}/{max_retries}: Starting navigation process...")
            target_url = random.choice(TARGET_URL)

            if not target_url:
                print("No target URLs found.")
                driver.quit()
                return
            
            driver.get(target_url)
            print(f"Opened target link: {target_url}")

            buttons = driver.find_elements(By.XPATH, BUTTON_XPATH)
            if not buttons:
                print("No buttons found to click.")
                return

            random.shuffle(buttons)
            num_clicks = random.randint(1, 3)
            print(f"Clicking {num_clicks} random button(s)...")

            min_delay = int(gui.min_delay_entry.get()) if gui.min_delay_entry.get() else 45
            max_delay = int(gui.max_delay_entry.get()) if gui.max_delay_entry.get() else 60
            
            for index, button in enumerate(buttons[:num_clicks]):  
                try:
                    driver.execute_script("arguments[0].scrollIntoView();", button)
                    WebDriverWait(driver, 10).until(EC.element_to_be_clickable(button))
                    button.click()
                    print(f"Button {index + 1} clicked")
                except Exception as button_error:
                    print(f"Error clicking button {index + 1}")
                    error_message = f"Error clicking button {index + 1}: {button_error}"
                    logging.error(error_message) 
                    try:
                        driver.execute_script("arguments[0].click();", button)
                        print(f"Button {index + 1} clicked using JavaScript.")
                    except Exception as js_error:
                        print(f"JavaScript click failed for button {index + 1}")
                        error_message = f"JavaScript click failed for button {index + 1}: {js_error}"
                        logging.error(error_message) 
                        return
            
            delay_time = random.randint(min_delay, max_delay)
            print(f"Waiting for {delay_time} seconds...")
            time.sleep(delay_time)
            task_queue.put(visits)
            print(f"Final Visits Count: {visits}")
            driver.quit()
            return  
        except (WebDriverException, TimeoutException, requests.exceptions.ReadTimeout, TimeoutError, asyncio.TimeoutError) as e:
            error_message = str(e)

            if "ERR_CONNECTION_TIMED_OUT" in error_message:
                error_type = "Network Timeout"
            elif "TimeoutError" in error_message or "Read timed out" in error_message:
                error_type = "Read Timeout"
            elif "ERR_INTERNET_DISCONNECTED" in error_message:
                error_type = "Internet Disconnected"
            elif "ERR_NAME_NOT_RESOLVED" in error_message:
                error_type = "DNS Resolution Failed"
            else:
                error_type = f"Unknown Error: {error_message}"

            print(f"Retrying... ({attempt + 1}) due to {error_type}")
            logging.error(f"Retrying... ({attempt + 1}) due to {error_type}: {error_message}")

            time.sleep(retry_delay)
            driver.refresh()

    print(f"❌ Max retries reached. Exiting without success. | Total Visits: {visits}")

    
import requests
import subprocess
def cycle_airplane_mode():
    print("Cycling Airplane Mode...")
    n = 1
    for i in range(n):
        print(f"Cycle {i+1}/{n}: Turning ON Airplane Mode...")
        subprocess.run(['adb', 'shell', 'su', '-c', 'settings put global airplane_mode_on 1'], check=True)
        subprocess.run(['adb', 'shell', 'su', '-c', 'am broadcast -a android.intent.action.AIRPLANE_MODE --ez state true'], check=True)
        time.sleep(1)

        print(f"Cycle {i+1}/{n}: Turning OFF Airplane Mode...")
        subprocess.run(['adb', 'shell', 'su', '-c', 'settings put global airplane_mode_on 0'], check=True)
        subprocess.run(['adb', 'shell', 'su', '-c', 'am broadcast -a android.intent.action.AIRPLANE_MODE --ez state false'], check=True)
        time.sleep(1)

def change_ip():
    cycle_airplane_mode()  

if __name__ == "__main__":
    root = tk.Tk()
    gui = WebTaskGUI(root)
    root.mainloop()


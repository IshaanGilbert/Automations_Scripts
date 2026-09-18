# # STATE_IP_BROWSER_PREVIEW_GUI.py
# import tkinter as tk
# from tkinter import ttk, messagebox, scrolledtext, filedialog
# from seleniumwire import webdriver
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.chrome.options import Options
# from webdriver_manager.chrome import ChromeDriverManager
# import random
# import threading
# import json
# import time
# import requests
# from datetime import datetime

# # ================== GEONODE & STATES ==================
# BASE_USER = "geonode_xvmYN44Bvz-type-residential-country-in"
# PASSWORD  = "CHANGE_ME_PASSWORD"
# HOST      = "sg.proxy.geonode.io:11000"

# ALLOWED_STATES = {
#     "GJ": "gujarat",
#     "MP": "madhya pradesh",
#     "DL": "delhi",
#     "WB": "west bengal",
#     "MH": "maharashtra",
#     "OR": "odisha",
#     "BR": "bihar",
#     "JH": "jharkhand",
#     "CG": "chhattisgarh"
# }

# TARGET_URL = "https://ipinfo.io/json"  # ← अपना असली URL बाद में डाल देना

# # ================== GLOBAL ==================
# is_running = False
# total_visits = 0
# log_text = None

# # ================== GET PROXY FOR RANDOM STATE ==================
# def get_random_state_proxy():
#     state_code = random.choice(list(ALLOWED_STATES.keys()))
#     state_name = ALLOWED_STATES[state_code]
#     proxy_user = f"{BASE_USER}-state-{state_name}"
#     proxy_url = f"socks5h://{proxy_user}:CHANGE_ME_PASSWORD@{HOST}"
#     return state_code, state_name, proxy_url

# # ================== FETCH IP INFO BEFORE OPENING BROWSER ==================
# def fetch_ip_via_proxy(proxy_url):
#     try:
#         proxies = {"http": proxy_url, "https": proxy_url}
#         resp = requests.get("https://ipinfo.io/json", proxies=proxies, timeout=20)
#         if resp.status_code == 200:
#             return resp.json()
#     except:
#         return None
#     return None

# # ================== OPEN BROWSER WITH PROXY + SHOW IP FIRST ==================
# def open_browser_with_preview():
#     global total_visits

#     while is_running:
#         state_code, state_name, proxy_url = get_random_state_proxy()
#         log_text.insert(tk.END, f"\n[TRY] चुना गया State → {state_code} ({state_name})\n")
#         log_text.insert(tk.END, f"[PROXY] {proxy_url}\n")
#         log_text.see(tk.END)

#         ip_data = fetch_ip_via_proxy(proxy_url)

#         if ip_data and ip_data.get("region", "").lower() in state_name.lower():
#             total_visits += 1
#             log_text.insert(tk.END, f"\nSUCCESS! सही State की IP मिली (Visit #{total_visits})\n")
#             log_text.insert(tk.END, "-" * 70 + "\n")
#             log_text.insert(tk.END, json.dumps(ip_data, indent=2, ensure_ascii=False) + "\n")
#             log_text.insert(tk.END, "-" * 70 + "\n")
#             log_text.insert(tk.END, f"Opening Browser → {ip_data['city']}, {ip_data['region']} ({ip_data['ip']})\n\n")
#             log_text.see(tk.END)

#             # === Selenium Wire + Auto ChromeDriver ===
#             options = Options()
#             options.add_argument("--no-sandbox")
#             options.add_argument("--disable-dev-shm-usage")
#             options.add_argument("--disable-blink-features=AutomationControlled")
#             options.add_experimental_option("excludeSwitches", ["enable-automation"])
#             options.add_argument("--start-maximized")

#             seleniumwire_options = {
#                 'proxy': {
#                     'http': proxy_url,
#                     'https': proxy_url,
#                 },
#                 'verify_ssl': False
#             }

#             driver = None
#             try:
#                 driver = webdriver.Chrome(
#                     service=Service(ChromeDriverManager().install()),
#                     options=options,
#                     seleniumwire_options=seleniumwire_options
#                 )
#                 driver.get(TARGET_URL)
#                 time.sleep(25)  # जितना देर देखना हो
#             except Exception as e:
#                 log_text.insert(tk.END, f"[ERROR] Browser crash: {e}\n")
#             finally:
#                 if driver:
#                     driver.quit()

#             time.sleep(5)  # अगला visit के लिए wait
#         else:
#             log_text.insert(tk.END, "[FAILED] गलत state या timeout – दोबारा try...\n")
#             time.sleep(3)

# # ================== GUI ==================
# class StateIPBrowserGUI:
#     def __init__(self, root):
#         self.root = root
#         self.root.title("9 States Only IP Browser + Preview")
#         self.root.geometry("980x720")
#         self.root.configure(bg="#0d1117")

#         self.create_widgets()

#     def create_widgets(self):
#         global log_text
#         title = tk.Label(self.root, text="9 STATES ONLY IP BROWSER", font=("Consolas", 22, "bold"), fg="#58a6ff", bg="#0d1117")
#         title.pack(pady=15)

#         subtitle = tk.Label(self.root, text="हर Visit से पहले IP JSON दिखेगा • सिर्फ GJ, MP, DL, WB, MH, OR, BR, JH, CG", 
#                            font=("Arial", 11), fg="#8b949e", bg="#0d1117")
#         subtitle.pack(pady=5)

#         # Target URL
#         url_frame = tk.Frame(self.root, bg="#0d1117")
#         url_frame.pack(pady=10)
#         tk.Label(url_frame, text="Target URL:", font=("Arial", 12, "bold"), fg="#fff", bg="#0d1117").pack(side="left", padx=10)
#         self.url_entry = tk.Entry(url_frame, width=80, font=("Consolas", 11), bg="#161b22", fg="#58a6ff")
#         self.url_entry.pack(side="left", padx=10)
#         self.url_entry.insert(0, TARGET_URL)

#         # Buttons
#         btn_frame = tk.Frame(self.root, bg="#0d1117")
#         btn_frame.pack(pady=15)
#         self.start_btn = tk.Button(btn_frame, text="START VISITS", font=("Arial", 14, "bold"), bg="#238636", fg="white", width=20, height=2,
#                                   command=self.start_visits)
#         self.start_btn.pack(side="left", padx=20)
#         self.stop_btn = tk.Button(btn_frame, text="STOP", font=("Arial", 14, "bold"), bg="#da3633", fg="white", width=15, height=2,
#                                  command=self.stop_visits, state="disabled")
#         self.stop_btn.pack(side="left", padx=20)

#         # Stats
#         self.stats_label = tk.Label(self.root, text="Total Visits: 0", font=("Arial", 12), fg="#58a6ff", bg="#0d1117")
#         self.stats_label.pack(pady=5)

#         # Log Area
#         log_frame = tk.Frame(self.root, bg="#0d1117")
#         log_frame.pack(pady=10, padx=20, fill="both", expand=True)
#         tk.Label(log_frame, text="Live Logs + IP Preview:", font=("Arial", 11, "bold"), fg="#fff", bg="#0d1117").pack(anchor="w")
#         log_text = scrolledtext.ScrolledText(log_frame, font=("Consolas", 10), bg="#161b22", fg="#f0f6fc", height=25)
#         log_text.pack(fill="both", expand=True, pady=5)

#         log_text.insert(tk.END, "Ready! START दबाओ → हर बार नई State IP + पूरा JSON दिखेगा\n\n")

#     def start_visits(self):
#         global is_running, TARGET_URL, total_visits
#         if is_running:
#             return
#         TARGET_URL = self.url_entry.get().strip()
#         if not TARGET_URL:
#             messagebox.showerror("Error", "Target URL डालो!")
#             return

#         is_running = True
#         total_visits = 0
#         self.start_btn.config(state="disabled")
#         self.stop_btn.config(state="normal")
#         self.url_entry.config(state="disabled")
#         log_text.insert(tk.END, "AUTOMATION STARTED! हर Visit पर नई State IP आएगी...\n\n")
#         log_text.see(tk.END)

#         threading.Thread(target=open_browser_with_preview, daemon=True).start()

#     def stop_visits(self):
#         global is_running
#         is_running = False
#         self.start_btn.config(state="normal")
#         self.stop_btn.config(state="disabled")
#         self.url_entry.config(state="normal")
#         log_text.insert(tk.END, "\nSTOPPED BY USER.\n")
#         log_text.see(tk.END)

# # ================== MAIN ==================
# if __name__ == "__main__":
#     root = tk.Tk()
#     app = StateIPBrowserGUI(root)
#     root.mainloop()



# # STATE_IP_BROWSER_PREVIEW_GUI.py
# import tkinter as tk
# from tkinter import ttk, messagebox, scrolledtext, filedialog
# from seleniumwire import webdriver
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.chrome.options import Options
# from webdriver_manager.chrome import ChromeDriverManager
# import random
# import threading
# import json
# import time
# import requests
# from datetime import datetime
# from selenium.webdriver.common.action_chains import ActionChains
# from selenium.webdriver.common.by import By

# # ================== GEONODE & STATES ==================
# BASE_USER = "geonode_xvmYN44Bvz-type-residential-country-in"
# PASSWORD  = "CHANGE_ME_PASSWORD"
# HOST      = "sg.proxy.geonode.io:11000"

# ALLOWED_STATES = {
#     "PB": "punjab",
#     "DL": "delhi",
#     "UP": "uttar pradesh",
#     "MP": "madhya pradesh",
#     "CG": "chhattisgarh",
#     "HR": "haryana",
#     "HP": "himachal pradesh",
#     "WB": "west bengal",
#     "JK": "jammu and kashmir"
# }

# TARGET_URL = "https://partners.marcadeo.com/click?oid=321&uid=14"  # ← अपना असली URL बाद में डाल देना

# # ================== GLOBAL ==================
# is_running = False
# total_visits = 0
# log_text = None
# max_visits_val = 0
# total_visits_lock = threading.Lock()

# # ================== GET PROXY FOR RANDOM STATE ==================
# def get_random_state_proxy():
#     state_code = random.choice(list(ALLOWED_STATES.keys()))
#     state_name = ALLOWED_STATES[state_code]
#     proxy_user = f"{BASE_USER}-state-{state_name}"
#     proxy_url = f"socks5h://{proxy_user}:CHANGE_ME_PASSWORD@{HOST}"
#     return state_code, state_name, proxy_url

# # ================== FETCH IP INFO BEFORE OPENING BROWSER ==================
# def fetch_ip_via_proxy(proxy_url):
#     try:
#         proxies = {"http": proxy_url, "https": proxy_url}
#         resp = requests.get("https://ipinfo.io/json", proxies=proxies, timeout=20)
#         if resp.status_code == 200:
#             return resp.json()
#     except:
#         return None
#     return None

# # ================== PERFORM RANDOM ACTIONS ==================
# def perform_random_actions(driver):
#     try:
#         time.sleep(random.uniform(2, 5))  # Wait for page to load
#         # Random scrolls
#         for _ in range(random.randint(3, 8)):
#             scroll_amount = random.randint(-400, 600)
#             driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
#             time.sleep(random.uniform(0.5, 2.5))
#         # Random mouse movements
#         actions = ActionChains(driver)
#         for _ in range(random.randint(5, 15)):
#             x_off = random.randint(-100, 100)
#             y_off = random.randint(-100, 100)
#             actions.move_by_offset(x_off, y_off).perform()
#             time.sleep(random.uniform(0.1, 0.5))
#         # Random clicks
#         clickable_elements = driver.find_elements(By.CSS_SELECTOR, "a, button, input[type='button'], input[type='submit']")
#         if clickable_elements:
#             for _ in range(random.randint(1, 3)):
#                 elem = random.choice(clickable_elements)
#                 try:
#                     elem.click()
#                     time.sleep(random.uniform(1, 3))
#                 except:
#                     pass
#     except Exception as e:
#         log_text.insert(tk.END, f"[ACTION ERROR] {e}\n")

# # ================== OPEN BROWSER WITH PROXY + SHOW IP FIRST ==================
# def open_browser_with_preview():
#     global total_visits, max_visits_val

#     while True:
#         with total_visits_lock:
#             if not is_running or (max_visits_val != 0 and total_visits >= max_visits_val):
#                 break

#         state_code, state_name, proxy_url = get_random_state_proxy()
#         log_text.insert(tk.END, f"\n[TRY] चुना गया State → {state_code} ({state_name})\n")
#         log_text.insert(tk.END, f"[PROXY] {proxy_url}\n")
#         log_text.see(tk.END)

#         ip_data = fetch_ip_via_proxy(proxy_url)

#         if ip_data and ip_data.get("region", "").lower() in state_name.lower():
#             with total_visits_lock:
#                 total_visits += 1
#                 root.after(0, app.update_stats)
#                 if max_visits_val != 0 and total_visits >= max_visits_val:
#                     root.after(0, app.stop_visits)
#             log_text.insert(tk.END, f"\nSUCCESS! सही State की IP मिली (Visit #{total_visits})\n")
#             log_text.insert(tk.END, "-" * 70 + "\n")
#             log_text.insert(tk.END, json.dumps(ip_data, indent=2, ensure_ascii=False) + "\n")
#             log_text.insert(tk.END, "-" * 70 + "\n")
#             log_text.insert(tk.END, f"Opening Browser → {ip_data['city']}, {ip_data['region']} ({ip_data['ip']})\n\n")
#             log_text.see(tk.END)

#             # === Selenium Wire + Auto ChromeDriver ===
#             options = Options()
#             options.add_argument("--no-sandbox")
#             options.add_argument("--disable-dev-shm-usage")
#             options.add_argument("--disable-blink-features=AutomationControlled")
#             options.add_experimental_option("excludeSwitches", ["enable-automation"])
#             options.add_argument("--start-maximized")

#             seleniumwire_options = {
#                 'proxy': {
#                     'http': proxy_url,
#                     'https': proxy_url,
#                 },
#                 'verify_ssl': False
#             }

#             driver = None
#             try:
#                 driver = webdriver.Chrome(
#                     service=Service(ChromeDriverManager().install()),
#                     options=options,
#                     seleniumwire_options=seleniumwire_options
#                 )
#                 driver.get(TARGET_URL)
#                 perform_random_actions(driver)
#                 time.sleep(5)  # Extra wait after actions
#             except Exception as e:
#                 log_text.insert(tk.END, f"[ERROR] Browser crash: {e}\n")
#             finally:
#                 if driver:
#                     driver.quit()

#             time.sleep(5)  # अगला visit के लिए wait
#         else:
#             log_text.insert(tk.END, "[FAILED] गलत state या timeout – दोबारा try...\n")
#             time.sleep(3)

# # ================== GUI ==================
# class StateIPBrowserGUI:
#     def __init__(self, root):
#         self.root = root
#         self.root.title("9 States Only IP Browser + Preview")
#         self.root.geometry("980x720")
#         self.root.configure(bg="#0d1117")

#         self.create_widgets()

#     def create_widgets(self):
#         global log_text
#         title = tk.Label(self.root, text="9 STATES ONLY IP BROWSER", font=("Consolas", 22, "bold"), fg="#58a6ff", bg="#0d1117")
#         title.pack(pady=15)

#         subtitle = tk.Label(self.root, text="हर Visit से पहले IP JSON दिखेगा • सिर्फ GJ, MP, DL, WB, MH, OR, BR, JH, CG", 
#                            font=("Arial", 11), fg="#8b949e", bg="#0d1117")
#         subtitle.pack(pady=5)

#         # Target URL
#         url_frame = tk.Frame(self.root, bg="#0d1117")
#         url_frame.pack(pady=10)
#         tk.Label(url_frame, text="Target URL:", font=("Arial", 12, "bold"), fg="#fff", bg="#0d1117").pack(side="left", padx=10)
#         self.url_entry = tk.Entry(url_frame, width=80, font=("Consolas", 11), bg="#161b22", fg="#58a6ff")
#         self.url_entry.pack(side="left", padx=10)
#         self.url_entry.insert(0, TARGET_URL)

#         # Settings: Max Visits and Parallel Sessions
#         settings_frame = tk.Frame(self.root, bg="#0d1117")
#         settings_frame.pack(pady=10)
#         tk.Label(settings_frame, text="Max Visits (0 for unlimited):", font=("Arial", 12, "bold"), fg="#fff", bg="#0d1117").pack(side="left", padx=10)
#         self.max_visits_entry = tk.Entry(settings_frame, width=10, font=("Consolas", 11), bg="#161b22", fg="#58a6ff")
#         self.max_visits_entry.pack(side="left", padx=10)
#         self.max_visits_entry.insert(0, "0")
#         tk.Label(settings_frame, text="Parallel Sessions:", font=("Arial", 12, "bold"), fg="#fff", bg="#0d1117").pack(side="left", padx=10)
#         self.num_sessions_entry = tk.Entry(settings_frame, width=10, font=("Consolas", 11), bg="#161b22", fg="#58a6ff")
#         self.num_sessions_entry.pack(side="left", padx=10)
#         self.num_sessions_entry.insert(0, "1")

#         # Buttons
#         btn_frame = tk.Frame(self.root, bg="#0d1117")
#         btn_frame.pack(pady=15)
#         self.start_btn = tk.Button(btn_frame, text="START VISITS", font=("Arial", 14, "bold"), bg="#238636", fg="white", width=20, height=2,
#                                   command=self.start_visits)
#         self.start_btn.pack(side="left", padx=20)
#         self.stop_btn = tk.Button(btn_frame, text="STOP", font=("Arial", 14, "bold"), bg="#da3633", fg="white", width=15, height=2,
#                                  command=self.stop_visits, state="disabled")
#         self.stop_btn.pack(side="left", padx=20)

#         # Stats
#         self.stats_label = tk.Label(self.root, text="Total Visits: 0", font=("Arial", 12), fg="#58a6ff", bg="#0d1117")
#         self.stats_label.pack(pady=5)

#         # Log Area
#         log_frame = tk.Frame(self.root, bg="#0d1117")
#         log_frame.pack(pady=10, padx=20, fill="both", expand=True)
#         tk.Label(log_frame, text="Live Logs + IP Preview:", font=("Arial", 11, "bold"), fg="#fff", bg="#0d1117").pack(anchor="w")
#         log_text = scrolledtext.ScrolledText(log_frame, font=("Consolas", 10), bg="#161b22", fg="#f0f6fc", height=25)
#         log_text.pack(fill="both", expand=True, pady=5)

#         log_text.insert(tk.END, "Ready! START दबाओ → हर बार नई State IP + पूरा JSON दिखेगा\n\n")

#     def update_stats(self):
#         global total_visits
#         self.stats_label.config(text=f"Total Visits: {total_visits}")

#     def start_visits(self):
#         global is_running, TARGET_URL, total_visits, max_visits_val
#         if is_running:
#             return
#         TARGET_URL = self.url_entry.get().strip()
#         if not TARGET_URL:
#             messagebox.showerror("Error", "Target URL डालो!")
#             return

#         try:
#             max_visits_val = int(self.max_visits_entry.get().strip() or "0")
#             num_sessions = int(self.num_sessions_entry.get().strip() or "1")
#         except ValueError:
#             messagebox.showerror("Error", "Max Visits और Parallel Sessions numbers होने चाहिए!")
#             return

#         is_running = True
#         total_visits = 0
#         self.start_btn.config(state="disabled")
#         self.stop_btn.config(state="normal")
#         self.url_entry.config(state="disabled")
#         self.max_visits_entry.config(state="disabled")
#         self.num_sessions_entry.config(state="disabled")
#         log_text.insert(tk.END, "AUTOMATION STARTED! हर Visit पर नई State IP आएगी...\n\n")
#         log_text.see(tk.END)

#         for _ in range(num_sessions):
#             threading.Thread(target=open_browser_with_preview, daemon=True).start()

#     def stop_visits(self):
#         global is_running
#         is_running = False
#         self.start_btn.config(state="normal")
#         self.stop_btn.config(state="disabled")
#         self.url_entry.config(state="normal")
#         self.max_visits_entry.config(state="normal")
#         self.num_sessions_entry.config(state="normal")
#         log_text.insert(tk.END, "\nSTOPPED BY USER.\n")
#         log_text.see(tk.END)

# # ================== MAIN ==================
# if __name__ == "__main__":
#     root = tk.Tk()
#     app = StateIPBrowserGUI(root)
#     root.mainloop()





# # STATE_IP_BROWSER_PREVIEW_GUI.py
# import tkinter as tk
# from tkinter import ttk, messagebox, scrolledtext, filedialog
# from seleniumwire import webdriver
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.chrome.options import Options
# from webdriver_manager.chrome import ChromeDriverManager
# import random
# import threading
# import json
# import time
# import requests
# from datetime import datetime
# from selenium.webdriver.common.action_chains import ActionChains
# from selenium.webdriver.common.by import By
# import os

# # =============== JSON LOG FILE ===============
# LOG_FILE = "visit_logs.json"

# # अगर file नहीं है तो खाली list डाल दो
# if not os.path.exists(LOG_FILE):
#     with open(LOG_FILE, "w") as f:
#         json.dump([], f, indent=2)

# # JSON में नया log add करने का function
# def save_log(entry):
#     try:
#         with open(LOG_FILE, "r") as f:
#             data = json.load(f)
#     except:
#         data = []

#     data.append(entry)

#     with open(LOG_FILE, "w") as f:
#         json.dump(data, f, indent=2, ensure_ascii=False)

# # ===============================================================

# BASE_USER = "geonode_xvmYN44Bvz-type-residential-country-in"
# PASSWORD  = "CHANGE_ME_PASSWORD"
# HOST      = "sg.proxy.geonode.io:11000"

# ALLOWED_STATES = {
#     "PB": "punjab",
#     "DL": "delhi",
#     "UP": "uttar pradesh",
#     "MP": "madhya pradesh",
#     "CG": "chhattisgarh",
#     "HR": "haryana",
#     "HP": "himachal pradesh",
#     "WB": "west bengal",
#     "JK": "jammu and kashmir"
# }

# TARGET_URL = "https://partners.marcadeo.com/click?oid=321&uid=14"

# is_running = False
# total_visits = 0
# max_visits_val = 0
# log_text = None
# total_visits_lock = threading.Lock()


# # =============== GET PROXY =====================
# def get_random_state_proxy():
#     state_code = random.choice(list(ALLOWED_STATES.keys()))
#     state_name = ALLOWED_STATES[state_code]
#     proxy_user = f"{BASE_USER}-state-{state_name}"
#     proxy_url = f"socks5h://{proxy_user}:CHANGE_ME_PASSWORD@{HOST}"
#     return state_code, state_name, proxy_url

# # =============== FETCH IP =========================
# def fetch_ip_via_proxy(proxy_url):
#     try:
#         proxies = {"http": proxy_url, "https": proxy_url}
#         resp = requests.get("https://ipinfo.io/json", proxies=proxies, timeout=20)
#         if resp.status_code == 200:
#             return resp.json()
#     except Exception as e:
#         # Return error as string
#         return str(e)
#     return None

# # =============== RANDOM ACTIONS ====================
# def perform_random_actions(driver):
#     try:
#         time.sleep(random.uniform(2, 5))
#         for _ in range(random.randint(3, 8)):
#             driver.execute_script(f"window.scrollBy(0, {random.randint(-400, 600)});")
#             time.sleep(random.uniform(0.5, 2.5))
#         actions = ActionChains(driver)
#         for _ in range(random.randint(5, 15)):
#             actions.move_by_offset(random.randint(-100, 100), random.randint(-100, 100)).perform()
#             time.sleep(random.uniform(0.1, 0.5))

#         clickable = driver.find_elements(By.CSS_SELECTOR, "a,button,input[type='button'],input[type='submit']")
#         if clickable:
#             for _ in range(random.randint(1, 3)):
#                 try:
#                     random.choice(clickable).click()
#                     time.sleep(random.uniform(1, 3))
#                 except:
#                     pass
#     except Exception as e:
#         log_text.insert(tk.END, f"[ACTION ERROR] {e}\n")

# # =============== MAIN VISIT FUNCTION ====================
# def open_browser_with_preview():
#     global total_visits, max_visits_val, TARGET_URL

#     while True:
#         with total_visits_lock:
#             if not is_running or (max_visits_val and total_visits >= max_visits_val):
#                 break

#         state_code, state_name, proxy_url = get_random_state_proxy()
#         log_text.insert(tk.END, f"\n[TRY] State → {state_code} ({state_name})\n")
#         log_text.insert(tk.END, f"[PROXY] {proxy_url}\n")
#         log_text.see(tk.END)

#         ip_info = fetch_ip_via_proxy(proxy_url)
#         error_text = None
#         ip_address = None

#         # ---- Check if IP is JSON or Error ----
#         if isinstance(ip_info, dict):
#             region = ip_info.get("region", "").lower()
#             ip_address = ip_info.get("ip", "N/A")
#         else:
#             region = ""
#             error_text = ip_info  # error string

#         # =============== SAVE LOG ENTRY ===============
#         log_entry = {
#             "no": total_visits + 1,
#             "time": datetime.now().strftime("%H:%M:%S"),
#             "state": state_name,
#             "state_code": state_code,
#             "ip": error_text if error_text else ip_address,
#             "url": TARGET_URL
#         }
#         save_log(log_entry)
#         # ==============================================

#         # Correct state IP found
#         if isinstance(ip_info, dict) and region in state_name.lower():
#             with total_visits_lock:
#                 total_visits += 1
#                 root.after(0, app.update_stats)

#             log_text.insert(tk.END, f"\nSUCCESS (Visit #{total_visits})\n")
#             log_text.insert(tk.END, json.dumps(ip_info, indent=2) + "\n")
#             log_text.see(tk.END)

#             # Selenium setup
#             options = Options()
#             options.add_argument("--disable-blink-features=AutomationControlled")
#             options.add_argument("--start-maximized")

#             seleniumwire_options = {
#                 'proxy': {'http': proxy_url, 'https': proxy_url},
#                 'verify_ssl': False
#             }

#             driver = None
#             try:
#                 driver = webdriver.Chrome(
#                     service=Service(ChromeDriverManager().install()),
#                     options=options,
#                     seleniumwire_options=seleniumwire_options
#                 )
#                 driver.get(TARGET_URL)
#                 perform_random_actions(driver)
#                 time.sleep(5)

#             except Exception as e:
#                 log_text.insert(tk.END, f"[ERROR Browser] {e}\n")

#             finally:
#                 if driver:
#                     driver.quit()

#             time.sleep(4)

#         else:
#             # WRONG state or ERRORED IP also already logged above
#             log_text.insert(tk.END, "[FAILED] Wrong state / timeout / error.\n")
#             log_text.see(tk.END)
#             time.sleep(3)

# # =============== GUI (unchanged except start/stop) ====================
# class StateIPBrowserGUI:
#     def __init__(self, root):
#         self.root = root
#         self.root.title("9 States IP Browser + Preview")
#         self.root.geometry("980x720")
#         self.root.configure(bg="#0d1117")
#         self.create_widgets()

#     def create_widgets(self):
#         global log_text
#         title = tk.Label(self.root, text="9 STATES ONLY IP BROWSER", font=("Consolas", 22, "bold"), fg="#58a6ff", bg="#0d1117")
#         title.pack(pady=15)

#         self.url_entry = tk.Entry(self.root, width=80)
#         self.url_entry.pack()
#         self.url_entry.insert(0, TARGET_URL)

#         self.max_visits_entry = tk.Entry(self.root, width=10)
#         self.max_visits_entry.pack()
#         self.max_visits_entry.insert(0, "0")

#         self.num_sessions_entry = tk.Entry(self.root, width=10)
#         self.num_sessions_entry.pack()
#         self.num_sessions_entry.insert(0, "1")

#         self.start_btn = tk.Button(self.root, text="START", command=self.start_visits)
#         self.start_btn.pack()

#         self.stop_btn = tk.Button(self.root, text="STOP", command=self.stop_visits, state="disabled")
#         self.stop_btn.pack()

#         self.stats_label = tk.Label(self.root, text="Total Visits: 0", fg="white", bg="#0d1117")
#         self.stats_label.pack()

#         log_text = scrolledtext.ScrolledText(self.root, font=("Consolas", 10), bg="#161b22", fg="#f0f6fc", height=25)
#         log_text.pack(fill="both", expand=True)

#     def update_stats(self):
#         self.stats_label.config(text=f"Total Visits: {total_visits}")

#     def start_visits(self):
#         global is_running, TARGET_URL, total_visits, max_visits_val

#         if is_running:
#             return

#         TARGET_URL = self.url_entry.get().strip()
#         max_visits_val = int(self.max_visits_entry.get().strip() or "0")
#         num_sessions = int(self.num_sessions_entry.get().strip() or "1")

#         is_running = True
#         total_visits = 0

#         self.start_btn.config(state="disabled")
#         self.stop_btn.config(state="normal")

#         for _ in range(num_sessions):
#             threading.Thread(target=open_browser_with_preview, daemon=True).start()

#     def stop_visits(self):
#         global is_running
#         is_running = False
#         self.start_btn.config(state="normal")
#         self.stop_btn.config(state="disabled")


# if __name__ == "__main__":
#     root = tk.Tk()
#     app = StateIPBrowserGUI(root)
#     root.mainloop()




# # STATE_IP_BROWSER_PREVIEW_GUI.py
# import tkinter as tk
# from tkinter import ttk, messagebox, scrolledtext, filedialog
# from seleniumwire import webdriver
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.chrome.options import Options
# from webdriver_manager.chrome import ChromeDriverManager
# import random
# import threading
# import json
# import time
# import requests
# from datetime import datetime
# from selenium.webdriver.common.action_chains import ActionChains
# from selenium.webdriver.common.by import By
# import os

# # =============== JSON LOG FILE ===============
# LOG_FILE = "visit_logs.json"

# # अगर file नहीं है तो खाली list डाल दो
# if not os.path.exists(LOG_FILE):
#     with open(LOG_FILE, "w") as f:
#         json.dump([], f, indent=2)

# # JSON में नया log add करने का function
# def save_log(entry):
#     try:
#         with open(LOG_FILE, "r") as f:
#             data = json.load(f)
#     except:
#         data = []

#     data.append(entry)

#     with open(LOG_FILE, "w") as f:
#         json.dump(data, f, indent=2, ensure_ascii=False)

# # ===============================================================

# BASE_USER = "geonode_xvmYN44Bvz-type-residential-country-in"
# PASSWORD  = "CHANGE_ME_PASSWORD"
# HOST      = "sg.proxy.geonode.io:11000"

# ALLOWED_STATES = {
#     "GJ": "gujarat",
#     "MP": "madhya pradesh",
#     "DL": "delhi",
#     "WB": "west bengal",
#     "MH": "maharashtra",
#     "OR": "odisha",
#     "BR": "bihar",
#     "JH": "jharkhand",
#     "CG": "chhattisgarh"
# }

# TARGET_URL = "https://partners.marcadeo.com/click?oid=320&uid=14"

# is_running = False
# total_visits = 0
# max_visits_val = 0
# log_text = None
# total_visits_lock = threading.Lock()


# # =============== GET PROXY =====================
# def get_random_state_proxy():
#     state_code = random.choice(list(ALLOWED_STATES.keys()))
#     state_name = ALLOWED_STATES[state_code]
#     proxy_user = f"{BASE_USER}-state-{state_name}"
#     proxy_url = f"socks5h://{proxy_user}:CHANGE_ME_PASSWORD@{HOST}"
#     return state_code, state_name, proxy_url

# # =============== FETCH IP =========================
# def fetch_ip_via_proxy(proxy_url):
#     try:
#         proxies = {"http": proxy_url, "https": proxy_url}
#         resp = requests.get("https://ipinfo.io/json", proxies=proxies, timeout=20)
#         if resp.status_code == 200:
#             return resp.json()
#     except Exception as e:
#         # Return error as string
#         return str(e)
#     return None

# # =============== RANDOM ACTIONS ====================
# def perform_random_actions(driver):
#     try:
#         time.sleep(random.uniform(2, 5))
#         for _ in range(random.randint(3, 8)):
#             driver.execute_script(f"window.scrollBy(0, {random.randint(-400, 600)});")
#             time.sleep(random.uniform(0.5, 2.5))
#         actions = ActionChains(driver)
#         for _ in range(random.randint(5, 15)):
#             actions.move_by_offset(random.randint(-100, 100), random.randint(-100, 100)).perform()
#             time.sleep(random.uniform(0.1, 0.5))

#         clickable = driver.find_elements(By.CSS_SELECTOR, "a,button,input[type='button'],input[type='submit']")
#         if clickable:
#             for _ in range(random.randint(1, 3)):
#                 try:
#                     random.choice(clickable).click()
#                     time.sleep(random.uniform(1, 3))
#                 except:
#                     pass
#     except Exception as e:
#         log_text.insert(tk.END, f"[ACTION ERROR] {e}\n")

# # =============== MAIN VISIT FUNCTION ====================
# def open_browser_with_preview():
#     global total_visits, max_visits_val, TARGET_URL

#     while True:
#         with total_visits_lock:
#             if not is_running or (max_visits_val and total_visits >= max_visits_val):
#                 break

#         state_code, state_name, proxy_url = get_random_state_proxy()
#         log_text.insert(tk.END, f"\n[TRY] State → {state_code} ({state_name})\n")
#         log_text.insert(tk.END, f"[PROXY] {proxy_url}\n")
#         log_text.see(tk.END)

#         ip_info = fetch_ip_via_proxy(proxy_url)
#         error_text = None
#         ip_address = None

#         # ---- Check if IP is JSON or Error ----
#         if isinstance(ip_info, dict):
#             region = ip_info.get("region", "").lower()
#             ip_address = ip_info.get("ip", "N/A")
#         else:
#             region = ""
#             error_text = ip_info  # error string

#         # =============== SAVE LOG ENTRY ===============
#         log_entry = {
#             "no": total_visits + 1,
#             "time": datetime.now().strftime("%H:%M:%S"),
#             "state": state_name,
#             "state_code": state_code,
#             "ip": error_text if error_text else ip_address,
#             "url": TARGET_URL
#         }
#         save_log(log_entry)
#         # ==============================================

#         # Correct state IP found
#         if isinstance(ip_info, dict) and region in state_name.lower():
#             with total_visits_lock:
#                 total_visits += 1
#                 root.after(0, app.update_stats)

#             log_text.insert(tk.END, f"\nSUCCESS (Visit #{total_visits})\n")
#             log_text.insert(tk.END, json.dumps(ip_info, indent=2) + "\n")
#             log_text.see(tk.END)

#             # Selenium setup
#             options = Options()
#             options.add_argument("--disable-blink-features=AutomationControlled")
#             options.add_argument("--start-maximized")

#             seleniumwire_options = {
#                 'proxy': {'http': proxy_url, 'https': proxy_url},
#                 'verify_ssl': False
#             }

#             driver = None
#             try:
#                 driver = webdriver.Chrome(
#                     service=Service(ChromeDriverManager().install()),
#                     options=options,
#                     seleniumwire_options=seleniumwire_options
#                 )
#                 driver.get(TARGET_URL)
#                 perform_random_actions(driver)
#                 time.sleep(5)

#             except Exception as e:
#                 log_text.insert(tk.END, f"[ERROR Browser] {e}\n")

#             finally:
#                 if driver:
#                     driver.quit()

#             time.sleep(4)

#         else:
#             # WRONG state or ERRORED IP also already logged above
#             log_text.insert(tk.END, "[FAILED] Wrong state / timeout / error.\n")
#             log_text.see(tk.END)
#             time.sleep(3)

# # =============== GUI (unchanged except start/stop) ====================
# class StateIPBrowserGUI:
#     def __init__(self, root):
#         self.root = root
#         self.root.title("9 States IP Browser + Preview")
#         self.root.geometry("980x720")
#         self.root.configure(bg="#0d1117")
#         self.create_widgets()

#     def create_widgets(self):
#         global log_text
#         title = tk.Label(self.root, text="9 STATES ONLY IP BROWSER", font=("Consolas", 22, "bold"), fg="#58a6ff", bg="#0d1117")
#         title.pack(pady=15)

#         self.url_entry = tk.Entry(self.root, width=80)
#         self.url_entry.pack()
#         self.url_entry.insert(0, TARGET_URL)

#         self.max_visits_entry = tk.Entry(self.root, width=10)
#         self.max_visits_entry.pack()
#         self.max_visits_entry.insert(0, "0")

#         self.num_sessions_entry = tk.Entry(self.root, width=10)
#         self.num_sessions_entry.pack()
#         self.num_sessions_entry.insert(0, "1")

#         self.start_btn = tk.Button(self.root, text="START", command=self.start_visits)
#         self.start_btn.pack()

#         self.stop_btn = tk.Button(self.root, text="STOP", command=self.stop_visits, state="disabled")
#         self.stop_btn.pack()

#         self.stats_label = tk.Label(self.root, text="Total Visits: 0", fg="white", bg="#0d1117")
#         self.stats_label.pack()

#         log_text = scrolledtext.ScrolledText(self.root, font=("Consolas", 10), bg="#161b22", fg="#f0f6fc", height=25)
#         log_text.pack(fill="both", expand=True)

#     def update_stats(self):
#         self.stats_label.config(text=f"Total Visits: {total_visits}")

#     def start_visits(self):
#         global is_running, TARGET_URL, total_visits, max_visits_val

#         if is_running:
#             return

#         TARGET_URL = self.url_entry.get().strip()
#         max_visits_val = int(self.max_visits_entry.get().strip() or "0")
#         num_sessions = int(self.num_sessions_entry.get().strip() or "1")

#         is_running = True
#         total_visits = 0

#         self.start_btn.config(state="disabled")
#         self.stop_btn.config(state="normal")

#         for _ in range(num_sessions):
#             threading.Thread(target=open_browser_with_preview, daemon=True).start()

#     def stop_visits(self):
#         global is_running
#         is_running = False
#         self.start_btn.config(state="normal")
#         self.stop_btn.config(state="disabled")


# if __name__ == "__main__":
#     root = tk.Tk()
#     app = StateIPBrowserGUI(root)
#     root.mainloop()



# # STATE_IP_BROWSER_PREVIEW_GUI.py
# import tkinter as tk
# from tkinter import ttk, messagebox, scrolledtext, filedialog
# from seleniumwire import webdriver
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.chrome.options import Options
# from webdriver_manager.chrome import ChromeDriverManager
# import random
# import threading
# import json
# import time
# import requests
# from datetime import datetime
# from selenium.webdriver.common.action_chains import ActionChains
# from selenium.webdriver.common.by import By
# import os

# # =============== JSON LOG FILE ===============
# LOG_FILE = "visit_logs.json"

# if not os.path.exists(LOG_FILE):
#     with open(LOG_FILE, "w") as f:
#         json.dump([], f, indent=2)

# def save_log(entry):
#     try:
#         with open(LOG_FILE, "r") as f:
#             data = json.load(f)
#     except:
#         data = []

#     data.append(entry)

#     with open(LOG_FILE, "w") as f:
#         json.dump(data, f, indent=2, ensure_ascii=False)

# # ===============================================================

# BASE_USER = "geonode_xvmYN44Bvz-type-residential-country-in"
# PASSWORD  = "CHANGE_ME_PASSWORD"
# HOST      = "sg.proxy.geonode.io:11000"

# ALLOWED_STATES = {
#     "GJ": "gujarat",
#     "MP": "madhya pradesh",
#     "DL": "delhi",
#     "WB": "west bengal",
#     "MH": "maharashtra",
#     "OR": "odisha",
#     "BR": "bihar",
#     "JH": "jharkhand",
#     "CG": "chhattisgarh"
# }

# TARGET_URL = "https://unfilteredgadgets.com/"

# is_running = False
# total_visits = 0
# max_visits_val = 0
# log_text = None
# total_visits_lock = threading.Lock()


# # =============== GET PROXY =====================
# def get_random_state_proxy():
#     state_code = random.choice(list(ALLOWED_STATES.keys()))
#     state_name = ALLOWED_STATES[state_code]
#     proxy_user = f"{BASE_USER}-state-{state_name}"
#     proxy_url = f"socks5h://{proxy_user}:CHANGE_ME_PASSWORD@{HOST}"
#     return state_code, state_name, proxy_url

# # =============== FETCH IP =========================
# def fetch_ip_via_proxy(proxy_url):
#     try:
#         proxies = {"http": proxy_url, "https": proxy_url}
#         resp = requests.get("https://ipinfo.io/json", proxies=proxies, timeout=20)
#         if resp.status_code == 200:
#             return resp.json()
#     except Exception as e:
#         return str(e)
#     return None

# # =============== RANDOM ACTIONS ====================
# def perform_random_actions(driver):
#     try:
#         time.sleep(random.uniform(2, 5))
#         for _ in range(random.randint(3, 8)):
#             driver.execute_script(f"window.scrollBy(0, {random.randint(-400, 600)});")
#             time.sleep(random.uniform(0.5, 2.5))
#         actions = ActionChains(driver)
#         for _ in range(random.randint(5, 15)):
#             actions.move_by_offset(random.randint(-100, 100), random.randint(-100, 100)).perform()
#             time.sleep(random.uniform(0.1, 0.5))

#         clickable = driver.find_elements(By.CSS_SELECTOR, "a,button,input[type='button'],input[type='submit']")
#         if clickable:
#             for _ in range(random.randint(1, 3)):
#                 try:
#                     random.choice(clickable).click()
#                     time.sleep(random.uniform(1, 3))
#                 except:
#                     pass
#     except Exception as e:
#         log_text.insert(tk.END, f"[ACTION ERROR] {e}\n")

# # =============== MAIN VISIT FUNCTION ====================
# def open_browser_with_preview():
#     global total_visits, max_visits_val, TARGET_URL

#     while True:
#         with total_visits_lock:
#             if not is_running or (max_visits_val and total_visits >= max_visits_val):
#                 break

#         state_code, state_name, proxy_url = get_random_state_proxy()
#         log_text.insert(tk.END, f"\n[TRY] State → {state_code} ({state_name})\n")
#         log_text.insert(tk.END, f"[PROXY] {proxy_url}\n")
#         log_text.see(tk.END)

#         ip_info = fetch_ip_via_proxy(proxy_url)
#         error_text = None
#         ip_address = None

#         if isinstance(ip_info, dict):
#             region = ip_info.get("region", "").lower()
#             ip_address = ip_info.get("ip", "N/A")
#         else:
#             region = ""
#             error_text = ip_info

#         log_entry = {
#             "no": total_visits + 1,
#             "time": datetime.now().strftime("%H:%M:%S"),
#             "state": state_name,
#             "state_code": state_code,
#             "ip": error_text if error_text else ip_address,
#             "url": TARGET_URL
#         }
#         save_log(log_entry)

#         if isinstance(ip_info, dict) and region in state_name.lower():
#             # Selenium setup
#             options = Options()
#             options.add_argument("--disable-blink-features=AutomationControlled")
#             options.add_argument("--start-maximized")

#             seleniumwire_options = {
#                 'proxy': {'http': proxy_url, 'https': proxy_url},
#                 'verify_ssl': False
#             }

#             driver = None
#             success = False
#             try:
#                 driver = webdriver.Chrome(
#                     service=Service(ChromeDriverManager().install()),
#                     options=options,
#                     seleniumwire_options=seleniumwire_options
#                 )

#                 max_retries = 3
#                 for attempt in range(max_retries + 1):
#                     log_text.insert(tk.END, f"[LOAD ATTEMPT {attempt + 1}/{max_retries + 1}] {TARGET_URL}\n")
#                     log_text.see(tk.END)

#                     driver.get(TARGET_URL)
#                     time.sleep(3)  # page load hone ka wait

#                     # Check for 502 Bad Gateway
#                     if "502 Bad Gateway" in driver.title or "Bad Gateway" in driver.page_source[:500]:
#                         log_text.insert(tk.END, "[DETECTED] 502 Bad Gateway → Retrying...\n")
#                         log_text.see(tk.END)
#                         time.sleep(random.uniform(3, 7))
#                         continue  # retry

#                     # Agar yahan tak aaya matlab success
#                     success = True
#                     with total_visits_lock:
#                         total_visits += 1
#                         root.after(0, app.update_stats)

#                     log_text.insert(tk.END, f"\nSUCCESS (Visit #{total_visits})\n")
#                     log_text.insert(tk.END, json.dumps(ip_info, indent=2) + "\n")
#                     log_text.see(tk.END)

#                     perform_random_actions(driver)
#                     time.sleep(5)
#                     break  # success hone par loop se bahar

#                 if not success:
#                     log_text.insert(tk.END, "[FAILED] 502 after all retries. Moving to next proxy.\n")
#                     log_text.see(tk.END)

#             except Exception as e:
#                 log_text.insert(tk.END, f"[ERROR Browser] {e}\n")

#             finally:
#                 if driver:
#                     driver.quit()

#             time.sleep(4)

#         else:
#             log_text.insert(tk.END, "[FAILED] Wrong state / timeout / error.\n")
#             log_text.see(tk.END)
#             time.sleep(3)

# # =============== GUI ====================
# class StateIPBrowserGUI:
#     def __init__(self, root):
#         self.root = root
#         self.root.title("9 States IP Browser + Preview")
#         self.root.geometry("980x720")
#         self.root.configure(bg="#0d1117")
#         self.create_widgets()

#     def create_widgets(self):
#         global log_text
#         title = tk.Label(self.root, text="9 STATES ONLY IP BROWSER", font=("Consolas", 22, "bold"), fg="#58a6ff", bg="#0d1117")
#         title.pack(pady=15)

#         self.url_entry = tk.Entry(self.root, width=80)
#         self.url_entry.pack()
#         self.url_entry.insert(0, TARGET_URL)

#         self.max_visits_entry = tk.Entry(self.root, width=10)
#         self.max_visits_entry.pack()
#         self.max_visits_entry.insert(0, "0")

#         self.num_sessions_entry = tk.Entry(self.root, width=10)
#         self.num_sessions_entry.pack()
#         self.num_sessions_entry.insert(0, "1")

#         self.start_btn = tk.Button(self.root, text="START", command=self.start_visits)
#         self.start_btn.pack()

#         self.stop_btn = tk.Button(self.root, text="STOP", command=self.stop_visits, state="disabled")
#         self.stop_btn.pack()

#         self.stats_label = tk.Label(self.root, text="Total Visits: 0", fg="white", bg="#0d1117")
#         self.stats_label.pack()

#         log_text = scrolledtext.ScrolledText(self.root, font=("Consolas", 10), bg="#161b22", fg="#f0f6fc", height=25)
#         log_text.pack(fill="both", expand=True)

#     def update_stats(self):
#         self.stats_label.config(text=f"Total Visits: {total_visits}")

#     def start_visits(self):
#         global is_running, TARGET_URL, total_visits, max_visits_val

#         if is_running:
#             return

#         TARGET_URL = self.url_entry.get().strip()
#         max_visits_val = int(self.max_visits_entry.get().strip() or "0")
#         num_sessions = int(self.num_sessions_entry.get().strip() or "1")

#         is_running = True
#         total_visits = 0

#         self.start_btn.config(state="disabled")
#         self.stop_btn.config(state="normal")

#         for _ in range(num_sessions):
#             threading.Thread(target=open_browser_with_preview, daemon=True).start()

#     def stop_visits(self):
#         global is_running
#         is_running = False
#         self.start_btn.config(state="normal")
#         self.stop_btn.config(state="disabled")


# if __name__ == "__main__":
#     root = tk.Tk()
#     app = StateIPBrowserGUI(root)
#     root.mainloop()





# # STATE_IP_BROWSER_PREVIEW_GUI.py
# import tkinter as tk
# from tkinter import ttk, messagebox, scrolledtext, filedialog
# from seleniumwire import webdriver
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.chrome.options import Options
# from webdriver_manager.chrome import ChromeDriverManager
# import random
# import threading
# import json
# import time
# import requests
# from datetime import datetime
# from selenium.webdriver.common.action_chains import ActionChains
# from selenium.webdriver.common.by import By
# import os
# from fake_useragent import UserAgent  # Added for random user-agents

# # =============== JSON LOG FILE ===============
# LOG_FILE = "visit_logs.json"

# if not os.path.exists(LOG_FILE):
#     with open(LOG_FILE, "w") as f:
#         json.dump([], f, indent=2)

# def save_log(entry):
#     try:
#         with open(LOG_FILE, "r") as f:
#             data = json.load(f)
#     except:
#         data = []

#     data.append(entry)

#     with open(LOG_FILE, "w") as f:
#         json.dump(data, f, indent=2, ensure_ascii=False)

# # ===============================================================

# BASE_USER = "geonode_xvmYN44Bvz-type-residential-country-in"
# PASSWORD  = "CHANGE_ME_PASSWORD"
# HOST      = "sg.proxy.geonode.io:11000"

# ALLOWED_STATES = {
#     "GJ": "gujarat",
#     "MP": "madhya pradesh",
#     "DL": "delhi",
#     "WB": "west bengal",
#     "MH": "maharashtra",
#     "OR": "odisha",
#     "BR": "bihar",
#     "JH": "jharkhand",
#     "CG": "chhattisgarh"
# }

# TARGET_URL = "https://unfilteredgadgets.com/"

# is_running = False
# total_visits = 0
# max_visits_val = 0
# log_text = None
# total_visits_lock = threading.Lock()

# # =============== GET PROXY =====================
# def get_random_state_proxy():
#     state_code = random.choice(list(ALLOWED_STATES.keys()))
#     state_name = ALLOWED_STATES[state_code]
#     proxy_user = f"{BASE_USER}-state-{state_name}"
#     proxy_url = f"socks5h://{proxy_user}:CHANGE_ME_PASSWORD@{HOST}"
#     return state_code, state_name, proxy_url

# # =============== FETCH IP =========================
# def fetch_ip_via_proxy(proxy_url):
#     try:
#         proxies = {"http": proxy_url, "https": proxy_url}
#         resp = requests.get("https://ipinfo.io/json", proxies=proxies, timeout=20)
#         if resp.status_code == 200:
#             return resp.json()
#     except Exception as e:
#         return str(e)
#     return None

# # =============== RANDOM ACTIONS ====================
# def perform_random_actions(driver):
#     try:
#         # Wait for page to settle
#         time.sleep(random.uniform(2, 5))
        
#         # Smooth scrolling: Perform multiple small smooth scrolls
#         scroll_steps = random.randint(3, 8)
#         for _ in range(scroll_steps):
#             scroll_amount = random.randint(-400, 600)
#             driver.execute_script(f"window.scrollBy({{left: 0, top: {scroll_amount}, behavior: 'smooth'}});")
#             time.sleep(random.uniform(0.5, 2.5))  # Wait for smooth scroll to complete
        
#         # Random mouse movements to simulate human behavior
#         actions = ActionChains(driver)
#         for _ in range(random.randint(5, 15)):
#             actions.move_by_offset(random.randint(-100, 100), random.randint(-100, 100)).perform()
#             time.sleep(random.uniform(0.1, 0.5))
        
#         # Random clicks: Ensure at least one random click per visit
#         clickable = driver.find_elements(By.CSS_SELECTOR, "a, button, input[type='button'], input[type='submit'], div.clickable, img")  # Expanded selectors
#         if clickable:
#             num_clicks = random.randint(1, 3)  # At least 1 click
#             for _ in range(num_clicks):
#                 try:
#                     element = random.choice(clickable)
#                     actions.move_to_element(element).click().perform()  # Move to element and click for better simulation
#                     time.sleep(random.uniform(1, 3))
#                 except:
#                     pass
#     except Exception as e:
#         log_text.insert(tk.END, f"[ACTION ERROR] {e}\n")

# # =============== MAIN VISIT FUNCTION ====================
# def open_browser_with_preview():
#     global total_visits, max_visits_val, TARGET_URL

#     ua = UserAgent()  # Initialize UserAgent for random user-agents

#     while True:
#         with total_visits_lock:
#             if not is_running or (max_visits_val and total_visits >= max_visits_val):
#                 break

#         state_code, state_name, proxy_url = get_random_state_proxy()
#         log_text.insert(tk.END, f"\n[TRY] State → {state_code} ({state_name})\n")
#         log_text.insert(tk.END, f"[PROXY] {proxy_url}\n")
#         log_text.see(tk.END)

#         ip_info = fetch_ip_via_proxy(proxy_url)
#         error_text = None
#         ip_address = None

#         if isinstance(ip_info, dict):
#             region = ip_info.get("region", "").lower()
#             ip_address = ip_info.get("ip", "N/A")
#         else:
#             region = ""
#             error_text = ip_info

#         log_entry = {
#             "no": total_visits + 1,
#             "time": datetime.now().strftime("%H:%M:%S"),
#             "state": state_name,
#             "state_code": state_code,
#             "ip": error_text if error_text else ip_address,
#             "url": TARGET_URL
#         }
#         save_log(log_entry)

#         if isinstance(ip_info, dict) and region in state_name.lower():
#             # Selenium setup with enhanced fingerprinting
#             options = Options()
#             options.add_argument("--disable-blink-features=AutomationControlled")
#             options.add_argument("--start-maximized")
#             options.add_experimental_option("excludeSwitches", ["enable-automation"])
#             options.add_experimental_option("useAutomationExtension", False)
            
#             # Random user-agent for each session
#             random_user_agent = ua.random
#             options.add_argument(f"user-agent={random_user_agent}")
            
#             # Additional fingerprint enhancements: Randomize some WebGL and Canvas (via JS injection if needed, but basic here)
#             options.add_argument("--disable-webgl")  # Optional: Disable WebGL to alter fingerprint
#             options.add_argument("--window-size=1920,1080")  # Fixed size for consistency, but can randomize if needed
            
#             seleniumwire_options = {
#                 'proxy': {'http': proxy_url, 'https': proxy_url},
#                 'verify_ssl': False
#             }

#             driver = None
#             success = False
#             try:
#                 driver = webdriver.Chrome(
#                     service=Service(ChromeDriverManager().install()),
#                     options=options,
#                     seleniumwire_options=seleniumwire_options
#                 )
                
#                 # Optional: Inject noise into canvas fingerprint (execute after load if needed)
#                 # driver.execute_script("/* canvas fingerprint spoofing script */")

#                 max_retries = 3
#                 for attempt in range(max_retries + 1):
#                     log_text.insert(tk.END, f"[LOAD ATTEMPT {attempt + 1}/{max_retries + 1}] {TARGET_URL}\n")
#                     log_text.see(tk.END)

#                     driver.get(TARGET_URL)
#                     time.sleep(3)  # page load hone ka wait

#                     # Check for 502 Bad Gateway
#                     if "502 Bad Gateway" in driver.title or "Bad Gateway" in driver.page_source[:500]:
#                         log_text.insert(tk.END, "[DETECTED] 502 Bad Gateway → Retrying...\n")
#                         log_text.see(tk.END)
#                         time.sleep(random.uniform(3, 7))
#                         continue  # retry

#                     # Agar yahan tak aaya matlab success
#                     success = True
#                     with total_visits_lock:
#                         total_visits += 1
#                         root.after(0, app.update_stats)

#                     log_text.insert(tk.END, f"\nSUCCESS (Visit #{total_visits})\n")
#                     log_text.insert(tk.END, json.dumps(ip_info, indent=2) + "\n")
#                     log_text.insert(tk.END, f"[USER-AGENT] {random_user_agent}\n")  # Log user-agent for verification
#                     log_text.see(tk.END)

#                     perform_random_actions(driver)
#                     time.sleep(5)
#                     break  # success hone par loop se bahar

#                 if not success:
#                     log_text.insert(tk.END, "[FAILED] 502 after all retries. Moving to next proxy.\n")
#                     log_text.see(tk.END)

#             except Exception as e:
#                 log_text.insert(tk.END, f"[ERROR Browser] {e}\n")

#             finally:
#                 if driver:
#                     driver.quit()

#             time.sleep(4)

#         else:
#             log_text.insert(tk.END, "[FAILED] Wrong state / timeout / error.\n")
#             log_text.see(tk.END)
#             time.sleep(3)

# # =============== GUI ====================
# class StateIPBrowserGUI:
#     def __init__(self, root):
#         self.root = root
#         self.root.title("9 States IP Browser + Preview")
#         self.root.geometry("980x720")
#         self.root.configure(bg="#0d1117")
#         self.create_widgets()

#     def create_widgets(self):
#         global log_text
#         title = tk.Label(self.root, text="9 STATES ONLY IP BROWSER", font=("Consolas", 22, "bold"), fg="#58a6ff", bg="#0d1117")
#         title.pack(pady=15)

#         self.url_entry = tk.Entry(self.root, width=80)
#         self.url_entry.pack()
#         self.url_entry.insert(0, TARGET_URL)

#         self.max_visits_entry = tk.Entry(self.root, width=10)
#         self.max_visits_entry.pack()
#         self.max_visits_entry.insert(0, "0")

#         self.num_sessions_entry = tk.Entry(self.root, width=10)
#         self.num_sessions_entry.pack()
#         self.num_sessions_entry.insert(0, "1")

#         self.start_btn = tk.Button(self.root, text="START", command=self.start_visits)
#         self.start_btn.pack()

#         self.stop_btn = tk.Button(self.root, text="STOP", command=self.stop_visits, state="disabled")
#         self.stop_btn.pack()

#         self.stats_label = tk.Label(self.root, text="Total Visits: 0", fg="white", bg="#0d1117")
#         self.stats_label.pack()

#         log_text = scrolledtext.ScrolledText(self.root, font=("Consolas", 10), bg="#161b22", fg="#f0f6fc", height=25)
#         log_text.pack(fill="both", expand=True)

#     def update_stats(self):
#         self.stats_label.config(text=f"Total Visits: {total_visits}")

#     def start_visits(self):
#         global is_running, TARGET_URL, total_visits, max_visits_val

#         if is_running:
#             return

#         TARGET_URL = self.url_entry.get().strip()
#         max_visits_val = int(self.max_visits_entry.get().strip() or "0")
#         num_sessions = int(self.num_sessions_entry.get().strip() or "1")

#         is_running = True
#         total_visits = 0

#         self.start_btn.config(state="disabled")
#         self.stop_btn.config(state="normal")

#         for _ in range(num_sessions):
#             threading.Thread(target=open_browser_with_preview, daemon=True).start()

#     def stop_visits(self):
#         global is_running
#         is_running = False
#         self.start_btn.config(state="normal")
#         self.stop_btn.config(state="disabled")


# if __name__ == "__main__":
#     root = tk.Tk()
#     app = StateIPBrowserGUI(root)
#     root.mainloop()



# # STATE_IP_BROWSER_PREVIEW_GUI.py
# import tkinter as tk
# from tkinter import scrolledtext
# from seleniumwire import webdriver
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.chrome.options import Options
# from webdriver_manager.chrome import ChromeDriverManager
# import random
# import threading
# import json
# import time
# import requests
# from datetime import datetime
# from selenium.webdriver.common.action_chains import ActionChains
# from selenium.webdriver.common.by import By
# import os
# from fake_useragent import UserAgent

# # =============== JSON LOG FILE ===============
# LOG_FILE = "visit_logs.json"

# if not os.path.exists(LOG_FILE):
#     with open(LOG_FILE, "w") as f:
#         json.dump([], f, indent=2)

# def save_log(entry):
#     try:
#         with open(LOG_FILE, "r") as f:
#             data = json.load(f)
#     except:
#         data = []
#     data.append(entry)
#     with open(LOG_FILE, "w") as f:
#         json.dump(data, f, indent=2, ensure_ascii=False)

# # ===============================================================

# BASE_USER = "geonode_xvmYN44Bvz-type-residential-country-in"
# PASSWORD  = "CHANGE_ME_PASSWORD"
# HOST      = "sg.proxy.geonode.io:11000"

# ALLOWED_STATES = {
#     "GJ": "gujarat",
#     "MP": "madhya pradesh",
#     "DL": "delhi",
#     "WB": "west bengal",
#     "MH": "maharashtra",
#     "OR": "odisha",
#     "BR": "bihar",
#     "JH": "jharkhand",
#     "CG": "chhattisgarh"
# }

# TARGET_URL = "https://unfilteredgadgets.com/"

# is_running = False
# total_visits = 0
# max_visits_val = 0
# log_text = None
# total_visits_lock = threading.Lock()
# root = None  # Will be set in GUI
# app = None

# # =============== GET PROXY =====================
# def get_random_state_proxy():
#     state_code = random.choice(list(ALLOWED_STATES.keys()))
#     state_name = ALLOWED_STATES[state_code]
#     proxy_user = f"{BASE_USER}-state-{state_name}"
#     proxy_url = f"socks5h://{proxy_user}:CHANGE_ME_PASSWORD@{HOST}"
#     return state_code, state_name, proxy_url

# # =============== FETCH IP =========================
# def fetch_ip_via_proxy(proxy_url):
#     try:
#         proxies = {"http": proxy_url, "https": proxy_url}
#         resp = requests.get("https://ipinfo.io/json", proxies=proxies, timeout=20)
#         if resp.status_code == 200:
#             return resp.json()
#     except Exception as e:
#         return str(e)
#     return None

# # =============== RANDOM ACTIONS (ENHANCED FOR REAL-LOOKING TRAFFIC) ====================
# def perform_random_actions(driver):
#     try:
#         # Initial wait after page load
#         initial_wait = random.uniform(3, 7)
#         time.sleep(initial_wait)

#         actions = ActionChains(driver)

#         # 1. Smooth scrolling (multiple human-like scrolls)
#         scroll_count = random.randint(4, 10)
#         for _ in range(scroll_count):
#             scroll_amount = random.randint(300, 800)
#             driver.execute_script(f"window.scrollBy({{top: {scroll_amount}, behavior: 'smooth'}});")
#             time.sleep(random.uniform(1.2, 3.5))  # Human reading/scroll pause

#         # Scroll back up a bit sometimes
#         if random.random() > 0.5:
#             driver.execute_script("window.scrollBy({top: -600, behavior: 'smooth'});")
#             time.sleep(random.uniform(1, 2.5))

#         # 2. Random mouse movements
#         for _ in range(random.randint(8, 20)):
#             actions.move_by_offset(random.randint(-150, 150), random.randint(-150, 150)).perform()
#             time.sleep(random.uniform(0.2, 0.8))

#         # 3. At least 1–4 random clicks on real elements (links, buttons, images, etc.)
#         clickable_selectors = "a, button, [onclick], img, div[role='button'], input[type='button'], input[type='submit']"
#         clickable_elements = driver.find_elements(By.CSS_SELECTOR, clickable_selectors)

#         if clickable_elements:
#             clicks_to_perform = random.randint(1, 4)  # Guaranteed at least 1 click
#             clicked = 0
#             shuffled = clickable_elements[:]
#             random.shuffle(shuffled)

#             for elem in shuffled:
#                 if clicked >= clicks_to_perform:
#                     break
#                 try:
#                     # Scroll element into view smoothly
#                     driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", elem)
#                     time.sleep(random.uniform(0.8, 2))

#                     # Move mouse to element and click
#                     actions.move_to_element(elem).pause(random.uniform(0.3, 1)).click().perform()
#                     clicked += 1

#                     # Wait after click (simulate reading new content or reaction)
#                     time.sleep(random.uniform(2, 6))

#                     # 20% chance to stop after a click (simulate leaving or deep dive)
#                     if random.random() < 0.2:
#                         break
#                 except Exception:
#                     continue

#         # 4. Final random dwell time to ensure total session > 15 seconds
#         extra_dwell = random.uniform(8, 25)  # Total stay easily 20–60+ seconds
#         time.sleep(extra_dwell)

#     except Exception as e:
#         if log_text:
#             log_text.insert(tk.END, f"[ACTION ERROR] {e}\n")
#             log_text.see(tk.END)

# # =============== MAIN VISIT FUNCTION ====================
# def open_browser_with_preview():
#     global total_visits, max_visits_val, TARGET_URL, root, app

#     ua = UserAgent()

#     while True:
#         with total_visits_lock:
#             if not is_running or (max_visits_val > 0 and total_visits >= max_visits_val):
#                 break

#         state_code, state_name, proxy_url = get_random_state_proxy()
#         if log_text:
#             log_text.insert(tk.END, f"\n[TRY] State → {state_code} ({state_name})\n")
#             log_text.insert(tk.END, f"[PROXY] {proxy_url}\n")
#             log_text.see(tk.END)

#         ip_info = fetch_ip_via_proxy(proxy_url)
#         error_text = None
#         ip_address = "N/A"

#         if isinstance(ip_info, dict):
#             region = ip_info.get("region", "").lower()
#             ip_address = ip_info.get("ip", "N/A")
#         else:
#             region = ""
#             error_text = ip_info

#         log_entry = {
#             "no": total_visits + 1,
#             "time": datetime.now().strftime("%H:%M:%S"),
#             "state": state_name,
#             "state_code": state_code,
#             "ip": error_text if error_text else ip_address,
#             "url": TARGET_URL
#         }
#         save_log(log_entry)

#         if isinstance(ip_info, dict) and region in state_name.lower():
#             options = Options()
#             options.add_argument("--disable-blink-features=AutomationControlled")
#             options.add_argument("--start-maximized")
#             options.add_experimental_option("excludeSwitches", ["enable-automation"])
#             options.add_experimental_option("useAutomationExtension", False)

#             random_user_agent = ua.random
#             options.add_argument(f"user-agent={random_user_agent}")

#             # Optional fingerprint tweaks
#             options.add_argument("--window-size=1920,1080")

#             seleniumwire_options = {
#                 'proxy': {'http': proxy_url, 'https': proxy_url},
#                 'verify_ssl': False
#             }

#             driver = None
#             success = False
#             try:
#                 driver = webdriver.Chrome(
#                     service=Service(ChromeDriverManager().install()),
#                     options=options,
#                     seleniumwire_options=seleniumwire_options
#                 )

#                 for attempt in range(4):  # 4 attempts max
#                     if log_text:
#                         log_text.insert(tk.END, f"[LOAD ATTEMPT {attempt + 1}/4] {TARGET_URL}\n")
#                         log_text.see(tk.END)

#                     driver.get(TARGET_URL)
#                     time.sleep(4)  # Initial load wait

#                     if "502 Bad Gateway" in driver.title or "Bad Gateway" in driver.page_source[:500]:
#                         if log_text:
#                             log_text.insert(tk.END, "[DETECTED] 502 Bad Gateway → Retrying...\n")
#                             log_text.see(tk.END)
#                         time.sleep(random.uniform(4, 8))
#                         continue

#                     success = True
#                     with total_visits_lock:
#                         total_visits += 1
#                         if root and app:
#                             root.after(0, app.update_stats)

#                     if log_text:
#                         log_text.insert(tk.END, f"\n[SUCCESS] Visit #{total_visits} | IP: {ip_address}\n")
#                         log_text.insert(tk.END, f"[USER-AGENT] {random_user_agent}\n")
#                         log_text.see(tk.END)

#                     # === MAIN HUMAN-LIKE BEHAVIOR ===
#                     perform_random_actions(driver)

#                     if log_text:
#                         log_text.insert(tk.END, "[COMPLETED] Realistic session finished.\n")
#                         log_text.see(tk.END)

#                     break  # Success → exit retry loop

#                 if not success and log_text:
#                     log_text.insert(tk.END, "[FAILED] All attempts failed (502 or load issue).\n")
#                     log_text.see(tk.END)

#             except Exception as e:
#                 if log_text:
#                     log_text.insert(tk.END, f"[BROWSER ERROR] {e}\n")
#                     log_text.see(tk.END)

#             finally:
#                 if driver:
#                     driver.quit()

#             time.sleep(random.uniform(3, 7))  # Pause before next visit

#         else:
#             if log_text:
#                 log_text.insert(tk.END, "[SKIPPED] Wrong state or proxy error.\n")
#                 log_text.see(tk.END)
#             time.sleep(3)

# # =============== GUI ====================
# class StateIPBrowserGUI:
#     def __init__(self, root_window):
#         global root, app, log_text
#         root = root_window
#         app = self
#         root.title("9 States IP Browser + Realistic Traffic")
#         root.geometry("1000x760")
#         root.configure(bg="#0d1117")
#         self.create_widgets()

#     def create_widgets(self):
#         global log_text
#         title = tk.Label(root, text="9 STATES REALISTIC TRAFFIC BOT", font=("Consolas", 24, "bold"), fg="#58a6ff", bg="#0d1117")
#         title.pack(pady=20)

#         tk.Label(root, text="Target URL:", fg="white", bg="#0d1117").pack()
#         self.url_entry = tk.Entry(root, width=90)
#         self.url_entry.pack(pady=5)
#         self.url_entry.insert(0, TARGET_URL)

#         frame = tk.Frame(root, bg="#0d1117")
#         frame.pack(pady=10)
#         tk.Label(frame, text="Max Visits (0 = unlimited):", fg="white", bg="#0d1117").grid(row=0, column=0, padx=10)
#         self.max_visits_entry = tk.Entry(frame, width=12)
#         self.max_visits_entry.grid(row=0, column=1)
#         self.max_visits_entry.insert(0, "0")

#         tk.Label(frame, text="Concurrent Sessions:", fg="white", bg="#0d1117").grid(row=0, column=2, padx=20)
#         self.num_sessions_entry = tk.Entry(frame, width=12)
#         self.num_sessions_entry.grid(row=0, column=3)
#         self.num_sessions_entry.insert(0, "1")

#         btn_frame = tk.Frame(root, bg="#0d1117")
#         btn_frame.pack(pady=15)
#         self.start_btn = tk.Button(btn_frame, text="START", font=("Consolas", 14), bg="#238636", fg="white", width=12, command=self.start_visits)
#         self.start_btn.grid(row=0, column=0, padx=10)
#         self.stop_btn = tk.Button(btn_frame, text="STOP", font=("Consolas", 14), bg="#da3633", fg="white", width=12, command=self.stop_visits, state="disabled")
#         self.stop_btn.grid(row=0, column=1, padx=10)

#         self.stats_label = tk.Label(root, text="Total Successful Visits: 0", font=("Consolas", 16), fg="#58a6ff", bg="#0d1117")
#         self.stats_label.pack(pady=10)

#         log_text = scrolledtext.ScrolledText(root, font=("Consolas", 10), bg="#161b22", fg="#f0f6fc", height=28)
#         log_text.pack(fill="both", expand=True, padx=15, pady=10)

#     def update_stats(self):
#         self.stats_label.config(text=f"Total Successful Visits: {total_visits}")

#     def start_visits(self):
#         global is_running, TARGET_URL, max_visits_val

#         if is_running:
#             return

#         TARGET_URL = self.url_entry.get().strip()
#         max_visits_val = int(self.max_visits_entry.get() or "0")
#         num_sessions = int(self.num_sessions_entry.get() or "1")

#         is_running = True
#         self.start_btn.config(state="disabled")
#         self.stop_btn.config(state="normal")

#         for _ in range(num_sessions):
#             threading.Thread(target=open_browser_with_preview, daemon=True).start()

#     def stop_visits(self):
#         global is_running
#         is_running = False
#         self.start_btn.config(state="normal")
#         self.stop_btn.config(state="disabled")


# if __name__ == "__main__":
#     root = tk.Tk()
#     app = StateIPBrowserGUI(root)
#     root.mainloop()



# # STATE_IP_BROWSER_PREVIEW_GUI.py
# import tkinter as tk
# from tkinter import scrolledtext
# from seleniumwire import webdriver
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.chrome.options import Options
# from webdriver_manager.chrome import ChromeDriverManager
# import random
# import threading
# import json
# import time
# import requests
# from datetime import datetime
# from selenium.webdriver.common.action_chains import ActionChains
# from selenium.webdriver.common.by import By
# import os
# from fake_useragent import UserAgent
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.common.exceptions import *

# # =============== JSON LOG FILE ===============
# LOG_FILE = "visit_logs.json"

# if not os.path.exists(LOG_FILE):
#     with open(LOG_FILE, "w") as f:
#         json.dump([], f, indent=2)

# def save_log(entry):
#     try:
#         with open(LOG_FILE, "r") as f:
#             data = json.load(f)
#     except:
#         data = []
#     data.append(entry)
#     with open(LOG_FILE, "w") as f:
#         json.dump(data, f, indent=2, ensure_ascii=False)

# # ===============================================================

# BASE_USER = "geonode_xvmYN44Bvz-type-residential-country-in"
# PASSWORD  = "CHANGE_ME_PASSWORD"
# HOST      = "sg.proxy.geonode.io:11000"

# ALLOWED_STATES = {
#     "GJ": "gujarat",
#     "MP": "madhya pradesh",
#     "DL": "delhi",
#     "WB": "west bengal",
#     "MH": "maharashtra",
#     "OR": "odisha",
#     "BR": "bihar",
#     "JH": "jharkhand",
#     "CG": "chhattisgarh"
# }

# TARGET_URL = "https://unfilteredgadgets.com/"

# is_running = False
# total_visits = 0
# max_visits_val = 0
# log_text = None
# total_visits_lock = threading.Lock()
# root = None  # Will be set in GUI
# app = None

# # =============== GET PROXY =====================
# def get_random_state_proxy():
#     state_code = random.choice(list(ALLOWED_STATES.keys()))
#     state_name = ALLOWED_STATES[state_code]
#     proxy_user = f"{BASE_USER}-state-{state_name}"
#     proxy_url = f"socks5h://{proxy_user}:CHANGE_ME_PASSWORD@{HOST}"
#     return state_code, state_name, proxy_url

# # =============== FETCH IP =========================
# def fetch_ip_via_proxy(proxy_url):
#     try:
#         proxies = {"http": proxy_url, "https": proxy_url}
#         resp = requests.get("https://ipinfo.io/json", proxies=proxies, timeout=20)
#         if resp.status_code == 200:
#             return resp.json()
#     except Exception as e:
#         return str(e)
#     return None

# # =============== SPOOF CANVAS FINGERPRINT JS ====================
# spoof_canvas_js = """
# const originalGetImageData = CanvasRenderingContext2D.prototype.getImageData;
# const noiseLevel = 0.1;
# CanvasRenderingContext2D.prototype.getImageData = function(...args) {
#   const result = originalGetImageData.apply(this, args);
#   const data = result.data;
#   for (let i = 0; i < data.length; i += 4) {
#     data[i] += Math.floor((Math.random() - 0.5) * noiseLevel * 255);
#     data[i + 1] += Math.floor((Math.random() - 0.5) * noiseLevel * 255);
#     data[i + 2] += Math.floor((Math.random() - 0.5) * noiseLevel * 255);
#   }
#   return result;
# };
# """

# # =============== RANDOM ACTIONS (ENHANCED WITH LOGGING) ====================
# def perform_random_actions(driver):
#     try:
#         # Initial wait after page load
#         initial_wait = random.uniform(3, 7)
#         time.sleep(initial_wait)
#         log_text.insert(tk.END, f"[ACTIONS] Initial wait: {initial_wait:.2f}s\n")
#         log_text.see(tk.END)

#         actions = ActionChains(driver)

#         # 1. Smooth scrolling (multiple human-like scrolls)
#         scroll_count = random.randint(4, 10)
#         log_text.insert(tk.END, f"[ACTIONS] Performing {scroll_count} scrolls\n")
#         for _ in range(scroll_count):
#             scroll_amount = random.randint(300, 800) if random.random() > 0.5 else -random.randint(300, 800)
#             driver.execute_script(f"window.scrollBy({{top: {scroll_amount}, behavior: 'smooth'}});")
#             pause = random.uniform(1.2, 3.5)
#             time.sleep(pause)
#             log_text.insert(tk.END, f"[SCROLL] Amount: {scroll_amount}, Pause: {pause:.2f}s\n")
#             log_text.see(tk.END)

#         # Scroll back up a bit sometimes
#         if random.random() > 0.5:
#             driver.execute_script("window.scrollBy({top: -600, behavior: 'smooth'});")
#             time.sleep(random.uniform(1, 2.5))
#             log_text.insert(tk.END, "[SCROLL] Back up\n")
#             log_text.see(tk.END)

#         # 2. Random mouse movements
#         mouse_moves = random.randint(8, 20)
#         log_text.insert(tk.END, f"[ACTIONS] Performing {mouse_moves} mouse moves\n")
#         for _ in range(mouse_moves):
#             actions.move_by_offset(random.randint(-150, 150), random.randint(-150, 150)).perform()
#             time.sleep(random.uniform(0.2, 0.8))

#         # 3. At least 1–4 random clicks on real elements
#         clickable_selectors = "a, button, [onclick], img, div[role='button'], input[type='button'], input[type='submit'], .wp-block-button__link, li.menu-item"
#         clickable_elements = driver.find_elements(By.CSS_SELECTOR, clickable_selectors)
#         num_elements = len(clickable_elements)
#         log_text.insert(tk.END, f"[CLICKS] Found {num_elements} potential clickable elements\n")
#         log_text.see(tk.END)

#         if clickable_elements:
#             clicks_to_perform = random.randint(1, 4)
#             log_text.insert(tk.END, f"[CLICKS] Attempting {clicks_to_perform} clicks\n")
#             clicked = 0
#             random.shuffle(clickable_elements)
#             wait = WebDriverWait(driver, 5)

#             for elem in clickable_elements:
#                 if clicked >= clicks_to_perform:
#                     break
#                 try:
#                     # Scroll into view
#                     driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", elem)
#                     time.sleep(random.uniform(0.8, 2))
                    
#                     # Wait for clickable
#                     wait.until(EC.element_to_be_clickable(elem))
                    
#                     # Click
#                     actions.reset_actions()
#                     actions.move_to_element(elem).pause(random.uniform(0.3, 1)).click().perform()
#                     clicked += 1
#                     log_text.insert(tk.END, f"[CLICK SUCCESS] On element: {elem.tag_name} (text: {elem.text[:20]}...)\n")
#                     log_text.see(tk.END)
                    
#                     # Wait after click
#                     time.sleep(random.uniform(2, 6))
                    
#                     if random.random() < 0.2:
#                         break
#                 except TimeoutException:
#                     log_text.insert(tk.END, "[CLICK SKIP] Timeout waiting for element to be clickable\n")
#                     log_text.see(tk.END)
#                     continue
#                 except ElementClickInterceptedException:
#                     log_text.insert(tk.END, "[CLICK SKIP] Click intercepted (overlay?)\n")
#                     log_text.see(tk.END)
#                     continue
#                 except ElementNotInteractableException:
#                     log_text.insert(tk.END, "[CLICK SKIP] Element not interactable\n")
#                     log_text.see(tk.END)
#                     continue
#                 except Exception as e:
#                     log_text.insert(tk.END, f"[CLICK ERROR] {type(e).__name__}: {str(e)[:50]}\n")
#                     log_text.see(tk.END)
#                     continue

#         # 4. Final random dwell time to ensure total session > 15-20 seconds
#         extra_dwell = random.uniform(10, 30)  # Increased min to 10s
#         time.sleep(extra_dwell)
#         log_text.insert(tk.END, f"[ACTIONS] Extra dwell: {extra_dwell:.2f}s\n")
#         log_text.see(tk.END)

#     except Exception as e:
#         log_text.insert(tk.END, f"[ACTION ERROR] {e}\n")
#         log_text.see(tk.END)

# # =============== MAIN VISIT FUNCTION ====================
# def open_browser_with_preview():
#     global total_visits, max_visits_val, TARGET_URL, root, app

#     ua = UserAgent()

#     while True:
#         with total_visits_lock:
#             if not is_running or (max_visits_val > 0 and total_visits >= max_visits_val):
#                 break

#         state_code, state_name, proxy_url = get_random_state_proxy()
#         log_text.insert(tk.END, f"\n[TRY] State → {state_code} ({state_name})\n")
#         log_text.insert(tk.END, f"[PROXY] {proxy_url}\n")
#         log_text.see(tk.END)

#         ip_info = fetch_ip_via_proxy(proxy_url)
#         error_text = None
#         ip_address = "N/A"

#         if isinstance(ip_info, dict):
#             region = ip_info.get("region", "").lower()
#             ip_address = ip_info.get("ip", "N/A")
#         else:
#             region = ""
#             error_text = ip_info

#         log_entry = {
#             "no": total_visits + 1,
#             "time": datetime.now().strftime("%H:%M:%S"),
#             "state": state_name,
#             "state_code": state_code,
#             "ip": error_text if error_text else ip_address,
#             "url": TARGET_URL
#         }
#         save_log(log_entry)

#         if isinstance(ip_info, dict) and region in state_name.lower():
#             options = Options()
#             options.add_argument("--disable-blink-features=AutomationControlled")
#             # Removed --start-maximized, use random window size for fingerprint variety
#             common_resolutions = [(1920, 1080), (1366, 768), (1440, 900), (1536, 864), (1280, 720), (1600, 900)]
#             res = random.choice(common_resolutions)
#             options.add_argument(f"--window-size={res[0]},{res[1]}")
#             log_text.insert(tk.END, f"[FINGERPRINT] Window size: {res[0]}x{res[1]}\n")
#             options.add_experimental_option("excludeSwitches", ["enable-automation"])
#             options.add_experimental_option("useAutomationExtension", False)

#             random_user_agent = ua.random
#             options.add_argument(f"user-agent={random_user_agent}")

#             if random.random() > 0.5:
#                 options.add_argument("--disable-webgl")
#                 log_text.insert(tk.END, "[FINGERPRINT] WebGL disabled\n")

#             seleniumwire_options = {
#                 'proxy': {'http': proxy_url, 'https': proxy_url},
#                 'verify_ssl': False
#             }

#             driver = None
#             success = False
#             try:
#                 driver = webdriver.Chrome(
#                     service=Service(ChromeDriverManager().install()),
#                     options=options,
#                     seleniumwire_options=seleniumwire_options
#                 )

#                 for attempt in range(4):
#                     log_text.insert(tk.END, f"[LOAD ATTEMPT {attempt + 1}/4] {TARGET_URL}\n")
#                     log_text.see(tk.END)

#                     driver.get(TARGET_URL)
#                     time.sleep(6)  # Increased load wait to 6s for dynamic content

#                     if "502 Bad Gateway" in driver.title or "Bad Gateway" in driver.page_source[:500]:
#                         log_text.insert(tk.END, "[DETECTED] 502 Bad Gateway → Retrying...\n")
#                         log_text.see(tk.END)
#                         time.sleep(random.uniform(4, 8))
#                         continue

#                     # Spoof canvas after load
#                     driver.execute_script(spoof_canvas_js)
#                     log_text.insert(tk.END, "[FINGERPRINT] Canvas spoof applied\n")

#                     success = True
#                     with total_visits_lock:
#                         total_visits += 1
#                         root.after(0, app.update_stats)

#                     log_text.insert(tk.END, f"\n[SUCCESS] Visit #{total_visits} | IP: {ip_address}\n")
#                     log_text.insert(tk.END, f"[USER-AGENT] {random_user_agent}\n")
#                     log_text.see(tk.END)

#                     perform_random_actions(driver)

#                     log_text.insert(tk.END, "[COMPLETED] Realistic session finished.\n")
#                     log_text.see(tk.END)

#                     break

#                 if not success:
#                     log_text.insert(tk.END, "[FAILED] All attempts failed (502 or load issue).\n")
#                     log_text.see(tk.END)

#             except Exception as e:
#                 log_text.insert(tk.END, f"[BROWSER ERROR] {e}\n")
#                 log_text.see(tk.END)

#             finally:
#                 if driver:
#                     driver.quit()

#             time.sleep(random.uniform(3, 7))

#         else:
#             log_text.insert(tk.END, "[SKIPPED] Wrong state or proxy error.\n")
#             log_text.see(tk.END)
#             time.sleep(3)

# # =============== GUI ====================
# class StateIPBrowserGUI:
#     def __init__(self, root_window):
#         global root, app, log_text
#         root = root_window
#         app = self
#         root.title("9 States IP Browser + Realistic Traffic")
#         root.geometry("1000x760")
#         root.configure(bg="#0d1117")
#         self.create_widgets()

#     def create_widgets(self):
#         global log_text
#         title = tk.Label(root, text="9 STATES REALISTIC TRAFFIC BOT", font=("Consolas", 24, "bold"), fg="#58a6ff", bg="#0d1117")
#         title.pack(pady=20)

#         tk.Label(root, text="Target URL:", fg="white", bg="#0d1117").pack()
#         self.url_entry = tk.Entry(root, width=90)
#         self.url_entry.pack(pady=5)
#         self.url_entry.insert(0, TARGET_URL)

#         frame = tk.Frame(root, bg="#0d1117")
#         frame.pack(pady=10)
#         tk.Label(frame, text="Max Visits (0 = unlimited):", fg="white", bg="#0d1117").grid(row=0, column=0, padx=10)
#         self.max_visits_entry = tk.Entry(frame, width=12)
#         self.max_visits_entry.grid(row=0, column=1)
#         self.max_visits_entry.insert(0, "0")

#         tk.Label(frame, text="Concurrent Sessions:", fg="white", bg="#0d1117").grid(row=0, column=2, padx=20)
#         self.num_sessions_entry = tk.Entry(frame, width=12)
#         self.num_sessions_entry.grid(row=0, column=3)
#         self.num_sessions_entry.insert(0, "1")

#         btn_frame = tk.Frame(root, bg="#0d1117")
#         btn_frame.pack(pady=15)
#         self.start_btn = tk.Button(btn_frame, text="START", font=("Consolas", 14), bg="#238636", fg="white", width=12, command=self.start_visits)
#         self.start_btn.grid(row=0, column=0, padx=10)
#         self.stop_btn = tk.Button(btn_frame, text="STOP", font=("Consolas", 14), bg="#da3633", fg="white", width=12, command=self.stop_visits, state="disabled")
#         self.stop_btn.grid(row=0, column=1, padx=10)

#         self.stats_label = tk.Label(root, text="Total Successful Visits: 0", font=("Consolas", 16), fg="#58a6ff", bg="#0d1117")
#         self.stats_label.pack(pady=10)

#         log_text = scrolledtext.ScrolledText(root, font=("Consolas", 10), bg="#161b22", fg="#f0f6fc", height=28)
#         log_text.pack(fill="both", expand=True, padx=15, pady=10)

#     def update_stats(self):
#         self.stats_label.config(text=f"Total Successful Visits: {total_visits}")

#     def start_visits(self):
#         global is_running, TARGET_URL, max_visits_val

#         if is_running:
#             return

#         TARGET_URL = self.url_entry.get().strip()
#         max_visits_val = int(self.max_visits_entry.get() or "0")
#         num_sessions = int(self.num_sessions_entry.get() or "1")

#         is_running = True
#         self.start_btn.config(state="disabled")
#         self.stop_btn.config(state="normal")

#         for _ in range(num_sessions):
#             threading.Thread(target=open_browser_with_preview, daemon=True).start()

#     def stop_visits(self):
#         global is_running
#         is_running = False
#         self.start_btn.config(state="normal")
#         self.stop_btn.config(state="disabled")


# if __name__ == "__main__":
#     root = tk.Tk()
#     app = StateIPBrowserGUI(root)
#     root.mainloop()




# # STATE_IP_BROWSER_PREVIEW_GUI.py
# import tkinter as tk
# from tkinter import scrolledtext
# from seleniumwire import webdriver
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.chrome.options import Options
# from webdriver_manager.chrome import ChromeDriverManager
# import random
# import threading
# import json
# import time
# import requests
# from datetime import datetime
# from selenium.webdriver.common.action_chains import ActionChains
# from selenium.webdriver.common.by import By
# import os
# from fake_useragent import UserAgent
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.common.exceptions import *

# # =============== JSON LOG FILE ===============
# LOG_FILE = "visit_logs.json"

# if not os.path.exists(LOG_FILE):
#     with open(LOG_FILE, "w") as f:
#         json.dump([], f, indent=2)

# def save_log(entry):
#     try:
#         with open(LOG_FILE, "r") as f:
#             data = json.load(f)
#     except:
#         data = []
#     data.append(entry)
#     with open(LOG_FILE, "w") as f:
#         json.dump(data, f, indent=2, ensure_ascii=False)

# # ===============================================================

# BASE_USER = "geonode_xvmYN44Bvz-type-residential-country-in"
# PASSWORD  = "CHANGE_ME_PASSWORD"
# HOST      = "sg.proxy.geonode.io:11000"

# ALLOWED_STATES = {
#     "GJ": "gujarat",
#     "MP": "madhya pradesh",
#     "DL": "delhi",
#     "WB": "west bengal",
#     "MH": "maharashtra",
#     "OR": "odisha",
#     "BR": "bihar",
#     "JH": "jharkhand",
#     "CG": "chhattisgarh"
# }

# TARGET_URL = "https://partners.marcadeo.com/click?oid=320&uid=14"

# is_running = False
# total_visits = 0
# max_visits_val = 0
# log_text = None
# total_visits_lock = threading.Lock()
# root = None  # Will be set in GUI
# app = None

# # =============== GET PROXY =====================
# def get_random_state_proxy():
#     state_code = random.choice(list(ALLOWED_STATES.keys()))
#     state_name = ALLOWED_STATES[state_code]
#     proxy_user = f"{BASE_USER}-state-{state_name}"
#     proxy_url = f"socks5h://{proxy_user}:CHANGE_ME_PASSWORD@{HOST}"
#     return state_code, state_name, proxy_url

# # =============== FETCH IP =========================
# def fetch_ip_via_proxy(proxy_url):
#     try:
#         proxies = {"http": proxy_url, "https": proxy_url}
#         resp = requests.get("https://ipinfo.io/json", proxies=proxies, timeout=20)
#         if resp.status_code == 200:
#             return resp.json()
#     except Exception as e:
#         return str(e)
#     return None

# # =============== SPOOF CANVAS FINGERPRINT JS ====================
# spoof_canvas_js = """
# const originalGetImageData = CanvasRenderingContext2D.prototype.getImageData;
# const noiseLevel = 0.1;
# CanvasRenderingContext2D.prototype.getImageData = function(...args) {
#   const result = originalGetImageData.apply(this, args);
#   const data = result.data;
#   for (let i = 0; i < data.length; i += 4) {
#     data[i] += Math.floor((Math.random() - 0.5) * noiseLevel * 255);
#     data[i + 1] += Math.floor((Math.random() - 0.5) * noiseLevel * 255);
#     data[i + 2] += Math.floor((Math.random() - 0.5) * noiseLevel * 255);
#   }
#   return result;
# };
# """

# # =============== RANDOM ACTIONS (ENHANCED WITH LOGGING) ====================
# def perform_random_actions(driver):
#     try:
#         # Initial wait after page load
#         initial_wait = random.uniform(3, 7)
#         time.sleep(initial_wait)
#         log_text.insert(tk.END, f"[ACTIONS] Initial wait: {initial_wait:.2f}s\n")
#         log_text.see(tk.END)

#         actions = ActionChains(driver)

#         # 1. Smooth scrolling (multiple human-like scrolls)
#         scroll_count = random.randint(4, 10)
#         log_text.insert(tk.END, f"[ACTIONS] Performing {scroll_count} scrolls\n")
#         for _ in range(scroll_count):
#             scroll_amount = random.randint(300, 800) if random.random() > 0.5 else -random.randint(300, 800)
#             driver.execute_script(f"window.scrollBy({{top: {scroll_amount}, behavior: 'smooth'}});")
#             pause = random.uniform(1.2, 3.5)
#             time.sleep(pause)
#             log_text.insert(tk.END, f"[SCROLL] Amount: {scroll_amount}, Pause: {pause:.2f}s\n")
#             log_text.see(tk.END)

#         # Scroll back up a bit sometimes
#         if random.random() > 0.5:
#             driver.execute_script("window.scrollBy({top: -600, behavior: 'smooth'});")
#             time.sleep(random.uniform(1, 2.5))
#             log_text.insert(tk.END, "[SCROLL] Back up\n")
#             log_text.see(tk.END)

#         # 2. Random mouse movements (smaller offsets to avoid out of bounds)
#         mouse_moves = random.randint(8, 20)
#         log_text.insert(tk.END, f"[ACTIONS] Performing {mouse_moves} mouse moves\n")
#         for _ in range(mouse_moves):
#             try:
#                 actions.reset_actions()  # Reset to prevent offset buildup
#                 actions.move_by_offset(random.randint(-100, 100), random.randint(-100, 100)).perform()
#                 time.sleep(random.uniform(0.2, 0.8))
#             except MoveTargetOutOfBoundsException:
#                 log_text.insert(tk.END, "[MOUSE SKIP] Out of bounds - skipping move\n")
#                 continue

#         # 3. At least 1–4 random clicks on real elements (enhanced selectors and JS fallback)
#         clickable_selectors = "a, button, [onclick], img, div[role='button'], input[type='button'], input[type='submit'], .wp-block-button__link, li.menu-item, .view-all, a[href]"
#         clickable_elements = driver.find_elements(By.CSS_SELECTOR, clickable_selectors)
#         num_elements = len(clickable_elements)
#         log_text.insert(tk.END, f"[CLICKS] Found {num_elements} potential clickable elements\n")
#         log_text.see(tk.END)

#         if clickable_elements:
#             clicks_to_perform = random.randint(1, 4)
#             log_text.insert(tk.END, f"[CLICKS] Attempting {clicks_to_perform} clicks\n")
#             clicked = 0
#             random.shuffle(clickable_elements)
#             wait = WebDriverWait(driver, 5)

#             for elem in clickable_elements:
#                 if clicked >= clicks_to_perform:
#                     break
#                 try:
#                     # Scroll into view
#                     driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", elem)
#                     time.sleep(random.uniform(0.8, 2))
                    
#                     # Wait for clickable
#                     wait.until(EC.element_to_be_clickable(elem))
                    
#                     # Try regular click
#                     actions.reset_actions()
#                     actions.move_to_element(elem).pause(random.uniform(0.3, 1)).click().perform()
#                     clicked += 1
#                     log_text.insert(tk.END, f"[CLICK SUCCESS] Regular click on {elem.tag_name} (text: {elem.text[:20]}...)\n")
                    
#                 except (ElementClickInterceptedException, ElementNotInteractableException):
#                     try:
#                         # JS fallback click
#                         driver.execute_script("arguments[0].click();", elem)
#                         clicked += 1
#                         log_text.insert(tk.END, f"[CLICK SUCCESS] JS fallback on {elem.tag_name} (text: {elem.text[:20]}...)\n")
#                     except Exception as js_e:
#                         log_text.insert(tk.END, f"[CLICK ERROR] JS fallback failed: {type(js_e).__name__}\n")
#                         continue
                
#                 except TimeoutException:
#                     log_text.insert(tk.END, "[CLICK SKIP] Timeout waiting for element to be clickable\n")
#                     continue
                
#                 except Exception as e:
#                     log_text.insert(tk.END, f"[CLICK ERROR] {type(e).__name__}: {str(e)[:50]}\n")
#                     continue
                
#                 finally:
#                     # Wait after click (simulate reading new content, good for page navigation)
#                     time.sleep(random.uniform(2, 6))
                    
#                     if random.random() < 0.2:
#                         break

#         # 4. Final random dwell time to ensure total session > 15-20 seconds
#         extra_dwell = random.uniform(10, 30)  # Increased min to 10s
#         time.sleep(extra_dwell)
#         log_text.insert(tk.END, f"[ACTIONS] Extra dwell: {extra_dwell:.2f}s\n")
#         log_text.see(tk.END)

#     except Exception as e:
#         log_text.insert(tk.END, f"[ACTION ERROR] {e}\n")
#         log_text.see(tk.END)

# # =============== MAIN VISIT FUNCTION ====================
# def open_browser_with_preview():
#     global total_visits, max_visits_val, TARGET_URL, root, app

#     ua = UserAgent()

#     while True:
#         with total_visits_lock:
#             if not is_running or (max_visits_val > 0 and total_visits >= max_visits_val):
#                 break

#         state_code, state_name, proxy_url = get_random_state_proxy()
#         log_text.insert(tk.END, f"\n[TRY] State → {state_code} ({state_name})\n")
#         log_text.insert(tk.END, f"[PROXY] {proxy_url}\n")
#         log_text.see(tk.END)

#         ip_info = fetch_ip_via_proxy(proxy_url)
#         error_text = None
#         ip_address = "N/A"

#         if isinstance(ip_info, dict):
#             region = ip_info.get("region", "").lower()
#             ip_address = ip_info.get("ip", "N/A")
#         else:
#             region = ""
#             error_text = ip_info

#         log_entry = {
#             "no": total_visits + 1,
#             "time": datetime.now().strftime("%H:%M:%S"),
#             "state": state_name,
#             "state_code": state_code,
#             "ip": error_text if error_text else ip_address,
#             "url": TARGET_URL
#         }
#         save_log(log_entry)

#         if isinstance(ip_info, dict) and region in state_name.lower():
#             options = Options()
#             options.add_argument("--disable-blink-features=AutomationControlled")
#             # Removed --start-maximized, use random window size for fingerprint variety
#             common_resolutions = [(1920, 1080), (1366, 768), (1440, 900), (1536, 864), (1280, 720), (1600, 900)]
#             res = random.choice(common_resolutions)
#             options.add_argument(f"--window-size={res[0]},{res[1]}")
#             log_text.insert(tk.END, f"[FINGERPRINT] Window size: {res[0]}x{res[1]}\n")
#             options.add_experimental_option("excludeSwitches", ["enable-automation"])
#             options.add_experimental_option("useAutomationExtension", False)

#             random_user_agent = ua.random
#             options.add_argument(f"user-agent={random_user_agent}")

#             if random.random() > 0.5:
#                 options.add_argument("--disable-webgl")
#                 log_text.insert(tk.END, "[FINGERPRINT] WebGL disabled\n")

#             # Memory optimization: Disable images/extensions if needed
#             options.add_argument("--disable-extensions")
#             prefs = {"profile.managed_default_content_settings.images": 2}  # Disable images to save memory
#             options.add_experimental_option("prefs", prefs)

#             seleniumwire_options = {
#                 'proxy': {'http': proxy_url, 'https': proxy_url},
#                 'verify_ssl': False
#             }

#             driver = None
#             success = False
#             try:
#                 driver = webdriver.Chrome(
#                     service=Service(ChromeDriverManager().install()),
#                     options=options,
#                     seleniumwire_options=seleniumwire_options
#                 )

#                 for attempt in range(4):
#                     log_text.insert(tk.END, f"[LOAD ATTEMPT {attempt + 1}/4] {TARGET_URL}\n")
#                     log_text.see(tk.END)

#                     driver.get(TARGET_URL)
#                     time.sleep(6)  # Increased load wait to 6s for dynamic content

#                     if "502 Bad Gateway" in driver.title or "Bad Gateway" in driver.page_source[:500]:
#                         log_text.insert(tk.END, "[DETECTED] 502 Bad Gateway → Retrying...\n")
#                         log_text.see(tk.END)
#                         time.sleep(random.uniform(4, 8))
#                         continue

#                     # Spoof canvas after load
#                     driver.execute_script(spoof_canvas_js)
#                     log_text.insert(tk.END, "[FINGERPRINT] Canvas spoof applied\n")

#                     success = True
#                     with total_visits_lock:
#                         total_visits += 1
#                         root.after(0, app.update_stats)

#                     log_text.insert(tk.END, f"\n[SUCCESS] Visit #{total_visits} | IP: {ip_address}\n")
#                     log_text.insert(tk.END, f"[USER-AGENT] {random_user_agent}\n")
#                     log_text.see(tk.END)

#                     perform_random_actions(driver)

#                     log_text.insert(tk.END, "[COMPLETED] Realistic session finished.\n")
#                     log_text.see(tk.END)

#                     break

#                 if not success:
#                     log_text.insert(tk.END, "[FAILED] All attempts failed (502 or load issue).\n")
#                     log_text.see(tk.END)

#             except Exception as e:
#                 log_text.insert(tk.END, f"[BROWSER ERROR] {e}\n")
#                 log_text.see(tk.END)

#             finally:
#                 if driver:
#                     driver.quit()

#             time.sleep(random.uniform(3, 7))

#         else:
#             log_text.insert(tk.END, "[SKIPPED] Wrong state or proxy error.\n")
#             log_text.see(tk.END)
#             time.sleep(3)

# # =============== GUI ====================
# class StateIPBrowserGUI:
#     def __init__(self, root_window):
#         global root, app, log_text
#         root = root_window
#         app = self
#         root.title("9 States IP Browser + Realistic Traffic")
#         root.geometry("1000x760")
#         root.configure(bg="#0d1117")
#         self.create_widgets()

#     def create_widgets(self):
#         global log_text
#         title = tk.Label(root, text="9 STATES REALISTIC TRAFFIC BOT", font=("Consolas", 24, "bold"), fg="#58a6ff", bg="#0d1117")
#         title.pack(pady=20)

#         tk.Label(root, text="Target URL:", fg="white", bg="#0d1117").pack()
#         self.url_entry = tk.Entry(root, width=90)
#         self.url_entry.pack(pady=5)
#         self.url_entry.insert(0, TARGET_URL)

#         frame = tk.Frame(root, bg="#0d1117")
#         frame.pack(pady=10)
#         tk.Label(frame, text="Max Visits (0 = unlimited):", fg="white", bg="#0d1117").grid(row=0, column=0, padx=10)
#         self.max_visits_entry = tk.Entry(frame, width=12)
#         self.max_visits_entry.grid(row=0, column=1)
#         self.max_visits_entry.insert(0, "0")

#         tk.Label(frame, text="Concurrent Sessions:", fg="white", bg="#0d1117").grid(row=0, column=2, padx=20)
#         self.num_sessions_entry = tk.Entry(frame, width=12)
#         self.num_sessions_entry.grid(row=0, column=3)
#         self.num_sessions_entry.insert(0, "1")

#         btn_frame = tk.Frame(root, bg="#0d1117")
#         btn_frame.pack(pady=15)
#         self.start_btn = tk.Button(btn_frame, text="START", font=("Consolas", 14), bg="#238636", fg="white", width=12, command=self.start_visits)
#         self.start_btn.grid(row=0, column=0, padx=10)
#         self.stop_btn = tk.Button(btn_frame, text="STOP", font=("Consolas", 14), bg="#da3633", fg="white", width=12, command=self.stop_visits, state="disabled")
#         self.stop_btn.grid(row=0, column=1, padx=10)

#         self.stats_label = tk.Label(root, text="Total Successful Visits: 0", font=("Consolas", 16), fg="#58a6ff", bg="#0d1117")
#         self.stats_label.pack(pady=10)

#         log_text = scrolledtext.ScrolledText(root, font=("Consolas", 10), bg="#161b22", fg="#f0f6fc", height=28)
#         log_text.pack(fill="both", expand=True, padx=15, pady=10)

#     def update_stats(self):
#         self.stats_label.config(text=f"Total Successful Visits: {total_visits}")

#     def start_visits(self):
#         global is_running, TARGET_URL, max_visits_val

#         if is_running:
#             return

#         TARGET_URL = self.url_entry.get().strip()
#         max_visits_val = int(self.max_visits_entry.get() or "0")
#         num_sessions = int(self.num_sessions_entry.get() or "1")

#         is_running = True
#         self.start_btn.config(state="disabled")
#         self.stop_btn.config(state="normal")

#         for _ in range(num_sessions):
#             threading.Thread(target=open_browser_with_preview, daemon=True).start()

#     def stop_visits(self):
#         global is_running
#         is_running = False
#         self.start_btn.config(state="normal")
#         self.stop_btn.config(state="disabled")


# if __name__ == "__main__":
#     root = tk.Tk()
#     app = StateIPBrowserGUI(root)
#     root.mainloop()





# # STATE_IP_BROWSER_PREVIEW_GUI.py
# import tkinter as tk
# from tkinter import scrolledtext
# from seleniumwire import webdriver
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.chrome.options import Options
# from webdriver_manager.chrome import ChromeDriverManager
# import random
# import threading
# import json
# import time
# import requests
# from datetime import datetime
# from selenium.webdriver.common.action_chains import ActionChains
# from selenium.webdriver.common.by import By
# import os
# from fake_useragent import UserAgent
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.common.exceptions import *

# # =============== JSON LOG FILE ===============
# LOG_FILE = "visit_logs.json"

# if not os.path.exists(LOG_FILE):
#     with open(LOG_FILE, "w") as f:
#         json.dump([], f, indent=2)

# def save_log(entry):
#     try:
#         with open(LOG_FILE, "r") as f:
#             data = json.load(f)
#     except:
#         data = []
#     data.append(entry)
#     with open(LOG_FILE, "w") as f:
#         json.dump(data, f, indent=2, ensure_ascii=False)

# # ===============================================================

# BASE_USER = "geonode_xvmYN44Bvz-type-residential-country-in"
# PASSWORD  = "CHANGE_ME_PASSWORD"
# HOST      = "sg.proxy.geonode.io:11000"

# ALLOWED_STATES = {
#     "GJ": "gujarat",
#     "MP": "madhya pradesh",
#     "DL": "delhi",
#     "WB": "west bengal",
#     "MH": "maharashtra",
#     "OR": "odisha",
#     "BR": "bihar",
#     "JH": "jharkhand",
#     "CG": "chhattisgarh"
# }

# TARGET_URL = "https://unfilteredgadgets.com/"

# # === NEW: Referrer, Viewports, Locales, Timezones ===
# REFERRERS = [
#     "https://www.google.com/",
#     "https://www.bing.com/",
#     "https://t.co/",
#     None  # Direct traffic
# ]

# VIEWPORTS = [
#     (1280, 720), (1366, 768), (1440, 900), (1920, 1080),
#     (1024, 768), (1600, 900), (1536, 864), (800, 600),
#     (360, 640), (375, 667),
# ]

# LOCALES = [
#     "en-US", "en-GB", "fr-FR", "de-DE", "hi-IN", "es-ES", "it-IT", "pt-BR"
# ]

# TIMEZONES = [
#     "Asia/Kolkata", "Europe/London", "America/New_York",
#     "Australia/Sydney", "Asia/Tokyo", "Europe/Paris", "America/Los_Angeles"
# ]

# is_running = False
# total_visits = 0
# max_visits_val = 0
# log_text = None
# total_visits_lock = threading.Lock()
# root = None  # Will be set in GUI
# app = None

# # =============== GET PROXY =====================
# def get_random_state_proxy():
#     state_code = random.choice(list(ALLOWED_STATES.keys()))
#     state_name = ALLOWED_STATES[state_code]
#     proxy_user = f"{BASE_USER}-state-{state_name}"
#     proxy_url = f"socks5h://{proxy_user}:CHANGE_ME_PASSWORD@{HOST}"
#     return state_code, state_name, proxy_url

# # =============== FETCH IP =========================
# def fetch_ip_via_proxy(proxy_url):
#     try:
#         proxies = {"http": proxy_url, "https": proxy_url}
#         resp = requests.get("https://ipinfo.io/json", proxies=proxies, timeout=20)
#         if resp.status_code == 200:
#             return resp.json()
#     except Exception as e:
#         return str(e)
#     return None

# # =============== SPOOF CANVAS FINGERPRINT JS ====================
# spoof_canvas_js = """
# const originalGetImageData = CanvasRenderingContext2D.prototype.getImageData;
# const noiseLevel = 0.1;
# CanvasRenderingContext2D.prototype.getImageData = function(...args) {
#   const result = originalGetImageData.apply(this, args);
#   const data = result.data;
#   for (let i = 0; i < data.length; i += 4) {
#     data[i] += Math.floor((Math.random() - 0.5) * noiseLevel * 255);
#     data[i + 1] += Math.floor((Math.random() - 0.5) * noiseLevel * 255);
#     data[i + 2] += Math.floor((Math.random() - 0.5) * noiseLevel * 255);
#   }
#   return result;
# };
# """

# # =============== RANDOM ACTIONS (ENHANCED WITH LOGGING) ====================
# def perform_random_actions(driver):
#     try:
#         # Initial wait after page load
#         initial_wait = random.uniform(3, 7)
#         time.sleep(initial_wait)
#         log_text.insert(tk.END, f"[ACTIONS] Initial wait: {initial_wait:.2f}s\n")
#         log_text.see(tk.END)

#         actions = ActionChains(driver)

#         # 1. Smooth scrolling (multiple human-like scrolls)
#         scroll_count = random.randint(4, 10)
#         log_text.insert(tk.END, f"[ACTIONS] Performing {scroll_count} scrolls\n")
#         for _ in range(scroll_count):
#             scroll_amount = random.randint(300, 800) if random.random() > 0.5 else -random.randint(300, 800)
#             driver.execute_script(f"window.scrollBy({{top: {scroll_amount}, behavior: 'smooth'}});")
#             pause = random.uniform(1.2, 3.5)
#             time.sleep(pause)
#             log_text.insert(tk.END, f"[SCROLL] Amount: {scroll_amount}, Pause: {pause:.2f}s\n")
#             log_text.see(tk.END)

#         # Scroll back up a bit sometimes
#         if random.random() > 0.5:
#             driver.execute_script("window.scrollBy({top: -600, behavior: 'smooth'});")
#             time.sleep(random.uniform(1, 2.5))
#             log_text.insert(tk.END, "[SCROLL] Back up\n")
#             log_text.see(tk.END)

#         # 2. Random mouse movements (smaller offsets to avoid out of bounds)
#         mouse_moves = random.randint(8, 20)
#         log_text.insert(tk.END, f"[ACTIONS] Performing {mouse_moves} mouse moves\n")
#         for _ in range(mouse_moves):
#             try:
#                 actions.reset_actions()  # Reset to prevent offset buildup
#                 actions.move_by_offset(random.randint(-100, 100), random.randint(-100, 100)).perform()
#                 time.sleep(random.uniform(0.2, 0.8))
#             except MoveTargetOutOfBoundsException:
#                 log_text.insert(tk.END, "[MOUSE SKIP] Out of bounds - skipping move\n")
#                 continue

#         # 3. At least 1–4 random clicks on real elements (enhanced selectors and JS fallback)
#         clickable_selectors = "a, button, [onclick], img, div[role='button'], input[type='button'], input[type='submit'], .wp-block-button__link, li.menu-item, .view-all, a[href]"
#         clickable_elements = driver.find_elements(By.CSS_SELECTOR, clickable_selectors)
#         num_elements = len(clickable_elements)
#         log_text.insert(tk.END, f"[CLICKS] Found {num_elements} potential clickable elements\n")
#         log_text.see(tk.END)

#         if clickable_elements:
#             clicks_to_perform = random.randint(1, 4)
#             log_text.insert(tk.END, f"[CLICKS] Attempting {clicks_to_perform} clicks\n")
#             clicked = 0
#             random.shuffle(clickable_elements)
#             wait = WebDriverWait(driver, 5)

#             for elem in clickable_elements:
#                 if clicked >= clicks_to_perform:
#                     break
#                 try:
#                     # Scroll into view
#                     driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", elem)
#                     time.sleep(random.uniform(0.8, 2))
                    
#                     # Wait for clickable
#                     wait.until(EC.element_to_be_clickable(elem))
                    
#                     # Try regular click
#                     actions.reset_actions()
#                     actions.move_to_element(elem).pause(random.uniform(0.3, 1)).click().perform()
#                     clicked += 1
#                     log_text.insert(tk.END, f"[CLICK SUCCESS] Regular click on {elem.tag_name} (text: {elem.text[:20]}...)\n")
                    
#                 except (ElementClickInterceptedException, ElementNotInteractableException):
#                     try:
#                         # JS fallback click
#                         driver.execute_script("arguments[0].click();", elem)
#                         clicked += 1
#                         log_text.insert(tk.END, f"[CLICK SUCCESS] JS fallback on {elem.tag_name} (text: {elem.text[:20]}...)\n")
#                     except Exception as js_e:
#                         log_text.insert(tk.END, f"[CLICK ERROR] JS fallback failed: {type(js_e).__name__}\n")
#                         continue
                
#                 except TimeoutException:
#                     log_text.insert(tk.END, "[CLICK SKIP] Timeout waiting for element to be clickable\n")
#                     continue
                
#                 except Exception as e:
#                     log_text.insert(tk.END, f"[CLICK ERROR] {type(e).__name__}: {str(e)[:50]}\n")
#                     continue
                
#                 finally:
#                     # Wait after click (simulate reading new content, good for page navigation)
#                     time.sleep(random.uniform(2, 6))
                    
#                     if random.random() < 0.2:
#                         break

#         # 4. Final random dwell time to ensure total session > 15-20 seconds
#         extra_dwell = random.uniform(10, 30)  # Increased min to 10s
#         time.sleep(extra_dwell)
#         log_text.insert(tk.END, f"[ACTIONS] Extra dwell: {extra_dwell:.2f}s\n")
#         log_text.see(tk.END)

#     except Exception as e:
#         log_text.insert(tk.END, f"[ACTION ERROR] {e}\n")
#         log_text.see(tk.END)

# # =============== MAIN VISIT FUNCTION ====================
# def open_browser_with_preview():
#     global total_visits, max_visits_val, TARGET_URL, root, app

#     ua = UserAgent()

#     while True:
#         with total_visits_lock:
#             if not is_running or (max_visits_val > 0 and total_visits >= max_visits_val):
#                 break

#         state_code, state_name, proxy_url = get_random_state_proxy()
#         log_text.insert(tk.END, f"\n[TRY] State → {state_code} ({state_name})\n")
#         log_text.insert(tk.END, f"[PROXY] {proxy_url}\n")
#         log_text.see(tk.END)

#         ip_info = fetch_ip_via_proxy(proxy_url)
#         error_text = None
#         ip_address = "N/A"

#         if isinstance(ip_info, dict):
#             region = ip_info.get("region", "").lower()
#             ip_address = ip_info.get("ip", "N/A")
#         else:
#             region = ""
#             error_text = ip_info

#         log_entry = {
#             "no": total_visits + 1,
#             "time": datetime.now().strftime("%H:%M:%S"),
#             "state": state_name,
#             "state_code": state_code,
#             "ip": error_text if error_text else ip_address,
#             "url": TARGET_URL
#         }
#         save_log(log_entry)

#         if isinstance(ip_info, dict) and region in state_name.lower():
#             options = Options()
#             options.add_argument("--disable-blink-features=AutomationControlled")
#             options.add_experimental_option("excludeSwitches", ["enable-automation"])
#             options.add_experimental_option("useAutomationExtension", False)

#             # === NEW: Random viewport, locale, timezone ===
#             res = random.choice(VIEWPORTS)
#             options.add_argument(f"--window-size={res[0]},{res[1]}")
#             log_text.insert(tk.END, f"[FINGERPRINT] Window size: {res[0]}x{res[1]}\n")

#             locale = random.choice(LOCALES)
#             options.add_argument(f"--accept-lang={locale}")
#             log_text.insert(tk.END, f"[FINGERPRINT] Locale: {locale}\n")

#             timezone = random.choice(TIMEZONES)
#             options.add_argument(f"--tz={timezone}")  # Not standard, but we spoof via JS below
#             log_text.insert(tk.END, f"[FINGERPRINT] Timezone (JS): {timezone}\n")

#             random_user_agent = ua.random
#             options.add_argument(f"user-agent={random_user_agent}")

#             if random.random() > 0.5:
#                 options.add_argument("--disable-webgl")
#                 log_text.insert(tk.END, "[FINGERPRINT] WebGL disabled\n")

#             # Memory optimization
#             options.add_argument("--disable-extensions")
#             prefs = {"profile.managed_default_content_settings.images": 2}
#             options.add_experimental_option("prefs", prefs)

#             seleniumwire_options = {
#                 'proxy': {'http': proxy_url, 'https': proxy_url},
#                 'verify_ssl': False
#             }

#             driver = None
#             success = False
#             try:
#                 driver = webdriver.Chrome(
#                     service=Service(ChromeDriverManager().install()),
#                     options=options,
#                     seleniumwire_options=seleniumwire_options
#                 )

#                 # === NEW: Spoof timezone via JS ===
#                 driver.execute_cdp_cmd("Emulation.setTimezoneOverride", {"timezoneId": timezone})

#                 # === NEW: Set Referrer ===
#                 referrer = random.choice(REFERRERS)
#                 if referrer:
#                     log_text.insert(tk.END, f"[REFERRER] Simulating referral from: {referrer}\n")
#                     # First visit referrer page briefly
#                     driver.get(referrer)
#                     time.sleep(random.uniform(2, 5))  # Stay on referrer
#                     # Then go to target (referrer header will be set automatically)
#                     driver.get(TARGET_URL)
#                 else:
#                     log_text.insert(tk.END, "[REFERRER] Direct traffic (no referrer)\n")
#                     driver.get(TARGET_URL)

#                 time.sleep(6)  # Load wait for target page

#                 for attempt in range(3):  # Reduced retries since we have referrer step
#                     if "502 Bad Gateway" in driver.title or "Bad Gateway" in driver.page_source[:500]:
#                         log_text.insert(tk.END, "[DETECTED] 502 Bad Gateway → Retrying...\n")
#                         log_text.see(tk.END)
#                         time.sleep(random.uniform(4, 8))
#                         driver.get(TARGET_URL)
#                         time.sleep(6)
#                         continue

#                     # Spoof canvas after final load
#                     driver.execute_script(spoof_canvas_js)
#                     log_text.insert(tk.END, "[FINGERPRINT] Canvas spoof applied\n")

#                     success = True
#                     with total_visits_lock:
#                         total_visits += 1
#                         root.after(0, app.update_stats)

#                     log_text.insert(tk.END, f"\n[SUCCESS] Visit #{total_visits} | IP: {ip_address}\n")
#                     log_text.insert(tk.END, f"[USER-AGENT] {random_user_agent}\n")
#                     log_text.see(tk.END)

#                     perform_random_actions(driver)

#                     log_text.insert(tk.END, "[COMPLETED] Realistic session finished.\n")
#                     log_text.see(tk.END)

#                     break

#                 if not success:
#                     log_text.insert(tk.END, "[FAILED] All attempts failed (502 or load issue).\n")
#                     log_text.see(tk.END)

#             except Exception as e:
#                 log_text.insert(tk.END, f"[BROWSER ERROR] {e}\n")
#                 log_text.see(tk.END)

#             finally:
#                 if driver:
#                     driver.quit()

#             time.sleep(random.uniform(3, 7))

#         else:
#             log_text.insert(tk.END, "[SKIPPED] Wrong state or proxy error.\n")
#             log_text.see(tk.END)
#             time.sleep(3)

# # =============== GUI ====================
# class StateIPBrowserGUI:
#     def __init__(self, root_window):
#         global root, app, log_text
#         root = root_window
#         app = self
#         root.title("9 States IP Browser + Realistic Traffic")
#         root.geometry("1000x760")
#         root.configure(bg="#0d1117")
#         self.create_widgets()

#     def create_widgets(self):
#         global log_text
#         title = tk.Label(root, text="9 STATES REALISTIC TRAFFIC BOT", font=("Consolas", 24, "bold"), fg="#58a6ff", bg="#0d1117")
#         title.pack(pady=20)

#         tk.Label(root, text="Target URL:", fg="white", bg="#0d1117").pack()
#         self.url_entry = tk.Entry(root, width=90)
#         self.url_entry.pack(pady=5)
#         self.url_entry.insert(0, TARGET_URL)

#         frame = tk.Frame(root, bg="#0d1117")
#         frame.pack(pady=10)
#         tk.Label(frame, text="Max Visits (0 = unlimited):", fg="white", bg="#0d1117").grid(row=0, column=0, padx=10)
#         self.max_visits_entry = tk.Entry(frame, width=12)
#         self.max_visits_entry.grid(row=0, column=1)
#         self.max_visits_entry.insert(0, "0")

#         tk.Label(frame, text="Concurrent Sessions:", fg="white", bg="#0d1117").grid(row=0, column=2, padx=20)
#         self.num_sessions_entry = tk.Entry(frame, width=12)
#         self.num_sessions_entry.grid(row=0, column=3)
#         self.num_sessions_entry.insert(0, "1")

#         btn_frame = tk.Frame(root, bg="#0d1117")
#         btn_frame.pack(pady=15)
#         self.start_btn = tk.Button(btn_frame, text="START", font=("Consolas", 14), bg="#238636", fg="white", width=12, command=self.start_visits)
#         self.start_btn.grid(row=0, column=0, padx=10)
#         self.stop_btn = tk.Button(btn_frame, text="STOP", font=("Consolas", 14), bg="#da3633", fg="white", width=12, command=self.stop_visits, state="disabled")
#         self.stop_btn.grid(row=0, column=1, padx=10)

#         self.stats_label = tk.Label(root, text="Total Successful Visits: 0", font=("Consolas", 16), fg="#58a6ff", bg="#0d1117")
#         self.stats_label.pack(pady=10)

#         log_text = scrolledtext.ScrolledText(root, font=("Consolas", 10), bg="#161b22", fg="#f0f6fc", height=28)
#         log_text.pack(fill="both", expand=True, padx=15, pady=10)

#     def update_stats(self):
#         self.stats_label.config(text=f"Total Successful Visits: {total_visits}")

#     def start_visits(self):
#         global is_running, TARGET_URL, max_visits_val

#         if is_running:
#             return

#         TARGET_URL = self.url_entry.get().strip()
#         max_visits_val = int(self.max_visits_entry.get() or "0")
#         num_sessions = int(self.num_sessions_entry.get() or "1")

#         is_running = True
#         self.start_btn.config(state="disabled")
#         self.stop_btn.config(state="normal")

#         for _ in range(num_sessions):
#             threading.Thread(target=open_browser_with_preview, daemon=True).start()

#     def stop_visits(self):
#         global is_running
#         is_running = False
#         self.start_btn.config(state="normal")
#         self.stop_btn.config(state="disabled")


# if __name__ == "__main__":
#     root = tk.Tk()
#     app = StateIPBrowserGUI(root)
#     root.mainloop()





# # STATE_IP_BROWSER_PREVIEW_GUI.py
# import tkinter as tk
# from tkinter import scrolledtext
# from seleniumwire import webdriver
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.chrome.options import Options
# from webdriver_manager.chrome import ChromeDriverManager
# import random
# import threading
# import json
# import time
# import requests
# from datetime import datetime
# from selenium.webdriver.common.action_chains import ActionChains
# from selenium.webdriver.common.by import By
# import os
# from fake_useragent import UserAgent
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.common.exceptions import *

# # =============== JSON LOG FILE ===============
# LOG_FILE = "visit_logs.json"

# if not os.path.exists(LOG_FILE):
#     with open(LOG_FILE, "w") as f:
#         json.dump([], f, indent=2)

# def save_log(entry):
#     try:
#         with open(LOG_FILE, "r") as f:
#             data = json.load(f)
#     except:
#         data = []
#     data.append(entry)
#     with open(LOG_FILE, "w") as f:
#         json.dump(data, f, indent=2, ensure_ascii=False)

# # ===============================================================

# BASE_USER = "geonode_xvmYN44Bvz-type-residential-country-in"
# PASSWORD  = "CHANGE_ME_PASSWORD"
# HOST      = "sg.proxy.geonode.io:11000"

# ALLOWED_STATES = {
#     "GJ": "gujarat",
#     "MP": "madhya pradesh",
#     "DL": "delhi",
#     "WB": "west bengal",
#     "MH": "maharashtra",
#     "OR": "odisha",
#     "BR": "bihar",
#     "JH": "jharkhand",
#     "CG": "chhattisgarh"
# }

# TARGET_URL = "https://unfilteredgadgets.com/"

# # === NEW: Referrer, Viewports, Locales, Timezones ===
# REFERRERS = [
#     "https://www.google.com/",
#     "https://www.bing.com/",
#     "https://t.co/",
#     None  # Direct traffic
# ]

# VIEWPORTS = [
#     (1280, 720), (1366, 768), (1440, 900), (1920, 1080),
#     (1024, 768), (1600, 900), (1536, 864), (800, 600),
#     (360, 640), (375, 667),
# ]

# LOCALES = [
#     "en-US", "en-GB", "fr-FR", "de-DE", "hi-IN", "es-ES", "it-IT", "pt-BR"
# ]

# TIMEZONES = [
#     "Asia/Kolkata", "Europe/London", "America/New_York",
#     "Australia/Sydney", "Asia/Tokyo", "Europe/Paris", "America/Los_Angeles"
# ]

# is_running = False
# total_visits = 0
# max_visits_val = 0
# log_text = None
# total_visits_lock = threading.Lock()
# root = None  # Will be set in GUI
# app = None

# # =============== GET PROXY =====================
# def get_random_state_proxy():
#     state_code = random.choice(list(ALLOWED_STATES.keys()))
#     state_name = ALLOWED_STATES[state_code]
#     proxy_user = f"{BASE_USER}-state-{state_name}"
#     proxy_url = f"socks5h://{proxy_user}:CHANGE_ME_PASSWORD@{HOST}"
#     return state_code, state_name, proxy_url

# # =============== FETCH IP =========================
# def fetch_ip_via_proxy(proxy_url):
#     try:
#         proxies = {"http": proxy_url, "https": proxy_url}
#         resp = requests.get("https://ipinfo.io/json", proxies=proxies, timeout=20)
#         if resp.status_code == 200:
#             return resp.json()
#     except Exception as e:
#         return str(e)
#     return None

# # =============== SPOOF CANVAS FINGERPRINT JS ====================
# spoof_canvas_js = """
# const originalGetImageData = CanvasRenderingContext2D.prototype.getImageData;
# const noiseLevel = 0.1;
# CanvasRenderingContext2D.prototype.getImageData = function(...args) {
#   const result = originalGetImageData.apply(this, args);
#   const data = result.data;
#   for (let i = 0; i < data.length; i += 4) {
#     data[i] += Math.floor((Math.random() - 0.5) * noiseLevel * 255);
#     data[i + 1] += Math.floor((Math.random() - 0.5) * noiseLevel * 255);
#     data[i + 2] += Math.floor((Math.random() - 0.5) * noiseLevel * 255);
#   }
#   return result;
# };
# """

# # =============== RANDOM ACTIONS (ENHANCED WITH LOGGING) ====================
# def perform_random_actions(driver):
#     try:
#         # Initial wait after page load
#         initial_wait = random.uniform(3, 7)
#         time.sleep(initial_wait)
#         log_text.insert(tk.END, f"[ACTIONS] Initial wait: {initial_wait:.2f}s\n")
#         log_text.see(tk.END)

#         actions = ActionChains(driver)

#         # 1. Smooth scrolling (multiple human-like scrolls)
#         scroll_count = random.randint(4, 10)
#         log_text.insert(tk.END, f"[ACTIONS] Performing {scroll_count} scrolls\n")
#         for _ in range(scroll_count):
#             scroll_amount = random.randint(300, 800) if random.random() > 0.5 else -random.randint(300, 800)
#             driver.execute_script(f"window.scrollBy({{top: {scroll_amount}, behavior: 'smooth'}});")
#             pause = random.uniform(1.2, 3.5)
#             time.sleep(pause)
#             log_text.insert(tk.END, f"[SCROLL] Amount: {scroll_amount}, Pause: {pause:.2f}s\n")
#             log_text.see(tk.END)

#         # Scroll back up a bit sometimes
#         if random.random() > 0.5:
#             driver.execute_script("window.scrollBy({top: -600, behavior: 'smooth'});")
#             time.sleep(random.uniform(1, 2.5))
#             log_text.insert(tk.END, "[SCROLL] Back up\n")
#             log_text.see(tk.END)

#         # 2. Random mouse movements (smaller offsets to avoid out of bounds)
#         mouse_moves = random.randint(8, 20)
#         log_text.insert(tk.END, f"[ACTIONS] Performing {mouse_moves} mouse moves\n")
#         for _ in range(mouse_moves):
#             try:
#                 actions.reset_actions()  # Reset to prevent offset buildup
#                 actions.move_by_offset(random.randint(-100, 100), random.randint(-100, 100)).perform()
#                 time.sleep(random.uniform(0.2, 0.8))
#             except MoveTargetOutOfBoundsException:
#                 log_text.insert(tk.END, "[MOUSE SKIP] Out of bounds - skipping move\n")
#                 continue

#         # 3. At least 1–4 random clicks on real elements (enhanced selectors and JS fallback)
#         clickable_selectors = "a, button, [onclick], img, div[role='button'], input[type='button'], input[type='submit'], .wp-block-button__link, li.menu-item, .view-all, a[href]"
#         clickable_elements = driver.find_elements(By.CSS_SELECTOR, clickable_selectors)
#         num_elements = len(clickable_elements)
#         log_text.insert(tk.END, f"[CLICKS] Found {num_elements} potential clickable elements\n")
#         log_text.see(tk.END)

#         if clickable_elements:
#             clicks_to_perform = random.randint(1, 4)
#             log_text.insert(tk.END, f"[CLICKS] Attempting {clicks_to_perform} clicks\n")
#             clicked = 0
#             random.shuffle(clickable_elements)
#             wait = WebDriverWait(driver, 5)

#             for elem in clickable_elements:
#                 if clicked >= clicks_to_perform:
#                     break
#                 try:
#                     # Scroll into view
#                     driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", elem)
#                     time.sleep(random.uniform(0.8, 2))
                    
#                     # Wait for clickable
#                     wait.until(EC.element_to_be_clickable(elem))
                    
#                     # Try regular click
#                     actions.reset_actions()
#                     actions.move_to_element(elem).pause(random.uniform(0.3, 1)).click().perform()
#                     clicked += 1
#                     log_text.insert(tk.END, f"[CLICK SUCCESS] Regular click on {elem.tag_name} (text: {elem.text[:20]}...)\n")
                    
#                 except (ElementClickInterceptedException, ElementNotInteractableException):
#                     try:
#                         # JS fallback click
#                         driver.execute_script("arguments[0].click();", elem)
#                         clicked += 1
#                         log_text.insert(tk.END, f"[CLICK SUCCESS] JS fallback on {elem.tag_name} (text: {elem.text[:20]}...)\n")
#                     except Exception as js_e:
#                         log_text.insert(tk.END, f"[CLICK ERROR] JS fallback failed: {type(js_e).__name__}\n")
#                         continue
                
#                 except TimeoutException:
#                     log_text.insert(tk.END, "[CLICK SKIP] Timeout waiting for element to be clickable\n")
#                     continue
                
#                 except Exception as e:
#                     log_text.insert(tk.END, f"[CLICK ERROR] {type(e).__name__}: {str(e)[:50]}\n")
#                     continue
                
#                 finally:
#                     # Wait after click (simulate reading new content, good for page navigation)
#                     time.sleep(random.uniform(2, 6))
                    
#                     if random.random() < 0.2:
#                         break

#         # 4. Final random dwell time to ensure total session > 15-20 seconds
#         extra_dwell = random.uniform(15, 30)  # Updated min to 15s
#         time.sleep(extra_dwell)
#         log_text.insert(tk.END, f"[ACTIONS] Extra dwell: {extra_dwell:.2f}s\n")
#         log_text.see(tk.END)

#     except Exception as e:
#         log_text.insert(tk.END, f"[ACTION ERROR] {e}\n")
#         log_text.see(tk.END)

# # =============== MAIN VISIT FUNCTION ====================
# def open_browser_with_preview():
#     global total_visits, max_visits_val, TARGET_URL, root, app

#     ua = UserAgent()

#     while True:
#         with total_visits_lock:
#             if not is_running or (max_visits_val > 0 and total_visits >= max_visits_val):
#                 break

#         state_code, state_name, proxy_url = get_random_state_proxy()
#         log_text.insert(tk.END, f"\n[TRY] State → {state_code} ({state_name})\n")
#         log_text.insert(tk.END, f"[PROXY] {proxy_url}\n")
#         log_text.see(tk.END)

#         ip_info = fetch_ip_via_proxy(proxy_url)
#         error_text = None
#         ip_address = "N/A"

#         if isinstance(ip_info, dict):
#             region = ip_info.get("region", "").lower()
#             ip_address = ip_info.get("ip", "N/A")
#         else:
#             region = ""
#             error_text = ip_info

#         log_entry = {
#             "no": total_visits + 1,
#             "time": datetime.now().strftime("%H:%M:%S"),
#             "state": state_name,
#             "state_code": state_code,
#             "ip": error_text if error_text else ip_address,
#             "url": TARGET_URL
#         }
#         save_log(log_entry)

#         if isinstance(ip_info, dict) and region in state_name.lower():
#             options = Options()
#             options.add_argument("--disable-blink-features=AutomationControlled")
#             options.add_experimental_option("excludeSwitches", ["enable-automation"])
#             options.add_experimental_option("useAutomationExtension", False)

#             # === NEW: Random viewport, locale, timezone ===
#             res = random.choice(VIEWPORTS)
#             options.add_argument(f"--window-size={res[0]},{res[1]}")
#             log_text.insert(tk.END, f"[FINGERPRINT] Window size: {res[0]}x{res[1]}\n")

#             locale = random.choice(LOCALES)
#             options.add_argument(f"--accept-lang={locale}")
#             log_text.insert(tk.END, f"[FINGERPRINT] Locale: {locale}\n")

#             timezone = random.choice(TIMEZONES)
#             options.add_argument(f"--tz={timezone}")  # Not standard, but we spoof via JS below
#             log_text.insert(tk.END, f"[FINGERPRINT] Timezone (JS): {timezone}\n")

#             random_user_agent = ua.random
#             options.add_argument(f"user-agent={random_user_agent}")

#             if random.random() > 0.5:
#                 options.add_argument("--disable-webgl")
#                 log_text.insert(tk.END, "[FINGERPRINT] WebGL disabled\n")

#             # Memory optimization
#             options.add_argument("--disable-extensions")
#             prefs = {"profile.managed_default_content_settings.images": 2}
#             options.add_experimental_option("prefs", prefs)

#             seleniumwire_options = {
#                 'proxy': {'http': proxy_url, 'https': proxy_url},
#                 'verify_ssl': False
#             }

#             driver = None
#             success = False
#             try:
#                 driver = webdriver.Chrome(
#                     service=Service(ChromeDriverManager().install()),
#                     options=options,
#                     seleniumwire_options=seleniumwire_options
#                 )

#                 # === NEW: Spoof timezone via JS ===
#                 driver.execute_cdp_cmd("Emulation.setTimezoneOverride", {"timezoneId": timezone})

#                 # === NEW: Set Referrer ===
#                 # 50-50 ratio: 50% direct (None), 50% organic
#                 if random.random() < 0.5:
#                     referrer = None
#                     log_text.insert(tk.END, "[REFERRER] Direct traffic (no referrer)\n")
#                 else:
#                     referrer = random.choice([r for r in REFERRERS if r is not None])
#                     log_text.insert(tk.END, f"[REFERRER] Simulating referral from: {referrer}\n")

#                 if referrer:
#                     # First visit referrer page briefly
#                     driver.get(referrer)
#                     time.sleep(random.uniform(2, 5))  # Stay on referrer
#                     # Then go to target (referrer header will be set automatically)
#                     driver.get(TARGET_URL)
#                 else:
#                     driver.get(TARGET_URL)

#                 time.sleep(6)  # Load wait for target page

#                 for attempt in range(3):  # Reduced retries since we have referrer step
#                     if "502 Bad Gateway" in driver.title or "Bad Gateway" in driver.page_source[:500]:
#                         log_text.insert(tk.END, "[DETECTED] 502 Bad Gateway → Retrying...\n")
#                         log_text.see(tk.END)
#                         time.sleep(random.uniform(4, 8))
#                         driver.get(TARGET_URL)
#                         time.sleep(6)
#                         continue

#                     # Spoof canvas after final load
#                     driver.execute_script(spoof_canvas_js)
#                     log_text.insert(tk.END, "[FINGERPRINT] Canvas spoof applied\n")

#                     success = True
#                     with total_visits_lock:
#                         total_visits += 1
#                         root.after(0, app.update_stats)

#                     log_text.insert(tk.END, f"\n[SUCCESS] Visit #{total_visits} | IP: {ip_address}\n")
#                     log_text.insert(tk.END, f"[USER-AGENT] {random_user_agent}\n")
#                     log_text.see(tk.END)

#                     perform_random_actions(driver)

#                     log_text.insert(tk.END, "[COMPLETED] Realistic session finished.\n")
#                     log_text.see(tk.END)

#                     break

#                 if not success:
#                     log_text.insert(tk.END, "[FAILED] All attempts failed (502 or load issue).\n")
#                     log_text.see(tk.END)

#             except Exception as e:
#                 log_text.insert(tk.END, f"[BROWSER ERROR] {e}\n")
#                 log_text.see(tk.END)

#             finally:
#                 if driver:
#                     driver.quit()

#             time.sleep(random.uniform(3, 7))

#         else:
#             log_text.insert(tk.END, "[SKIPPED] Wrong state or proxy error.\n")
#             log_text.see(tk.END)
#             time.sleep(3)

# # =============== GUI ====================
# class StateIPBrowserGUI:
#     def __init__(self, root_window):
#         global root, app, log_text
#         root = root_window
#         app = self
#         root.title("9 States IP Browser + Realistic Traffic")
#         root.geometry("1000x760")
#         root.configure(bg="#0d1117")
#         self.create_widgets()

#     def create_widgets(self):
#         global log_text
#         title = tk.Label(root, text="9 STATES REALISTIC TRAFFIC BOT", font=("Consolas", 24, "bold"), fg="#58a6ff", bg="#0d1117")
#         title.pack(pady=20)

#         tk.Label(root, text="Target URL:", fg="white", bg="#0d1117").pack()
#         self.url_entry = tk.Entry(root, width=90)
#         self.url_entry.pack(pady=5)
#         self.url_entry.insert(0, TARGET_URL)

#         frame = tk.Frame(root, bg="#0d1117")
#         frame.pack(pady=10)
#         tk.Label(frame, text="Max Visits (0 = unlimited):", fg="white", bg="#0d1117").grid(row=0, column=0, padx=10)
#         self.max_visits_entry = tk.Entry(frame, width=12)
#         self.max_visits_entry.grid(row=0, column=1)
#         self.max_visits_entry.insert(0, "0")

#         tk.Label(frame, text="Concurrent Sessions:", fg="white", bg="#0d1117").grid(row=0, column=2, padx=20)
#         self.num_sessions_entry = tk.Entry(frame, width=12)
#         self.num_sessions_entry.grid(row=0, column=3)
#         self.num_sessions_entry.insert(0, "1")

#         btn_frame = tk.Frame(root, bg="#0d1117")
#         btn_frame.pack(pady=15)
#         self.start_btn = tk.Button(btn_frame, text="START", font=("Consolas", 14), bg="#238636", fg="white", width=12, command=self.start_visits)
#         self.start_btn.grid(row=0, column=0, padx=10)
#         self.stop_btn = tk.Button(btn_frame, text="STOP", font=("Consolas", 14), bg="#da3633", fg="white", width=12, command=self.stop_visits, state="disabled")
#         self.stop_btn.grid(row=0, column=1, padx=10)

#         self.stats_label = tk.Label(root, text="Total Successful Visits: 0", font=("Consolas", 16), fg="#58a6ff", bg="#0d1117")
#         self.stats_label.pack(pady=10)

#         log_text = scrolledtext.ScrolledText(root, font=("Consolas", 10), bg="#161b22", fg="#f0f6fc", height=28)
#         log_text.pack(fill="both", expand=True, padx=15, pady=10)

#     def update_stats(self):
#         self.stats_label.config(text=f"Total Successful Visits: {total_visits}")

#     def start_visits(self):
#         global is_running, TARGET_URL, max_visits_val

#         if is_running:
#             return

#         TARGET_URL = self.url_entry.get().strip()
#         max_visits_val = int(self.max_visits_entry.get() or "0")
#         num_sessions = int(self.num_sessions_entry.get() or "1")

#         is_running = True
#         self.start_btn.config(state="disabled")
#         self.stop_btn.config(state="normal")

#         for _ in range(num_sessions):
#             threading.Thread(target=open_browser_with_preview, daemon=True).start()

#     def stop_visits(self):
#         global is_running
#         is_running = False
#         self.start_btn.config(state="normal")
#         self.stop_btn.config(state="disabled")


# if __name__ == "__main__":
#     root = tk.Tk()
#     app = StateIPBrowserGUI(root)
#     root.mainloop()


# import os
# import time
# import random
# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.common.action_chains import ActionChains
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from webdriver_manager.chrome import ChromeDriverManager

# # ================= CONFIG =================
# TARGET_URL = "https://greendotball.com/?utm_source=herody&utm_medium=2"   # ✅ apni site ka URL
# IMAGE_FOLDER = "images"                        # ✅ images folder

# SELECTORS = {
#     "file_input": (By.ID, "fileInput"),
#     "phone_input": (By.CSS_SELECTOR, "input.mobile-number"),
#     "checkbox":   (By.ID, "termsCheckbox"),
#     "slider_btn": (By.ID, "slideButton"),
#     "slider_bar": (By.ID, "slideTrack"),
# }

# # ================= UTILS =================
# def generate_random_phone():
#     start = random.choice(["9", "8", "7", "6"])
#     return start + "".join(str(random.randint(0, 9)) for _ in range(9))

# def get_random_image():
#     folder = os.path.join(os.getcwd(), IMAGE_FOLDER)
#     images = [
#         os.path.join(folder, f)
#         for f in os.listdir(folder)
#         if f.lower().endswith((".jpg", ".jpeg", ".png"))
#     ]
#     if not images:
#         raise Exception("Images folder is empty")
#     return random.choice(images)

# # ================= MAIN AUTOMATION =================
# def run_bot():
#     options = Options()
#     options.add_argument("--start-maximized")

#     driver = webdriver.Chrome(
#         service=Service(ChromeDriverManager().install()),
#         options=options
#     )

#     wait = WebDriverWait(driver, 20)

#     try:
#         print("[INFO] Opening website...")
#         driver.get(TARGET_URL)

#         # ---------- IMAGE UPLOAD ----------
#         print("[INFO] Uploading image...")
#         image_path = get_random_image()

#         file_input = wait.until(
#             EC.presence_of_element_located(SELECTORS["file_input"])
#         )
#         file_input.send_keys(image_path)
#         time.sleep(2)

#         # ---------- PHONE NUMBER ----------
#         print("[INFO] Filling phone number...")
#         phone_input = wait.until(
#             EC.presence_of_element_located(SELECTORS["phone_input"])
#         )
#         phone_number = generate_random_phone()
#         phone_input.clear()
#         phone_input.send_keys(phone_number)
#         time.sleep(1)

#         # ---------- CHECKBOX ----------
#         print("[INFO] Clicking checkbox...")
#         checkbox = wait.until(
#             EC.element_to_be_clickable(SELECTORS["checkbox"])
#         )
#         if not checkbox.is_selected():
#             checkbox.click()
#         time.sleep(1)

#         # ---------- SLIDER SUBMIT ----------
#         print("[INFO] Dragging slider...")
#         slider_btn = wait.until(
#             EC.presence_of_element_located(SELECTORS["slider_btn"])
#         )
#         slider_bar = wait.until(
#             EC.presence_of_element_located(SELECTORS["slider_bar"])
#         )

#         width = slider_bar.size["width"]
#         move_x = width - 50

#         actions = ActionChains(driver)
#         actions.click_and_hold(slider_btn)
#         actions.move_by_offset(move_x, 0)
#         actions.release()
#         actions.perform()

#         print("[SUCCESS] Form submitted successfully 🎉")
#         time.sleep(5)

#     except Exception as e:
#         print("[ERROR]", e)

#     finally:
#         driver.quit()

# # ================= RUN =================
# if __name__ == "__main__":
#     run_bot()

#script change force js checkbox click updated

# import os
# import time
# import random
# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.common.action_chains import ActionChains
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from webdriver_manager.chrome import ChromeDriverManager

# # ================= CONFIG =================
# TARGET_URL = "https://greendotball.com/?utm_source=herody&utm_medium=2"   # Site URL
# IMAGE_FOLDER = "images"                        # Images folder ka naam

# SELECTORS = {
#     "file_input": (By.ID, "fileInput"),
#     "phone_input": (By.CSS_SELECTOR, "input.mobile-number"),
#     "checkbox":   (By.ID, "termsCheckbox"),
#     "slider_btn": (By.ID, "slideButton"),
#     "slider_bar": (By.ID, "slideTrack"),
# }

# # ================= UTILS =================
# def generate_random_phone():
#     start = random.choice(["9", "8", "7", "6"])
#     return start + "".join(str(random.randint(0, 9)) for _ in range(9))

# def get_random_image():
#     folder = os.path.join(os.getcwd(), IMAGE_FOLDER)
#     images = [
#         os.path.join(folder, f)
#         for f in os.listdir(folder)
#         if f.lower().endswith((".jpg", ".jpeg", ".png"))
#     ]
#     if not images:
#         raise Exception("Images folder khali hai bhai! Images daal")
#     return random.choice(images)

# # ================= MAIN AUTOMATION =================
# def run_bot():
#     options = Options()
#     options.add_argument("--start-maximized")
#     # options.add_argument("--headless")  # Agar hidden mein chalana ho toh uncomment kar

#     driver = webdriver.Chrome(
#         service=Service(ChromeDriverManager().install()),
#         options=options
#     )

#     wait = WebDriverWait(driver, 20)

#     try:
#         print("[INFO] Website khol raha hoon...")
#         driver.get(TARGET_URL)
#         time.sleep(4)  # Page fully load hone ka wait

#         # ---------- IMAGE UPLOAD ----------
#         print("[INFO] Random image upload kar raha hoon...")
#         image_path = get_random_image()

#         file_input = wait.until(
#             EC.presence_of_element_located(SELECTORS["file_input"])
#         )
#         driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", file_input)
#         file_input.send_keys(image_path)
#         time.sleep(2)

#         # ---------- PHONE NUMBER ----------
#         print("[INFO] Random phone number daal raha hoon...")
#         phone_input = wait.until(
#             EC.presence_of_element_located(SELECTORS["phone_input"])
#         )
#         driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", phone_input)
#         phone_number = generate_random_phone()
#         phone_input.clear()
#         phone_input.send_keys(phone_number)
#         time.sleep(1 + random.uniform(0.5, 1.5))

#         # ---------- CHECKBOX ----------
#         print("[INFO] Terms checkbox tick kar raha hoon...")
#         checkbox = wait.until(
#             EC.presence_of_element_located(SELECTORS["checkbox"])
#         )
#         driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", checkbox)
#         time.sleep(1)
        
#         # JavaScript se force click (intercepted error ka best fix)
#         driver.execute_script("arguments[0].click();", checkbox)
        
#         time.sleep(1 + random.uniform(0.3, 0.8))

#         # ---------- SLIDER SUBMIT ----------
#         print("[INFO] Slider drag kar raha hoon (human jaise)...")
#         slider_btn = wait.until(
#             EC.presence_of_element_located(SELECTORS["slider_btn"])
#         )
#         slider_bar = wait.until(
#             EC.presence_of_element_located(SELECTORS["slider_bar"])
#         )

#         driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", slider_bar)
#         time.sleep(1)

#         # Accurate distance calculate kar (button ka size minus)
#         btn_width = slider_btn.size["width"]
#         track_width = slider_bar.size["width"]
#         move_distance = track_width - btn_width - random.randint(5, 20)  # Thoda short rakha detection se bachne

#         actions = ActionChains(driver)
#         actions.move_to_element(slider_btn).click_and_hold().pause(random.uniform(0.2, 0.4))

#         # Human-like curve drag (3 parts mein)
#         actions.move_by_offset(move_distance // 3, random.randint(-8, 8))
#         actions.pause(random.uniform(0.1, 0.3))
#         actions.move_by_offset(move_distance // 3, random.randint(-12, 12))
#         actions.pause(random.uniform(0.1, 0.3))
#         actions.move_by_offset(move_distance - 2*(move_distance // 3) + random.randint(-5, 5), random.randint(-8, 8))

#         actions.pause(random.uniform(0.2, 0.5)).release().perform()

#         print("[SUCCESS] Form successfully submit ho gaya! 🎉")
#         time.sleep(8)  # Success message dekhne ke liye

#     except Exception as e:
#         print("[ERROR] Kuch galat hua:", e)

#     finally:
#         driver.quit()

# # ================= RUN =================
# if __name__ == "__main__":
#     run_bot()


# import os
# import time
# import random
# import json
# import datetime
# import threading
# import tkinter as tk
# from tkinter import messagebox, filedialog
# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.common.action_chains import ActionChains
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from webdriver_manager.chrome import ChromeDriverManager

# # ================= CONFIG =================
# LOG_FILE = "log.json"  # Log file ka naam
# SELECTORS = {
#     "file_input": (By.ID, "fileInput"),
#     "phone_input": (By.CSS_SELECTOR, "input.mobile-number"),
#     "checkbox": (By.ID, "termsCheckbox"),
#     "slider_btn": (By.ID, "slideButton"),
#     "slider_bar": (By.ID, "slideTrack"),
# }

# # ================= UTILS =================
# def generate_random_phone():
#     start = random.choice(["9", "8", "7", "6"])
#     return start + "".join(str(random.randint(0, 9)) for _ in range(9))

# def get_image_list(folder_path):
#     if not os.path.isdir(folder_path):
#         raise Exception("Folder path valid nahi hai!")
#     images = [
#         os.path.join(folder_path, f)
#         for f in os.listdir(folder_path)
#         if f.lower().endswith((".jpg", ".jpeg", ".png"))
#     ]
#     if not images:
#         raise Exception("Folder mein koi image nahi mili!")
#     # Natural sort: alphabetical (jo usually serial wise hota hai screenshots mein)
#     images.sort()
#     return images

# def load_logs():
#     if os.path.exists(LOG_FILE):
#         with open(LOG_FILE, "r", encoding="utf-8") as f:
#             return json.load(f)
#     return []

# def save_logs(logs):
#     with open(LOG_FILE, "w", encoding="utf-8") as f:
#         json.dump(logs, f, indent=4, ensure_ascii=False)

# # ================= MAIN AUTOMATION =================
# def run_bot(target_url, image_path):
#     options = Options()
#     options.add_argument("--start-maximized")
#     # options.add_argument("--headless")  # Hidden mode ke liye uncomment
#     driver = webdriver.Chrome(
#         service=Service(ChromeDriverManager().install()),
#         options=options
#     )
#     wait = WebDriverWait(driver, 20)
#     try:
#         print("[INFO] Website khol raha hoon...")
#         driver.get(target_url)
#         time.sleep(4)

#         # ---------- IMAGE UPLOAD ----------
#         print("[INFO] Image upload kar raha hoon:", os.path.basename(image_path))
#         file_input = wait.until(
#             EC.presence_of_element_located(SELECTORS["file_input"])
#         )
#         driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", file_input)
#         file_input.send_keys(image_path)
#         time.sleep(2)

#         # ---------- PHONE NUMBER ----------
#         print("[INFO] Random phone number daal raha hoon...")
#         phone_input = wait.until(
#             EC.presence_of_element_located(SELECTORS["phone_input"])
#         )
#         driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", phone_input)
#         phone_number = generate_random_phone()
#         phone_input.clear()
#         phone_input.send_keys(phone_number)
#         time.sleep(1 + random.uniform(0.5, 1.5))

#         # ---------- CHECKBOX ----------
#         print("[INFO] Terms checkbox tick kar raha hoon...")
#         checkbox = wait.until(
#             EC.presence_of_element_located(SELECTORS["checkbox"])
#         )
#         driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", checkbox)
#         time.sleep(1)
#         driver.execute_script("arguments[0].click();", checkbox)
#         time.sleep(1 + random.uniform(0.3, 0.8))

#         # ---------- SLIDER SUBMIT ----------
#         print("[INFO] Slider drag kar raha hoon (human jaise)...")
#         slider_btn = wait.until(
#             EC.presence_of_element_located(SELECTORS["slider_btn"])
#         )
#         slider_bar = wait.until(
#             EC.presence_of_element_located(SELECTORS["slider_bar"])
#         )
#         driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", slider_bar)
#         time.sleep(1)

#         btn_width = slider_btn.size["width"]
#         track_width = slider_bar.size["width"]
#         move_distance = track_width - btn_width - random.randint(5, 20)
#         actions = ActionChains(driver)
#         actions.move_to_element(slider_btn).click_and_hold().pause(random.uniform(0.2, 0.4))
#         actions.move_by_offset(move_distance // 3, random.randint(-8, 8))
#         actions.pause(random.uniform(0.1, 0.3))
#         actions.move_by_offset(move_distance // 3, random.randint(-12, 12))
#         actions.pause(random.uniform(0.1, 0.3))
#         actions.move_by_offset(move_distance - 2*(move_distance // 3) + random.randint(-5, 5), random.randint(-8, 8))
#         actions.pause(random.uniform(0.2, 0.5)).release().perform()

#         print("[SUCCESS] Form submit ho gaya! 🎉")
#         time.sleep(8)

#         return {"phone_number": phone_number, "image_name": os.path.basename(image_path)}
#     except Exception as e:
#         print("[ERROR] Kuch galat hua:", e)
#         return None
#     finally:
#         driver.quit()

# # ================= GUI =================
# stop_flag = False

# def run_loop(url_entry, folder_entry, num_entry):
#     global stop_flag
#     stop_flag = False
#     target_url = url_entry.get().strip()
#     folder_path = folder_entry.get().strip()
#     try:
#         num_visits = int(num_entry.get())
#     except ValueError:
#         messagebox.showerror("Error", "Number of visits valid integer daal!")
#         return

#     if not target_url:
#         messagebox.showerror("Error", "Target URL daal!")
#         return
#     if not folder_path:
#         messagebox.showerror("Error", "Images folder path daal!")
#         return

#     try:
#         image_list = get_image_list(folder_path)
#     except Exception as e:
#         messagebox.showerror("Error", str(e))
#         return

#     if len(image_list) < num_visits:
#         messagebox.showwarning("Warning", f"Folder mein sirf {len(image_list)} images hain, lekin {num_visits} visits maange. Sirf {len(image_list)} visits karunga.")
#         num_visits = len(image_list)

#     logs = load_logs()
#     start_visit = len(logs) + 1

#     for i in range(num_visits):
#         if stop_flag:
#             print("[INFO] Automation user ne stop kar diya.")
#             messagebox.showinfo("Stopped", "Automation rok di gayi.")
#             break

#         current_image = image_list[i]
#         print(f"[INFO] Visit {start_visit + i} shuru - Image: {os.path.basename(current_image)}")
#         result = run_bot(target_url, current_image)

#         if result:
#             timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#             log_entry = {
#                 "visit_number": start_visit + i,
#                 "timestamp": timestamp,
#                 "phone_number": result["phone_number"],
#                 "image_name": result["image_name"]
#             }
#             logs.append(log_entry)
#             save_logs(logs)
#             print(f"[INFO] Visit {start_visit + i} logged.")
#         else:
#             print(f"[WARNING] Visit {start_visit + i} fail hua, log nahi kiya.")

# def start_automation(url_entry, folder_entry, num_entry):
#     thread = threading.Thread(target=run_loop, args=(url_entry, folder_entry, num_entry))
#     thread.start()

# def stop_automation():
#     global stop_flag
#     stop_flag = True

# def browse_folder(folder_entry):
#     folder = filedialog.askdirectory()
#     if folder:
#         folder_entry.delete(0, tk.END)
#         folder_entry.insert(0, folder)

# def create_gui():
#     root = tk.Tk()
#     root.title("Automation Bot GUI")
#     root.geometry("600x300")

#     tk.Label(root, text="Target URL:").grid(row=0, column=0, padx=10, pady=10, sticky="e")
#     url_entry = tk.Entry(root, width=60)
#     url_entry.insert(0, "https://greendotball.com/?utm_source=herody&utm_medium=2")
#     url_entry.grid(row=0, column=1, padx=10, pady=10)

#     tk.Label(root, text="Images Folder Path:").grid(row=1, column=0, padx=10, pady=10, sticky="e")
#     folder_entry = tk.Entry(root, width=60)
#     folder_entry.insert(0, os.path.join(os.getcwd(), "images"))  # Default current folder ka images
#     folder_entry.grid(row=1, column=1, padx=10, pady=10)
#     browse_btn = tk.Button(root, text="Browse", command=lambda: browse_folder(folder_entry))
#     browse_btn.grid(row=1, column=2, padx=10, pady=10)

#     tk.Label(root, text="Number of Visits:").grid(row=2, column=0, padx=10, pady=10, sticky="e")
#     num_entry = tk.Entry(root, width=60)
#     num_entry.insert(0, "10")
#     num_entry.grid(row=2, column=1, padx=10, pady=10)

#     start_button = tk.Button(root, text="START", bg="green", fg="white", width=15, command=lambda: start_automation(url_entry, folder_entry, num_entry))
#     start_button.grid(row=3, column=0, columnspan=1, pady=20)

#     stop_button = tk.Button(root, text="STOP", bg="red", fg="white", width=15, command=stop_automation)
#     stop_button.grid(row=3, column=1, columnspan=1, pady=20)

#     tk.Label(root, text="Note: Attach Images Folder Path", fg="blue").grid(row=4, column=0, columnspan=3, pady=10)

#     root.mainloop()

# # ================= RUN =================
# if __name__ == "__main__":
#     create_gui()



# import os
# import time
# import random
# import json
# import datetime
# import threading
# import tkinter as tk
# from tkinter import messagebox, filedialog
# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.common.action_chains import ActionChains
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from webdriver_manager.chrome import ChromeDriverManager

# # ================= CONFIG =================
# LOG_FILE = "log.json"
# SELECTORS = {
#     "file_input": (By.ID, "fileInput"),
#     "phone_input": (By.CSS_SELECTOR, "input.mobile-number"),
#     "checkbox": (By.ID, "termsCheckbox"),
#     "slider_btn": (By.ID, "slideButton"),
#     "slider_bar": (By.ID, "slideTrack"),
# }

# # List of common realistic User-Agents (2025-2026 era)
# USER_AGENTS = [
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0",
#     "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_6_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
#     "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_6_3) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Edg/120.0.0.0",
#     "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
# ]

# # Common desktop/laptop screen resolutions (width x height)
# SCREEN_SIZES = [
#     (1920, 1080),
#     (1366, 768),
#     (1536, 864),
#     (1440, 900),
#     (1280, 720),
#     (1600, 900),
#     (2560, 1440),
#     (3840, 2160),
# ]

# # ================= UTILS =================
# def generate_random_phone():
#     start = random.choice(["9", "8", "7", "6"])
#     return start + "".join(str(random.randint(0, 9)) for _ in range(9))

# def get_image_list(folder_path):
#     if not os.path.isdir(folder_path):
#         raise Exception("Invalid folder path!")
#     valid_extensions = (".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".tiff", ".tif", ".svg")
#     images = [
#         os.path.join(folder_path, f)
#         for f in os.listdir(folder_path)
#         if f.lower().endswith(valid_extensions)
#     ]
#     if not images:
#         raise Exception("No images found in the folder!")
#     images.sort(key=lambda x: x.lower())
#     return images

# def load_logs():
#     if os.path.exists(LOG_FILE):
#         with open(LOG_FILE, "r", encoding="utf-8") as f:
#             return json.load(f)
#     return []

# def save_logs(logs):
#     with open(LOG_FILE, "w", encoding="utf-8") as f:
#         json.dump(logs, f, indent=4, ensure_ascii=False)

# # ================= MAIN AUTOMATION =================
# def run_bot(target_url, image_path):
#     # Randomly select a User-Agent and matching screen size for fingerprint variation
#     user_agent = random.choice(USER_AGENTS)
#     width, height = random.choice(SCREEN_SIZES)

#     options = Options()
#     options.add_argument(f"--user-agent={user_agent}")
#     options.add_argument(f"--window-size={width},{height}")
#     # options.add_argument("--start-maximized")  # Removed - we control size manually
#     options.add_argument("--disable-blink-features=AutomationControlled")
#     options.add_experimental_option("excludeSwitches", ["enable-automation"])
#     options.add_experimental_option("useAutomationExtension", False)

#     # Additional stealth options
#     options.add_argument("--disable-infobars")
#     options.add_argument("--no-sandbox")
#     options.add_argument("--disable-dev-shm-usage")

#     driver = webdriver.Chrome(
#         service=Service(ChromeDriverManager().install()),
#         options=options
#     )
#     wait = WebDriverWait(driver, 30)

#     try:
#         print(f"[INFO] Opening website with resolution {width}x{height} and UA: {user_agent[:60]}...")
#         driver.get(target_url)
#         time.sleep(4 + random.uniform(0, 2))  # Small random delay

#         # ---------- IMAGE UPLOAD ----------
#         print(f"[INFO] Uploading image: {os.path.basename(image_path)}")
#         file_input = wait.until(EC.presence_of_element_located(SELECTORS["file_input"]))
#         driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", file_input)
#         file_input.send_keys(image_path)
#         time.sleep(2 + random.uniform(0, 1))

#         # ---------- PHONE NUMBER ----------
#         print("[INFO] Entering random phone number...")
#         phone_input = wait.until(EC.presence_of_element_located(SELECTORS["phone_input"]))
#         driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", phone_input)
#         phone_number = generate_random_phone()
#         phone_input.clear()
#         phone_input.send_keys(phone_number)
#         time.sleep(1 + random.uniform(0.5, 1.5))

#         # ---------- CHECKBOX ----------
#         print("[INFO] Checking terms checkbox...")
#         checkbox = wait.until(EC.presence_of_element_located(SELECTORS["checkbox"]))
#         driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", checkbox)
#         time.sleep(1)
#         driver.execute_script("arguments[0].click();", checkbox)
#         time.sleep(1 + random.uniform(0.3, 0.8))

#         # ---------- SLIDER SUBMIT ----------
#         print("[INFO] Performing slider action (human-like)...")
#         slider_btn = wait.until(EC.presence_of_element_located(SELECTORS["slider_btn"]))
#         slider_bar = wait.until(EC.presence_of_element_located(SELECTORS["slider_bar"]))
#         driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", slider_bar)
#         time.sleep(1)

#         btn_width = slider_btn.size["width"]
#         track_width = slider_bar.size["width"]
#         move_distance = track_width - btn_width - random.randint(5, 20)

#         actions = ActionChains(driver)
#         actions.move_to_element(slider_btn).click_and_hold().pause(random.uniform(0.2, 0.4))
#         actions.move_by_offset(move_distance // 3, random.randint(-8, 8)).pause(random.uniform(0.1, 0.3))
#         actions.move_by_offset(move_distance // 3, random.randint(-12, 12)).pause(random.uniform(0.1, 0.3))
#         actions.move_by_offset(move_distance - 2 * (move_distance // 3) + random.randint(-5, 5), random.randint(-8, 8))
#         actions.pause(random.uniform(0.2, 0.5)).release().perform()

#         print("[SUCCESS] Form submitted successfully!")
#         time.sleep(8)

#         return {"phone_number": phone_number, "image_name": os.path.basename(image_path)}

#     except Exception as e:
#         print(f"[ERROR] Something went wrong: {e}")
#         return None
#     finally:
#         driver.quit()

# # ================= GUI =================
# stop_flag = False

# def run_loop(url_entry, folder_entry, num_entry):
#     global stop_flag
#     stop_flag = False

#     target_url = url_entry.get().strip()
#     folder_path = folder_entry.get().strip()

#     try:
#         num_visits = int(num_entry.get())
#         if num_visits <= 0:
#             raise ValueError
#     except ValueError:
#         messagebox.showerror("Error", "Please enter a valid positive integer for Number of Visits!")
#         return

#     if not target_url:
#         messagebox.showerror("Error", "Please enter Target URL!")
#         return
#     if not folder_path:
#         messagebox.showerror("Error", "Please select Images Folder Path!")
#         return

#     try:
#         image_list = get_image_list(folder_path)
#     except Exception as e:
#         messagebox.showerror("Error", str(e))
#         return

#     available_images = len(image_list)
#     if available_images < num_visits:
#         messagebox.showwarning(
#             "Warning",
#             f"Only {available_images} images found in folder, but {num_visits} visits requested.\n"
#             f"Will perform only {available_images} visits."
#         )
#         num_visits = available_images

#     logs = load_logs()
#     start_visit = len(logs) + 1

#     for i in range(num_visits):
#         if stop_flag:
#             print("[INFO] Automation stopped by user.")
#             messagebox.showinfo("Stopped", "Automation has been stopped.")
#             break

#         current_image = image_list[i]
#         print(f"[INFO] Starting Visit {start_visit + i} - Using Image: {os.path.basename(current_image)}")

#         result = run_bot(target_url, current_image)

#         if result:
#             timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#             log_entry = {
#                 "visit_number": start_visit + i,
#                 "timestamp": timestamp,
#                 "phone_number": result["phone_number"],
#                 "image_name": result["image_name"]
#             }
#             logs.append(log_entry)
#             save_logs(logs)
#             print(f"[INFO] Visit {start_visit + i} completed and logged.")
#         else:
#             print(f"[WARNING] Visit {start_visit + i} failed - not logged.")

#         if i < num_visits - 1 and not stop_flag:
#             time.sleep(random.uniform(3, 7))  # Longer natural delay between visits

# def start_automation(url_entry, folder_entry, num_entry):
#     thread = threading.Thread(target=run_loop, args=(url_entry, folder_entry, num_entry), daemon=True)
#     thread.start()

# def stop_automation():
#     global stop_flag
#     stop_flag = True
#     messagebox.showinfo("Stop", "Stopping automation after current visit completes...")

# def browse_folder(folder_entry):
#     folder = filedialog.askdirectory(title="Select Images Folder")
#     if folder:
#         folder_entry.delete(0, tk.END)
#         folder_entry.insert(0, folder)

# def create_gui():
#     root = tk.Tk()
#     root.title("Automation Bot - Fingerprint Rotation Enabled")
#     root.geometry("700x380")
#     root.resizable(False, False)

#     tk.Label(root, text="Target URL:", font=("Arial", 10, "bold")).grid(row=0, column=0, padx=15, pady=15, sticky="e")
#     url_entry = tk.Entry(root, width=70)
#     url_entry.insert(0, "https://greendotball.com/?utm_source=herody&utm_medium=26")
#     url_entry.grid(row=0, column=1, padx=10, pady=15)

#     tk.Label(root, text="Images Folder Path:", font=("Arial", 10, "bold")).grid(row=1, column=0, padx=15, pady=10, sticky="e")
#     folder_entry = tk.Entry(root, width=70)
#     folder_entry.insert(0, os.path.join(os.getcwd(), "images"))
#     folder_entry.grid(row=1, column=1, padx=10, pady=10)
#     browse_btn = tk.Button(root, text="Browse", command=lambda: browse_folder(folder_entry))
#     browse_btn.grid(row=1, column=2, padx=10, pady=10)

#     tk.Label(root, text="Number of Visits:", font=("Arial", 10, "bold")).grid(row=2, column=0, padx=15, pady=10, sticky="e")
#     num_entry = tk.Entry(root, width=70)
#     num_entry.insert(0, "10")
#     num_entry.grid(row=2, column=1, padx=10, pady=10)

#     start_button = tk.Button(root, text="START", bg="green", fg="white", font=("Arial", 12, "bold"), width=15,
#                              command=lambda: start_automation(url_entry, folder_entry, num_entry))
#     start_button.grid(row=3, column=0, pady=30)

#     stop_button = tk.Button(root, text="STOP", bg="red", fg="white", font=("Arial", 12, "bold"), width=15,
#                             command=stop_automation)
#     stop_button.grid(row=3, column=1, pady=30)

#     tk.Label(root, text="Fingerprint Rotation: Each visit uses random User-Agent + different screen resolution for better stealth.\n"
#                         "Supports all common image formats.",
#              fg="green", wraplength=650, justify="left").grid(row=4, column=0, columnspan=3, pady=15)

#     root.mainloop()

# # ================= RUN =================
# if __name__ == "__main__":
#     create_gui()


# import os
# import time
# import random
# import json
# import datetime
# import threading
# import tkinter as tk
# from tkinter import messagebox, filedialog
# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.common.action_chains import ActionChains
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from webdriver_manager.chrome import ChromeDriverManager

# # ================= CONFIG =================
# LOG_FILE = "log.json"
# SELECTORS = {
#     "file_input": (By.ID, "fileInput"),
#     "phone_input": (By.CSS_SELECTOR, "input.mobile-number"),
#     "checkbox": (By.ID, "termsCheckbox"),
#     "slider_btn": (By.ID, "slideButton"),
#     "slider_bar": (By.ID, "slideTrack"),
# }

# # List of common realistic User-Agents (2025-2026 era)
# USER_AGENTS = [
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0",
#     "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_6_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
#     "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_6_3) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Edg/120.0.0.0",
#     "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
# ]

# # Common desktop/laptop screen resolutions (width x height)
# SCREEN_SIZES = [
#     (1920, 1080),
#     (1366, 768),
#     (1536, 864),
#     (1440, 900),
#     (1280, 720),
#     (1600, 900),
#     (2560, 1440),
#     (3840, 2160),
# ]

# # ================= UTILS =================
# def generate_random_phone():
#     start = random.choice(["9", "8", "7", "6"])
#     return start + "".join(str(random.randint(0, 9)) for _ in range(9))

# def get_image_list(folder_path):
#     if not os.path.isdir(folder_path):
#         raise Exception("Invalid folder path!")
#     valid_extensions = (".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".tiff", ".tif", ".svg")
#     images = [
#         os.path.join(folder_path, f)
#         for f in os.listdir(folder_path)
#         if f.lower().endswith(valid_extensions)
#     ]
#     if not images:
#         raise Exception("No images found in the folder!")
#     images.sort(key=lambda x: x.lower())
#     return images

# def load_logs():
#     if os.path.exists(LOG_FILE):
#         with open(LOG_FILE, "r", encoding="utf-8") as f:
#             return json.load(f)
#     return []

# def save_logs(logs):
#     with open(LOG_FILE, "w", encoding="utf-8") as f:
#         json.dump(logs, f, indent=4, ensure_ascii=False)

# # ================= MAIN AUTOMATION =================
# def run_bot(target_url, image_path):
#     # Randomly select a User-Agent and matching screen size for fingerprint variation
#     user_agent = random.choice(USER_AGENTS)
#     width, height = random.choice(SCREEN_SIZES)

#     options = Options()
#     options.add_argument(f"--user-agent={user_agent}")
#     options.add_argument(f"--window-size={width},{height}")
#     # options.add_argument("--start-maximized")  # Removed - we control size manually
#     options.add_argument("--disable-blink-features=AutomationControlled")
#     options.add_experimental_option("excludeSwitches", ["enable-automation"])
#     options.add_experimental_option("useAutomationExtension", False)

#     # Additional stealth options
#     options.add_argument("--disable-infobars")
#     options.add_argument("--no-sandbox")
#     options.add_argument("--disable-dev-shm-usage")

#     driver = webdriver.Chrome(
#         service=Service(ChromeDriverManager().install()),
#         options=options
#     )
#     wait = WebDriverWait(driver, 30)

#     try:
#         print(f"[INFO] Opening website with resolution {width}x{height} and UA: {user_agent[:60]}...")
#         driver.get(target_url)
#         time.sleep(4 + random.uniform(0, 2))  # Small random delay

#         # ---------- IMAGE UPLOAD ----------
#         print(f"[INFO] Uploading image: {os.path.basename(image_path)}")
#         file_input = wait.until(EC.presence_of_element_located(SELECTORS["file_input"]))
#         driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", file_input)
#         file_input.send_keys(image_path)
#         time.sleep(2 + random.uniform(0, 1))

#         # ---------- PHONE NUMBER ----------
#         print("[INFO] Entering random phone number...")
#         phone_input = wait.until(EC.presence_of_element_located(SELECTORS["phone_input"]))
#         driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", phone_input)
#         phone_number = generate_random_phone()
#         phone_input.clear()
#         phone_input.send_keys(phone_number)
#         time.sleep(1 + random.uniform(0.5, 1.5))

#         # ---------- CHECKBOX ----------
#         print("[INFO] Checking terms checkbox...")
#         checkbox = wait.until(EC.presence_of_element_located(SELECTORS["checkbox"]))
#         driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", checkbox)
#         time.sleep(1)
#         driver.execute_script("arguments[0].click();", checkbox)
#         time.sleep(1 + random.uniform(0.3, 0.8))

#         # ---------- SLIDER SUBMIT ----------
#         print("[INFO] Performing slider action (human-like)...")
#         slider_btn = wait.until(EC.presence_of_element_located(SELECTORS["slider_btn"]))
#         slider_bar = wait.until(EC.presence_of_element_located(SELECTORS["slider_bar"]))
#         driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", slider_bar)
#         time.sleep(1)

#         btn_width = slider_btn.size["width"]
#         track_width = slider_bar.size["width"]
#         move_distance = track_width - btn_width - random.randint(5, 20)

#         actions = ActionChains(driver)
#         actions.move_to_element(slider_btn).click_and_hold().pause(random.uniform(0.2, 0.4))
#         actions.move_by_offset(move_distance // 3, random.randint(-8, 8)).pause(random.uniform(0.1, 0.3))
#         actions.move_by_offset(move_distance // 3, random.randint(-12, 12)).pause(random.uniform(0.1, 0.3))
#         actions.move_by_offset(move_distance - 2 * (move_distance // 3) + random.randint(-5, 5), random.randint(-8, 8))
#         actions.pause(random.uniform(0.2, 0.5)).release().perform()

#         print("[SUCCESS] Form submitted successfully!")
#         time.sleep(8)

#         return {"phone_number": phone_number, "image_name": os.path.basename(image_path)}

#     except Exception as e:
#         print(f"[ERROR] Something went wrong: {e}")
#         return None
#     finally:
#         driver.quit()

# # ================= GUI =================
# stop_flag = False

# def run_loop(url_entry, folder_entry, num_entry):
#     global stop_flag
#     stop_flag = False

#     target_url = url_entry.get().strip()
#     folder_path = folder_entry.get().strip()

#     try:
#         num_visits = int(num_entry.get())
#         if num_visits <= 0:
#             raise ValueError
#     except ValueError:
#         messagebox.showerror("Error", "Please enter a valid positive integer for Number of Visits!")
#         return

#     if not target_url:
#         messagebox.showerror("Error", "Please enter Target URL!")
#         return
#     if not folder_path:
#         messagebox.showerror("Error", "Please select Images Folder Path!")
#         return

#     try:
#         image_list = get_image_list(folder_path)
#     except Exception as e:
#         messagebox.showerror("Error", str(e))
#         return

#     available_images = len(image_list)
#     if available_images < num_visits:
#         messagebox.showwarning(
#             "Warning",
#             f"Only {available_images} images found in folder, but {num_visits} visits requested.\n"
#             f"Will perform only {available_images} visits."
#         )
#         num_visits = available_images

#     logs = load_logs()
#     start_visit = len(logs) + 1

#     for i in range(num_visits):
#         if stop_flag:
#             print("[INFO] Automation stopped by user.")
#             messagebox.showinfo("Stopped", "Automation has been stopped.")
#             break

#         current_image = image_list[i]
#         print(f"[INFO] Starting Visit {start_visit + i} - Using Image: {os.path.basename(current_image)}")

#         result = run_bot(target_url, current_image)

#         if result:
#             timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#             log_entry = {
#                 "visit_number": start_visit + i,
#                 "timestamp": timestamp,
#                 "phone_number": result["phone_number"],
#                 "image_name": result["image_name"]
#             }
#             logs.append(log_entry)
#             save_logs(logs)
#             print(f"[INFO] Visit {start_visit + i} completed and logged.")

#             # Move the used image to 'used_img' folder
#             used_dir = os.path.join(folder_path, "used_img")
#             os.makedirs(used_dir, exist_ok=True)
#             new_path = os.path.join(used_dir, os.path.basename(current_image))
#             os.rename(current_image, new_path)
#             print(f"[INFO] Moved used image to: {new_path}")
#         else:
#             print(f"[WARNING] Visit {start_visit + i} failed - not logged.")

#         if i < num_visits - 1 and not stop_flag:
#             time.sleep(random.uniform(3, 7))  # Longer natural delay between visits

# def start_automation(url_entry, folder_entry, num_entry):
#     thread = threading.Thread(target=run_loop, args=(url_entry, folder_entry, num_entry), daemon=True)
#     thread.start()

# def stop_automation():
#     global stop_flag
#     stop_flag = True
#     messagebox.showinfo("Stop", "Stopping automation after current visit completes...")

# def browse_folder(folder_entry):
#     folder = filedialog.askdirectory(title="Select Images Folder")
#     if folder:
#         folder_entry.delete(0, tk.END)
#         folder_entry.insert(0, folder)

# def create_gui():
#     root = tk.Tk()
#     root.title("Automation Bot - Fingerprint Rotation Enabled")
#     root.geometry("700x380")
#     root.resizable(False, False)

#     tk.Label(root, text="Target URL:", font=("Arial", 10, "bold")).grid(row=0, column=0, padx=15, pady=15, sticky="e")
#     url_entry = tk.Entry(root, width=70)
#     url_entry.insert(0, "https://greendotball.com/?utm_source=herody&utm_medium=26")
#     url_entry.grid(row=0, column=1, padx=10, pady=15)

#     tk.Label(root, text="Images Folder Path:", font=("Arial", 10, "bold")).grid(row=1, column=0, padx=15, pady=10, sticky="e")
#     folder_entry = tk.Entry(root, width=70)
#     folder_entry.insert(0, os.path.join(os.getcwd(), "images"))
#     folder_entry.grid(row=1, column=1, padx=10, pady=10)
#     browse_btn = tk.Button(root, text="Browse", command=lambda: browse_folder(folder_entry))
#     browse_btn.grid(row=1, column=2, padx=10, pady=10)

#     tk.Label(root, text="Number of Visits:", font=("Arial", 10, "bold")).grid(row=2, column=0, padx=15, pady=10, sticky="e")
#     num_entry = tk.Entry(root, width=70)
#     num_entry.insert(0, "10")
#     num_entry.grid(row=2, column=1, padx=10, pady=10)

#     start_button = tk.Button(root, text="START", bg="green", fg="white", font=("Arial", 12, "bold"), width=15,
#                              command=lambda: start_automation(url_entry, folder_entry, num_entry))
#     start_button.grid(row=3, column=0, pady=30)

#     stop_button = tk.Button(root, text="STOP", bg="red", fg="white", font=("Arial", 12, "bold"), width=15,
#                             command=stop_automation)
#     stop_button.grid(row=3, column=1, pady=30)

#     tk.Label(root, text="Fingerprint Rotation: Each visit uses random User-Agent + different screen resolution for better stealth.\n"
#                         "Supports all common image formats.",
#              fg="green", wraplength=650, justify="left").grid(row=4, column=0, columnspan=3, pady=15)

#     root.mainloop()

# # ================= RUN =================
# if __name__ == "__main__":
#     create_gui()



# import os
# import time
# import random
# import json
# import datetime
# import threading
# import tkinter as tk
# from tkinter import messagebox, filedialog
# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.common.action_chains import ActionChains
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from webdriver_manager.chrome import ChromeDriverManager
# from queue import Queue, Empty
# # ================= CONFIG =================
# LOG_FILE = "log.json"
# SELECTORS = {
#     "file_input": (By.ID, "fileInput"),
#     "phone_input": (By.CSS_SELECTOR, "input.mobile-number"),
#     "checkbox": (By.ID, "termsCheckbox"),
#     "slider_btn": (By.ID, "slideButton"),
#     "slider_bar": (By.ID, "slideTrack"),
# }

# # List of common realistic User-Agents (2025-2026 era)
# USER_AGENTS = [
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0",
#     "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_6_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
#     "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_6_3) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Edg/120.0.0.0",
#     "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
# ]

# # Common desktop/laptop screen resolutions (width x height)
# SCREEN_SIZES = [
#     (1920, 1080),
#     (1366, 768),
#     (1536, 864),
#     (1440, 900),
#     (1280, 720),
#     (1600, 900),
#     (2560, 1440),
#     (3840, 2160),
# ]

# # ================= UTILS =================
# def generate_random_phone():
#     start = random.choice(["9", "8", "7", "6"])
#     return start + "".join(str(random.randint(0, 9)) for _ in range(9))

# def get_image_list(folder_path):
#     if not os.path.isdir(folder_path):
#         raise Exception("Invalid folder path!")
#     valid_extensions = (".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".tiff", ".tif", ".svg")
#     images = [
#         os.path.join(folder_path, f)
#         for f in os.listdir(folder_path)
#         if f.lower().endswith(valid_extensions)
#     ]
#     if not images:
#         raise Exception("No images found in the folder!")
#     images.sort(key=lambda x: x.lower())
#     return images

# def load_logs():
#     if os.path.exists(LOG_FILE):
#         with open(LOG_FILE, "r", encoding="utf-8") as f:
#             return json.load(f)
#     return []

# def save_logs(logs):
#     with open(LOG_FILE, "w", encoding="utf-8") as f:
#         json.dump(logs, f, indent=4, ensure_ascii=False)

# # ================= MAIN AUTOMATION =================
# def run_bot(target_url, image_path):
#     # Randomly select a User-Agent and matching screen size for fingerprint variation
#     user_agent = random.choice(USER_AGENTS)
#     width, height = random.choice(SCREEN_SIZES)

#     options = Options()
#     options.add_argument(f"--user-agent={user_agent}")
#     options.add_argument(f"--window-size={width},{height}")
#     # options.add_argument("--start-maximized")  # Removed - we control size manually
#     options.add_argument("--disable-blink-features=AutomationControlled")
#     options.add_experimental_option("excludeSwitches", ["enable-automation"])
#     options.add_experimental_option("useAutomationExtension", False)

#     # Additional stealth options
#     options.add_argument("--disable-infobars")
#     options.add_argument("--no-sandbox")
#     options.add_argument("--disable-dev-shm-usage")

#     driver = webdriver.Chrome(
#         service=Service(ChromeDriverManager().install()),
#         options=options
#     )
#     wait = WebDriverWait(driver, 30)

#     try:
#         print(f"[INFO] Opening website with resolution {width}x{height} and UA: {user_agent[:60]}...")
#         driver.get(target_url)
#         time.sleep(4 + random.uniform(0, 2))  # Small random delay

#         # ---------- IMAGE UPLOAD ----------
#         print(f"[INFO] Uploading image: {os.path.basename(image_path)}")
#         file_input = wait.until(EC.presence_of_element_located(SELECTORS["file_input"]))
#         driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", file_input)
#         file_input.send_keys(image_path)
#         time.sleep(2 + random.uniform(0, 1))

#         # ---------- PHONE NUMBER ----------
#         print("[INFO] Entering random phone number...")
#         phone_input = wait.until(EC.presence_of_element_located(SELECTORS["phone_input"]))
#         driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", phone_input)
#         phone_number = generate_random_phone()
#         phone_input.clear()
#         phone_input.send_keys(phone_number)
#         time.sleep(1 + random.uniform(0.5, 1.5))

#         # ---------- CHECKBOX ----------
#         print("[INFO] Checking terms checkbox...")
#         checkbox = wait.until(EC.presence_of_element_located(SELECTORS["checkbox"]))
#         driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", checkbox)
#         time.sleep(1)
#         driver.execute_script("arguments[0].click();", checkbox)
#         time.sleep(1 + random.uniform(0.3, 0.8))

#         # ---------- SLIDER SUBMIT ----------
#         print("[INFO] Performing slider action (human-like)...")
#         slider_btn = wait.until(EC.presence_of_element_located(SELECTORS["slider_btn"]))
#         slider_bar = wait.until(EC.presence_of_element_located(SELECTORS["slider_bar"]))
#         driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", slider_bar)
#         time.sleep(1)

#         btn_width = slider_btn.size["width"]
#         track_width = slider_bar.size["width"]
#         move_distance = track_width - btn_width - random.randint(5, 20)

#         actions = ActionChains(driver)
#         actions.move_to_element(slider_btn).click_and_hold().pause(random.uniform(0.2, 0.4))
#         actions.move_by_offset(move_distance // 3, random.randint(-8, 8)).pause(random.uniform(0.1, 0.3))
#         actions.move_by_offset(move_distance // 3, random.randint(-12, 12)).pause(random.uniform(0.1, 0.3))
#         actions.move_by_offset(move_distance - 2 * (move_distance // 3) + random.randint(-5, 5), random.randint(-8, 8))
#         actions.pause(random.uniform(0.2, 0.5)).release().perform()

#         print("[SUCCESS] Form submitted successfully!")
#         time.sleep(8)

#         return {"phone_number": phone_number, "image_name": os.path.basename(image_path)}

#     except Exception as e:
#         print(f"[ERROR] Something went wrong: {e}")
#         return None
#     finally:
#         driver.quit()

# # ================= WORKER =================
# def worker(target_url, image_queue, used_dir, logs, lock):
#     global stop_flag
#     while not stop_flag:
#         try:
#             current_image = image_queue.get(timeout=1)
#         except Empty:
#             break

#         print(f"[INFO] Starting Visit - Using Image: {os.path.basename(current_image)}")

#         result = run_bot(target_url, current_image)

#         if result:
#             timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#             with lock:
#                 visit_number = len(logs) + 1
#                 log_entry = {
#                     "visit_number": visit_number,
#                     "timestamp": timestamp,
#                     "phone_number": result["phone_number"],
#                     "image_name": result["image_name"]
#                 }
#                 logs.append(log_entry)
#             print(f"[INFO] Visit {visit_number} completed and logged.")

#             new_path = os.path.join(used_dir, os.path.basename(current_image))
#             try:
#                 os.rename(current_image, new_path)
#                 print(f"[INFO] Moved used image to: {new_path}")
#             except Exception as e:
#                 print(f"[ERROR] Failed to move image: {e}")
#         else:
#             print(f"[WARNING] Visit failed - not logged.")

#         if not stop_flag:
#             time.sleep(random.uniform(3, 7))  # Delay between visits for this worker

# # ================= GUI =================
# stop_flag = False

# def run_loop(url_entry, folder_entry, num_entry, parallel_entry):
#     global stop_flag
#     stop_flag = False

#     target_url = url_entry.get().strip()
#     folder_path = folder_entry.get().strip()

#     try:
#         num_visits = int(num_entry.get())
#         if num_visits <= 0:
#             raise ValueError
#     except ValueError:
#         messagebox.showerror("Error", "Please enter a valid positive integer for Number of Visits!")
#         return

#     try:
#         parallel = int(parallel_entry.get())
#         if parallel <= 0:
#             raise ValueError
#     except ValueError:
#         messagebox.showerror("Error", "Please enter a valid positive integer for Number of Parallel Sessions!")
#         return

#     if not target_url:
#         messagebox.showerror("Error", "Please enter Target URL!")
#         return
#     if not folder_path:
#         messagebox.showerror("Error", "Please select Images Folder Path!")
#         return

#     try:
#         image_list = get_image_list(folder_path)
#     except Exception as e:
#         messagebox.showerror("Error", str(e))
#         return

#     available_images = len(image_list)
#     if available_images < num_visits:
#         messagebox.showwarning(
#             "Warning",
#             f"Only {available_images} images found in folder, but {num_visits} visits requested.\n"
#             f"Will perform only {available_images} visits."
#         )
#         num_visits = available_images

#     logs = load_logs()
#     lock = threading.Lock()
#     image_queue = Queue()
#     for i in range(num_visits):
#         image_queue.put(image_list[i])

#     used_dir = os.path.join(folder_path, "used_img")
#     os.makedirs(used_dir, exist_ok=True)

#     threads = []
#     for _ in range(min(parallel, num_visits)):
#         t = threading.Thread(target=worker, args=(target_url, image_queue, used_dir, logs, lock), daemon=True)
#         t.start()
#         threads.append(t)

#     for t in threads:
#         t.join()

#     save_logs(logs)
#     if stop_flag:
#         print("[INFO] Automation stopped by user.")
#         messagebox.showinfo("Stopped", "Automation has been stopped.")
#     else:
#         messagebox.showinfo("Completed", "Automation has completed.")

# def start_automation(url_entry, folder_entry, num_entry, parallel_entry):
#     thread = threading.Thread(target=run_loop, args=(url_entry, folder_entry, num_entry, parallel_entry), daemon=True)
#     thread.start()

# def stop_automation():
#     global stop_flag
#     stop_flag = True
#     messagebox.showinfo("Stop", "Stopping automation after current visits complete...")

# def browse_folder(folder_entry):
#     folder = filedialog.askdirectory(title="Select Images Folder")
#     if folder:
#         folder_entry.delete(0, tk.END)
#         folder_entry.insert(0, folder)

# def create_gui():
#     root = tk.Tk()
#     root.title("Automation Bot - Fingerprint Rotation Enabled")
#     root.geometry("700x420")
#     root.resizable(False, False)

#     tk.Label(root, text="Target URL:", font=("Arial", 10, "bold")).grid(row=0, column=0, padx=15, pady=15, sticky="e")
#     url_entry = tk.Entry(root, width=70)
#     url_entry.insert(0, "https://greendotball.com/?utm_source=herody&utm_medium=26")
#     url_entry.grid(row=0, column=1, padx=10, pady=15)

#     tk.Label(root, text="Images Folder Path:", font=("Arial", 10, "bold")).grid(row=1, column=0, padx=15, pady=10, sticky="e")
#     folder_entry = tk.Entry(root, width=70)
#     folder_entry.insert(0, os.path.join(os.getcwd(), "images"))
#     folder_entry.grid(row=1, column=1, padx=10, pady=10)
#     browse_btn = tk.Button(root, text="Browse", command=lambda: browse_folder(folder_entry))
#     browse_btn.grid(row=1, column=2, padx=10, pady=10)

#     tk.Label(root, text="Number of Visits:", font=("Arial", 10, "bold")).grid(row=2, column=0, padx=15, pady=10, sticky="e")
#     num_entry = tk.Entry(root, width=70)
#     num_entry.insert(0, "10")
#     num_entry.grid(row=2, column=1, padx=10, pady=10)

#     tk.Label(root, text="Number of Parallel Sessions:", font=("Arial", 10, "bold")).grid(row=3, column=0, padx=15, pady=10, sticky="e")
#     parallel_entry = tk.Entry(root, width=70)
#     parallel_entry.insert(0, "1")
#     parallel_entry.grid(row=3, column=1, padx=10, pady=10)

#     start_button = tk.Button(root, text="START", bg="green", fg="white", font=("Arial", 12, "bold"), width=15,
#                              command=lambda: start_automation(url_entry, folder_entry, num_entry, parallel_entry))
#     start_button.grid(row=4, column=0, pady=30)

#     stop_button = tk.Button(root, text="STOP", bg="red", fg="white", font=("Arial", 12, "bold"), width=15,
#                             command=stop_automation)
#     stop_button.grid(row=4, column=1, pady=30)

#     tk.Label(root, text="Fingerprint Rotation: Each visit uses random User-Agent + different screen resolution for better stealth.\n"
#                         "Supports all common image formats.",
#              fg="green", wraplength=650, justify="left").grid(row=5, column=0, columnspan=3, pady=15)

#     root.mainloop()

# # ================= RUN =================
# if __name__ == "__main__":
#     create_gui()




# import os
# import time
# import random
# import json
# import datetime
# import threading
# import tkinter as tk
# from tkinter import messagebox, filedialog
# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.common.action_chains import ActionChains
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.common.exceptions import TimeoutException, WebDriverException, NoSuchElementException
# from webdriver_manager.chrome import ChromeDriverManager
# from queue import Queue, Empty
# import logging

# # ================= LOGGING SETUP =================
# logging.basicConfig(
#     level=logging.INFO,
#     format='%(asctime)s [%(levelname)s] %(message)s',
#     handlers=[
#         logging.FileHandler("automation.log", encoding='utf-8'),
#         logging.StreamHandler()
#     ]
# )
# logger = logging.getLogger(__name__)

# # ================= CONFIG =================
# LOG_FILE = "visits.json"
# SELECTORS = {
#     "file_input": (By.ID, "fileInput"),
#     "phone_input": (By.CSS_SELECTOR, "input.mobile-number"),
#     "checkbox": (By.ID, "termsCheckbox"),
#     "slider_btn": (By.ID, "slideButton"),
#     "slider_bar": (By.ID, "slideTrack"),
# }

# USER_AGENTS = [
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0",
#     "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Edg/121.0.0.0",
# ]

# SCREEN_SIZES = [
#     (1920, 1080), (1366, 768), (1536, 864), (1440, 900),
#     (1280, 720), (1600, 900), (2560, 1440), (3440, 1440),
# ]

# # ================= UTILS =================
# def generate_random_phone():
#     start = random.choice(["6", "7", "8", "9"])
#     return start + "".join(str(random.randint(0, 9)) for _ in range(9))


# def get_image_list(folder_path):
#     if not os.path.isdir(folder_path):
#         raise Exception("Invalid folder path!")
#     valid_extensions = (".jpg", ".jpeg", ".png", ".gif", ".webp")
#     images = [os.path.join(folder_path, f) for f in os.listdir(folder_path)
#               if f.lower().endswith(valid_extensions)]
#     if not images:
#         raise Exception("No images found!")
#     images.sort(key=lambda x: x.lower())
#     return images


# def load_logs():
#     if os.path.exists(LOG_FILE):
#         try:
#             with open(LOG_FILE, "r", encoding="utf-8") as f:
#                 return json.load(f)
#         except:
#             return []
#     return []


# def save_logs(logs):
#     try:
#         with open(LOG_FILE, "w", encoding="utf-8") as f:
#             json.dump(logs, f, indent=4, ensure_ascii=False)
#     except Exception as e:
#         logger.error(f"Failed to save logs: {e}")


# # ================= ROBUST BOT FUNCTION =================
# def run_bot(target_url, image_path, retry_count=0, max_retries=2):
#     user_agent = random.choice(USER_AGENTS)
#     width, height = random.choice(SCREEN_SIZES)

#     options = Options()
#     options.add_argument(f"--user-agent={user_agent}")
#     options.add_argument(f"--window-size={width},{height}")
#     options.add_argument("--disable-blink-features=AutomationControlled")
#     options.add_argument("--no-sandbox")
#     options.add_argument("--disable-dev-shm-usage")
#     options.add_argument("--disable-gpu")              # memory stability
#     options.add_argument("--disable-extensions")
#     options.add_argument("--disable-infobars")
#     options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
#     options.add_experimental_option("useAutomationExtension", False)

#     # Uncomment next line for long runs (headless)
#     # options.add_argument("--headless=new")

#     driver = None
#     try:
#         driver = webdriver.Chrome(
#             service=Service(ChromeDriverManager().install()),
#             options=options
#         )
#         wait = WebDriverWait(driver, 25)

#         logger.info(f"Visit started | UA: {user_agent[:50]}... | Res: {width}x{height} | Image: {os.path.basename(image_path)}")

#         driver.get(target_url)
#         time.sleep(random.uniform(3.5, 6.5))

#         # Image upload
#         file_input = wait.until(EC.presence_of_element_located(SELECTORS["file_input"]))
#         file_input.send_keys(image_path)

#         # Phone
#         phone_input = wait.until(EC.element_to_be_clickable(SELECTORS["phone_input"]))
#         phone_number = generate_random_phone()
#         phone_input.clear()
#         phone_input.send_keys(phone_number)

#         # Checkbox
#         checkbox = wait.until(EC.element_to_be_clickable(SELECTORS["checkbox"]))
#         driver.execute_script("arguments[0].click();", checkbox)

#         # Slider
#         slider_btn = wait.until(EC.element_to_be_clickable(SELECTORS["slider_btn"]))
#         slider_bar = wait.until(EC.presence_of_element_located(SELECTORS["slider_bar"]))

#         btn_w = slider_btn.size["width"]
#         track_w = slider_bar.size["width"]
#         distance = track_w - btn_w - random.randint(8, 25)

#         actions = ActionChains(driver)
#         actions.click_and_hold(slider_btn).pause(random.uniform(0.15, 0.45))
#         for step in [distance//3, distance//3, distance - (distance//3*2)]:
#             actions.move_by_offset(step, random.randint(-12, 12)).pause(random.uniform(0.08, 0.25))
#         actions.release().perform()

#         time.sleep(random.uniform(6, 10))  # wait for possible redirect/confirmation

#         logger.info(f"[SUCCESS] Visit completed | Phone: {phone_number}")
#         return {"phone_number": phone_number, "image_name": os.path.basename(image_path)}

#     except (TimeoutException, NoSuchElementException, WebDriverException) as e:
#         logger.warning(f"Visit failed (attempt {retry_count+1}): {type(e).__name__} - {e}")
#         if retry_count < max_retries:
#             time.sleep(random.uniform(10, 25))
#             return run_bot(target_url, image_path, retry_count + 1, max_retries)
#         return None

#     finally:
#         if driver:
#             try:
#                 driver.quit()
#             except:
#                 pass
#             time.sleep(0.5)  # give OS some breathing room


# # ================= WORKER =================
# def worker(target_url, image_queue, used_dir, logs, lock):
#     global stop_flag
#     while not stop_flag:
#         try:
#             current_image = image_queue.get(timeout=1.2)
#         except Empty:
#             break

#         result = run_bot(target_url, current_image)

#         if result:
#             timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#             with lock:
#                 visit_number = len(logs) + 1
#                 log_entry = {
#                     "visit": visit_number,
#                     "time": timestamp,
#                     "phone": result["phone_number"],
#                     "image": result["image_name"]
#                 }
#                 logs.append(log_entry)
#             save_logs(logs)  # save after every success

#             try:
#                 new_path = os.path.join(used_dir, os.path.basename(current_image))
#                 os.rename(current_image, new_path)
#                 logger.info(f"Moved: {os.path.basename(current_image)} → used_img")
#             except Exception as e:
#                 logger.error(f"Move failed: {e}")
#         else:
#             # Failed → put back in queue (with some delay)
#             logger.warning("Visit failed → re-queuing image")
#             time.sleep(15)
#             image_queue.put(current_image)  # retry later

#         time.sleep(random.uniform(4, 12))  # natural delay


# # ================= MAIN LOOP & GUI =================
# stop_flag = False


# def run_loop(url_entry, folder_entry, num_entry, parallel_entry):
#     global stop_flag
#     stop_flag = False

#     target_url = url_entry.get().strip()
#     folder_path = folder_entry.get().strip()

#     try:
#         num_visits = int(num_entry.get())
#         parallel = int(parallel_entry.get())
#         if num_visits <= 0 or parallel <= 0:
#             raise ValueError
#     except:
#         messagebox.showerror("Error", "Invalid number!")
#         return

#     if not target_url or not folder_path:
#         messagebox.showerror("Error", "URL aur Folder dono daal do!")
#         return

#     try:
#         image_list = get_image_list(folder_path)
#     except Exception as e:
#         messagebox.showerror("Error", str(e))
#         return

#     if len(image_list) < num_visits:
#         num_visits = len(image_list)
#         messagebox.showwarning("Warning", f"Sirf {num_visits} images available hain")

#     logs = load_logs()
#     lock = threading.Lock()
#     image_queue = Queue()
#     for img in image_list[:num_visits]:
#         image_queue.put(img)

#     used_dir = os.path.join(folder_path, "used_img")
#     os.makedirs(used_dir, exist_ok=True)

#     threads = []
#     for _ in range(min(parallel, num_visits, 5)):  # max 5 parallel recommended
#         t = threading.Thread(target=worker, args=(target_url, image_queue, used_dir, logs, lock), daemon=True)
#         t.start()
#         threads.append(t)

#     # Monitor stop flag
#     while any(t.is_alive() for t in threads):
#         if stop_flag:
#             logger.info("Stop signal received. Waiting for current visits to finish...")
#             break
#         time.sleep(1.5)

#     for t in threads:
#         t.join(timeout=45)  # give some time to finish

#     save_logs(logs)
#     msg = "Stopped by user" if stop_flag else "Completed"
#     messagebox.showinfo("Status", f"Automation {msg} ✓")


# def start_automation(*args):
#     threading.Thread(target=run_loop, args=args, daemon=True).start()


# def stop_automation():
#     global stop_flag
#     stop_flag = True
#     messagebox.showinfo("Stopping", "Current visits khatam hone ke baad ruk jayega...")


# def browse_folder(entry):
#     path = filedialog.askdirectory()
#     if path:
#         entry.delete(0, tk.END)
#         entry.insert(0, path)


# def create_gui():
#     root = tk.Tk()
#     root.title("Automation Bot - Long Run Stable v2")
#     root.geometry("720x450")
#     root.resizable(False, False)

#     entries = {}

#     # URL
#     tk.Label(root, text="Target URL:", font=("Arial", 10, "bold")).grid(row=0, column=0, padx=12, pady=12, sticky="e")
#     entries['url'] = tk.Entry(root, width=75)
#     entries['url'].insert(0, "https://greendotball.com/?utm_source=herody&utm_medium=26")
#     entries['url'].grid(row=0, column=1, padx=10, pady=12)

#     # Folder
#     tk.Label(root, text="Images Folder:", font=("Arial", 10, "bold")).grid(row=1, column=0, padx=12, pady=8, sticky="e")
#     entries['folder'] = tk.Entry(root, width=75)
#     entries['folder'].insert(0, os.path.join(os.getcwd(), "images"))
#     entries['folder'].grid(row=1, column=1, padx=10, pady=8)
#     tk.Button(root, text="Browse", command=lambda: browse_folder(entries['folder'])).grid(row=1, column=2, padx=8)

#     # Visits & Parallel
#     tk.Label(root, text="Total Visits:", font=("Arial", 10, "bold")).grid(row=2, column=0, padx=12, pady=8, sticky="e")
#     entries['visits'] = tk.Entry(root, width=75)
#     entries['visits'].insert(0, "50")
#     entries['visits'].grid(row=2, column=1, padx=10, pady=8)

#     tk.Label(root, text="Parallel Sessions:", font=("Arial", 10, "bold")).grid(row=3, column=0, padx=12, pady=8, sticky="e")
#     entries['parallel'] = tk.Entry(root, width=75)
#     entries['parallel'].insert(0, "3")
#     entries['parallel'].grid(row=3, column=1, padx=10, pady=8)

#     # Buttons
#     tk.Button(root, text="START", bg="#2ecc71", fg="white", font=("Arial", 12, "bold"),
#               command=lambda: start_automation(entries['url'], entries['folder'], entries['visits'], entries['parallel']))\
#         .grid(row=4, column=0, pady=25, padx=20)

#     tk.Button(root, text="STOP", bg="#e74c3c", fg="white", font=("Arial", 12, "bold"),
#               command=stop_automation)\
#         .grid(row=4, column=1, pady=25, sticky="w")

#     tk.Label(root, text="• Max parallel 3-5 rakhein (memory ke liye)\n"
#                         "• Logs → automation.log aur visits.json\n"
#                         "• Failed visits automatically retry honge",
#              fg="#27ae60", justify="left").grid(row=5, column=0, columnspan=3, pady=10)

#     root.mainloop()


# if __name__ == "__main__":
#     create_gui()



# import os
# import time
# import random
# import json
# import datetime
# import threading
# import tkinter as tk
# from tkinter import messagebox, filedialog
# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.common.action_chains import ActionChains
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.common.exceptions import TimeoutException, WebDriverException, NoSuchElementException
# from queue import Queue, Empty
# import logging

# # ================= LOGGING SETUP =================
# logging.basicConfig(
#     level=logging.INFO,
#     format='%(asctime)s [%(levelname)s] %(message)s',
#     handlers=[
#         logging.FileHandler("automation.log", encoding='utf-8'),
#         logging.StreamHandler()
#     ]
# )
# logger = logging.getLogger(__name__)

# # ================= FIXED CHROMEDRIVER PATH =================
# # Yeh path bilkul wahi daalo jahan tumne chromedriver.exe rakha hai
# CHROMEDRIVER_PATH = r"C:\Users\HP\Downloads\chromedriver-win64 (5)\chromedriver-win64\chromedriver.exe"

# # ================= CONFIG =================
# LOG_FILE = "visits.json"
# SELECTORS = {
#     "file_input": (By.ID, "fileInput"),
#     "phone_input": (By.CSS_SELECTOR, "input.mobile-number"),
#     "checkbox": (By.ID, "termsCheckbox"),
#     "slider_btn": (By.ID, "slideButton"),
#     "slider_bar": (By.ID, "slideTrack"),
# }

# USER_AGENTS = [
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0",
#     "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Edg/121.0.0.0",
# ]

# SCREEN_SIZES = [
#     (1920, 1080), (1366, 768), (1536, 864), (1440, 900),
#     (1280, 720), (1600, 900), (2560, 1440), (3440, 1440),
# ]

# # ================= UTILS =================
# def generate_random_phone():
#     start = random.choice(["6", "7", "8", "9"])
#     return start + "".join(str(random.randint(0, 9)) for _ in range(9))

# def get_image_list(folder_path):
#     if not os.path.isdir(folder_path):
#         raise Exception("Invalid folder path!")
#     valid_extensions = (".jpg", ".jpeg", ".png", ".gif", ".webp")
#     images = [os.path.join(folder_path, f) for f in os.listdir(folder_path)
#               if f.lower().endswith(valid_extensions)]
#     if not images:
#         raise Exception("No images found!")
#     images.sort(key=lambda x: x.lower())
#     return images

# def load_logs():
#     if os.path.exists(LOG_FILE):
#         try:
#             with open(LOG_FILE, "r", encoding="utf-8") as f:
#                 return json.load(f)
#         except:
#             return []
#     return []

# def save_logs(logs):
#     try:
#         with open(LOG_FILE, "w", encoding="utf-8") as f:
#             json.dump(logs, f, indent=4, ensure_ascii=False)
#     except Exception as e:
#         logger.error(f"Failed to save logs: {e}")

# # ================= ROBUST BOT FUNCTION =================
# def run_bot(target_url, image_path, retry_count=0, max_retries=2):
#     user_agent = random.choice(USER_AGENTS)
#     width, height = random.choice(SCREEN_SIZES)

#     options = Options()
#     options.add_argument(f"--user-agent={user_agent}")
#     options.add_argument(f"--window-size={width},{height}")
#     options.add_argument("--disable-blink-features=AutomationControlled")
#     options.add_argument("--no-sandbox")
#     options.add_argument("--disable-dev-shm-usage")
#     options.add_argument("--disable-gpu")
#     options.add_argument("--disable-extensions")
#     options.add_argument("--disable-infobars")
#     options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
#     options.add_experimental_option("useAutomationExtension", False)

#     # Headless mode (long run ke liye recommended - comment hata do agar chahiye)
#     # options.add_argument("--headless=new")

#     driver = None
#     try:
#         # Fixed chromedriver path use kar rahe hain
#         driver = webdriver.Chrome(
#             service=Service(CHROMEDRIVER_PATH),
#             options=options
#         )
        
#         # Important: Timeout badha diya timeout errors se bachne ke liye
#         driver.set_page_load_timeout(180)   # 3 minutes
#         driver.set_script_timeout(120)
        
#         wait = WebDriverWait(driver, 40)    # wait bhi badha diya

#         logger.info(f"Visit started | UA: {user_agent[:50]}... | Res: {width}x{height} | Image: {os.path.basename(image_path)}")

#         driver.get(target_url)
#         time.sleep(random.uniform(3.5, 7.5))

#         # Image upload
#         file_input = wait.until(EC.presence_of_element_located(SELECTORS["file_input"]))
#         file_input.send_keys(image_path)
#         time.sleep(random.uniform(1.5, 3))

#         # Phone
#         phone_input = wait.until(EC.element_to_be_clickable(SELECTORS["phone_input"]))
#         phone_number = generate_random_phone()
#         phone_input.clear()
#         phone_input.send_keys(phone_number)

#         # Checkbox
#         checkbox = wait.until(EC.element_to_be_clickable(SELECTORS["checkbox"]))
#         driver.execute_script("arguments[0].click();", checkbox)

#         # Slider
#         slider_btn = wait.until(EC.element_to_be_clickable(SELECTORS["slider_btn"]))
#         slider_bar = wait.until(EC.presence_of_element_located(SELECTORS["slider_bar"]))

#         btn_w = slider_btn.size["width"]
#         track_w = slider_bar.size["width"]
#         distance = track_w - btn_w - random.randint(8, 25)

#         actions = ActionChains(driver)
#         actions.click_and_hold(slider_btn).pause(random.uniform(0.15, 0.45))
#         for step in [distance//3, distance//3, distance - (distance//3*2)]:
#             actions.move_by_offset(step, random.randint(-12, 12)).pause(random.uniform(0.08, 0.25))
#         actions.release().perform()

#         time.sleep(random.uniform(7, 12))  # confirmation ke liye wait

#         logger.info(f"[SUCCESS] Visit completed | Phone: {phone_number}")
#         return {"phone_number": phone_number, "image_name": os.path.basename(image_path)}

#     except (TimeoutException, NoSuchElementException, WebDriverException) as e:
#         logger.warning(f"Visit failed (attempt {retry_count+1}): {type(e).__name__} - {e}")
#         if retry_count < max_retries:
#             time.sleep(random.uniform(15, 35))
#             return run_bot(target_url, image_path, retry_count + 1, max_retries)
#         return None

#     finally:
#         if driver:
#             try:
#                 driver.quit()
#             except:
#                 pass
#             time.sleep(0.8)  # OS ko thoda time do

# # ================= WORKER =================
# def worker(target_url, image_queue, used_dir, logs, lock):
#     global stop_flag
#     while not stop_flag:
#         try:
#             current_image = image_queue.get(timeout=1.5)
#         except Empty:
#             break

#         result = run_bot(target_url, current_image)

#         if result:
#             timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#             with lock:
#                 visit_number = len(logs) + 1
#                 log_entry = {
#                     "visit": visit_number,
#                     "time": timestamp,
#                     "phone": result["phone_number"],
#                     "image": result["image_name"]
#                 }
#                 logs.append(log_entry)
#             save_logs(logs)

#             try:
#                 new_path = os.path.join(used_dir, os.path.basename(current_image))
#                 os.rename(current_image, new_path)
#                 logger.info(f"Moved: {os.path.basename(current_image)} → used_img")
#             except Exception as e:
#                 logger.error(f"Move failed: {e}")
#         else:
#             logger.warning("Visit failed → re-queuing image")
#             time.sleep(20)
#             image_queue.put(current_image)

#         time.sleep(random.uniform(5, 15))

# # ================= MAIN LOOP & GUI =================
# stop_flag = False

# def run_loop(url_entry, folder_entry, num_entry, parallel_entry):
#     global stop_flag
#     stop_flag = False

#     target_url = url_entry.get().strip()
#     folder_path = folder_entry.get().strip()

#     try:
#         num_visits = int(num_entry.get())
#         parallel = int(parallel_entry.get())
#         if num_visits <= 0 or parallel <= 0:
#             raise ValueError
#     except:
#         messagebox.showerror("Error", "Invalid number!")
#         return

#     if not target_url or not folder_path:
#         messagebox.showerror("Error", "URL aur Folder dono daal do!")
#         return

#     try:
#         image_list = get_image_list(folder_path)
#     except Exception as e:
#         messagebox.showerror("Error", str(e))
#         return

#     if len(image_list) < num_visits:
#         num_visits = len(image_list)
#         messagebox.showwarning("Warning", f"Sirf {num_visits} images available hain")

#     logs = load_logs()
#     lock = threading.Lock()
#     image_queue = Queue()
#     for img in image_list[:num_visits]:
#         image_queue.put(img)

#     used_dir = os.path.join(folder_path, "used_img")
#     os.makedirs(used_dir, exist_ok=True)

#     threads = []
#     for _ in range(min(parallel, num_visits, 3)):  # 3 se zyada mat karo stability ke liye
#         t = threading.Thread(target=worker, args=(target_url, image_queue, used_dir, logs, lock), daemon=True)
#         t.start()
#         threads.append(t)

#     while any(t.is_alive() for t in threads):
#         if stop_flag:
#             logger.info("Stop signal received. Waiting for current visits...")
#             break
#         time.sleep(2)

#     for t in threads:
#         t.join(timeout=60)

#     save_logs(logs)
#     msg = "Stopped by user" if stop_flag else "Completed"
#     messagebox.showinfo("Status", f"Automation {msg} ✓")

# def start_automation(*args):
#     threading.Thread(target=run_loop, args=args, daemon=True).start()

# def stop_automation():
#     global stop_flag
#     stop_flag = True
#     messagebox.showinfo("Stopping", "Current visits khatam hone ke baad ruk jayega...")

# def browse_folder(entry):
#     path = filedialog.askdirectory()
#     if path:
#         entry.delete(0, tk.END)
#         entry.insert(0, path)

# def create_gui():
#     root = tk.Tk()
#     root.title("Automation Bot - Stable Fixed Driver")
#     root.geometry("720x450")
#     root.resizable(False, False)

#     entries = {}

#     tk.Label(root, text="Target URL:", font=("Arial", 10, "bold")).grid(row=0, column=0, padx=12, pady=12, sticky="e")
#     entries['url'] = tk.Entry(root, width=75)
#     entries['url'].insert(0, "https://greendotball.com/?utm_source=herody&utm_medium=26")
#     entries['url'].grid(row=0, column=1, padx=10, pady=12)

#     tk.Label(root, text="Images Folder:", font=("Arial", 10, "bold")).grid(row=1, column=0, padx=12, pady=8, sticky="e")
#     entries['folder'] = tk.Entry(root, width=75)
#     entries['folder'].insert(0, os.path.join(os.getcwd(), "images"))
#     entries['folder'].grid(row=1, column=1, padx=10, pady=8)
#     tk.Button(root, text="Browse", command=lambda: browse_folder(entries['folder'])).grid(row=1, column=2, padx=8)

#     tk.Label(root, text="Total Visits:", font=("Arial", 10, "bold")).grid(row=2, column=0, padx=12, pady=8, sticky="e")
#     entries['visits'] = tk.Entry(root, width=75)
#     entries['visits'].insert(0, "50")
#     entries['visits'].grid(row=2, column=1, padx=10, pady=8)

#     tk.Label(root, text="Parallel Sessions (max 3):", font=("Arial", 10, "bold")).grid(row=3, column=0, padx=12, pady=8, sticky="e")
#     entries['parallel'] = tk.Entry(root, width=75)
#     entries['parallel'].insert(0, "2")
#     entries['parallel'].grid(row=3, column=1, padx=10, pady=8)

#     tk.Button(root, text="START", bg="#2ecc71", fg="white", font=("Arial", 12, "bold"),
#               command=lambda: start_automation(entries['url'], entries['folder'], entries['visits'], entries['parallel']))\
#         .grid(row=4, column=0, pady=25, padx=20)

#     tk.Button(root, text="STOP", bg="#e74c3c", fg="white", font=("Arial", 12, "bold"),
#               command=stop_automation)\
#         .grid(row=4, column=1, pady=25, sticky="w")

#     tk.Label(root, text="• Fixed ChromeDriver v143 use ho raha hai\n"
#                         "• Parallel 2-3 rakho (memory ke liye)\n"
#                         "• Logs: automation.log + visits.json",
#              fg="#27ae60", justify="left").grid(row=5, column=0, columnspan=3, pady=10)

#     root.mainloop()

# if __name__ == "__main__":
#     create_gui()



# import os
# import time
# import random
# import json
# import datetime
# import threading
# import tkinter as tk
# from tkinter import messagebox, filedialog, ttk
# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.common.action_chains import ActionChains
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.common.exceptions import TimeoutException, WebDriverException, NoSuchElementException

# from queue import Queue, Empty
# import logging

# # ================= LOGGING SETUP =================
# logging.basicConfig(
#     level=logging.INFO,
#     format='%(asctime)s [%(levelname)s] %(message)s',
#     handlers=[
#         logging.FileHandler("automation.log", encoding='utf-8'),
#         logging.StreamHandler()
#     ]
# )
# logger = logging.getLogger(__name__)

# # ================= CONFIG =================
# LOG_FILE = "visits.json"
# SELECTORS = {
#     "file_input": (By.ID, "fileInput"),
#     "phone_input": (By.CSS_SELECTOR, "input.mobile-number"),
#     "checkbox": (By.ID, "termsCheckbox"),
#     "slider_btn": (By.ID, "slideButton"),
#     "slider_bar": (By.ID, "slideTrack"),
# }

# USER_AGENTS = [
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36",
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:131.0) Gecko/20100101 Firefox/131.0",
#     "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_6_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36",
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Edg/143.0.0.0",
# ]

# SCREEN_SIZES = [
#     (1920, 1080), (1366, 768), (1536, 864), (1440, 900),
#     (1280, 720), (1600, 900), (2560, 1440),
# ]

# # ================= UTILS =================
# def generate_random_phone():
#     prefixes = ["6", "7", "8", "9"]
#     return random.choice(prefixes) + "".join(str(random.randint(0, 9)) for _ in range(9))

# def get_image_list(folder_path):
#     if not os.path.isdir(folder_path):
#         raise Exception("Invalid folder path!")
#     valid_ext = (".jpg", ".jpeg", ".png", ".gif", ".webp")
#     images = [os.path.join(folder_path, f) for f in os.listdir(folder_path)
#               if f.lower().endswith(valid_ext)]
#     if not images:
#         raise Exception("No valid images found in folder!")
#     images.sort(key=str.lower)
#     return images

# def load_logs():
#     if os.path.exists(LOG_FILE):
#         try:
#             with open(LOG_FILE, "r", encoding="utf-8") as f:
#                 return json.load(f)
#         except:
#             return []
#     return []

# def save_logs(logs):
#     try:
#         with open(LOG_FILE, "w", encoding="utf-8") as f:
#             json.dump(logs, f, indent=4, ensure_ascii=False)
#     except Exception as e:
#         logger.error(f"Failed to save logs: {e}")

# # ================= MAIN BOT FUNCTION =================
# def run_bot(target_url, image_path, headless=False, retry_count=0, max_retries=2):
#     user_agent = random.choice(USER_AGENTS)
#     width, height = random.choice(SCREEN_SIZES)

#     options = Options()
#     options.add_argument(f"--user-agent={user_agent}")
#     options.add_argument(f"--window-size={width},{height}")
#     options.add_argument("--disable-blink-features=AutomationControlled")
#     options.add_argument("--no-sandbox")
#     options.add_argument("--disable-dev-shm-usage")
#     options.add_argument("--disable-gpu")
#     options.add_argument("--disable-extensions")
#     options.add_argument("--disable-infobars")
#     options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
#     options.add_experimental_option("useAutomationExtension", False)

#     if headless:
#         options.add_argument("--headless=new")
#         options.add_argument("--window-size=1920,1080")

#     driver = None
#     try:
#         # Selenium Manager automatically handles ChromeDriver (no path needed)
#         driver = webdriver.Chrome(options=options)

#         driver.set_page_load_timeout(200)
#         driver.set_script_timeout(120)
#         wait = WebDriverWait(driver, 45)

#         logger.info(f"Visit shuru | UA: {user_agent[:50]}... | Res: {width}x{height} | Img: {os.path.basename(image_path)}")

#         driver.get(target_url)
#         time.sleep(random.uniform(4, 8))

#         # Image upload
#         file_input = wait.until(EC.presence_of_element_located(SELECTORS["file_input"]))
#         file_input.send_keys(image_path)
#         time.sleep(random.uniform(2, 4))

#         # Phone number
#         phone_input = wait.until(EC.element_to_be_clickable(SELECTORS["phone_input"]))
#         phone = generate_random_phone()
#         phone_input.clear()
#         phone_input.send_keys(phone)
#         time.sleep(random.uniform(0.8, 1.8))

#         # Checkbox
#         checkbox = wait.until(EC.element_to_be_clickable(SELECTORS["checkbox"]))
#         driver.execute_script("arguments[0].click();", checkbox)

#         # Improved slider
#         slider_btn = wait.until(EC.element_to_be_clickable(SELECTORS["slider_btn"]))
#         slider_bar = wait.until(EC.presence_of_element_located(SELECTORS["slider_bar"]))

#         track_width = slider_bar.size['width']
#         btn_width = slider_btn.size['width']
#         max_distance = track_width - btn_width - 10

#         actions = ActionChains(driver)
#         actions.click_and_hold(slider_btn).pause(random.uniform(0.2, 0.6))

#         current_pos = 0
#         while current_pos < max_distance:
#             step = random.randint(18, 45)
#             if current_pos + step > max_distance:
#                 step = max_distance - current_pos
#             jitter = random.randint(-14, 14)
#             actions.move_by_offset(step, jitter).pause(random.uniform(0.06, 0.18))
#             current_pos += step

#         if random.random() < 0.6:
#             actions.move_by_offset(random.randint(-12, -5), random.randint(-8, 8)).pause(0.1)

#         actions.release().perform()

#         time.sleep(random.uniform(6, 13))

#         logger.info(f"[SUCCESS] Visit pura | Phone: {phone}")
#         return {"phone_number": phone, "image_name": os.path.basename(image_path)}

#     except Exception as e:
#         logger.warning(f"Visit fail (try {retry_count+1}/{max_retries+1}): {type(e).__name__} - {str(e)}")
#         if retry_count < max_retries:
#             time.sleep(random.uniform(20, 45))
#             return run_bot(target_url, image_path, headless, retry_count + 1, max_retries)
#         return None

#     finally:
#         if driver:
#             try:
#                 driver.quit()
#             except:
#                 pass
#             time.sleep(1)

# # ================= WORKER =================
# def worker(target_url, image_queue, used_dir, logs, lock, headless, progress_callback):
#     global stop_flag
#     while not stop_flag:
#         try:
#             img_path = image_queue.get(timeout=2)
#         except Empty:
#             break

#         result = run_bot(target_url, img_path, headless)

#         if result:
#             timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#             with lock:
#                 visit_num = len(logs) + 1
#                 logs.append({
#                     "visit": visit_num,
#                     "time": timestamp,
#                     "phone": result["phone_number"],
#                     "image": result["image_name"]
#                 })
#             save_logs(logs)

#             try:
#                 dest = os.path.join(used_dir, os.path.basename(img_path))
#                 os.rename(img_path, dest)
#                 logger.info(f"Moved → used_img: {os.path.basename(img_path)}")
#             except Exception as e:
#                 logger.error(f"Move fail: {e}")

#             progress_callback(1)
#         else:
#             logger.warning("Fail → image wapas queue mein")
#             time.sleep(25)
#             image_queue.put(img_path)

#         time.sleep(random.uniform(6, 18))

# # ================= GUI =================
# stop_flag = False
# progress_var = None

# def update_progress(increment=1):
#     global progress_var
#     if progress_var:
#         progress_var.set(progress_var.get() + increment)

# def run_automation(url_entry, folder_entry, visits_entry, parallel_entry, headless_var, status_label, progress_bar):
#     global stop_flag, progress_var
#     stop_flag = False

#     target_url = url_entry.get().strip()
#     folder = folder_entry.get().strip()

#     try:
#         total_visits = int(visits_entry.get())
#         parallel = int(parallel_entry.get())
#         if total_visits <= 0 or parallel <= 0:
#             raise ValueError
#     except:
#         messagebox.showerror("Galat Input", "Visits aur Parallel number sahi daalo!")
#         return

#     if not target_url or not folder:
#         messagebox.showerror("Error", "URL aur Images folder dono bharo!")
#         return

#     try:
#         images = get_image_list(folder)
#     except Exception as e:
#         messagebox.showerror("Error", str(e))
#         return

#     total_visits = min(total_visits, len(images))
#     if total_visits == 0:
#         messagebox.showwarning("Warning", "Koi image nahi mili!")
#         return

#     status_label.config(text=f"Shuru ho raha hai... ({total_visits} visits)", fg="blue")

#     logs = load_logs()
#     lock = threading.Lock()
#     q = Queue()
#     for img in images[:total_visits]:
#         q.put(img)

#     used_folder = os.path.join(folder, "used_img")
#     os.makedirs(used_folder, exist_ok=True)

#     progress_var = tk.DoubleVar(value=0)
#     progress_bar['maximum'] = total_visits
#     progress_bar['variable'] = progress_var

#     threads = []
#     for _ in range(min(parallel, 3)):
#         t = threading.Thread(
#             target=worker,
#             args=(target_url, q, used_folder, logs, lock, headless_var.get(), update_progress),
#             daemon=True
#         )
#         t.start()
#         threads.append(t)

#     def monitor():
#         while any(t.is_alive() for t in threads) and not stop_flag:
#             time.sleep(1.5)
#         if stop_flag:
#             status_label.config(text="Ruk gaya (current visits khatam hone do)", fg="orange")
#         else:
#             status_label.config(text="Sab complete ✓", fg="green")
#             messagebox.showinfo("Done", "Automation successfully complete!")

#     threading.Thread(target=monitor, daemon=True).start()

# def stop_now():
#     global stop_flag
#     stop_flag = True
#     status_label.config(text="Stopping... wait karo", fg="red")

# def select_folder(entry):
#     path = filedialog.askdirectory()
#     if path:
#         entry.delete(0, tk.END)
#         entry.insert(0, path)

# def create_gui():
#     root = tk.Tk()
#     root.title("GreenDot Visit Bot - Auto Driver v3")
#     root.geometry("780x520")
#     root.resizable(False, False)

#     style = ttk.Style()
#     style.configure("TProgressbar", thickness=18)

#     tk.Label(root, text="Target URL:", font=("Segoe UI", 11, "bold")).grid(row=0, column=0, padx=15, pady=12, sticky="e")
#     url_entry = tk.Entry(root, width=80)
#     url_entry.insert(0, "https://greendotball.com/?utm_source=herody&utm_medium=26")
#     url_entry.grid(row=0, column=1, columnspan=2, padx=10, pady=12)

#     tk.Label(root, text="Images Folder:", font=("Segoe UI", 11, "bold")).grid(row=1, column=0, padx=15, pady=8, sticky="e")
#     folder_entry = tk.Entry(root, width=80)
#     folder_entry.insert(0, os.path.join(os.getcwd(), "images"))
#     folder_entry.grid(row=1, column=1, padx=10, pady=8)
#     tk.Button(root, text="Browse", command=lambda: select_folder(folder_entry)).grid(row=1, column=2, padx=10)

#     tk.Label(root, text="Total Visits:", font=("Segoe UI", 11, "bold")).grid(row=2, column=0, padx=15, pady=8, sticky="e")
#     visits_entry = tk.Entry(root, width=80)
#     visits_entry.insert(0, "50")
#     visits_entry.grid(row=2, column=1, columnspan=2, padx=10, pady=8)

#     tk.Label(root, text="Parallel (max 3):", font=("Segoe UI", 11, "bold")).grid(row=3, column=0, padx=15, pady=8, sticky="e")
#     parallel_entry = tk.Entry(root, width=80)
#     parallel_entry.insert(0, "2")
#     parallel_entry.grid(row=3, column=1, columnspan=2, padx=10, pady=8)

#     headless_var = tk.BooleanVar(value=False)
#     tk.Checkbutton(root, text="Headless Mode (browser hide)", variable=headless_var, font=("Segoe UI", 10)).grid(row=4, column=1, sticky="w", padx=10, pady=8)

#     status_label = tk.Label(root, text="Ready...", font=("Segoe UI", 10), fg="#555")
#     status_label.grid(row=5, column=0, columnspan=3, pady=8)

#     progress_bar = ttk.Progressbar(root, orient="horizontal", length=680, mode="determinate")
#     progress_bar.grid(row=6, column=0, columnspan=3, padx=15, pady=10)

#     btn_frame = tk.Frame(root)
#     btn_frame.grid(row=7, column=0, columnspan=3, pady=20)

#     tk.Button(btn_frame, text="START", bg="#28a745", fg="white", font=("Segoe UI", 13, "bold"), width=12,
#               command=lambda: threading.Thread(target=run_automation, args=(
#                   url_entry, folder_entry, visits_entry, parallel_entry, headless_var,
#                   status_label, progress_bar), daemon=True).start()).pack(side="left", padx=20)

#     tk.Button(btn_frame, text="STOP", bg="#dc3545", fg="white", font=("Segoe UI", 13, "bold"), width=12,
#               command=stop_now).pack(side="left", padx=20)

#     tk.Label(root, text="• System ka Chrome + Auto ChromeDriver use ho raha hai\n"
#                         "• Chrome latest rakho for best results\n"
#                         "• Parallel 2-3 se zyada mat karo",
#              fg="#6c757d", font=("Segoe UI", 9)).grid(row=8, column=0, columnspan=3, pady=10)

#     root.mainloop()

# if __name__ == "__main__":
#     create_gui()


# import os
# import time
# import random
# import json
# import datetime
# import threading
# import tkinter as tk
# from tkinter import messagebox, filedialog, ttk
# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.common.action_chains import ActionChains
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.common.exceptions import TimeoutException, WebDriverException, NoSuchElementException
# from queue import Queue, Empty
# import logging

# # ================= LOGGING SETUP =================
# logging.basicConfig(
#     level=logging.INFO,
#     format='%(asctime)s [%(levelname)s] %(message)s',
#     handlers=[logging.FileHandler("automation.log", encoding='utf-8'), logging.StreamHandler()]
# )
# logger = logging.getLogger(__name__)

# # ================= CONFIG =================
# LOG_FILE = "visits.json"
# SELECTORS = {
#     "file_input": (By.ID, "fileInput"),
#     "phone_input": (By.CSS_SELECTOR, "input.mobile-number"),
#     "checkbox": (By.ID, "termsCheckbox"),
#     "slider_btn": (By.ID, "slideButton"),
#     "slider_bar": (By.ID, "slideTrack"),
# }

# USER_AGENTS = [
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36",
#     "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_6_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36",
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Edg/143.0.0.0",
# ]

# SCREEN_SIZES = [(1920, 1080), (1366, 768), (1536, 864), (1440, 900), (1600, 900)]

# # ================= UTILS =================
# def generate_random_phone():
#     return random.choice(["6","7","8","9"]) + "".join(str(random.randint(0,9)) for _ in range(9))

# def get_image_list(folder_path):
#     if not os.path.isdir(folder_path):
#         raise Exception("Invalid folder path!")
#     valid_ext = (".jpg", ".jpeg", ".png", ".gif", ".webp")
#     images = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.lower().endswith(valid_ext)]
#     if not images:
#         raise Exception("No valid images found!")
#     images.sort(key=str.lower)
#     return images

# def load_logs():
#     if os.path.exists(LOG_FILE):
#         try:
#             with open(LOG_FILE, "r", encoding="utf-8") as f:
#                 return json.load(f)
#         except:
#             return []
#     return []

# def save_logs(logs):
#     try:
#         with open(LOG_FILE, "w", encoding="utf-8") as f:
#             json.dump(logs, f, indent=4, ensure_ascii=False)
#     except Exception as e:
#         logger.error(f"Failed to save logs: {e}")

# # ================= BOT FUNCTION =================
# def run_bot(target_url, image_path, headless=False):
#     user_agent = random.choice(USER_AGENTS)
#     width, height = random.choice(SCREEN_SIZES)

#     options = Options()
#     options.add_argument(f"--user-agent={user_agent}")
#     options.add_argument(f"--window-size={width},{height}")
#     options.add_argument("--disable-blink-features=AutomationControlled")
#     options.add_argument("--no-sandbox")
#     options.add_argument("--disable-dev-shm-usage")
#     options.add_argument("--disable-gpu")
#     options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
#     options.add_experimental_option("useAutomationExtension", False)

#     if headless:
#         options.add_argument("--headless=new")

#     driver = None
#     try:
#         driver = webdriver.Chrome(options=options)
#         driver.set_page_load_timeout(180)
#         wait = WebDriverWait(driver, 40)

#         logger.info(f"Visit start | UA: {user_agent[:40]}... | {width}x{height} | {os.path.basename(image_path)}")

#         driver.get(target_url)
#         time.sleep(random.uniform(3, 7))

#         file_input = wait.until(EC.presence_of_element_located(SELECTORS["file_input"]))
#         file_input.send_keys(image_path)

#         phone_input = wait.until(EC.element_to_be_clickable(SELECTORS["phone_input"]))
#         phone = generate_random_phone()
#         phone_input.clear()
#         phone_input.send_keys(phone)

#         checkbox = wait.until(EC.element_to_be_clickable(SELECTORS["checkbox"]))
#         driver.execute_script("arguments[0].click();", checkbox)

#         # Slider (human-like)
#         slider_btn = wait.until(EC.element_to_be_clickable(SELECTORS["slider_btn"]))
#         slider_bar = wait.until(EC.presence_of_element_located(SELECTORS["slider_bar"]))
#         track_w = slider_bar.size['width']
#         btn_w = slider_btn.size['width']
#         distance = track_w - btn_w - random.randint(10, 25)

#         actions = ActionChains(driver)
#         actions.click_and_hold(slider_btn).pause(random.uniform(0.2, 0.5))

#         for _ in range(5):
#             move = random.randint(20, distance//6 + 10)
#             actions.move_by_offset(move, random.randint(-10, 10)).pause(random.uniform(0.05, 0.15))
#             distance -= move
#             if distance <= 0: break

#         actions.move_by_offset(distance, random.randint(-8, 8)).pause(0.1)
#         actions.release().perform()

#         time.sleep(random.uniform(5, 11))

#         logger.info(f"[SUCCESS] | Phone: {phone}")
#         return {"phone_number": phone, "image_name": os.path.basename(image_path)}

#     except Exception as e:
#         logger.warning(f"Visit failed: {type(e).__name__} - {str(e)}")
#         return None

#     finally:
#         if driver:
#             try:
#                 driver.quit()
#             except:
#                 pass
#             time.sleep(0.5)

# # ================= WORKER (Maintains exact number of active sessions) =================
# def worker(target_url, image_queue, used_dir, logs, lock, headless, progress_callback):
#     global stop_flag
#     while not stop_flag:
#         try:
#             img_path = image_queue.get_nowait()
#         except Empty:
#             break

#         result = run_bot(target_url, img_path, headless)

#         if result:
#             timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#             with lock:
#                 logs.append({
#                     "visit": len(logs) + 1,
#                     "time": timestamp,
#                     "phone": result["phone_number"],
#                     "image": result["image_name"]
#                 })
#             save_logs(logs)

#             try:
#                 dest = os.path.join(used_dir, os.path.basename(img_path))
#                 os.rename(img_path, dest)
#                 logger.info(f"Moved: {os.path.basename(img_path)} → used_img")
#             except Exception as e:
#                 logger.error(f"Move failed: {e}")

#             progress_callback(1)
#         else:
#             logger.warning("Failed → re-queuing image")
#             image_queue.put(img_path)  # Wapas queue mein daal do
#             time.sleep(10)

#         # Important: yeh sleep nahi hataana – CPU overload se bachata hai
#         time.sleep(random.uniform(4, 10))

# # ================= MAIN AUTOMATION =================
# stop_flag = False
# progress_var = None

# def update_progress(increment=1):
#     global progress_var
#     if progress_var:
#         progress_var.set(progress_var.get() + increment)

# def run_automation(url_entry, folder_entry, visits_entry, parallel_entry, headless_var, status_label, progress_bar):
#     global stop_flag, progress_var
#     stop_flag = False

#     target_url = url_entry.get().strip()
#     folder = folder_entry.get().strip()

#     try:
#         total_visits = int(visits_entry.get())
#         parallel = int(parallel_entry.get())
#         if total_visits <= 0 or parallel <= 0:
#             raise ValueError
#     except:
#         messagebox.showerror("Error", "Visits aur Parallel sahi number daalo!")
#         return

#     if not target_url or not folder:
#         messagebox.showerror("Error", "URL aur Folder dono daalo!")
#         return

#     try:
#         images = get_image_list(folder)
#     except Exception as e:
#         messagebox.showerror("Error", str(e))
#         return

#     total_visits = min(total_visits, len(images))
#     if total_visits == 0:
#         messagebox.showwarning("Warning", "Koi image nahi mili!")
#         return

#     status_label.config(text=f"Shuru... ({total_visits} visits, {parallel} parallel)", fg="blue")

#     logs = load_logs()
#     lock = threading.Lock()
#     q = Queue()
#     for img in images[:total_visits]:
#         q.put(img)

#     used_folder = os.path.join(folder, "used_img")
#     os.makedirs(used_folder, exist_ok=True)

#     progress_var = tk.DoubleVar(value=0)
#     progress_bar['maximum'] = total_visits
#     progress_bar['variable'] = progress_var

#     # ------------------ Important Change ------------------
#     # Har parallel ke liye ek thread, aur har thread apna session maintain karta rahega
#     threads = []
#     for _ in range(parallel):
#         t = threading.Thread(
#             target=worker,
#             args=(target_url, q, used_folder, logs, lock, headless_var.get(), update_progress),
#             daemon=True
#         )
#         t.start()
#         threads.append(t)

#     def monitor():
#         while q.qsize() > 0 or any(t.is_alive() for t in threads):
#             if stop_flag:
#                 break
#             time.sleep(1.2)
#         if stop_flag:
#             status_label.config(text="Stopped by user", fg="orange")
#         else:
#             status_label.config(text="Completed ✓", fg="green")
#             messagebox.showinfo("Done", f"Sab {total_visits} visits complete ho gaye!")

#     threading.Thread(target=monitor, daemon=True).start()

# def stop_now():
#     global stop_flag
#     stop_flag = True
#     status_label.config(text="Stopping...", fg="red")

# def select_folder(entry):
#     path = filedialog.askdirectory()
#     if path:
#         entry.delete(0, tk.END)
#         entry.insert(0, path)

# # ================= GUI =================
# def create_gui():
#     root = tk.Tk()
#     root.title("GreenDot Bot - Smooth Parallel")
#     root.geometry("780x520")
#     root.resizable(False, False)

#     tk.Label(root, text="Target URL:").grid(row=0, column=0, padx=15, pady=10, sticky="e")
#     url_entry = tk.Entry(root, width=80)
#     url_entry.insert(0, "https://greendotball.com/?utm_source=herody&utm_medium=26")
#     url_entry.grid(row=0, column=1, columnspan=2, padx=10)

#     tk.Label(root, text="Images Folder:").grid(row=1, column=0, padx=15, pady=8, sticky="e")
#     folder_entry = tk.Entry(root, width=80)
#     folder_entry.insert(0, os.path.join(os.getcwd(), "images"))
#     folder_entry.grid(row=1, column=1, padx=10)
#     tk.Button(root, text="Browse", command=lambda: select_folder(folder_entry)).grid(row=1, column=2)

#     tk.Label(root, text="Total Visits:").grid(row=2, column=0, padx=15, pady=8, sticky="e")
#     visits_entry = tk.Entry(root, width=80)
#     visits_entry.insert(0, "50")
#     visits_entry.grid(row=2, column=1, columnspan=2)

#     tk.Label(root, text="Parallel Sessions:").grid(row=3, column=0, padx=15, pady=8, sticky="e")
#     parallel_entry = tk.Entry(root, width=80)
#     parallel_entry.insert(0, "5")
#     parallel_entry.grid(row=3, column=1, columnspan=2)

#     headless_var = tk.BooleanVar(value=False)
#     tk.Checkbutton(root, text="Headless Mode", variable=headless_var).grid(row=4, column=1, sticky="w", padx=10, pady=8)

#     status_label = tk.Label(root, text="Ready...", fg="#555")
#     status_label.grid(row=5, column=0, columnspan=3, pady=10)

#     progress_bar = ttk.Progressbar(root, orient="horizontal", length=680, mode="determinate")
#     progress_bar.grid(row=6, column=0, columnspan=3, padx=15, pady=10)

#     btn_frame = tk.Frame(root)
#     btn_frame.grid(row=7, column=0, columnspan=3, pady=20)

#     tk.Button(btn_frame, text="START", bg="#28a745", fg="white", font=("Arial", 12, "bold"),
#               command=lambda: threading.Thread(target=run_automation, args=(
#                   url_entry, folder_entry, visits_entry, parallel_entry, headless_var,
#                   status_label, progress_bar), daemon=True).start()).pack(side="left", padx=30)

#     tk.Button(btn_frame, text="STOP", bg="#dc3545", fg="white", font=("Arial", 12, "bold"),
#               command=stop_now).pack(side="left", padx=30)

#     tk.Label(root, text="• Parallel jitna daalo utne browsers chalenge\n"
#                         "• Ek complete hone pe next shuru ho jayega", fg="#666").grid(row=8, column=0, columnspan=3, pady=10)

#     root.mainloop()

# if __name__ == "__main__":
#     create_gui()



# import os
# import sys
# import time
# import random
# import json
# import datetime
# import threading
# import tkinter as tk
# from tkinter import messagebox, filedialog, ttk
# from selenium import webdriver
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.common.by import By
# from selenium.webdriver.common.action_chains import ActionChains
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.common.exceptions import TimeoutException, WebDriverException, NoSuchElementException
# from queue import Queue, Empty
# import logging

# # webdriver-manager ko import kar rahe hain
# from webdriver_manager.chrome import ChromeDriverManager

# # ================= LOGGING SETUP =================
# logging.basicConfig(
#     level=logging.INFO,
#     format='%(asctime)s [%(levelname)s] %(message)s',
#     handlers=[
#         logging.FileHandler("automation.log", encoding='utf-8'),
#         logging.StreamHandler()
#     ]
# )
# logger = logging.getLogger(__name__)

# # ================= CONFIG =================
# LOG_FILE = "visits.json"

# SELECTORS = {
#     "file_input":    (By.ID, "fileInput"),
#     "phone_input":   (By.CSS_SELECTOR, "input.mobile-number"),
#     "checkbox":      (By.ID, "termsCheckbox"),
#     "slider_btn":    (By.ID, "slideButton"),
#     "slider_bar":    (By.ID, "slideTrack"),
# }

# USER_AGENTS = [
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
#     "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_6_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Edg/129.0.0.0",
# ]

# SCREEN_SIZES = [(1920, 1080), (1366, 768), (1536, 864), (1440, 900), (1600, 900), (1280, 720)]

# # ================= UTILS =================
# def generate_random_phone():
#     return random.choice(["6","7","8","9"]) + "".join(str(random.randint(0,9)) for _ in range(9))

# def get_image_list(folder_path):
#     if not os.path.isdir(folder_path):
#         raise Exception("Invalid folder path!")
    
#     valid_ext = (".jpg", ".jpeg", ".png", ".gif", ".webp")
#     images = [
#         os.path.join(folder_path, f)
#         for f in os.listdir(folder_path)
#         if f.lower().endswith(valid_ext)
#     ]
    
#     if not images:
#         raise Exception("No valid images found in folder!")
    
#     images.sort(key=str.lower)
#     return images

# def load_logs():
#     if os.path.exists(LOG_FILE):
#         try:
#             with open(LOG_FILE, "r", encoding="utf-8") as f:
#                 return json.load(f)
#         except:
#             return []
#     return []

# def save_logs(logs):
#     try:
#         with open(LOG_FILE, "w", encoding="utf-8") as f:
#             json.dump(logs, f, indent=4, ensure_ascii=False)
#     except Exception as e:
#         logger.error(f"Failed to save logs: {e}")

# # ================= BOT FUNCTION =================
# def run_bot(target_url, image_path, headless=False):
#     user_agent = random.choice(USER_AGENTS)
#     width, height = random.choice(SCREEN_SIZES)

#     options = Options()
#     options.add_argument(f"--user-agent={user_agent}")
#     options.add_argument(f"--window-size={width},{height}")
#     options.add_argument("--disable-blink-features=AutomationControlled")
#     options.add_argument("--no-sandbox")
#     options.add_argument("--disable-dev-shm-usage")
#     options.add_argument("--disable-gpu")
#     options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
#     options.add_experimental_option("useAutomationExtension", False)

#     if headless:
#         options.add_argument("--headless=new")
#         options.add_argument("--disable-extensions")
#         options.add_argument("--window-position=0,0")

#     driver = None
#     try:
#         # ←←← Yeh important change hai! ←←←
#         service = Service(ChromeDriverManager().install())
#         driver = webdriver.Chrome(service=service, options=options)

#         driver.set_page_load_timeout(180)
#         wait = WebDriverWait(driver, 45)

#         logger.info(f"START | UA: {user_agent[:45]}... | {width}x{height} | {os.path.basename(image_path)}")

#         driver.get(target_url)
#         time.sleep(random.uniform(3.5, 8.2))

#         file_input = wait.until(EC.presence_of_element_located(SELECTORS["file_input"]))
#         file_input.send_keys(os.path.abspath(image_path))  # absolute path better hota hai

#         phone_input = wait.until(EC.element_to_be_clickable(SELECTORS["phone_input"]))
#         phone = generate_random_phone()
#         phone_input.clear()
#         phone_input.send_keys(phone)
#         time.sleep(random.uniform(0.4, 1.1))

#         checkbox = wait.until(EC.element_to_be_clickable(SELECTORS["checkbox"]))
#         driver.execute_script("arguments[0].click();", checkbox)
#         time.sleep(random.uniform(0.6, 1.3))

#         # Slider simulation - thodi aur natural banayi
#         slider_btn = wait.until(EC.element_to_be_clickable(SELECTORS["slider_btn"]))
#         slider_bar = wait.until(EC.presence_of_element_located(SELECTORS["slider_bar"]))

#         track_w = slider_bar.size['width']
#         btn_w = slider_btn.size['width']
#         max_distance = track_w - btn_w - random.randint(12, 28)

#         actions = ActionChains(driver)
#         actions.click_and_hold(slider_btn).pause(random.uniform(0.25, 0.65))

#         current = 0
#         while current < max_distance:
#             step = random.randint(18, max(35, max_distance//5))
#             y_offset = random.randint(-11, 11)
#             actions.move_by_offset(step, y_offset).pause(random.uniform(0.06, 0.14))
#             current += step

#         # last adjustment
#         if current > max_distance:
#             actions.move_by_offset(max_distance - current, random.randint(-9, 9))
#         else:
#             actions.move_by_offset(max_distance - current, random.randint(-7, 7))

#         actions.pause(random.uniform(0.08, 0.22)).release().perform()

#         time.sleep(random.uniform(5.5, 12.5))

#         logger.info(f"[SUCCESS] Phone: {phone}")
#         return {"phone_number": phone, "image_name": os.path.basename(image_path)}

#     except Exception as e:
#         logger.warning(f"Visit failed: {type(e).__name__} → {str(e)}")
#         return None

#     finally:
#         if driver is not None:
#             try:
#                 driver.quit()
#             except:
#                 pass
#             time.sleep(0.6)

# # ================= WORKER THREAD =================
# def worker(target_url, image_queue, used_dir, logs, lock, headless, progress_callback):
#     global stop_flag

#     while not stop_flag:
#         try:
#             img_path = image_queue.get_nowait()
#         except Empty:
#             break

#         result = run_bot(target_url, img_path, headless)

#         if result:
#             timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#             with lock:
#                 logs.append({
#                     "visit": len(logs) + 1,
#                     "time": timestamp,
#                     "phone": result["phone_number"],
#                     "image": result["image_name"]
#                 })
#                 save_logs(logs)

#             try:
#                 dest = os.path.join(used_dir, os.path.basename(img_path))
#                 os.rename(img_path, dest)
#                 logger.info(f"Moved → used_img: {os.path.basename(img_path)}")
#             except Exception as e:
#                 logger.error(f"Move failed: {e}")

#             progress_callback(1)
#         else:
#             logger.warning("Failed → re-queuing same image")
#             image_queue.put(img_path)
#             time.sleep(12)  # thoda zyada wait jab fail ho

#         time.sleep(random.uniform(5, 11))   # breathing space between attempts

# # ================= MAIN AUTOMATION LOGIC =================
# stop_flag = False
# progress_var = None

# def update_progress(increment=1):
#     global progress_var
#     if progress_var is not None:
#         progress_var.set(progress_var.get() + increment)

# def run_automation(url_entry, folder_entry, visits_entry, parallel_entry, headless_var, status_label, progress_bar):
#     global stop_flag, progress_var
#     stop_flag = False

#     target_url = url_entry.get().strip()
#     folder = folder_entry.get().strip()

#     try:
#         total_visits = int(visits_entry.get())
#         parallel = int(parallel_entry.get())
#         if total_visits <= 0 or parallel <= 0:
#             raise ValueError
#     except:
#         messagebox.showerror("Error", "Visits aur Parallel sahi number daalo!")
#         return

#     if not target_url or not folder:
#         messagebox.showerror("Error", "URL aur Folder path daalna zaroori hai!")
#         return

#     try:
#         images = get_image_list(folder)
#     except Exception as e:
#         messagebox.showerror("Error", str(e))
#         return

#     total_visits = min(total_visits, len(images))
#     if total_visits == 0:
#         messagebox.showwarning("Warning", "Folder mein koi valid image nahi mili!")
#         return

#     status_label.config(text=f"Starting... ({total_visits} visits, {parallel} parallel)", fg="blue")

#     logs = load_logs()
#     lock = threading.Lock()
#     q = Queue()

#     for img in images[:total_visits]:
#         q.put(img)

#     used_folder = os.path.join(folder, "used_img")
#     os.makedirs(used_folder, exist_ok=True)

#     progress_var = tk.DoubleVar(value=0)
#     progress_bar['maximum'] = total_visits
#     progress_bar['variable'] = progress_var

#     threads = []
#     for _ in range(parallel):
#         t = threading.Thread(
#             target=worker,
#             args=(target_url, q, used_folder, logs, lock, headless_var.get(), update_progress),
#             daemon=True
#         )
#         t.start()
#         threads.append(t)

#     def monitor():
#         while q.qsize() > 0 or any(t.is_alive() for t in threads):
#             if stop_flag:
#                 break
#             time.sleep(1.3)

#         if stop_flag:
#             status_label.config(text="Stopped by user", fg="orange")
#         else:
#             status_label.config(text="Completed ✓", fg="green")
#             messagebox.showinfo("Success", f"{total_visits} visits complete ho gaye!")

#     threading.Thread(target=monitor, daemon=True).start()

# def stop_now():
#     global stop_flag
#     stop_flag = True
#     # status_label ko yahan access karna safe nahi, run_automation ke andar se hi manage kar rahe hain

# def select_folder(entry):
#     path = filedialog.askdirectory()
#     if path:
#         entry.delete(0, tk.END)
#         entry.insert(0, path)

# # ================= GUI =================
# def create_gui():
#     root = tk.Tk()
#     root.title("GreenDot Bot - Parallel Visits")
#     root.geometry("800x540")
#     root.resizable(False, False)

#     tk.Label(root, text="Target URL:").grid(row=0, column=0, padx=18, pady=12, sticky="e")
#     url_entry = tk.Entry(root, width=82)
#     url_entry.insert(0, "https://greendotball.com/?utm_source=herody&utm_medium=26")
#     url_entry.grid(row=0, column=1, columnspan=2, padx=10, pady=8)

#     tk.Label(root, text="Images Folder:").grid(row=1, column=0, padx=18, pady=10, sticky="e")
#     folder_entry = tk.Entry(root, width=82)
#     folder_entry.insert(0, os.path.join(os.getcwd(), "images"))
#     folder_entry.grid(row=1, column=1, padx=10, pady=8)
#     tk.Button(root, text="Browse", command=lambda: select_folder(folder_entry)).grid(row=1, column=2, padx=8)

#     tk.Label(root, text="Total Visits:").grid(row=2, column=0, padx=18, pady=10, sticky="e")
#     visits_entry = tk.Entry(root, width=82)
#     visits_entry.insert(0, "50")
#     visits_entry.grid(row=2, column=1, columnspan=2, padx=10, pady=8)

#     tk.Label(root, text="Parallel Sessions:").grid(row=3, column=0, padx=18, pady=10, sticky="e")
#     parallel_entry = tk.Entry(root, width=82)
#     parallel_entry.insert(0, "5")
#     parallel_entry.grid(row=3, column=1, columnspan=2, padx=10, pady=8)

#     headless_var = tk.BooleanVar(value=False)
#     tk.Checkbutton(root, text="Headless Mode (Invisible)", variable=headless_var).grid(row=4, column=1, sticky="w", padx=10, pady=8)

#     status_label = tk.Label(root, text="Ready...", fg="#555", font=("Segoe UI", 10))
#     status_label.grid(row=5, column=0, columnspan=3, pady=12)

#     progress_bar = ttk.Progressbar(root, orient="horizontal", length=720, mode="determinate")
#     progress_bar.grid(row=6, column=0, columnspan=3, padx=20, pady=8)

#     btn_frame = tk.Frame(root)
#     btn_frame.grid(row=7, column=0, columnspan=3, pady=20)

#     tk.Button(btn_frame, text="START", bg="#28a745", fg="white", font=("Segoe UI", 13, "bold"),
#               width=12, command=lambda: threading.Thread(target=run_automation, args=(
#                   url_entry, folder_entry, visits_entry, parallel_entry, headless_var,
#                   status_label, progress_bar), daemon=True).start()
#               ).pack(side="left", padx=40)

#     tk.Button(btn_frame, text="STOP", bg="#dc3545", fg="white", font=("Segoe UI", 13, "bold"),
#               width=12, command=stop_now).pack(side="left", padx=40)

#     tk.Label(root, text="Note: Parallel jitna daalo utne browsers ek saath chalenge\n"
#                         "Failed visits automatically retry honge", fg="#666", justify="left"
#              ).grid(row=8, column=0, columnspan=3, pady=6, padx=20, sticky="w")

#     root.mainloop()

# if __name__ == "__main__":
#     create_gui()



# import time
# import random
# from selenium import webdriver
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.chrome.options import Options
# from webdriver_manager.chrome import ChromeDriverManager

# # ================= CONFIG =================
# TARGET_URL = "https://partners.streakads.com/click?aid=3&oid=396"

# # Tumhara Geonode credentials (sirf username aur password change karna hai)
# GEONODE_USER = "geonode_xvmYN44Bvz-type-residential-country-{}"   # {} country code ke liye placeholder hai
# GEONODE_PASS = "CHANGE_ME_SECRET"
# GEONODE_HOST = "sg.proxy.geonode.io"
# GEONODE_PORT = "11000"

# COUNTRIES = {
#     "CA": "Canada",
#     "IT": "Italy",
#     "FR": "France",
#     "AU": "Australia",
#     "PL": "Poland",
#     "GR": "Greece",
#     "CH": "Switzerland"
# }

# # ================= PROXY SETUP =================
# def get_proxy_for_country(country_code):
#     username = GEONODE_USER.format(country_code.lower())
#     proxy_url = f"socks5://{username}:CHANGE_ME_PASSWORD@{GEONODE_HOST}:{GEONODE_PORT}"
#     return proxy_url

# # ================= MAIN FUNCTION =================
# def open_with_proxy():
#     country_code = random.choice(list(COUNTRIES.keys()))
#     country_name = COUNTRIES[country_code]
    
#     proxy = get_proxy_for_country(country_code)
    
#     print(f"🌍 Country selected: {country_name} ({country_code})")
#     print(f"🔗 Using Proxy: {proxy}")

#     options = Options()
    
#     # Proxy set kar rahe hain (SOCKS5 with auth)
#     options.add_argument(f"--proxy-server={proxy}")
    
#     # Basic anti-detection + realistic settings
#     options.add_argument("--disable-blink-features=AutomationControlled")
#     options.add_experimental_option("excludeSwitches", ["enable-automation"])
#     options.add_experimental_option("useAutomationExtension", False)
#     options.add_argument("--no-sandbox")
#     options.add_argument("--disable-dev-shm-usage")
    
#     # Random window size
#     width = random.choice([1280, 1366, 1440, 1536, 1920])
#     height = random.choice([720, 768, 864, 900, 1080])
#     options.add_argument(f"--window-size={width},{height}")

#     driver = None
#     try:
#         service = Service(ChromeDriverManager().install())
#         driver = webdriver.Chrome(service=service, options=options)
        
#         print("🚀 Opening browser with proxy...")
#         driver.get(TARGET_URL)
        
#         # Page load hone do + random wait
#         time.sleep(random.uniform(6, 12))
        
#         # Natural scroll down
#         print("📜 Scrolling...")
#         driver.execute_script("window.scrollTo(0, document.body.scrollHeight * 0.4);")
#         time.sleep(random.uniform(2.5, 5.5))
        
#         driver.execute_script("window.scrollTo(0, document.body.scrollHeight * 0.85);")
#         time.sleep(random.uniform(3, 7))
        
#         print(f"✅ Task completed for {country_name}")
        
#     except Exception as e:
#         print(f"❌ Error: {e}")
#     finally:
#         if driver:
#             time.sleep(random.uniform(2, 4))   # thoda aur rukne do
#             driver.quit()
#             print("🔒 Browser closed\n")

# # ================= RUN =================
# if __name__ == "__main__":
#     print("=== Geonode Country Specific Browser Opener Started ===\n")
    
#     # Ek baar run karne ke liye
#     open_with_proxy()
    
#     # Agar multiple times chalana hai toh niche wala uncomment kar do
#     # for i in range(10):        # 10 baar chalega
#     #     print(f"\n--- Run {i+1} ---")
#     #     open_with_proxy()
#     #     time.sleep(random.uniform(8, 20))   # har run ke beech gap




# import time
# import random
# import undetected_chromedriver as uc

# # ================= CONFIG =================
# TARGET_URL = "https://partners.streakads.com/click?aid=3&oid=396"

# GEONODE_USER_BASE = "geonode_xvmYN44Bvz-type-residential-country-{}"
# GEONODE_PASS = "CHANGE_ME_SECRET"
# GEONODE_HOST = "sg.proxy.geonode.io"
# GEONODE_PORT = "11000"

# COUNTRIES = ["CA", "IT", "FR", "AU", "PL", "GR", "CH"]

# # ================= MAIN FUNCTION =================
# def open_with_proxy():
#     country_code = random.choice(COUNTRIES)
#     username = GEONODE_USER_BASE.format(country_code.lower())
    
#     proxy = f"socks5://{username}:CHANGE_ME_PASSWORD@{GEONODE_HOST}:{GEONODE_PORT}"
    
#     print(f"🌍 Country: {country_code} | Proxy: {proxy[:65]}...")

#     options = uc.ChromeOptions()
    
#     options.add_argument(f'--proxy-server={proxy}')
#     options.add_argument("--no-sandbox")
#     options.add_argument("--disable-dev-shm-usage")
#     options.add_argument("--disable-blink-features=AutomationControlled")
#     options.add_argument("--disable-extensions")
    
#     # Random realistic window size
#     width = random.choice([1366, 1440, 1536, 1920])
#     height = random.choice([768, 900, 1080])
#     options.add_argument(f"--window-size={width},{height}")

#     driver = None
#     try:
#         # ←←← Yeh line important hai version mismatch fix ke liye ←←←
#         driver = uc.Chrome(
#             options=options, 
#             use_subprocess=True,
#             version_main=146          # Tumhara Chrome 146 hai isliye yeh daala
#         )
        
#         print("🚀 Opening browser with Geonode proxy...")
#         driver.get(TARGET_URL)
        
#         # Wait for page to load
#         time.sleep(random.uniform(8, 15))
        
#         # Natural scrolling
#         print("📜 Scrolling slowly...")
#         driver.execute_script("window.scrollTo(0, document.body.scrollHeight * 0.35);")
#         time.sleep(random.uniform(2.5, 5.5))
        
#         driver.execute_script("window.scrollTo(0, document.body.scrollHeight * 0.8);")
#         time.sleep(random.uniform(3.5, 7))
        
#         print(f"✅ Task completed for {country_code}\n")
        
#     except Exception as e:
#         print(f"❌ Error: {e}")
#     finally:
#         if driver:
#             time.sleep(random.uniform(2, 4))
#             try:
#                 driver.quit()
#             except:
#                 pass
#             print("🔒 Browser closed\n")

# # ================= RUN =================
# if __name__ == "__main__":
#     print("=== Geonode Country Proxy Opener (Fixed Version) ===\n")
    
#     # Ek baar test ke liye
#     open_with_proxy()
    
#     # Agar multiple times chalana hai to niche wala loop uncomment kar do
#     # for i in range(5):   # 5 baar chalega
#     #     print(f"\n--- Run {i+1} ---")
#     #     open_with_proxy()
#     #     time.sleep(random.uniform(10, 25))



# import time
# import random
# import undetected_chromedriver as uc
# from seleniumwire import webdriver   # selenium-wire ka webdriver

# # ================= CONFIG =================
# TARGET_URL = "https://partners.streakads.com/click?aid=3&oid=396"

# GEONODE_USER_BASE = "geonode_xvmYN44Bvz-type-residential-country-{}"
# GEONODE_PASS = "CHANGE_ME_SECRET"
# GEONODE_HOST = "sg.proxy.geonode.io"
# GEONODE_PORT = "11000"

# COUNTRIES = ["CA", "IT", "FR", "AU", "PL", "GR", "CH"]

# # ================= MAIN FUNCTION =================
# def open_with_proxy():
#     country_code = random.choice(COUNTRIES)
#     username = GEONODE_USER_BASE.format(country_code.lower())
    
#     proxy_url = f"socks5://{username}:CHANGE_ME_PASSWORD@{GEONODE_HOST}:{GEONODE_PORT}"
    
#     print(f"🌍 Country Selected : {country_code}")
#     print(f"🔗 Proxy            : {proxy_url[:75]}...")

#     # Selenium Wire Proxy Settings
#     seleniumwire_options = {
#         'proxy': {
#             'http':  proxy_url,
#             'https': proxy_url,
#             'no_proxy': 'localhost,127.0.0.1'
#         }
#     }

#     options = uc.ChromeOptions()
#     options.add_argument("--no-sandbox")
#     options.add_argument("--disable-dev-shm-usage")
#     options.add_argument("--disable-blink-features=AutomationControlled")
#     options.add_argument("--disable-extensions")

#     width = random.choice([1366, 1440, 1536, 1920])
#     height = random.choice([768, 900, 1080])
#     options.add_argument(f"--window-size={width},{height}")

#     driver = None
#     try:
#         # Important: undetected_chromedriver + seleniumwire combine
#         driver = webdriver.Chrome(
#             options=options,
#             seleniumwire_options=seleniumwire_options
#         )
        
#         print("🚀 Opening browser with Geonode proxy...")

#         # IP Check
#         driver.get("https://api.ipify.org?format=json")
#         time.sleep(random.uniform(5, 8))
        
#         try:
#             ip_text = driver.find_element("tag name", "body").text.strip()
#             print(f"🌐 Real Exit IP     : {ip_text}")
#         except:
#             print("🌐 Real Exit IP     : Unable to fetch cleanly")

#         # Target URL
#         print(f"🔗 Opening Target   : {TARGET_URL}")
#         driver.get(TARGET_URL)
        
#         time.sleep(random.uniform(8, 16))
        
#         print("📜 Scrolling slowly...")
#         driver.execute_script("window.scrollTo(0, document.body.scrollHeight * 0.35);")
#         time.sleep(random.uniform(3, 6))
        
#         driver.execute_script("window.scrollTo(0, document.body.scrollHeight * 0.85);")
#         time.sleep(random.uniform(4, 8))

#         print(f"✅ Visit Completed for {country_code}\n")

#     except Exception as e:
#         print(f"❌ Error: {e}")
#     finally:
#         if driver:
#             time.sleep(random.uniform(2, 4))
#             try:
#                 driver.quit()
#             except:
#                 pass
#             print("🔒 Browser closed\n")

# # ================= RUN =================
# if __name__ == "__main__":
#     print("=== Geonode SOCKS5 Proxy + Real IP Show ===\n")
#     open_with_proxy()
    
#     # Multiple visits ke liye (uncomment kar do)
#     # for i in range(5):
#     #     print(f"\n--- Run {i+1} ---")
#     #     open_with_proxy()
#     #     time.sleep(random.uniform(12, 30))



# import time
# import random
# import undetected_chromedriver as uc
# from seleniumwire import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.common.action_chains import ActionChains
# from selenium.common.exceptions import TimeoutException

# # ================= CONFIG =================
# TARGET_URL = "https://partners.streakads.com/click?aid=3&oid=396"

# GEONODE_USER_BASE = "geonode_xvmYN44Bvz-type-residential-country-{}"
# GEONODE_PASS = "CHANGE_ME_SECRET"
# GEONODE_HOST = "sg.proxy.geonode.io"
# GEONODE_PORT = "11000"

# COUNTRIES = ["CA", "IT", "FR", "AU", "PL", "GR", "CH"]

# # Realistic User Agents
# USER_AGENTS = [
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36",
#     "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:135.0) Gecko/20100101 Firefox/135.0"
# ]

# # ================= MAIN FUNCTION =================
# def open_with_proxy():
#     country_code = random.choice(COUNTRIES)
#     username = GEONODE_USER_BASE.format(country_code.lower())
    
#     proxy_url = f"socks5://{username}:CHANGE_ME_PASSWORD@{GEONODE_HOST}:{GEONODE_PORT}"
    
#     print(f"🌍 Country Selected : {country_code}")
#     print(f"🔗 Proxy            : {proxy_url[:75]}...")

#     seleniumwire_options = {
#         'proxy': {
#             'http':  proxy_url,
#             'https': proxy_url,
#             'no_proxy': 'localhost,127.0.0.1'
#         }
#     }

#     options = uc.ChromeOptions()
    
#     # Better anti-detection
#     options.add_argument(f"--user-agent={random.choice(USER_AGENTS)}")
#     options.add_argument("--no-sandbox")
#     options.add_argument("--disable-dev-shm-usage")
#     options.add_argument("--disable-blink-features=AutomationControlled")
#     options.add_argument("--disable-extensions")
#     options.add_argument("--disable-infobars")
#     options.add_argument("--start-maximized")

#     width = random.choice([1366, 1440, 1536, 1920])
#     height = random.choice([768, 900, 1080])
#     options.add_argument(f"--window-size={width},{height}")

#     driver = None
#     try:
#         driver = webdriver.Chrome(
#             options=options,
#             seleniumwire_options=seleniumwire_options
#         )
        
#         print("🚀 Opening browser...")

#         # IP Check
#         driver.get("https://api.ipify.org?format=json")
#         time.sleep(random.uniform(4, 7))
#         try:
#             ip_text = driver.find_element("tag name", "body").text.strip()
#             print(f"🌐 Real Exit IP     : {ip_text}")
#         except:
#             print("🌐 Real Exit IP     : (parsed)")

#         # === Target URL with human-like behavior ===
#         print(f"🔗 Opening Target URL...")
#         driver.get(TARGET_URL)
        
#         # Wait for page to start loading + random human delay
#         time.sleep(random.uniform(6, 12))

#         # Human-like scrolling (slow + random pauses)
#         print("📜 Human-like Scrolling...")
#         scroll_height = driver.execute_script("return document.body.scrollHeight")
        
#         # Scroll in small steps with pauses
#         for i in range(3):
#             scroll_pos = random.randint(300, scroll_height // 3)
#             driver.execute_script(f"window.scrollTo(0, {scroll_pos});")
#             time.sleep(random.uniform(1.5, 3.5))
            
#             # Random small mouse movement
#             try:
#                 actions = ActionChains(driver)
#                 actions.move_by_offset(random.randint(-50, 50), random.randint(-30, 30)).perform()
#                 time.sleep(random.uniform(0.8, 2.2))
#             except:
#                 pass

#         # Final slow scroll to bottom
#         driver.execute_script("window.scrollTo(0, document.body.scrollHeight * 0.85);")
#         time.sleep(random.uniform(4, 9))

#         # Random clicks on non-important areas (to look more human)
#         try:
#             body = driver.find_element(By.TAG_NAME, "body")
#             actions = ActionChains(driver)
#             actions.move_to_element_with_offset(body, random.randint(100, 400), random.randint(100, 400))
#             actions.click()
#             actions.perform()
#             time.sleep(random.uniform(1, 3))
#         except:
#             pass

#         print(f"✅ Visit Completed for {country_code} (Human-like behavior applied)\n")

#     except Exception as e:
#         print(f"❌ Error: {e}")
#     finally:
#         if driver:
#             time.sleep(random.uniform(3, 6))   # extra wait before closing
#             try:
#                 driver.quit()
#             except:
#                 pass
#             print("🔒 Browser closed\n")

# # ================= RUN =================
# if __name__ == "__main__":
#     print("=== Geonode + Human-like Traffic Script ===\n")
    
#     # Single test
#     open_with_proxy()
    
#     # Multiple visits (uncomment aur number change kar sakte ho)
#     # for i in range(8):
#     #     print(f"\n=== Run {i+1} ===")
#     #     open_with_proxy()
#     #     time.sleep(random.uniform(15, 35))   # natural delay between visits



# import time
# import random
# import undetected_chromedriver as uc
# from seleniumwire import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.common.action_chains import ActionChains

# # ================= CONFIG =================
# TARGET_URL = "https://partners.streakads.com/click?aid=3&oid=396"

# GEONODE_USER_BASE = "geonode_xvmYN44Bvz-type-residential-country-{}"
# GEONODE_PASS = "CHANGE_ME_SECRET"
# GEONODE_HOST = "sg.proxy.geonode.io"
# GEONODE_PORT = "11000"

# COUNTRIES = ["CA", "IT", "FR", "AU", "PL", "GR", "CH"]

# USER_AGENTS = [
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36",
#     "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36"
# ]

# # ================= MAIN FUNCTION =================
# def open_with_proxy():
#     country_code = random.choice(COUNTRIES)
#     username = GEONODE_USER_BASE.format(country_code.lower())
    
#     proxy_url = f"socks5://{username}:CHANGE_ME_PASSWORD@{GEONODE_HOST}:{GEONODE_PORT}"
    
#     print(f"🌍 Country : {country_code}")
#     print(f"🔗 Proxy   : {proxy_url[:75]}...")

#     seleniumwire_options = {
#         'proxy': {'http': proxy_url, 'https': proxy_url, 'no_proxy': 'localhost,127.0.0.1'}
#     }

#     options = uc.ChromeOptions()
#     options.add_argument(f"--user-agent={random.choice(USER_AGENTS)}")
#     options.add_argument("--no-sandbox")
#     options.add_argument("--disable-dev-shm-usage")
#     options.add_argument("--disable-blink-features=AutomationControlled")
#     options.add_argument("--start-maximized")

#     width = random.choice([1366, 1440, 1536, 1920])
#     height = random.choice([768, 900, 1080])
#     options.add_argument(f"--window-size={width},{height}")

#     driver = None
#     try:
#         driver = webdriver.Chrome(options=options, seleniumwire_options=seleniumwire_options)
        
#         print("🚀 Browser opened...")

#         # IP Check
#         driver.get("https://api.ipify.org?format=json")
#         time.sleep(random.uniform(4, 7))
#         try:
#             ip_text = driver.find_element("tag name", "body").text.strip()
#             print(f"🌐 Real Exit IP : {ip_text}")
#         except:
#             print("🌐 Real Exit IP : (fetched)")

#         # Target URL
#         print(f"🔗 Opening rotator URL...")
#         driver.get(TARGET_URL)
        
#         # Pehle thoda wait (redirect hone do)
#         time.sleep(random.uniform(5, 10))

#         current_url = driver.current_url
#         print(f"📍 Landed on    : {current_url[:90]}...")

#         # Human-like behavior on final page
#         print("📜 Human-like interaction...")
        
#         # Safe scrolling
#         try:
#             for _ in range(random.randint(2, 4)):
#                 scroll_amount = random.randint(400, 900)
#                 driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
#                 time.sleep(random.uniform(1.8, 4.2))
                
#                 # Random mouse move
#                 try:
#                     actions = ActionChains(driver)
#                     actions.move_by_offset(random.randint(-80, 80), random.randint(-40, 40)).perform()
#                     time.sleep(random.uniform(0.7, 2.1))
#                 except:
#                     pass
#         except:
#             pass

#         # Final wait on the casino page
#         time.sleep(random.uniform(6, 14))

#         print(f"✅ Visit done for {country_code} → Landed on casino page\n")

#     except Exception as e:
#         print(f"❌ Error: {e}")
#     finally:
#         if driver:
#             time.sleep(random.uniform(3, 7))
#             try:
#                 driver.quit()
#             except:
#                 pass
#             print("🔒 Browser closed\n")

# # ================= RUN =================
# if __name__ == "__main__":
#     print("=== Geonode + Human-like Casino Rotator Traffic ===\n")
    
#     open_with_proxy()   # single test
    
#     # Multiple visits ke liye uncomment kar do
#     # for i in range(6):
#     #     print(f"\n=== Run {i+1} ===")
#     #     open_with_proxy()
#     #     time.sleep(random.uniform(18, 40))


# import time
# import random
# from seleniumwire import webdriver
# from selenium.webdriver.firefox.options import Options
# from selenium.webdriver.common.by import By
# from selenium.webdriver.common.action_chains import ActionChains
# from selenium.webdriver.firefox.service import Service
# from webdriver_manager.firefox import GeckoDriverManager   # agar use karna ho to

# # ================= CONFIG =================
# TARGET_URL = "https://partners.streakads.com/click?aid=3&oid=396"

# GEONODE_USER_BASE = "geonode_xvmYN44Bvz-type-residential-country-{}"
# GEONODE_PASS = "CHANGE_ME_SECRET"
# GEONODE_HOST = "sg.proxy.geonode.io"
# GEONODE_PORT = "11000"

# COUNTRIES = ["CA", "IT", "FR", "AU", "PL", "GR", "CH"]

# USER_AGENTS = [
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:135.0) Gecko/20100101 Firefox/135.0 Waterfox/135.0",
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:133.0) Gecko/20100101 Firefox/133.0 Waterfox/133.0",
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:132.0) Gecko/20100101 Firefox/132.0",
# ]

# WATERFOX_PATH = r"C:\Users\HP\Downloads\Scrap\Waterfox\waterfox.exe"   # agar waterfox.exe yahan hai to exact path daal do

# # ================= MAIN FUNCTION =================
# def open_with_proxy():
#     country_code = random.choice(COUNTRIES)
#     username = GEONODE_USER_BASE.format(country_code.lower())
    
#     proxy_url = f"socks5://{username}:CHANGE_ME_PASSWORD@{GEONODE_HOST}:{GEONODE_PORT}"
    
#     print(f"🌍 Country : {country_code}")
#     print(f"🔗 Proxy   : {proxy_url[:75]}...")

#     seleniumwire_options = {
#         'proxy': {'http': proxy_url, 'https': proxy_url, 'no_proxy': 'localhost,127.0.0.1'}
#     }

#     options = Options()
    
#     # Waterfox binary location
#     options.binary_location = WATERFOX_PATH
    
#     # User-Agent
#     options.set_preference("general.useragent.override", random.choice(USER_AGENTS))
    
#     # Anti-detection preferences
#     options.set_preference("dom.webdriver.enabled", False)
#     options.set_preference("useAutomationExtension", False)
#     options.set_preference("privacy.resistFingerprinting", False)
#     options.set_preference("webdriver.assume_untrusted", False)
    
#     options.add_argument("--no-sandbox")
#     options.add_argument("--disable-dev-shm-usage")
#     options.add_argument("--start-maximized")

#     # Window size
#     width = random.choice([1366, 1440, 1536, 1920])
#     height = random.choice([768, 900, 1080])
#     options.add_argument(f"--width={width}")
#     options.add_argument(f"--height={height}")

#     driver = None
#     try:
#         # GeckoDriver auto manage (recommended)
#         service = Service(GeckoDriverManager().install())
        
#         driver = webdriver.Chrome(   # ← Yeh galti nahi hai, seleniumwire ke saath Firefox bhi Chrome naam se hi call hota hai kabhi kabhi, lekin sahi hai Firefox
#             seleniumwire_options=seleniumwire_options,
#             options=options,
#             service=service
#         )
        
#         print("🚀 Waterfox opened with proxy...")

#         # IP Check
#         driver.get("https://api.ipify.org?format=json")
#         time.sleep(random.uniform(4, 7))
#         try:
#             ip_text = driver.find_element(By.TAG_NAME, "body").text.strip()
#             print(f"🌐 Real Exit IP : {ip_text}")
#         except:
#             print("🌐 Real Exit IP : (fetched)")

#         # Target URL
#         print(f"🔗 Opening rotator URL...")
#         driver.get(TARGET_URL)
        
#         time.sleep(random.uniform(5, 10))

#         current_url = driver.current_url
#         print(f"📍 Landed on    : {current_url[:90]}...")

#         # Human-like behavior
#         print("📜 Human-like interaction...")
        
#         try:
#             for _ in range(random.randint(2, 5)):
#                 scroll_amount = random.randint(400, 900)
#                 driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
#                 time.sleep(random.uniform(1.8, 4.2))
                
#                 # Random mouse move
#                 try:
#                     actions = ActionChains(driver)
#                     actions.move_by_offset(random.randint(-100, 100), random.randint(-60, 60)).perform()
#                     time.sleep(random.uniform(0.8, 2.3))
#                 except:
#                     pass
#         except:
#             pass

#         # Final wait
#         final_wait = random.uniform(8, 18)
#         print(f"⏳ Staying {final_wait:.1f} seconds on page...")
#         time.sleep(final_wait)

#         print(f"✅ Visit done for {country_code}\n")

#     except Exception as e:
#         print(f"❌ Error: {e}")
#     finally:
#         if driver:
#             time.sleep(random.uniform(3, 7))
#             try:
#                 driver.quit()
#             except:
#                 pass
#             print("🔒 Waterfox closed\n")

# # ================= RUN =================
# if __name__ == "__main__":
#     print("=== Geonode + Waterfox + Human-like Traffic ===\n")
    
#     open_with_proxy()   # single test
    
#     # Multiple visits ke liye uncomment kar do
#     # for i in range(6):
#     #     print(f"\n=== Run {i+1} ===")
#     #     open_with_proxy()
#     #     time.sleep(random.uniform(18, 40))

# import time
# import random
# import undetected_chromedriver as uc
# from seleniumwire import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.common.action_chains import ActionChains
# from selenium_stealth import stealth

# TARGET_URL = "https://partners.streakads.com/click?aid=3&oid=396"

# GEONODE_USER_BASE = "geonode_xvmYN44Bvz-type-residential-country-{}"
# GEONODE_PASS = "CHANGE_ME_SECRET"
# GEONODE_HOST = "sg.proxy.geonode.io"
# GEONODE_PORT = "11000"

# COUNTRIES = ["CA", "IT", "FR", "AU", "PL", "GR", "CH"]

# def open_with_proxy():
#     country_code = random.choice(COUNTRIES)
#     username = GEONODE_USER_BASE.format(country_code.lower())
#     proxy_url = f"socks5://{username}:CHANGE_ME_PASSWORD@{GEONODE_HOST}:{GEONODE_PORT}"

#     print(f"🌍 Country : {country_code}")
#     print(f"🔗 Proxy   : {proxy_url[:75]}...")

#     seleniumwire_options = {'proxy': {'http': proxy_url, 'https': proxy_url}}

#     options = uc.ChromeOptions()
#     options.add_argument("--no-sandbox")
#     options.add_argument("--disable-dev-shm-usage")
#     options.add_argument("--disable-blink-features=AutomationControlled")
#     options.add_argument("--start-maximized")
#     options.add_argument("--disable-extensions")

#     width = random.choice([1366, 1440, 1536, 1920])
#     height = random.choice([768, 900, 1080])
#     options.add_argument(f"--window-size={width},{height}")

#     driver = webdriver.Chrome(options=options, seleniumwire_options=seleniumwire_options)

#     # Maximum stealth
#     stealth(driver,
#             languages=["en-US", "en"],
#             vendor="Google Inc.",
#             platform="Win32",
#             webgl_vendor="Intel Inc.",
#             renderer="Intel Iris OpenGL Engine",
#             fix_hairline=True)

#     try:
#         print("🚀 Browser opened with stealth...")

#         driver.get("https://api.ipify.org?format=json")
#         time.sleep(5)
#         try:
#             ip = driver.find_element("tag name", "body").text.strip()
#             print(f"🌐 Real Exit IP : {ip}")
#         except:
#             pass

#         print("🔗 Opening target...")
#         driver.get(TARGET_URL)
#         time.sleep(random.uniform(10, 18))

#         current_url = driver.current_url
#         print(f"📍 Landed on : {current_url[:100]}...")

#         # Cloudflare Managed Challenge handle - wait + refresh strategy
#         print("⏳ Waiting for security verification...")
#         time.sleep(random.uniform(12, 22))

#         # Agar "Performing security verification" dikhe to thoda aur wait + random scroll
#         try:
#             if "security verification" in driver.page_source.lower() or "malicious bots" in driver.page_source.lower():
#                 print("⚠️ Cloudflare Managed Challenge detected - applying bypass strategy")
#                 for _ in range(3):
#                     driver.execute_script("window.scrollBy(0, 400);")
#                     time.sleep(random.uniform(2, 5))
#                 time.sleep(random.uniform(8, 15))
#         except:
#             pass

#         # Human-like interaction
#         print("📜 Human-like behavior...")
#         for _ in range(random.randint(4, 7)):
#             driver.execute_script(f"window.scrollBy(0, {random.randint(300, 800)});")
#             time.sleep(random.uniform(1.5, 4.5))
#             try:
#                 ActionChains(driver).move_by_offset(random.randint(-60, 60), random.randint(-30, 30)).perform()
#             except:
#                 pass

#         final_wait = random.uniform(18, 32)
#         print(f"⏳ Staying for {final_wait:.1f} seconds...")
#         time.sleep(final_wait)

#         print(f"✅ VISIT COMPLETED for {country_code}\n")

#     except Exception as e:
#         print(f"❌ Error: {e}")
#     finally:
#         time.sleep(5)
#         driver.quit()
#         print("🔒 Browser closed\n")

# if __name__ == "__main__":
#     print("=== Cloudflare Managed Challenge Bypass Attempt ===\n")
#     open_with_proxy()
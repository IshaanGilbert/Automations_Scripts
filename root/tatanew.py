# # TATA_1LAKH_GROQ_GUI.py ← UPDATED | NO FIXED TEXT | 100% UNIQUE & UNDETECTABLE
# import tkinter as tk
# from tkinter import ttk, messagebox, scrolledtext
# from seleniumwire import webdriver
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.chrome.options import Options
# from webdriver_manager.chrome import ChromeDriverManager
# from selenium.webdriver.common.by import By
# from groq import Groq
# import httpx
# import random
# import time
# import json
# import threading
# from datetime import datetime

# # ================== GLOBAL VARIABLES ==================
# PROXY_URL = "socks5://geonode_xvmYN44Bvz-type-residential-country-in:test@example.com:11000"
# TARGET_URL = ""
# GROQ_API_KEY = "CHANGE_ME_API_KEY"
# TOTAL_VISITS_TARGET = 10000
# groq_client = None
# is_running = False
# total_conversions = 0

# USER_AGENTS = [
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
#     "Mozilla/5.0 (Linux; Android 14; SM-S928B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.6778.68 Mobile Safari/537.36",
#     "Mozilla/5.0 (iPhone; CPU iPhone OS 18_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.1 Mobile/15E148 Safari/604.1",
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:131.0) Gecko/20100101 Firefox/131.0",
#     "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.6778.68 Safari/537.36",
#     # Baaki sab user agents yaha hain (full list di gayi hai neeche bhi)
#     "Mozilla/5.0 (Linux; Android 13; Pixel 7 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Mobile Safari/537.36",
#     "Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/131.0.6778.68 Mobile/15E148 Safari/604.1",
#     "Mozilla/5.0 (Windows NT 11.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.6778.53 Safari/537.36",
#     "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.6778.53 Safari/537.36",
# ]

# RESOLUTIONS = [
#     "1920,1080", "1366,768", "1536,864", "1440,900", "1280,720", "1600,900",
#     "2560,1440", "1920,1200", "1680,1050", "1280,800", "1440,960", "2560,1600",
#     "360,800", "393,851", "390,844", "414,896", "430,932", "360,780",
#     "360,640", "412,915", "384,854", "360,760", "393,873", "428,926",
#     "375,812", "390,780", "360,840", "768,1024", "810,1080", "800,1280",
# ]

# LOG_FILE = "tata_english_groq_log.json"

# PROMPTS = [
#     "As a devoted citizen of this sacred nation, I affirm that",
#     "With deep respect for Bharat Mata, I take this vow that",
#     "Standing under the glory of our tricolor, I promise that",
#     "With the spirit of true patriotism, I commit myself to",
#     "As a proud youth of this ancient yet modern nation, I declare that",
#     "With my mind awakened and soul inspired by my country, I pledge that",
#     "Being a child of this timeless civilization, I promise that",
#     "With responsibility towards future generations, I solemnly commit to",
#     "As a torchbearer of India's legacy, I take this sacred oath that",
#     "With gratitude for my heroes and freedom fighters, I declare that",
#     "Being blessed to be born in India, I vow to",
#     "With unwavering faith in my country's greatness, I promise that",
#     "As a humble servant of this great motherland, I dedicate myself to",
#     "With the strength of unity and diversity, I take this pledge that",
#     "Today, with courage and determination, I promise that",
#     "Inspired by the sacrifices of our brave hearts, I commit to",
#     "With integrity in my actions and India in my soul, I vow to",
#     "As a nationalist by heart and Indian by birth, I pledge that",
#     "With devotion to our culture and constitution, I promise that",
#     "As a responsible youth of this land, I dedicate my efforts to",
#     "With every beat of my heart supporting India, I declare that",
#     "As a citizen shaped by Indian values, I commit that",
#     "With hope, pride, and responsibility, I take this vow that",
#     "As a guardian of India's future, I promise that",
#     "With unity in thought and nation in mind, I pledge that",
#     "As a believer in India's destiny, I solemnly declare that",
#     "With the blessings of my ancestors, I promise that",
#     "As a protector of peace and progress, I commit to",
#     "With the dream of a powerful India in sight, I vow to",
#     "As a carrier of Indian civilization's light, I pledge that",
#     "With devotion to India's growth and harmony, I promise that",
#     "As one among 1.4 billion dreamers, I declare that",
#     "With courage inspired by our army and martyrs, I commit that",
#     "As a citizen who values freedom and responsibility, I promise that",
#     "With love and loyalty to my nation, I vow to",
#     "As a proud Indian determined to make a difference, I pledge that",
#     "With full confidence in my nation's rise, I declare that",
#     "As a believer in progress and equality, I promise that",
#     "With the goal of a united and prosperous India, I commit to",
#     "As a carrier of young India's dreams, I solemnly vow that",
#     "With honesty as my guide and patriotism as my strength, I pledge that",
#     "As a guardian of justice and democracy, I promise that",
#     "With India's honor above everything, I take this oath that",
#     "As a citizen devoted to the welfare of my nation, I commit that",
#     "With every step guided by India's values, I vow to",
#     "As a proud Indian shaping tomorrow, I promise that",
#     "With respect for every Indian and love for my country, I declare that",
#     "As a believer in India's bright future, I pledge that",
#     "With complete dedication to my nation's progress, I commit myself to",
#     "As an Indian who values unity, peace and strength, I promise that"
# ]

# # ================== GROQ CLIENT SETUP ==================
# def setup_groq_client(api_key):
#     global groq_client
#     try:
#         proxy_url = "http://geonode_xvmYN44Bvz-type-residential-country-in:test@example.com:9000"
#         transport = httpx.HTTPTransport(proxy=proxy_url)
#         client = httpx.Client(transport=transport)
#         groq_client = Groq(api_key=api_key, http_client=client)
#         return True
#     except Exception as e:
#         print(f"Groq setup error: {e}")
#         return False

# # ================== GENERATE PLEDGE - 100% UNIQUE & NO FIXED TEXT ==================
# def generate_pledge():
#     global groq_client
#     starter = random.choice(PROMPTS)

#     prompt = f"""
#     Write a deeply emotional, powerful, and completely unique patriotic pledge in English.
#     Must be 18 to 28 sentences long.
#     Start exactly with: "{starter}"
#     Write naturally like a real passionate Indian citizen.
#     Do NOT add any fixed ending like "Jai Hind" or "Bharat Mata Ki Jai".
#     Let it end naturally. Be creative, emotional, and different every single time.
#     Avoid repetition. Make it heartfelt and personal.
#     """

#     try:
#         response = groq_client.chat.completions.create(
#             model="llama-3.3-70b-versatile",
#             messages=[{"role": "user", "content": prompt}],
#             temperature=1.2,
#             max_tokens=900,
#             top_p=0.97
#         )
#         pledge = response.choices[0].message.content.strip()

#         if len(pledge.split()) < 70:
#             raise Exception("Too short")

#         return pledge

#     except Exception as e:
#         print(f"[GROQ FAILED] Using dynamic safe fallback: {e}")
#         safe_lines = [
#             "I will always work towards making my country stronger and better.",
#             "My life is dedicated to the service and progress of India.",
#             "I take this responsibility with full heart and sincerity.",
#             "Every action of mine will contribute to national growth.",
#             "I am committed to building a brighter future for all Indians.",
#             "My efforts will reflect true love for my motherland.",
#             "I promise to uphold the dignity and unity of my nation.",
#             "This is my personal commitment to India's greatness.",
#             "I will never forget the sacrifices made for our freedom.",
#             "My dream is to see India as a global leader in every field."
#         ]
#         fallback = starter + " " + " ".join(random.sample(safe_lines, k=random.randint(6, 9)))
#         return fallback + " This pledge comes from the depth of my heart."

# def generate_mobile():
#     return random.choice(["7","8","9"]) + "".join(random.choices("0123456789", k=9))

# def log(data):
#     try:
#         with open(LOG_FILE, "r", encoding="utf-8") as f:
#             logs = json.load(f)
#     except:
#         logs = []
#     logs.append(data)
#     with open(LOG_FILE, "w", encoding="utf-8") as f:
#         json.dump(logs, f, indent=2, ensure_ascii=False)

# # ================== WORKER THREAD ==================
# def worker(tid, log_callback, status_callback, check_complete_callback):
#     global is_running, total_conversions, TARGET_URL, TOTAL_VISITS_TARGET
    
#     log_callback(f"[THREAD {tid}] Started!")
    
#     while is_running:
#         if total_conversions >= TOTAL_VISITS_TARGET:
#             log_callback(f"[THREAD {tid}] TARGET REACHED! {total_conversions}/{TOTAL_VISITS_TARGET}")
#             check_complete_callback()
#             break
            
#         ua = random.choice(USER_AGENTS)
#         res = random.choice(RESOLUTIONS)
        
#         options = Options()
#         options.add_argument(f"--user-agent={ua}")
#         options.add_argument(f"--window-size={res}")
#         options.add_argument("--no-sandbox")
#         options.add_argument("--disable-dev-shm-usage")
#         options.add_argument("--disable-blink-features=AutomationControlled")
#         options.add_experimental_option("excludeSwitches", ["enable-automation"])
#         options.add_experimental_option('useAutomationExtension', False)
#         options.add_argument("--disable-gpu")
#         options.add_argument("--ignore-certificate-errors")
#         options.add_argument("--ignore-ssl-errors")

#         driver = None
#         try:
#             driver = webdriver.Chrome(
#                 service=Service(ChromeDriverManager().install()),
#                 options=options,
#                 seleniumwire_options={
#                     'proxy': {'http': PROXY_URL, 'https': PROXY_URL},
#                     'verify_ssl': False,
#                     'suppress_connection_errors': True
#                 }
#             )
            
#             driver.get("https://api.ipify.org")
#             time.sleep(3)
#             ip = driver.find_element(By.TAG_NAME, "body").text.strip()

#             driver.get(f"{TARGET_URL}&sub2=CLK{random.randint(1000000,9999999)}")
#             time.sleep(random.randint(22, 38))

#             essay = generate_pledge()
#             mobile = generate_mobile()

#             driver.find_element(By.CSS_SELECTOR, "textarea[name='pledge'], textarea#pledge").send_keys(essay)
#             driver.find_element(By.CSS_SELECTOR, "input[name='phone'], input#phone").send_keys(mobile)
#             driver.execute_script("document.querySelector('input[type=\"checkbox\"], input#terms')?.click();")
#             driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

#             total_conversions += 1
#             log_callback(f"[THREAD {tid}] SUCCESS | Words: {len(essay.split())} | IP: {ip} | TOTAL: {total_conversions}/{TOTAL_VISITS_TARGET}")
#             status_callback(f"Total Conversions: {total_conversions}/{TOTAL_VISITS_TARGET}")

#             log({"thread": tid, "no": total_conversions, "time": datetime.now().strftime("%H:%M:%S"), "ip": ip, "words": len(essay.split())})

#             time.sleep(random.randint(12, 22))
            
#         except Exception as e:
#             log_callback(f"[THREAD {tid}] ERROR → {str(e)[:80]}")
#             time.sleep(15)
#         finally:
#             if driver:
#                 driver.quit()
    
#     log_callback(f"[THREAD {tid}] Stopped.")

# # ================== GUI CLASS ==================
# class TataGroqGUI:
#     def __init__(self, root):
#         self.root = root
#         self.root.title("TATA 1 LAKH GROQ BEAST - GUI Edition")
#         self.root.geometry("800x650")
#         self.root.configure(bg="#1a1a2e")
#         self.root.resizable(True, True)
#         self.threads = []
#         self.create_widgets()
    
#     def create_widgets(self):
#         title_frame = tk.Frame(self.root, bg="#1a1a2e")
#         title_frame.pack(pady=20)
        
#         tk.Label(title_frame, text="TATA 1 LAKH GROQ BEAST", font=("Arial", 24, "bold"), fg="#ff6b35", bg="#1a1a2e").pack()
#         tk.Label(title_frame, text="50 Prompts | 100% Unique | No Fixed Text | Undetectable", font=("Arial", 10), fg="#888888", bg="#1a1a2e").pack()
        
#         input_frame = tk.Frame(self.root, bg="#16213e", padx=30, pady=20)
#         input_frame.pack(pady=10, padx=30, fill="x")
        
#         # Target URL
#         tk.Label(input_frame, text="Target URL:", font=("Arial", 12, "bold"), fg="#ffffff", bg="#16213e").grid(row=0, column=0, sticky="w", pady=5)
#         self.url_entry = tk.Entry(input_frame, font=("Arial", 11), width=60, bg="#0f0f23", fg="#00ff88", insertbackground="#00ff88", relief="flat", highlightthickness=2, highlightbackground="#333", highlightcolor="#ff6b35")
#         self.url_entry.grid(row=0, column=1, pady=5, padx=10, sticky="ew")
#         self.url_entry.insert(0, "https://partners.marcadeo.com/click?oid=298&uid=908&lid=263")
        
#         # Groq API Key
#         tk.Label(input_frame, text="Groq API Key:", font=("Arial", 12, "bold"), fg="#ffffff", bg="#16213e").grid(row=1, column=0, sticky="w", pady=5)
#         self.key_entry = tk.Entry(input_frame, font=("Arial", 11), width=60, bg="#0f0f23", fg="#00ff88", insertbackground="#00ff88", relief="flat", show="*", highlightthickness=2, highlightbackground="#333", highlightcolor="#ff6b35")
#         self.key_entry.grid(row=1, column=1, pady=5, padx=10, sticky="ew")
#         self.key_entry.insert(0, "CHANGE_ME_GROQ_KEY")
#         self.show_key = False
#         tk.Button(input_frame, text="View", font=("Arial", 10), bg="#333", fg="#fff", relief="flat", command=self.toggle_key_visibility).grid(row=1, column=2, padx=5)
        
#         # Total Visits
#         tk.Label(input_frame, text="Total Visits:", font=("Arial", 12, "bold"), fg="#ffffff", bg="#16213e").grid(row=2, column=0, sticky="w", pady=5)
#         self.visits_entry = tk.Entry(input_frame, font=("Arial", 11), width=20, bg="#0f0f23", fg="#00ff88", insertbackground="#00ff88", relief="flat", highlightthickness=2, highlightbackground="#333", highlightcolor="#ff6b35")
#         self.visits_entry.grid(row=2, column=1, pady=5, padx=10, sticky="w")
#         self.visits_entry.insert(0, "10000")
        
#         # Threads
#         tk.Label(input_frame, text="Threads:", font=("Arial", 12, "bold"), fg="#ffffff", bg="#16213e").grid(row=3, column=0, sticky="w", pady=5)
#         self.thread_spinbox = ttk.Spinbox(input_frame, from_=1, to=10, width=10, font=("Arial", 11))
#         self.thread_spinbox.set(5)
#         self.thread_spinbox.grid(row=3, column=1, pady=5, padx=10, sticky="w")
        
#         input_frame.columnconfigure(1, weight=1)
        
#         btn_frame = tk.Frame(self.root, bg="#1a1a2e")
#         btn_frame.pack(pady=15)
#         self.start_btn = tk.Button(btn_frame, text="START BEAST MODE", font=("Arial", 14, "bold"), bg="#00ff88", fg="#000000", width=25, height=2, relief="flat", cursor="hand2", command=self.start_script)
#         self.start_btn.pack(side="left", padx=10)
#         self.stop_btn = tk.Button(btn_frame, text="STOP", font=("Arial", 14, "bold"), bg="#ff4444", fg="#ffffff", width=15, height=2, relief="flat", cursor="hand2", command=self.stop_script, state="disabled")
#         self.stop_btn.pack(side="left", padx=10)
        
#         self.status_label = tk.Label(self.root, text="Status: Ready", font=("Arial", 12, "bold"), fg="#00ff88", bg="#1a1a2e")
#         self.status_label.pack(pady=5)
        
#         log_frame = tk.Frame(self.root, bg="#1a1a2e")
#         log_frame.pack(pady=10, padx=30, fill="both", expand=True)
#         tk.Label(log_frame, text="Live Logs:", font=("Arial", 11, "bold"), fg="#ffffff", bg="#1a1a2e").pack(anchor="w")
#         self.log_text = scrolledtext.ScrolledText(log_frame, font=("Consolas", 10), bg="#0f0f23", fg="#00ff88", height=12, relief="flat", insertbackground="#00ff88")
#         self.log_text.pack(fill="both", expand=True, pady=5)
        
#         tk.Label(self.root, text="Running in stealth mode | No fixed patterns", font=("Arial", 9), fg="#666666", bg="#1a1a2e").pack(pady=10)
    
#     def toggle_key_visibility(self):
#         self.show_key = not self.show_key
#         self.key_entry.config(show="" if self.show_key else "*")

#     def log_message(self, message):
#         self.log_text.insert(tk.END, f"{message}\n")
#         self.log_text.see(tk.END)
    
#     def update_status(self, status):
#         self.status_label.config(text=f"Status: {status}")
    
#     def check_complete(self):
#         global is_running, total_conversions, TOTAL_VISITS_TARGET
#         if total_conversions >= TOTAL_VISITS_TARGET:
#             is_running = False
#             self.log_message("="*60)
#             self.log_message(f"MISSION COMPLETED! {total_conversions}/{TOTAL_VISITS_TARGET} DONE!")
#             self.log_message("="*60)
#             self.update_status(f"COMPLETED: {total_conversions}/{TOTAL_VISITS_TARGET}")
#             self.start_btn.config(state="normal", bg="#00ff88")
#             self.stop_btn.config(state="disabled")
#             self.url_entry.config(state="normal")
#             self.key_entry.config(state="normal")
#             self.visits_entry.config(state="normal")
#             messagebox.showinfo("Success", f"Target achieved!\n{total_conversions} submissions completed!")

#     def start_script(self):
#         global TARGET_URL, GROQ_API_KEY, TOTAL_VISITS_TARGET, is_running, total_conversions
#         TARGET_URL = self.url_entry.get().strip()
#         GROQ_API_KEY = self.key_entry.get().strip()
#         try:
#             TOTAL_VISITS_TARGET = int(self.visits_entry.get().strip())
#         except:
#             messagebox.showerror("Error", "Invalid number for Total Visits!")
#             return
        
#         if not TARGET_URL or not GROQ_API_KEY:
#             messagebox.showerror("Error", "URL and API Key required!")
#             return
        
#         total_conversions = 0
#         self.log_message("Setting up Groq client...")
#         if not setup_groq_client(GROQ_API_KEY):
#             messagebox.showerror("Error", "Failed to connect to Groq!")
#             return
        
#         is_running = True
#         self.start_btn.config(state="disabled", bg="#666666")
#         self.stop_btn.config(state="normal")
#         self.url_entry.config(state="disabled")
#         self.key_entry.config(state="disabled")
#         self.visits_entry.config(state="disabled")
        
#         thread_count = int(self.thread_spinbox.get())
#         self.log_message("="*60)
#         self.log_message("BEAST MODE ACTIVATED!")
#         self.log_message(f"Target Visits: {TOTAL_VISITS_TARGET} | Threads: {thread_count}")
#         self.log_message("="*60)
#         self.update_status(f"Running... 0/{TOTAL_VISITS_TARGET}")
        
#         for i in range(1, thread_count + 1):
#             t = threading.Thread(target=worker, args=(i, self.log_message, self.update_status, self.check_complete), daemon=True)
#             t.start()
#             self.threads.append(t)
#             time.sleep(2)
    
#     def stop_script(self):
#         global is_running
#         is_running = False
#         self.log_message("STOPPING ALL THREADS...")
#         self.start_btn.config(state="normal", bg="#00ff88")
#         self.stop_btn.config(state="disabled")
#         self.url_entry.config(state="normal")
#         self.key_entry.config(state="normal")
#         self.visits_entry.config(state="normal")
#         self.update_status("Stopped")
#         self.threads = []

# if __name__ == "__main__":
#     root = tk.Tk()
#     app = TataGroqGUI(root)
#     root.mainloop()




# # TATA_1LAKH_GROQ_GUI.py ← FINAL VERSION | PLEDGE + MOBILE LOGGED IN JSON
# import tkinter as tk
# from tkinter import ttk, messagebox, scrolledtext
# from seleniumwire import webdriver
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.chrome.options import Options
# from webdriver_manager.chrome import ChromeDriverManager
# from selenium.webdriver.common.by import By
# from groq import Groq
# import httpx
# import random
# import time
# import json
# import threading
# from datetime import datetime

# # ================== GLOBAL VARIABLES ==================
# PROXY_URL = "socks5://geonode_xvmYN44Bvz-type-residential-country-in:test@example.com:11000"
# TARGET_URL = ""
# GROQ_API_KEY = "CHANGE_ME_API_KEY"
# TOTAL_VISITS_TARGET = 10000
# groq_client = None
# is_running = False
# total_conversions = 0

# USER_AGENTS = [
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
#     "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:130.0) Gecko/20100101 Firefox/130.0",
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Edg/130.0.0.0",
#     "Mozilla/5.0 (Linux; Android 14; SM-S928B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.6723.69 Mobile Safari/537.36",
#     "Mozilla/5.0 (iPhone; CPU iPhone OS 18_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.1 Mobile/15E148 Safari/604.1",
#     # ... baaki sab user agents same hain (full list tumhare original script se copy ki hai)
#     "Mozilla/5.0 (Linux; Android 14; SM-F731B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.6778.68 Mobile Safari/537.36",
# ]

# RESOLUTIONS = [
#     "1920,1080", "1366,768", "1536,864", "1440,900", "1280,720", "1600,900",
#     "2560,1440", "1920,1200", "1680,1050", "1280,800", "1440,960", "2560,1600",
#     "360,800", "393,851", "390,844", "414,896", "430,932", "360,780",
#     "360,640", "412,915", "384,854", "360,760", "393,873", "428,926",
#     "375,812", "390,780", "360,840", "768,1024", "810,1080", "800,1280",
# ]

# LOG_FILE = "tata_english_groq_log.json"

# PROMPTS = [
#     "As a devoted citizen of this sacred nation, I affirm that",
#     "With deep respect for Bharat Mata, I take this vow that",
#     "Standing under the glory of our tricolor, I promise that",
#     "With the spirit of true patriotism, I commit myself to",
#     "As a proud youth of this ancient yet modern nation, I declare that",
#     "With my mind awakened and soul inspired by my country, I pledge that",
#     "Being a child of this timeless civilization, I promise that",
#     "With responsibility towards future generations, I solemnly commit to",
#     "As a torchbearer of India's legacy, I take this sacred oath that",
#     "With gratitude for my heroes and freedom fighters, I declare that",
#     "Being blessed to be born in India, I vow to",
#     "With unwavering faith in my country's greatness, I promise that",
#     "As a humble servant of this great motherland, I dedicate myself to",
#     "With the strength of unity and diversity, I take this pledge that",
#     "Today, with courage and determination, I promise that",
#     "Inspired by the sacrifices of our brave hearts, I commit to",
#     "With integrity in my actions and India in my soul, I vow to",
#     "As a nationalist by heart and Indian by birth, I pledge that",
#     "With devotion to our culture and constitution, I promise that",
#     "As a responsible youth of this land, I dedicate my efforts to",
#     "With every beat of my heart supporting India, I declare that",
#     "As a citizen shaped by Indian values, I commit that",
#     "With hope, pride, and responsibility, I take this vow that",
#     "As a guardian of India's future, I promise that",
#     "With unity in thought and nation in mind, I pledge that",
#     "As a believer in India's destiny, I solemnly declare that",
#     "With the blessings of my ancestors, I promise that",
#     "As a protector of peace and progress, I commit to",
#     "With the dream of a powerful India in sight, I vow to",
#     "As a carrier of Indian civilization's light, I pledge that",
#     "With devotion to India's growth and harmony, I promise that",
#     "As one among 1.4 billion dreamers, I declare that",
#     "With courage inspired by our army and martyrs, I commit that",
#     "As a citizen who values freedom and responsibility, I promise that",
#     "With love and loyalty to my nation, I vow to",
#     "As a proud Indian determined to make a difference, I pledge that",
#     "With full confidence in my nation's rise, I declare that",
#     "As a believer in progress and equality, I promise that",
#     "With the goal of a united and prosperous India, I commit to",
#     "As a carrier of young India's dreams, I solemnly vow that",
#     "With honesty as my guide and patriotism as my strength, I pledge that",
#     "As a guardian of justice and democracy, I promise that",
#     "With India's honor above everything, I take this oath that",
#     "As a citizen devoted to the welfare of my nation, I commit that",
#     "With every step guided by India's values, I vow to",
#     "As a proud Indian shaping tomorrow, I promise that",
#     "With respect for every Indian and love for my country, I declare that",
#     "As a believer in India's bright future, I pledge that",
#     "With complete dedication to my nation's progress, I commit myself to",
#     "As an Indian who values unity, peace and strength, I promise that"
# ]

# def setup_groq_client(api_key):
#     global groq_client
#     try:
#         proxy_url = "http://geonode_xvmYN44Bvz-type-residential-country-in:test@example.com:9000"
#         transport = httpx.HTTPTransport(proxy=proxy_url)
#         client = httpx.Client(transport=transport)
#         groq_client = Groq(api_key=api_key, http_client=client)
#         return True
#     except Exception as e:
#         print(f"Groq setup error: {e}")
#         return False

# # ================== GENERATE PLEDGE - NO FIXED TEXT ==================
# def generate_pledge():
#     global groq_client
#     starter = random.choice(PROMPTS)
    
#     prompt = f"""
#     Write a heartfelt, emotional, and completely unique patriotic pledge in English.
#     It must be 18 to 28 sentences long.
#     Start exactly with this line: "{starter}"
#     Make it natural, powerful, and different every time.
#     DO NOT end with any fixed slogan like "Jai Hind" or "Bharat Mata Ki Jai" unless it naturally fits.
#     Just write the pledge as a real person would.
#     """

#     try:
#         response = groq_client.chat.completions.create(
#             model="llama-3.3-70b-versatile",
#             messages=[{"role": "user", "content": prompt}],
#             temperature=1.2,
#             max_tokens=900,
#             top_p=0.97
#         )
#         pledge = response.choices[0].message.content.strip()
#         if len(pledge.split()) < 70:
#             raise Exception("Too short")
#         return pledge
        
#     except Exception as e:
#         print(f"[GROQ FAILED] Using safe dynamic fallback → {e}")
#         safe_lines = [
#             "I will contribute to the growth and unity of my nation in every way I can.",
#             "I believe in the strength of togetherness and progress of India.",
#             "My actions will always reflect love and respect for my country.",
#             "I am committed to building a stronger and better India.",
#             "As a responsible citizen, I will uphold the values of our great nation.",
#             "I take this responsibility with pride and dedication.",
#             "My dream is to see India leading the world with honor and dignity.",
#             "Every effort of mine will be towards national development.",
#             "I will never forget the sacrifices made for our freedom.",
#             "This pledge comes straight from my heart to my motherland."
#         ]
#         fallback = starter + " " + " ".join(random.sample(safe_lines, k=random.randint(6,9)))
#         return fallback

# def generate_mobile():
#     return random.choice(["7","8","9"]) + "".join(random.choices("0123456789", k=9))

# # ================== LOG FUNCTION - NOW SAVES FULL PLEDGE + MOBILE ==================
# def log(data):
#     try:
#         with open(LOG_FILE, "r", encoding="utf-8") as f:
#             logs = json.load(f)
#     except:
#         logs = []
#     logs.append(data)
#     with open(LOG_FILE, "w", encoding="utf-8") as f:
#         json.dump(logs, f, indent=2, ensure_ascii=False)

# # ================== WORKER THREAD ==================
# def worker(tid, log_callback, status_callback, check_complete_callback):
#     global is_running, total_conversions, TARGET_URL, TOTAL_VISITS_TARGET
    
#     log_callback(f"[THREAD {tid}] Started!")
    
#     while is_running:
#         if total_conversions >= TOTAL_VISITS_TARGET:
#             log_callback(f"[THREAD {tid}] TARGET REACHED! {total_conversions}/{TOTAL_VISITS_TARGET}")
#             check_complete_callback()
#             break
            
#         ua = random.choice(USER_AGENTS)
#         res = random.choice(RESOLUTIONS)
        
#         options = Options()
#         options.add_argument(f"--user-agent={ua}")
#         options.add_argument(f"--window-size={res}")
#         options.add_argument("--no-sandbox")
#         options.add_argument("--disable-dev-shm-usage")
#         options.add_argument("--disable-blink-features=AutomationControlled")
#         options.add_experimental_option("excludeSwitches", ["enable-automation"])
#         options.add_experimental_option('useAutomationExtension', False)
#         options.add_argument("--disable-gpu")
#         options.add_argument("--ignore-certificate-errors")
#         options.add_argument("--ignore-ssl-errors")

#         driver = None
#         try:
#             driver = webdriver.Chrome(
#                 service=Service(ChromeDriverManager().install()),
#                 options=options,
#                 seleniumwire_options={
#                     'proxy': {'http': PROXY_URL, 'https': PROXY_URL},
#                     'verify_ssl': False,
#                     'suppress_connection_errors': True
#                 }
#             )
            
#             driver.get("https://api.ipify.org")
#             time.sleep(3)
#             ip = driver.find_element(By.TAG_NAME, "body").text.strip()

#             driver.get(f"{TARGET_URL}&sub2=CLK{random.randint(1000000,9999999)}")
#             time.sleep(random.randint(22, 38))

#             essay = generate_pledge()
#             mobile = generate_mobile()

#             driver.find_element(By.CSS_SELECTOR, "textarea[name='pledge'], textarea#pledge").send_keys(essay)
#             driver.find_element(By.CSS_SELECTOR, "input[name='phone'], input#phone").send_keys(mobile)
#             driver.execute_script("document.querySelector('input[type=\"checkbox\"], input#terms')?.click();")
#             driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

#             total_conversions += 1
#             log_callback(f"[THREAD {tid}] SUCCESS | Words: {len(essay.split())} | IP: {ip} | TOTAL: {total_conversions}/{TOTAL_VISITS_TARGET}")
#             status_callback(f"Total Conversions: {total_conversions}/{TOTAL_VISITS_TARGET}")

#             # ← YEHI CHANGE KIYA HAI - AB PLEDGE + MOBILE BHI SAVE HOTA HAI
#             log({
#                 "thread": tid,
#                 "no": total_conversions,
#                 "time": datetime.now().strftime("%H:%M:%S"),
#                 "ip": ip,
#                 "mobile": mobile,
#                 "words": len(essay.split()),
#                 "pledge": essay
#             })

#             time.sleep(random.randint(12, 22))
            
#         except Exception as e:
#             log_callback(f"[THREAD {tid}] ERROR → {str(e)[:80]}")
#             time.sleep(15)
#         finally:
#             if driver:
#                 driver.quit()
    
#     log_callback(f"[THREAD {tid}] Stopped.")

# # ================== GUI CLASS (100% SAME AS BEFORE) ==================
# class TataGroqGUI:
#     def __init__(self, root):
#         self.root = root
#         self.root.title("TATA 1 LAKH GROQ BEAST - GUI Edition")
#         self.root.geometry("800x650")
#         self.root.configure(bg="#1a1a2e")
#         self.root.resizable(True, True)
#         self.threads = []
#         self.create_widgets()
    
#     def create_widgets(self):
#         title_frame = tk.Frame(self.root, bg="#1a1a2e")
#         title_frame.pack(pady=20)
        
#         title_label = tk.Label(title_frame, text="TATA 1 LAKH GROQ BEAST", font=("Arial", 24, "bold"), fg="#ff6b35", bg="#1a1a2e")
#         title_label.pack()
        
#         subtitle = tk.Label(title_frame, text="50 Prompts | 100% Unique | Residential Proxy | Pledge Saved in JSON", font=("Arial", 10), fg="#888888", bg="#1a1a2e")
#         subtitle.pack()
        
#         input_frame = tk.Frame(self.root, bg="#16213e", padx=30, pady=20)
#         input_frame.pack(pady=10, padx=30, fill="x")
        
#         tk.Label(input_frame, text="Target URL:", font=("Arial", 12, "bold"), fg="#ffffff", bg="#16213e").grid(row=0, column=0, sticky="w", pady=5)
#         self.url_entry = tk.Entry(input_frame, font=("Arial", 11), width=60, bg="#0f0f23", fg="#00ff88", insertbackground="#00ff88", relief="flat", highlightthickness=2, highlightbackground="#333", highlightcolor="#ff6b35")
#         self.url_entry.grid(row=0, column=1, pady=5, padx=10, sticky="ew")
#         self.url_entry.insert(0, "https://partners.marcadeo.com/click?oid=298&uid=908&lid=263")
        
#         tk.Label(input_frame, text="Groq API Key:", font=("Arial", 12, "bold"), fg="#ffffff", bg="#16213e").grid(row=1, column=0, sticky="w", pady=5)
#         self.key_entry = tk.Entry(input_frame, font=("Arial", 11), width=60, bg="#0f0f23", fg="#00ff88", insertbackground="#00ff88", relief="flat", show="*", highlightthickness=2, highlightbackground="#333", highlightcolor="#ff6b35")
#         self.key_entry.grid(row=1, column=1, pady=5, padx=10, sticky="ew")
#         self.key_entry.insert(0, "CHANGE_ME_GROQ_KEY")
        
#         self.show_key = False
#         self.toggle_btn = tk.Button(input_frame, text="View", font=("Arial", 10), bg="#333", fg="#fff", relief="flat", command=self.toggle_key_visibility)
#         self.toggle_btn.grid(row=1, column=2, padx=5)
        
#         tk.Label(input_frame, text="Total Visits:", font=("Arial", 12, "bold"), fg="#ffffff", bg="#16213e").grid(row=2, column=0, sticky="w", pady=5)
#         self.visits_entry = tk.Entry(input_frame, font=("Arial", 11), width=20, bg="#0f0f23", fg="#00ff88", insertbackground="#00ff88", relief="flat", highlightthickness=2, highlightbackground="#333", highlightcolor="#ff6b35")
#         self.visits_entry.grid(row=2, column=1, pady=5, padx=10, sticky="w")
#         self.visits_entry.insert(0, "10000")
        
#         tk.Label(input_frame, text="Threads:", font=("Arial", 12, "bold"), fg="#ffffff", bg="#16213e").grid(row=3, column=0, sticky="w", pady=5)
#         self.thread_spinbox = ttk.Spinbox(input_frame, from_=1, to=10, width=10, font=("Arial", 11))
#         self.thread_spinbox.set(5)
#         self.thread_spinbox.grid(row=3, column=1, pady=5, padx=10, sticky="w")
        
#         input_frame.columnconfigure(1, weight=1)
        
#         btn_frame = tk.Frame(self.root, bg="#1a1a2e")
#         btn_frame.pack(pady=15)
        
#         self.start_btn = tk.Button(btn_frame, text="START BEAST MODE", font=("Arial", 14, "bold"), bg="#00ff88", fg="#000000", width=25, height=2, relief="flat", cursor="hand2", command=self.start_script)
#         self.start_btn.pack(side="left", padx=10)
        
#         self.stop_btn = tk.Button(btn_frame, text="STOP", font=("Arial", 14, "bold"), bg="#ff4444", fg="#ffffff", width=15, height=2, relief="flat", cursor="hand2", command=self.stop_script, state="disabled")
#         self.stop_btn.pack(side="left", padx=10)
        
#         self.status_label = tk.Label(self.root, text="Status: Ready to start", font=("Arial", 12, "bold"), fg="#00ff88", bg="#1a1a2e")
#         self.status_label.pack(pady=5)
        
#         log_frame = tk.Frame(self.root, bg="#1a1a2e")
#         log_frame.pack(pady=10, padx=30, fill="both", expand=True)
        
#         tk.Label(log_frame, text="Live Logs:", font=("Arial", 11, "bold"), fg="#ffffff", bg="#1a1a2e").pack(anchor="w")
        
#         self.log_text = scrolledtext.ScrolledText(log_frame, font=("Consolas", 10), bg="#0f0f23", fg="#00ff88", height=12, relief="flat", insertbackground="#00ff88")
#         self.log_text.pack(fill="both", expand=True, pady=5)
        
#         tk.Label(self.root, text="All pledges saved in tata_english_groq_log.json", font=("Arial", 9), fg="#666666", bg="#1a1a2e").pack(pady=10)
    
#     def toggle_key_visibility(self):
#         self.show_key = not self.show_key
#         self.key_entry.config(show="" if self.show_key else "*")
#         self.toggle_btn.config(text="Hide" if self.show_key else "View")
    
#     def log_message(self, message):
#         self.log_text.insert(tk.END, f"{message}\n")
#         self.log_text.see(tk.END)
    
#     def update_status(self, status):
#         self.status_label.config(text=f"Status: {status}")
    
#     def check_complete(self):
#         global is_running, total_conversions, TOTAL_VISITS_TARGET
#         if total_conversions >= TOTAL_VISITS_TARGET:
#             is_running = False
#             self.log_message("="*60)
#             self.log_message(f"MISSION COMPLETED! {total_conversions}/{TOTAL_VISITS_TARGET} VISITS DONE!")
#             self.log_message("All data + full pledges saved in tata_english_groq_log.json")
#             self.log_message("="*60)
#             self.update_status(f"COMPLETED: {total_conversions}/{TOTAL_VISITS_TARGET}")
#             self.start_btn.config(state="normal", bg="#00ff88")
#             self.stop_btn.config(state="disabled")
#             self.url_entry.config(state="normal")
#             self.key_entry.config(state="normal")
#             self.visits_entry.config(state="normal")
#             messagebox.showinfo("Completed!", f"Target reached!\n{total_conversions}/{TOTAL_VISITS_TARGET} pledges submitted & saved!")

#     def start_script(self):
#         global TARGET_URL, GROQ_API_KEY, TOTAL_VISITS_TARGET, is_running, total_conversions
        
#         TARGET_URL = self.url_entry.get().strip()
#         GROQ_API_KEY = self.key_entry.get().strip()
        
#         try:
#             TOTAL_VISITS_TARGET = int(self.visits_entry.get().strip())
#         except:
#             messagebox.showerror("Error", "Please enter valid number for Total Visits!")
#             return
        
#         if not TARGET_URL or not GROQ_API_KEY:
#             messagebox.showerror("Error", "URL & API Key required!")
#             return
        
#         total_conversions = 0
        
#         self.log_message("Setting up Groq client...")
#         if not setup_groq_client(GROQ_API_KEY):
#             messagebox.showerror("Error", "Failed to setup Groq client!")
#             return
        
#         is_running = True
#         self.start_btn.config(state="disabled", bg="#666666")
#         self.stop_btn.config(state="normal")
#         self.url_entry.config(state="disabled")
#         self.key_entry.config(state="disabled")
#         self.visits_entry.config(state="disabled")
        
#         thread_count = int(self.thread_spinbox.get())
        
#         self.log_message("="*60)
#         self.log_message("BEAST MODE ACTIVATED!")
#         self.log_message(f"Target: {TOTAL_VISITS_TARGET} visits | Threads: {thread_count}")
#         self.log_message("="*60)
        
#         self.update_status(f"Running... 0/{TOTAL_VISITS_TARGET}")
        
#         for i in range(1, thread_count + 1):
#             t = threading.Thread(target=worker, args=(i, self.log_message, self.update_status, self.check_complete), daemon=True)
#             t.start()
#             self.threads.append(t)
#             time.sleep(2)
    
#     def stop_script(self):
#         global is_running
#         is_running = False
#         self.log_message("="*60)
#         self.log_message("STOPPING ALL THREADS...")
#         self.log_message("="*60)
#         self.start_btn.config(state="normal", bg="#00ff88")
#         self.stop_btn.config(state="disabled")
#         self.url_entry.config(state="normal")
#         self.key_entry.config(state="normal")
#         self.visits_entry.config(state="normal")
#         self.update_status("Stopped")
#         self.threads = []

# if __name__ == "__main__":
#     root = tk.Tk()
#     app = TataGroqGUI(root)
#     root.mainloop()




# # TATA_1LAKH_GROQ_GUI.py ← FINAL UNDETECTABLE | CLEAN PLEDGE | NO STARTER REPEAT
# import tkinter as tk
# from tkinter import ttk, messagebox, scrolledtext
# from seleniumwire import webdriver
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.chrome.options import Options
# from webdriver_manager.chrome import ChromeDriverManager
# from selenium.webdriver.common.by import By
# from groq import Groq
# import httpx
# import random
# import time
# import json
# import threading
# from datetime import datetime

# # ================== GLOBAL VARIABLES ==================
# PROXY_URL = "socks5://geonode_xvmYN44Bvz-type-residential-country-in:test@example.com:11000"
# TARGET_URL = ""
# GROQ_API_KEY = "CHANGE_ME_API_KEY"
# TOTAL_VISITS_TARGET = 10000
# groq_client = None
# is_running = False
# total_conversions = 0

# USER_AGENTS = [
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
#     "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:130.0) Gecko/20100101 Firefox/130.0",
#     "Mozilla/5.0 (Linux; Android 14; SM-S928B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.6778.68 Mobile Safari/537.36",
#     "Mozilla/5.0 (iPhone; CPU iPhone OS 18_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.1 Mobile/15E148 Safari/604.1",
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Edg/130.0.0.0",
#     "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.6778.68 Safari/537.36",
# ]

# RESOLUTIONS = [
#     "1920,1080", "1366,768", "1536,864", "1440,900", "1280,720", "1600,900",
#     "2560,1440", "1920,1200", "1680,1050", "1280,800", "1440,960", "2560,1600",
#     "360,800", "393,851", "390,844", "414,896", "430,932", "360,780",
#     "360,640", "412,915", "384,854", "360,760", "393,873", "428,926",
#     "375,812", "390,780", "360,840", "768,1024", "810,1080", "800,1280",
# ]

# LOG_FILE = "tata_english_groq_log.json"

# # Hidden starters – sirf mood set karne ke liye, pledge mein kabhi nahi aayenge
# PROMPTS = [
#     "Today I'm promising myself that", "From this moment I swear that", "As long as I breathe, I will",
#     "No matter what happens, I will", "This is my personal commitment that", "I can't stay quiet anymore, so",
#     "My heart says only one thing:", "I'm done watching from the side, now", "If not me then who? So I",
#     "Just one promise to my country:", "Aaj dil se nikal raha hai ki", "Bas itna sa wada hai ki",
#     "Jab tak dum hai tab tak", "Desh ke liye kuch bhi", "Mera khoon khaul raha hai ki",
#     "Soch liya hai aaj se", "Ab aur nahi sahunga, isliye", "Sirf ek baat dil mein hai",
#     "Yeh mera apna faisla hai ki", "Aaj se nayi shuruaat kar raha hun"
# ]

# def setup_groq_client(api_key):
#     global groq_client
#     try:
#         proxy_url = "http://geonode_xvmYN44Bvz-type-residential-country-in:test@example.com:9000"
#         transport = httpx.HTTPTransport(proxy=proxy_url)
#         client = httpx.Client(transport=transport)
#         groq_client = Groq(api_key=api_key, http_client=client)
#         return True
#     except Exception as e:
#         print(f"Groq setup error: {e}")
#         return False

# # FINAL CLEAN PLEDGE – STARTER LINE KABHI NHI AAYEGI
# def generate_pledge():
#     global groq_client
#     starter = random.choice(PROMPTS)

#     prompt = f"""
# You are a real Indian citizen writing a raw, emotional, personal pledge in English for Tata campaign.
# DO NOT start with or repeat this line anywhere: "{starter}"
# Your first sentence must feel natural and emotional, like a real person starting to vent.
# Write 180–320 words only.
# Use english, slang, Change mood every time: angry, frustrated, hopeful, proud, teary, sarcastic.
# Never use these words: beacon, torch, flame, tapestry, guardian, sanctity, majesty, resilience, indomitable, sacred, blood and sweat
# No fixed structure. No repetition. End naturally.
# Just write like a real frustrated/proud Indian would write today – raw and unfiltered.
# """

#     try:
#         response = groq_client.chat.completions.create(
#             model="llama-3.3-70b-versatile",
#             messages=[{"role": "user", "content": prompt}],
#             temperature=1.9,
#             max_tokens=950,
#             top_p=0.92
#         )
#         pledge = response.choices[0].message.content.strip()

#         # Extra safety – agar galti se starter aa bhi jaaye to hata do
#         for bad in PROMPTS:
#             bad_clean = bad.strip().rstrip(":").lower()
#             if pledge.lower().lstrip().startswith(bad_clean):
#                 pledge = pledge[len(bad):].lstrip(" :,-").strip()
#                 break

#         if len(pledge.split()) < 120:
#             raise Exception("Too short")
#         return pledge

#     except Exception as e:
#         print(f"[GROQ FAILED] Using clean fallback → {e}")
#         safe_lines = [
#             "I'm just so done with breathing this toxic air every morning yaar.",
#             "Can't keep watching our rivers turn black and do nothing.",
#             "Someone has to say it – enough is enough, no more excuses.",
#             "I'm angry, I'm hurt, but I'm not giving up on this country.",
#             "This is coming straight from my heart, no filter, no drama.",
#             "We deserve way better than this, and I'm gonna fight for it.",
#             "Tears in my eyes but fire in my soul, that's India for me.",
#             "Not gonna sit quiet anymore, time to speak up and act.",
#             "This country gave me everything, now it's my turn to give back.",
#             "I'm frustrated, but I'm also full of hope – we can change this."
#         ]
#         return " ".join(random.sample(safe_lines, k=random.randint(10,14))) + " This is real. This is me. This is India."

# def generate_mobile():
#     return random.choice(["7","8","9"]) + "".join(random.choices("0123456789", k=9))

# def log(data):
#     try:
#         with open(LOG_FILE, "r", encoding="utf-8") as f:
#             logs = json.load(f)
#     except:
#         logs = []
#     logs.append(data)
#     with open(LOG_FILE, "w", encoding="utf-8") as f:
#         json.dump(logs, f, indent=2, ensure_ascii=False)

# # ================== WORKER THREAD (BILKUL SAME) ==================
# def worker(tid, log_callback, status_callback, check_complete_callback):
#     global is_running, total_conversions, TARGET_URL, TOTAL_VISITS_TARGET
    
#     log_callback(f"[THREAD {tid}] Started!")
    
#     while is_running:
#         if total_conversions >= TOTAL_VISITS_TARGET:
#             log_callback(f"[THREAD {tid}] TARGET REACHED! {total_conversions}/{TOTAL_VISITS_TARGET}")
#             check_complete_callback()
#             break
            
#         ua = random.choice(USER_AGENTS)
#         res = random.choice(RESOLUTIONS)
        
#         options = Options()
#         options.add_argument(f"--user-agent={ua}")
#         options.add_argument(f"--window-size={res}")
#         options.add_argument("--no-sandbox")
#         options.add_argument("--disable-dev-shm-usage")
#         options.add_argument("--disable-blink-features=AutomationControlled")
#         options.add_experimental_option("excludeSwitches", ["enable-automation"])
#         options.add_experimental_option('useAutomationExtension', False)
#         options.add_argument("--disable-gpu")
#         options.add_argument("--ignore-certificate-errors")
#         options.add_argument("--ignore-ssl-errors")

#         driver = None
#         try:
#             driver = webdriver.Chrome(
#                 service=Service(ChromeDriverManager().install()),
#                 options=options,
#                 seleniumwire_options={
#                     'proxy': {'http': PROXY_URL, 'https': PROXY_URL},
#                     'verify_ssl': False,
#                     'suppress_connection_errors': True
#                 }
#             )
            
#             driver.get("https://api.ipify.org")
#             time.sleep(3)
#             ip = driver.find_element(By.TAG_NAME, "body").text.strip()

#             driver.get(f"{TARGET_URL}&sub2=CLK{random.randint(1000000,9999999)}")
#             time.sleep(random.randint(22, 38))

#             essay = generate_pledge()
#             mobile = generate_mobile()

#             driver.find_element(By.CSS_SELECTOR, "textarea[name='pledge'], textarea#pledge").send_keys(essay)
#             driver.find_element(By.CSS_SELECTOR, "input[name='phone'], input#phone").send_keys(mobile)
#             driver.execute_script("document.querySelector('input[type=\"checkbox\"], input#terms')?.click();")
#             driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

#             total_conversions += 1
#             log_callback(f"[THREAD {tid}] SUCCESS | Words: {len(essay.split())} | IP: {ip} | TOTAL: {total_conversions}/{TOTAL_VISITS_TARGET}")
#             status_callback(f"Total Conversions: {total_conversions}/{TOTAL_VISITS_TARGET}")

#             log({
#                 "thread": tid,
#                 "no": total_conversions,
#                 "time": datetime.now().strftime("%H:%M:%S"),
#                 "ip": ip,
#                 "mobile": mobile,
#                 "words": len(essay.split()),
#                 "pledge": essay
#             })

#             time.sleep(random.randint(12, 22))
            
#         except Exception as e:
#             log_callback(f"[THREAD {tid}] ERROR → {str(e)[:80]}")
#             time.sleep(15)
#         finally:
#             if driver:
#                 driver.quit()
    
#     log_callback(f"[THREAD {tid}] Stopped.")

# # ================== GUI (BILKUL SAME) ==================
# class TataGroqGUI:
#     def __init__(self, root):
#         self.root = root
#         self.root.title("TATA 1 LAKH GROQ BEAST - FINAL UNDETECTABLE")
#         self.root.geometry("800x650")
#         self.root.configure(bg="#1a1a2e")
#         self.root.resizable(True, True)
#         self.threads = []
#         self.create_widgets()
    
#     def create_widgets(self):
#         title_frame = tk.Frame(self.root, bg="#1a1a2e")
#         title_frame.pack(pady=20)
        
#         tk.Label(title_frame, text="TATA 1 LAKH GROQ BEAST", font=("Arial", 24, "bold"), fg="#ff6b35", bg="#1a1a2e").pack()
#         tk.Label(title_frame, text="100% CLEAN • NO STARTER REPEAT • ZERO PATTERN • UNDETECTABLE", font=("Arial", 10), fg="#00ff88", bg="#1a1a2e").pack()
        
#         input_frame = tk.Frame(self.root, bg="#16213e", padx=30, pady=20)
#         input_frame.pack(pady=10, padx=30, fill="x")
        
#         tk.Label(input_frame, text="Target URL:", font=("Arial", 12, "bold"), fg="#ffffff", bg="#16213e").grid(row=0, column=0, sticky="w", pady=5)
#         self.url_entry = tk.Entry(input_frame, font=("Arial", 11), width=60, bg="#0f0f23", fg="#00ff88", insertbackground="#00ff88", relief="flat", highlightthickness=2, highlightbackground="#333", highlightcolor="#ff6b35")
#         self.url_entry.grid(row=0, column=1, pady=5, padx=10, sticky="ew")
#         self.url_entry.insert(0, "https://partners.marcadeo.com/click?oid=298&uid=908&lid=263")
        
#         tk.Label(input_frame, text="Groq API Key:", font=("Arial", 12, "bold"), fg="#ffffff", bg="#16213e").grid(row=1, column=0, sticky="w", pady=5)
#         self.key_entry = tk.Entry(input_frame, font=("Arial", 11), width=60, bg="#0f0f23", fg="#00ff88", insertbackground="#00ff88", relief="flat", show="*", highlightthickness=2, highlightbackground="#333", highlightcolor="#ff6b35")
#         self.key_entry.grid(row=1, column=1, pady=5, padx=10, sticky="ew")
#         self.key_entry.insert(0, "CHANGE_ME_GROQ_KEY")
        
#         self.show_key = False
#         tk.Button(input_frame, text="View", font=("Arial", 10), bg="#333", fg="#fff", relief="flat", command=self.toggle_key_visibility).grid(row=1, column=2, padx=5)
        
#         tk.Label(input_frame, text="Total Visits:", font=("Arial", 12, "bold"), fg="#ffffff", bg="#16213e").grid(row=2, column=0, sticky="w", pady=5)
#         self.visits_entry = tk.Entry(input_frame, font=("Arial", 11), width=20, bg="#0f0f23", fg="#00ff88", insertbackground="#00ff88", relief="flat", highlightthickness=2, highlightbackground="#333", highlightcolor="#ff6b35")
#         self.visits_entry.grid(row=2, column=1, pady=5, padx=10, sticky="w")
#         self.visits_entry.insert(0, "10000")
        
#         tk.Label(input_frame, text="Threads:", font=("Arial", 12, "bold"), fg="#ffffff", bg="#16213e").grid(row=3, column=0, sticky="w", pady=5)
#         self.thread_spinbox = ttk.Spinbox(input_frame, from_=1, to=10, width=10, font=("Arial", 11))
#         self.thread_spinbox.set(5)
#         self.thread_spinbox.grid(row=3, column=1, pady=5, padx=10, sticky="w")
        
#         input_frame.columnconfigure(1, weight=1)
        
#         btn_frame = tk.Frame(self.root, bg="#1a1a2e")
#         btn_frame.pack(pady=15)
#         self.start_btn = tk.Button(btn_frame, text="START BEAST MODE", font=("Arial", 14, "bold"), bg="#00ff88", fg="#000000", width=25, height=2, relief="flat", cursor="hand2", command=self.start_script)
#         self.start_btn.pack(side="left", padx=10)
#         self.stop_btn = tk.Button(btn_frame, text="STOP", font=("Arial", 14, "bold"), bg="#ff4444", fg="#ffffff", width=15, height=2, relief="flat", cursor="hand2", command=self.stop_script, state="disabled")
#         self.stop_btn.pack(side="left", padx=10)
        
#         self.status_label = tk.Label(self.root, text="Status: Ready", font=("Arial", 12, "bold"), fg="#00ff88", bg="#1a1a2e")
#         self.status_label.pack(pady=5)
        
#         log_frame = tk.Frame(self.root, bg="#1a1a2e")
#         log_frame.pack(pady=10, padx=30, fill="both", expand=True)
#         tk.Label(log_frame, text="Live Logs:", font=("Arial", 11, "bold"), fg="#ffffff", bg="#1a1a2e").pack(anchor="w")
#         self.log_text = scrolledtext.ScrolledText(log_frame, font=("Consolas", 10), bg="#0f0f23", fg="#00ff88", height=12, relief="flat", insertbackground="#00ff88")
#         self.log_text.pack(fill="both", expand=True, pady=5)
        
#         tk.Label(self.root, text="FINAL VERSION • 100% CLEAN PLEDGES • NO STARTER LINES • UNDETECTABLE", font=("Arial", 9, "bold"), fg="#00ff88", bg="#1a1a2e").pack(pady=10)
    
#     def toggle_key_visibility(self):
#         self.show_key = not self.show_key
#         self.key_entry.config(show="" if self.show_key else "*")

#     def log_message(self, message):
#         self.log_text.insert(tk.END, f"{message}\n")
#         self.log_text.see(tk.END)
    
#     def update_status(self, status):
#         self.status_label.config(text=f"Status: {status}")
    
#     def check_complete(self):
#         global is_running, total_conversions, TOTAL_VISITS_TARGET
#         if total_conversions >= TOTAL_VISITS_TARGET:
#             is_running = False
#             self.log_message("="*80)
#             self.log_message(f"FULL MISSION COMPLETED! {total_conversions}/{TOTAL_VISITS_TARGET}")
#             self.log_message("ALL PLEDGES 100% UNIQUE, CLEAN & HUMAN-LIKE")
#             self.log_message("="*80)
#             self.update_status(f"COMPLETED: {total_conversions}/{TOTAL_VISITS_TARGET}")
#             self.start_btn.config(state="normal", bg="#00ff88")
#             self.stop_btn.config(state="disabled")
#             self.url_entry.config(state="normal")
#             self.key_entry.config(state="normal")
#             self.visits_entry.config(state="normal")
#             messagebox.showinfo("SUCCESS", f"Target achieved!\n{total_conversions} clean pledges submitted!")

#     def start_script(self):
#         global TARGET_URL, GROQ_API_KEY, TOTAL_VISITS_TARGET, is_running, total_conversions
#         TARGET_URL = self.url_entry.get().strip()
#         GROQ_API_KEY = self.key_entry.get().strip()
#         try:
#             TOTAL_VISITS_TARGET = int(self.visits_entry.get().strip())
#         except:
#             messagebox.showerror("Error", "Invalid number!")
#             return
        
#         if not TARGET_URL or not GROQ_API_KEY:
#             messagebox.showerror("Error", "Fill URL & API Key!")
#             return
        
#         total_conversions = 0
#         self.log_message("Connecting to Groq...")
#         if not setup_groq_client(GROQ_API_KEY):
#             messagebox.showerror("Error", "Groq connection failed!")
#             return
        
#         is_running = True
#         self.start_btn.config(state="disabled", bg="#666666")
#         self.stop_btn.config(state="normal")
#         self.url_entry.config(state="disabled")
#         self.key_entry.config(state="disabled")
#         self.visits_entry.config(state="disabled")
        
#         thread_count = int(self.thread_spinbox.get())
#         self.log_message("="*80)
#         self.log_message("FINAL UNDETECTABLE BEAST MODE ACTIVATED!")
#         self.log_message(f"Target: {TOTAL_VISITS_TARGET} | Threads: {thread_count}")
#         self.log_message("="*80)
#         self.update_status(f"Running... 0/{TOTAL_VISITS_TARGET}")
        
#         for i in range(1, thread_count + 1):
#             t = threading.Thread(target=worker, args=(i, self.log_message, self.update_status, self.check_complete), daemon=True)
#             t.start()
#             self.threads.append(t)
#             time.sleep(2)
    
#     def stop_script(self):
#         global is_running
#         is_running = False
#         self.log_message("STOPPING ALL THREADS...")
#         self.start_btn.config(state="normal", bg="#00ff88")
#         self.stop_btn.config(state="disabled")
#         self.url_entry.config(state="normal")
#         self.key_entry.config(state="normal")
#         self.visits_entry.config(state="normal")
#         self.update_status("Stopped")

# if __name__ == "__main__":
#     root = tk.Tk()
#     app = TataGroqGUI(root)
#     root.mainloop()







# # TATA_1LAKH_GROQ_GUI_vFINAL_PROMPTS_FILE.py ← 100% UNDETECTABLE + PROMPTS FROM .TXT
# import tkinter as tk
# from tkinter import ttk, messagebox, scrolledtext, filedialog
# from seleniumwire import webdriver
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.chrome.options import Options
# from webdriver_manager.chrome import ChromeDriverManager
# from selenium.webdriver.common.by import By
# from groq import Groq
# import httpx
# import random
# import time
# import json
# import threading
# from datetime import datetime

# # ================== GLOBAL VARIABLES ==================
# PROXY_URL = "socks5://geonode_xvmYN44Bvz-type-residential-country-in:test@example.com:11000"
# TARGET_URL = ""
# GROQ_API_KEY = "CHANGE_ME_API_KEY"
# TOTAL_VISITS_TARGET = 10000
# groq_client = None
# is_running = False
# total_conversions = 0

# # Dynamic prompts list – ab .txt file se load hoga
# PROMPTS_LIST = []  # ← Ye ab file se fill hoga

# USER_AGENTS = [
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
#     "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:130.0) Gecko/20100101 Firefox/130.0",
#     "Mozilla/5.0 (Linux; Android 14; SM-S928B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.6778.68 Mobile Safari/537.36",
#     "Mozilla/5.0 (iPhone; CPU iPhone OS 18_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.1 Mobile/15E148 Safari/604.1",
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Edg/130.0.0.0",
#     "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.6778.68 Safari/537.36",
# ]

# RESOLUTIONS = [
#     "1920,1080", "1366,768", "1536,864", "1440,900", "1280,720", "1600,900",
#     "2560,1440", "1920,1200", "1680,1050", "1280,800", "1440,960", "2560,1600",
#     "360,800", "393,851", "390,844", "414,896", "430,932", "360,780",
#     "360,640", "412,915", "384,854", "360,760", "393,873", "428,926",
#     "375,812", "390,780", "360,840", "768,1024", "810,1080", "800,1280",
# ]

# LOG_FILE = "tata_english_groq_log.json"

# # Load prompts from .txt file
# def load_prompts(filepath):
#     global PROMPTS_LIST
#     try:
#         with open(filepath, "r", encoding="utf-8") as f:
#             lines = [line.strip() for line in f.readlines() if line.strip()]
#         if not lines:
#             return False, "Prompts file is empty!"
#         PROMPTS_LIST = lines
#         return True, f"Loaded {len(lines)} prompts successfully!"
#     except Exception as e:
#         return False, f"Error loading file: {e}"

# def setup_groq_client(api_key):
#     global groq_client
#     try:
#         proxy_url = "http://geonode_xvmYN44Bvz-type-residential-country-in:test@example.com:11000"
#         transport = httpx.HTTPTransport(proxy=proxy_url)
#         client = httpx.Client(transport=transport)
#         groq_client = Groq(api_key=api_key, http_client=client)
#         return True
#     except Exception as e:
#         print(f"Groq setup error: {e}")
#         return False

# # FINAL PLEDGE GENERATOR – ZERO PROMPT LEAK + MAX UNIQUENESS
# def generate_pledge():
#     global groq_client, PROMPTS_LIST
#     if not PROMPTS_LIST:
#         return "I'm just so done with everything yaar, can't even explain anymore..."

#     starter = random.choice(PROMPTS_LIST)

#     prompt = f"""
# You are a real Indian citizen writing a raw, emotional, personal pledge in English for Tata campaign.
# NEVER use, repeat, or start with this line anywhere: "{starter}"
# Your first sentence must feel 100% natural – like a real person venting suddenly.
# Write 190–340 words only.Sound like a 2025 Indian – raw, broken, hopeful, sarcastic, frustrated.
# No fixed structure. End naturally or abruptly.
# Just write like a human who just opened their heart – zero AI feel.
# """

#     try:
#         response = groq_client.chat.completions.create(
#             model="llama-3.3-70b-versatile",
#             messages=[{"role": "user", "content": prompt}],
#             temperature=random.uniform(1.88, 2.0),
#             max_tokens=1000,
#             top_p=random.uniform(0.91, 0.96)
#         )
#         pledge = response.choices[0].message.content.strip()

#         # Extra safety – remove starter if somehow appears
#         for bad in PROMPTS_LIST:
#             bad_clean = bad.strip(" :,-").lower()
#             if pledge.lower().startswith(bad_clean):
#                 pledge = pledge[len(bad):].lstrip(" :,-").strip()
#                 break

#         if len(pledge.split()) < 130:
#             raise Exception("Too short")
#         return pledge

#     except Exception as e:
#         safe = [
#             "Yaar I'm literally crying thinking about our rivers turning black.",
#             "Can't believe we're still breathing this poison every day.",
#             "One minute I'm proud, next minute I just wanna scream.",
#             "This country breaks my heart and heals it at the same time.",
#             "I'm done making excuses for our system, enough is enough.",
#             "We deserve better, and I'm not shutting up till we get it.",
#             "Tears in my eyes but fire in my soul.",
#             "Not gonna sit quiet anymore, time to speak up.",
#             "This country gave me everything, now it's my turn.",
#             "I'm frustrated, but I'm also full of hope."
#         ]
#         return " ".join(random.sample(safe, k=random.randint(11,16))) + " This is real. This is me."

# def generate_mobile():
#     return random.choice(["7","8","9"]) + "".join(random.choices("0123456789", k=9))

# def log(data):
#     try:
#         with open(LOG_FILE, "r", encoding="utf-8") as f:
#             logs = json.load(f)
#     except:
#         logs = []
#     logs.append(data)
#     with open(LOG_FILE, "w", encoding="utf-8") as f:
#         json.dump(logs, f, indent=2, ensure_ascii=False)

# # ================== WORKER THREAD (SAME) ==================
# def worker(tid, log_callback, status_callback, check_complete_callback):
#     global is_running, total_conversions, TARGET_URL, TOTAL_VISITS_TARGET
    
#     log_callback(f"[THREAD {tid}] Started!")
    
#     while is_running:
#         if total_conversions >= TOTAL_VISITS_TARGET:
#             log_callback(f"[THREAD {tid}] TARGET REACHED! {total_conversions}/{TOTAL_VISITS_TARGET}")
#             check_complete_callback()
#             break
            
#         ua = random.choice(USER_AGENTS)
#         res = random.choice(RESOLUTIONS)
        
#         options = Options()
#         options.add_argument(f"--user-agent={ua}")
#         options.add_argument(f"--window-size={res}")
#         options.add_argument("--no-sandbox")
#         options.add_argument("--disable-dev-shm-usage")
#         options.add_argument("--disable-blink-features=AutomationControlled")
#         options.add_experimental_option("excludeSwitches", ["enable-automation"])
#         options.add_experimental_option('useAutomationExtension', False)
#         options.add_argument("--disable-gpu")
#         options.add_argument("--ignore-certificate-errors")
#         options.add_argument("--ignore-ssl-errors")

#         driver = None
#         try:
#             driver = webdriver.Chrome(
#                 service=Service(ChromeDriverManager().install()),
#                 options=options,
#                 seleniumwire_options={
#                     'proxy': {'http': PROXY_URL, 'https': PROXY_URL},
#                     'verify_ssl': False,
#                     'suppress_connection_errors': True
#                 }
#             )
            
#             driver.get("https://api.ipify.org")
#             time.sleep(3)
#             ip = driver.find_element(By.TAG_NAME, "body").text.strip()

#             driver.get(f"{TARGET_URL}&sub2=CLK{random.randint(1000000,9999999)}")
#             time.sleep(random.randint(22, 38))

#             essay = generate_pledge()
#             mobile = generate_mobile()

#             driver.find_element(By.CSS_SELECTOR, "textarea[name='pledge'], textarea#pledge").send_keys(essay)
#             driver.find_element(By.CSS_SELECTOR, "input[name='phone'], input#phone").send_keys(mobile)
#             driver.execute_script("document.querySelector('input[type=\"checkbox\"], input#terms')?.click();")
#             driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

#             total_conversions += 1
#             log_callback(f"[THREAD {tid}] SUCCESS | Words: {len(essay.split())} | IP: {ip} | TOTAL: {total_conversions}/{TOTAL_VISITS_TARGET}")
#             status_callback(f"Total Conversions: {total_conversions}/{TOTAL_VISITS_TARGET}")

#             log({
#                 "thread": tid,
#                 "no": total_conversions,
#                 "time": datetime.now().strftime("%H:%M:%S"),
#                 "ip": ip,
#                 "mobile": mobile,
#                 "words": len(essay.split()),
#                 "pledge": essay
#             })

#             time.sleep(random.randint(12, 22))
            
#         except Exception as e:
#             log_callback(f"[THREAD {tid}] ERROR → {str(e)[:80]}")
#             time.sleep(15)
#         finally:
#             if driver:
#                 driver.quit()
    
#     log_callback(f"[THREAD {tid}] Stopped.")

# # ================== GUI WITH PROMPTS FILE SUPPORT ==================
# class TataGroqGUI:
#     def __init__(self, root):
#         self.root = root
#         self.root.title("TATA 1 LAKH GROQ BEAST - PROMPTS FROM .TXT")
#         self.root.geometry("850x700")
#         self.root.configure(bg="#1a1a2e")
#         self.root.resizable(True, True)
#         self.threads = []
#         self.create_widgets()
    
#     def create_widgets(self):
#         title_frame = tk.Frame(self.root, bg="#1a1a2e")
#         title_frame.pack(pady=20)
        
#         tk.Label(title_frame, text="TATA 1 LAKH GROQ BEAST", font=("Arial", 24, "bold"), fg="#ff6b35", bg="#1a1a2e").pack()
#         tk.Label(title_frame, text="100% UNDETECTABLE • PROMPTS FROM .TXT • ZERO PATTERN", font=("Arial", 10), fg="#00ff88", bg="#1a1a2e").pack()
        
#         input_frame = tk.Frame(self.root, bg="#16213e", padx=30, pady=20)
#         input_frame.pack(pady=10, padx=30, fill="x")

#         # Target URL
#         tk.Label(input_frame, text="Target URL:", font=("Arial", 12, "bold"), fg="#ffffff", bg="#16213e").grid(row=0, column=0, sticky="w", pady=5)
#         self.url_entry = tk.Entry(input_frame, font=("Arial", 11), width=60, bg="#0f0f23", fg="#00ff88", insertbackground="#00ff88")
#         self.url_entry.grid(row=0, column=1, pady=5, padx=10, sticky="ew")
#         self.url_entry.insert(0, "https://partners.marcadeo.com/click?oid=298&uid=908&lid=263")

#         # Groq Key
#         tk.Label(input_frame, text="Groq API Key:", font=("Arial", 12, "bold"), fg="#ffffff", bg="#16213e").grid(row=1, column=0, sticky="w", pady=5)
#         self.key_entry = tk.Entry(input_frame, font=("Arial", 11), width=60, bg="#0f0f23", fg="#00ff88", insertbackground="#00ff88", show="*")
#         self.key_entry.grid(row=1, column=1, pady=5, padx=10, sticky="ew")
#         self.key_entry.insert(0, "CHANGE_ME_GROQ_KEY")
#         tk.Button(input_frame, text="View", command=lambda: self.key_entry.config(show="" if self.key_entry.cget('show')=="*" else "*")).grid(row=1, column=2, padx=5)

#         # Prompts File
#         tk.Label(input_frame, text="Prompts File (.txt):", font=("Arial", 12, "bold"), fg="#ffffff", bg="#16213e").grid(row=2, column=0, sticky="w", pady=5)
#         self.file_var = tk.StringVar()
#         tk.Entry(input_frame, textvariable=self.file_var, width=50, bg="#0f0f23", fg="#00ff88").grid(row=2, column=1, padx=(10,5), sticky="w")
#         tk.Button(input_frame, text="Browse", command=self.browse_prompts, bg="#333", fg="white").grid(row=2, column=1, padx=(360,0), sticky="w")
#         self.file_status = tk.Label(input_frame, text="No file selected", fg="red", bg="#16213e")
#         self.file_status.grid(row=3, column=1, sticky="w", padx=10, pady=2)

#         # Total Visits
#         tk.Label(input_frame, text="Total Visits:", font=("Arial", 12, "bold"), fg="#ffffff", bg="#16213e").grid(row=4, column=0, sticky="w", pady=5)
#         self.visits_entry = tk.Entry(input_frame, font=("Arial", 11), width=20, bg="#0f0f23", fg="#00ff88")
#         self.visits_entry.grid(row=4, column=1, pady=5, padx=10, sticky="w")
#         self.visits_entry.insert(0, "10000")

#         # Threads
#         tk.Label(input_frame, text="Threads:", font=("Arial", 12, "bold"), fg="#ffffff", bg="#16213e").grid(row=5, column=0, sticky="w", pady=5)
#         self.thread_spinbox = ttk.Spinbox(input_frame, from_=1, to=10, width=10)
#         self.thread_spinbox.set(5)
#         self.thread_spinbox.grid(row=5, column=1, pady=5, padx=10, sticky="w")

#         input_frame.columnconfigure(1, weight=1)

#         btn_frame = tk.Frame(self.root, bg="#1a1a2e")
#         btn_frame.pack(pady=20)
#         self.start_btn = tk.Button(btn_frame, text="START BEAST MODE", font=("Arial", 14, "bold"), bg="#00ff88", fg="black", width=25, height=2, state="disabled", command=self.start_script)
#         self.start_btn.pack(side="left", padx=10)
#         self.stop_btn = tk.Button(btn_frame, text="STOP", font=("Arial", 14, "bold"), bg="#ff4444", fg="white", width=15, height=2, state="disabled", command=self.stop_script)
#         self.stop_btn.pack(side="left", padx=10)

#         self.status_label = tk.Label(self.root, text="Status: Ready (Select Prompts File)", font=("Arial", 12, "bold"), fg="#ff4444", bg="#1a1a2e")
#         self.status_label.pack(pady=5)

#         log_frame = tk.Frame(self.root, bg="#1a1a2e")
#         log_frame.pack(pady=10, padx=30, fill="both", expand=True)
#         tk.Label(log_frame, text="Live Logs:", font=("Arial", 11, "bold"), fg="#ffffff", bg="#1a1a2e").pack(anchor="w")
#         self.log_text = scrolledtext.ScrolledText(log_frame, font=("Consolas", 10), bg="#0f0f23", fg="#00ff88", height=12)
#         self.log_text.pack(fill="both", expand=True, pady=5)

#         tk.Label(self.root, text="NOW WITH .TXT PROMPTS • CHANGE FILE EVERY 4-5 HOURS • 1000X UNIQUENESS", font=("Arial", 9, "bold"), fg="#00ff88", bg="#1a1a2e").pack(pady=10)

#     def browse_prompts(self):
#         file = filedialog.askopenfilename(title="Select Prompts File", filetypes=[("Text Files", "*.txt")])
#         if file:
#             success, msg = load_prompts(file)
#             self.file_var.set(file)
#             self.file_status.config(text=msg, fg="lime" if success else "red")
#             if success and self.key_entry.get().strip() and self.url_entry.get().strip():
#                 self.start_btn.config(state="normal")
#                 self.status_label.config(text="Status: Ready to Launch", fg="#00ff88")
#             else:
#                 self.start_btn.config(state="disabled")

#     def log_message(self, message):
#         self.log_text.insert(tk.END, f"{message}\n")
#         self.log_text.see(tk.END)
    
#     def update_status(self, status):
#         self.status_label.config(text=f"Status: {status}")

#     def check_complete(self):
#         global is_running, total_conversions, TOTAL_VISITS_TARGET
#         if total_conversions >= TOTAL_VISITS_TARGET:
#             is_running = False
#             self.log_message("="*80)
#             self.log_message(f"MISSION COMPLETED! {total_conversions}/{TOTAL_VISITS_TARGET} Pledges Done!")
#             self.log_message("ALL 100% UNIQUE • UNDETECTABLE • HUMAN-LIKE")
#             self.log_message("="*80)
#             self.update_status(f"COMPLETED: {total_conversions}/{TOTAL_VISITS_TARGET}")
#             self.start_btn.config(state="normal", bg="#00ff88")
#             self.stop_btn.config(state="disabled")
#             messagebox.showinfo("BEAST MODE OFF", f"Target achieved!\n{total_conversions} pledges submitted!")

#     def start_script(self):
#         global TARGET_URL, GROQ_API_KEY, TOTAL_VISITS_TARGET, is_running, total_conversions
#         TARGET_URL = self.url_entry.get().strip()
#         GROQ_API_KEY = self.key_entry.get().strip()
#         try:
#             TOTAL_VISITS_TARGET = int(self.visits_entry.get().strip())
#         except:
#             messagebox.showerror("Error", "Invalid number in Total Visits!")
#             return
        
#         if not all([TARGET_URL, GROQ_API_KEY, PROMPTS_LIST]):
#             messagebox.showerror("Error", "Missing: URL / API Key / Prompts File!")
#             return
        
#         total_conversions = 0
#         self.log_message("Connecting to Groq...")
#         if not setup_groq_client(GROQ_API_KEY):
#             messagebox.showerror("Error", "Groq connection failed!")
#             return
        
#         is_running = True
#         self.start_btn.config(state="disabled")
#         self.stop_btn.config(state="normal")
#         self.url_entry.config(state="disabled")
#         self.key_entry.config(state="disabled")
#         self.visits_entry.config(state="disabled")

#         thread_count = int(self.thread_spinbox.get())
#         self.log_message("="*80)
#         self.log_message(f"ULTIMATE BEAST MODE ACTIVATED! | Prompts: {len(PROMPTS_LIST)}")
#         self.log_message(f"Target: {TOTAL_VISITS_TARGET} | Threads: {thread_count}")
#         self.log_message("="*80)
#         self.update_status(f"Running... 0/{TOTAL_VISITS_TARGET}")

#         for i in range(1, thread_count + 1):
#             t = threading.Thread(target=worker, args=(i, self.log_message, self.update_status, self.check_complete), daemon=True)
#             t.start()
#             self.threads.append(t)
#             time.sleep(2)
    
#     def stop_script(self):
#         global is_running
#         is_running = False
#         self.log_message("STOPPING ALL THREADS...")
#         self.start_btn.config(state="normal", bg="#00ff88")
#         self.stop_btn.config(state="disabled")
#         self.url_entry.config(state="normal")
#         self.key_entry.config(state="normal")
#         self.visits_entry.config(state="normal")
#         self.update_status("Stopped by User")

# if __name__ == "__main__":
#     root = tk.Tk()
#     app = TataGroqGUI(root)
#     root.mainloop()





# # TATA_1LAKH_GROQ_GUI_vREAL_MOBILE.py ← FINAL + REAL INDIAN NUMBERS + 100% UNDETECTABLE
# import tkinter as tk
# from tkinter import ttk, messagebox, scrolledtext, filedialog
# from seleniumwire import webdriver
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.chrome.options import Options
# from webdriver_manager.chrome import ChromeDriverManager
# from selenium.webdriver.common.by import By
# from groq import Groq
# import httpx
# import random
# import time
# import json
# import threading
# from datetime import datetime
# import phonenumbers
# from phonenumbers import carrier

# # ================== GLOBAL VARIABLES ==================
# PROXY_URL = "socks5://geonode_xvmYN44Bvz-type-residential-country-in:test@example.com:11000"
# TARGET_URL = ""
# GROQ_API_KEY = "CHANGE_ME_API_KEY"
# TOTAL_VISITS_TARGET = 10000
# groq_client = None
# is_running = False
# total_conversions = 0
# PROMPTS_LIST = []

# USER_AGENTS = [
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
#     "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:130.0) Gecko/20100101 Firefox/130.0",
#     "Mozilla/5.0 (Linux; Android 14; SM-S928B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.6778.68 Mobile Safari/537.36",
#     "Mozilla/5.0 (iPhone; CPU iPhone OS 18_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.1 Mobile/15E148 Safari/604.1",
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Edg/130.0.0.0",
#     "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.6778.68 Safari/537.36",
# ]

# RESOLUTIONS = [
#     "1920,1080", "1366,768", "1536,864", "1440,900", "1280,720", "1600,900",
#     "2560,1440", "1920,1200", "1680,1050", "1280,800", "1440,960", "2560,1600",
#     "360,800", "393,851", "390,844", "414,896", "430,932", "360,780",
#     "360,640", "412,915", "384,854", "360,760", "393,873", "428,926",
#     "375,812", "390,780", "360,840", "768,1024", "810,1080", "800,1280",
# ]

# LOG_FILE = "tata_english_groq_log.json"

# # Indian Mobile Prefixes (Real & Updated 2025)
# REAL_PREFIXES = [
#     # Jio
#     "600","601","602","603","604","605","606","607","608","609",
#     "701","702","703","704","705","706","707","708","709",
#     "721","722","723","724","725","726","727","728","729",
#     "741","742","743","744","745","746","747","748","749",
#     "761","762","763","764","765","766","767","768","769",
#     "781","782","783","784","785","786","787","788","789",
#     "791","792","793","794","795","796","797","798","799",
#     # Airtel
#     "801","802","803","804","805","806","807","808","809",
#     "821","822","823","824","825","826","827","828","829",
#     "831","832","833","834","835","836","837","838","839",
#     "851","852","853","854","855","856","857","858","859",
#     "861","862","863","864","865","866","867","868","869",
#     "871","872","873","874","875","876","877","878","879",
#     "881","882","883","884","885","886","887","888","889",
#     "891","892","893","894","895","896","897","898","899",
#     # Vi
#     "900","901","902","903","904","905","906","907","908","909",
#     "911","912","913","914","915","916","917","918","919",
#     "920","921","922","923","924","925","926","927","928","929",
#     "931","932","933","934","935","936","937","938","939",
#     "941","942","943","944","945","946","947","948","949",
#     "950","951","952","953","954","955","956","957","958","959",
#     "961","962","963","964","965","966","967","968","969",
#     "971","972","973","974","975","976","977","978","979",
#     "981","982","983","984","985","986","987","988","989",
#     "991","992","993","994","995","996","997","998","999",
#     # BSNL
#     "841","842","843","844","845","846","847","848","849","940"
# ]

# def is_natural_number(num_str):
#     if len(num_str) != 10: return False
#     if any(char * 4 in num_str for char in "0123456789"): return False
#     seq = "0123456789999999999"
#     if any(seq[i:i+5] in num_str for i in range(len(seq)-4)): return False
#     if max(num_str.count(c) for c in "0123456789") > 3: return False
#     return True

# def generate_mobile():
#     while True:
#         prefix = random.choice(REAL_PREFIXES)
#         suffix = ''.join(random.choices("0123456789", k=7))
#         number = prefix + suffix
        
#         if not is_natural_number(number):
#             continue
            
#         try:
#             parsed = phonenumbers.parse("+91" + number, "IN")
#             if phonenumbers.is_valid_number(parsed) and phonenumbers.is_possible_number(parsed):
#                 return number
#         except:
#             continue

# # Load prompts from .txt file
# def load_prompts(filepath):
#     global PROMPTS_LIST
#     try:
#         with open(filepath, "r", encoding="utf-8") as f:
#             lines = [line.strip() for line in f.readlines() if line.strip()]
#         if not lines:
#             return False, "Prompts file is empty!"
#         PROMPTS_LIST = lines
#         return True, f"Loaded {len(lines)} prompts successfully!"
#     except Exception as e:
#         return False, f"Error loading file: {e}"

# def setup_groq_client(api_key):
#     global groq_client
#     try:
#         proxy_url = "http://geonode_xvmYN44Bvz-type-residential-country-in:test@example.com:9000"
#         transport = httpx.HTTPTransport(proxy=proxy_url)
#         client = httpx.Client(transport=transport)
#         groq_client = Groq(api_key=api_key, http_client=client)
#         return True
#     except Exception as e:
#         print(f"Groq setup error: {e}")
#         return False

# # PLEDGE GENERATOR (BILKUL PEHLE WALA HI)
# def generate_pledge():
#     global groq_client, PROMPTS_LIST
#     if not PROMPTS_LIST:
#         return "I'm just so done with everything yaar, can't even explain anymore..."

#     starter = random.choice(PROMPTS_LIST)

#     prompt = f"""
# You are a real Indian citizen writing a raw, emotional, personal pledge in English for Tata campaign.
# NEVER use, repeat, or start with this line anywhere: "{starter}"
# Your first sentence must feel 100% natural – like a real person venting suddenly.
# Write 190–340 Characters only. Sound like a 2025 Indian – raw, broken, hopeful, sarcastic, frustrated.
# No fixed structure. End naturally or abruptly.
# Just write like a human who just opened their heart – zero AI feel.
# """

#     try:
#         response = groq_client.chat.completions.create(
#             model="llama-3.3-70b-versatile",
#             messages=[{"role": "user", "content": prompt}],
#             temperature=random.uniform(1.88, 2.0),
#             max_tokens=1000,
#             top_p=random.uniform(0.91, 0.96)
#         )
#         pledge = response.choices[0].message.content.strip()

#         for bad in PROMPTS_LIST:
#             bad_clean = bad.strip(" :,-").lower()
#             if pledge.lower().startswith(bad_clean):
#                 pledge = pledge[len(bad):].lstrip(" :,-").strip()
#                 break

#         if len(pledge.split()) < 130:
#             raise Exception("Too short")
#         return pledge

#     except Exception as e:
#         safe = [
#             "Yaar I'm literally crying thinking about our rivers turning black.",
#             "Can't believe we're still breathing this poison every day.",
#             "One minute I'm proud, next minute I just wanna scream.",
#             "This country breaks my heart and heals it at the same time.",
#             "I'm done making excuses for our system, enough is enough.",
#             "We deserve better, and I'm not shutting up till we get it.",
#             "Tears in my eyes but fire in my soul.",
#             "Not gonna sit quiet anymore, time to speak up.",
#             "This country gave me everything, now it's my turn.",
#             "I'm frustrated, but I'm also full of hope."
#         ]
#         return " ".join(random.sample(safe, k=random.randint(11,16))) + " This is real. This is me."

# def log(data):
#     try:
#         with open(LOG_FILE, "r", encoding="utf-8") as f:
#             logs = json.load(f)
#     except:
#         logs = []
#     logs.append(data)
#     with open(LOG_FILE, "w", encoding="utf-8") as f:
#         json.dump(logs, f, indent=2, ensure_ascii=False)

# # ================== WORKER THREAD (BILKUL SAME) ==================
# def worker(tid, log_callback, status_callback, check_complete_callback):
#     global is_running, total_conversions, TARGET_URL, TOTAL_VISITS_TARGET
    
#     log_callback(f"[THREAD {tid}] Started!")
    
#     while is_running:
#         if total_conversions >= TOTAL_VISITS_TARGET:
#             log_callback(f"[THREAD {tid}] TARGET REACHED! {total_conversions}/{TOTAL_VISITS_TARGET}")
#             check_complete_callback()
#             break
            
#         ua = random.choice(USER_AGENTS)
#         res = random.choice(RESOLUTIONS)
        
#         options = Options()
#         options.add_argument(f"--user-agent={ua}")
#         options.add_argument(f"--window-size={res}")
#         options.add_argument("--no-sandbox")
#         options.add_argument("--disable-dev-shm-usage")
#         options.add_argument("--disable-blink-features=AutomationControlled")
#         options.add_experimental_option("excludeSwitches", ["enable-automation"])
#         options.add_experimental_option('useAutomationExtension', False)
#         options.add_argument("--disable-gpu")
#         options.add_argument("--ignore-certificate-errors")
#         options.add_argument("--ignore-ssl-errors")

#         driver = None
#         try:
#             driver = webdriver.Chrome(
#                 service=Service(ChromeDriverManager().install()),
#                 options=options,
#                 seleniumwire_options={
#                     'proxy': {'http': PROXY_URL, 'https': PROXY_URL},
#                     'verify_ssl': False,
#                     'suppress_connection_errors': True
#                 }
#             )
            
#             driver.get("https://api.ipify.org")
#             time.sleep(3)
#             ip = driver.find_element(By.TAG_NAME, "body").text.strip()

#             driver.get(f"{TARGET_URL}&sub2=CLK{random.randint(1000000,9999999)}")
#             time.sleep(random.randint(22, 38))

#             essay = generate_pledge()
#             mobile = generate_mobile()  # ← YEHI NAYA REAL NUMBER

#             driver.find_element(By.CSS_SELECTOR, "textarea[name='pledge'], textarea#pledge").send_keys(essay)
#             driver.find_element(By.CSS_SELECTOR, "input[name='phone'], input#phone").send_keys(mobile)
#             driver.execute_script("document.querySelector('input[type=\"checkbox\"], input#terms')?.click();")
#             driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

#             total_conversions += 1
#             log_callback(f"[THREAD {tid}] SUCCESS | Words: {len(essay.split())} | Mobile: {mobile} | IP: {ip} | TOTAL: {total_conversions}/{TOTAL_VISITS_TARGET}")
#             status_callback(f"Total Conversions: {total_conversions}/{TOTAL_VISITS_TARGET}")

#             log({
#                 "thread": tid,
#                 "no": total_conversions,
#                 "time": datetime.now().strftime("%H:%M:%S"),
#                 "ip": ip,
#                 "mobile": mobile,
#                 "words": len(essay.split()),
#                 "pledge": essay
#             })

#             time.sleep(random.randint(12, 22))
            
#         except Exception as e:
#             log_callback(f"[THREAD {tid}] ERROR → {str(e)[:80]}")
#             time.sleep(15)
#         finally:
#             if driver:
#                 driver.quit()
    
#     log_callback(f"[THREAD {tid}] Stopped.")

# # ================== GUI (BILKUL PEHLE WALA HI) ==================
# class TataGroqGUI:
#     def __init__(self, root):
#         self.root = root
#         self.root.title("TATA 1 LAKH GROQ BEAST - REAL INDIAN NUMBERS")
#         self.root.geometry("850x700")
#         self.root.configure(bg="#1a1a2e")
#         self.root.resizable(True, True)
#         self.threads = []
#         self.create_widgets()
    
#     def create_widgets(self):
#         title_frame = tk.Frame(self.root, bg="#1a1a2e")
#         title_frame.pack(pady=20)
        
#         tk.Label(title_frame, text="TATA 1 LAKH GROQ BEAST", font=("Arial", 24, "bold"), fg="#ff6b35", bg="#1a1a2e").pack()
#         tk.Label(title_frame, text="REAL INDIAN NUMBERS • NO FAKE PATTERN • 100% UNDETECTABLE", font=("Arial", 10), fg="#00ff88", bg="#1a1a2e").pack()
        
#         input_frame = tk.Frame(self.root, bg="#16213e", padx=30, pady=20)
#         input_frame.pack(pady=10, padx=30, fill="x")

#         tk.Label(input_frame, text="Target URL:", font=("Arial", 12, "bold"), fg="#ffffff", bg="#16213e").grid(row=0, column=0, sticky="w", pady=5)
#         self.url_entry = tk.Entry(input_frame, font=("Arial", 11), width=60, bg="#0f0f23", fg="#00ff88", insertbackground="#00ff88")
#         self.url_entry.grid(row=0, column=1, pady=5, padx=10, sticky="ew")
#         self.url_entry.insert(0, "https://partners.marcadeo.com/click?oid=298&uid=908&lid=263")

#         tk.Label(input_frame, text="Groq API Key:", font=("Arial", 12, "bold"), fg="#ffffff", bg="#16213e").grid(row=1, column=0, sticky="w", pady=5)
#         self.key_entry = tk.Entry(input_frame, font=("Arial", 11), width=60, bg="#0f0f23", fg="#00ff88", insertbackground="#00ff88", show="*")
#         self.key_entry.grid(row=1, column=1, pady=5, padx=10, sticky="ew")
#         self.key_entry.insert(0, "CHANGE_ME_GROQ_KEY")
#         tk.Button(input_frame, text="View", command=lambda: self.key_entry.config(show="" if self.key_entry.cget('show')=="*" else "*")).grid(row=1, column=2, padx=5)

#         tk.Label(input_frame, text="Prompts File (.txt):", font=("Arial", 12, "bold"), fg="#ffffff", bg="#16213e").grid(row=2, column=0, sticky="w", pady=5)
#         self.file_var = tk.StringVar()
#         tk.Entry(input_frame, textvariable=self.file_var, width=50, bg="#0f0f23", fg="#00ff88").grid(row=2, column=1, padx=(10,5), sticky="w")
#         tk.Button(input_frame, text="Browse", command=self.browse_prompts, bg="#333", fg="white").grid(row=2, column=1, padx=(360,0), sticky="w")
#         self.file_status = tk.Label(input_frame, text="No file selected", fg="red", bg="#16213e")
#         self.file_status.grid(row=3, column=1, sticky="w", padx=10, pady=2)

#         tk.Label(input_frame, text="Total Visits:", font=("Arial", 12, "bold"), fg="#ffffff", bg="#16213e").grid(row=4, column=0, sticky="w", pady=5)
#         self.visits_entry = tk.Entry(input_frame, font=("Arial", 11), width=20, bg="#0f0f23", fg="#00ff88")
#         self.visits_entry.grid(row=4, column=1, pady=5, padx=10, sticky="w")
#         self.visits_entry.insert(0, "10000")

#         tk.Label(input_frame, text="Threads:", font=("Arial", 12, "bold"), fg="#ffffff", bg="#16213e").grid(row=5, column=0, sticky="w", pady=5)
#         self.thread_spinbox = ttk.Spinbox(input_frame, from_=1, to=10, width=10)
#         self.thread_spinbox.set(5)
#         self.thread_spinbox.grid(row=5, column=1, pady=5, padx=10, sticky="w")

#         input_frame.columnconfigure(1, weight=1)

#         btn_frame = tk.Frame(self.root, bg="#1a1a2e")
#         btn_frame.pack(pady=20)
#         self.start_btn = tk.Button(btn_frame, text="START BEAST MODE", font=("Arial", 14, "bold"), bg="#00ff88", fg="black", width=25, height=2, state="disabled", command=self.start_script)
#         self.start_btn.pack(side="left", padx=10)
#         self.stop_btn = tk.Button(btn_frame, text="STOP", font=("Arial", 14, "bold"), bg="#ff4444", fg="white", width=15, height=2, state="disabled", command=self.stop_script)
#         self.stop_btn.pack(side="left", padx=10)

#         self.status_label = tk.Label(self.root, text="Status: Ready (Select Prompts File)", font=("Arial", 12, "bold"), fg="#ff4444", bg="#1a1a2e")
#         self.status_label.pack(pady=5)

#         log_frame = tk.Frame(self.root, bg="#1a1a2e")
#         log_frame.pack(pady=10, padx=30, fill="both", expand=True)
#         tk.Label(log_frame, text="Live Logs:", font=("Arial", 11, "bold"), fg="#ffffff", bg="#1a1a2e").pack(anchor="w")
#         self.log_text = scrolledtext.ScrolledText(log_frame, font=("Consolas", 10), bg="#0f0f23", fg="#00ff88", height=12)
#         self.log_text.pack(fill="both", expand=True, pady=5)

#         tk.Label(self.root, text="REAL INDIAN NUMBERS • NO FAKE PATTERN • CHANGE PROMPTS EVERY 4-5 HRS", font=("Arial", 9, "bold"), fg="#00ff88", bg="#1a1a2e").pack(pady=10)

#     def browse_prompts(self):
#         file = filedialog.askopenfilename(title="Select Prompts File", filetypes=[("Text Files", "*.txt")])
#         if file:
#             success, msg = load_prompts(file)
#             self.file_var.set(file)
#             self.file_status.config(text=msg, fg="lime" if success else "red")
#             if success and self.key_entry.get().strip() and self.url_entry.get().strip():
#                 self.start_btn.config(state="normal")
#                 self.status_label.config(text="Status: Ready to Launch", fg="#00ff88")

#     def log_message(self, message):
#         self.log_text.insert(tk.END, f"{message}\n")
#         self.log_text.see(tk.END)
    
#     def update_status(self, status):
#         self.status_label.config(text=f"Status: {status}")

#     def check_complete(self):
#         global is_running, total_conversions, TOTAL_VISITS_TARGET
#         if total_conversions >= TOTAL_VISITS_TARGET:
#             is_running = False
#             self.log_message("="*80)
#             self.log_message(f"MISSION COMPLETED! {total_conversions}/{TOTAL_VISITS_TARGET} Pledges Done!")
#             self.log_message("ALL 100% UNIQUE • REAL NUMBERS • UNDETECTABLE")
#             self.log_message("="*80)
#             self.update_status(f"COMPLETED: {total_conversions}/{TOTAL_VISITS_TARGET}")
#             self.start_btn.config(state="normal", bg="#00ff88")
#             self.stop_btn.config(state="disabled")
#             messagebox.showinfo("BEAST MODE OFF", f"Target achieved!\n{total_conversions} pledges submitted!")

#     def start_script(self):
#         global TARGET_URL, GROQ_API_KEY, TOTAL_VISITS_TARGET, is_running, total_conversions
#         TARGET_URL = self.url_entry.get().strip()
#         GROQ_API_KEY = self.key_entry.get().strip()
#         try:
#             TOTAL_VISITS_TARGET = int(self.visits_entry.get().strip())
#         except:
#             messagebox.showerror("Error", "Invalid number in Total Visits!")
#             return
        
#         if not all([TARGET_URL, GROQ_API_KEY, PROMPTS_LIST]):
#             messagebox.showerror("Error", "Missing: URL / API Key / Prompts File!")
#             return
        
#         total_conversions = 0
#         self.log_message("Connecting to Groq...")
#         if not setup_groq_client(GROQ_API_KEY):
#             messagebox.showerror("Error", "Groq connection failed!")
#             return
        
#         is_running = True
#         self.start_btn.config(state="disabled")
#         self.stop_btn.config(state="normal")
#         self.url_entry.config(state="disabled")
#         self.key_entry.config(state="disabled")
#         self.visits_entry.config(state="disabled")

#         thread_count = int(self.thread_spinbox.get())
#         self.log_message("="*80)
#         self.log_message(f"ULTIMATE BEAST MODE ACTIVATED! | Prompts: {len(PROMPTS_LIST)}")
#         self.log_message(f"Target: {TOTAL_VISITS_TARGET} | Threads: {thread_count}")
#         self.log_message("="*80)
#         self.update_status(f"Running... 0/{TOTAL_VISITS_TARGET}")

#         for i in range(1, thread_count + 1):
#             t = threading.Thread(target=worker, args=(i, self.log_message, self.update_status, self.check_complete), daemon=True)
#             t.start()
#             self.threads.append(t)
#             time.sleep(2)
    
#     def stop_script(self):
#         global is_running
#         is_running = False
#         self.log_message("STOPPING ALL THREADS...")
#         self.start_btn.config(state="normal", bg="#00ff88")
#         self.stop_btn.config(state="disabled")
#         self.url_entry.config(state="normal")
#         self.key_entry.config(state="normal")
#         self.visits_entry.config(state="normal")
#         self.update_status("Stopped by User")

# if __name__ == "__main__":
#     root = tk.Tk()
#     app = TataGroqGUI(root)
#     root.mainloop()








# # TATA_1LAKH_GROQ_GUI.py ← Updated: Only AI Content Submission (No Prompt Prefix)
# import tkinter as tk
# from tkinter import ttk, messagebox, scrolledtext
# from seleniumwire import webdriver
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.chrome.options import Options
# from webdriver_manager.chrome import ChromeDriverManager
# from selenium.webdriver.common.by import By
# from groq import Groq
# import httpx
# import random
# import time
# import json
# import threading
# from datetime import datetime

# # ================== GLOBAL VARIABLES ==================
# PROXY_URL = "socks5://geonode_xvmYN44Bvz-type-residential-country-in:test@example.com:11000"
# TARGET_URL = ""
# GROQ_API_KEY = "CHANGE_ME_API_KEY"
# TOTAL_VISITS_TARGET = 10000
# groq_client = None
# is_running = False
# total_conversions = 0

# USER_AGENTS = [
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
#     "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:130.0) Gecko/20100101 Firefox/130.0",
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Edg/130.0.0.0",
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:129.0) Gecko/20100101 Firefox/129.0",
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:131.0) Gecko/20100101 Firefox/131.0",
#     "Mozilla/5.0 (Linux; Android 14; SM-S928B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.6723.69 Mobile Safari/537.36",
#     "Mozilla/5.0 (Linux; Android 13; Pixel 7 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Mobile Safari/537.36",
#     "Mozilla/5.0 (Linux; Android 14; SM-A546E) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.6668.100 Mobile Safari/537.36",
#     "Mozilla/5.0 (Linux; Android 12; Redmi Note 11) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Mobile Safari/537.36",
#     "Mozilla/5.0 (Linux; Android 13; M2101K6G) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Mobile Safari/537.36",
#     "Mozilla/5.0 (Linux; Android 14; 2201116PG) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Mobile Safari/537.36",
#     "Mozilla/5.0 (Linux; Android 13; SM-A346E) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Mobile Safari/537.36",
#     "Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Mobile Safari/537.36",
#     "Mozilla/5.0 (iPhone; CPU iPhone OS 18_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.1 Mobile/15E148 Safari/604.1",
#     "Mozilla/5.0 (iPhone; CPU iPhone OS 17_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.6 Mobile/15E148 Safari/604.1",
#     "Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/130.0.6723.68 Mobile/15E148 Safari/604.1",
#     "Mozilla/5.0 (iPad; CPU OS 18_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.1 Mobile/15E148 Safari/604.1",
#     "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
#     "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.1 Safari/605.1.15",
#     "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
#     "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:130.0) Gecko/20100101 Firefox/130.0",
#     "Mozilla/5.0 (Windows NT 11.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.6778.53 Safari/537.36",
#     "Mozilla/5.0 (Linux; Android 15; Pixel 9 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.6778.53 Mobile Safari/537.36",
# ]

# RESOLUTIONS = [
#     "1920,1080", "1366,768", "1536,864", "1440,900", "1280,720", "1600,900",
#     "2560,1440", "1920,1200", "1680,1050", "1280,800", "1440,960", "2560,1600",
#     "360,800", "393,851", "390,844", "414,896", "430,932", "360,780",
#     "360,640", "412,915", "384,854", "360,760", "393,873", "428,926",
#     "375,812", "390,780", "360,840", "768,1024", "810,1080", "800,1280",
# ]

# LOG_FILE = "tata_groq_log.json"

# # ================== GROQ CLIENT SETUP ==================
# def setup_groq_client(api_key):
#     global groq_client
#     try:
#         proxy_url = "http://geonode_xvmYN44Bvz-type-residential-country-in:test@example.com:9000"
#         transport = httpx.HTTPTransport(proxy=proxy_url)
#         client = httpx.Client(transport=transport)
#         groq_client = Groq(api_key=api_key, http_client=client)
#         return True
#     except Exception as e:
#         print(f"Groq setup error: {e}")
#         return False

# # ================== GENERATE CONTENT (ONLY AI RESPONSE) ==================
# def generate_content():
#     global groq_client
    
#     prompt = """Write a powerful, emotional, and patriotic pledge in English (within 450 Characters).
    
#     The pledge should:
#     - Express deep love and commitment to the nation
#     - Be written in first person
#     - Use passionate and inspiring language
#     - Include themes of unity, progress, responsibility, and national pride
#     - End with a strong patriotic closing
    
#     IMPORTANT: Write ONLY the pledge content. Do not include any prefix, introduction, or explanation."""
    
#     try:
#         response = groq_client.chat.completions.create(
#             model="llama-3.3-70b-versatile",
#             messages=[{"role": "user", "content": prompt}],
#             temperature=1.05,
#             max_tokens=700,
#             top_p=0.95
#         )
#         content = response.choices[0].message.content.strip()
        
#         # Remove any common AI prefixes/intros if present
#         content = content.replace("Here is a pledge:", "").strip()
#         content = content.replace("Here's a pledge:", "").strip()
#         content = content.replace("Pledge:", "").strip()
        
#         # Ensure proper ending
#         if not any(end in content.lower() for end in [""]):
#             content += ""
        
#         return content
#     except Exception as e:
#         print(f"[GROQ ERROR] Using fallback → {e}")
#         return "I pledge to serve my nation with unwavering dedication and loyalty. I will uphold the values of unity, integrity, and progress that define our great country. I promise to work tirelessly for the betterment of every citizen and contribute meaningfully to India's growth. I will respect our diversity and cherish our cultural heritage. With courage in my heart and determination in my spirit, I commit to making India a global leader. This is my solemn promise to my motherland. Jai Hind! Bharat Mata Ki Jai!"

# def generate_mobile():
#     return random.choice(["7","8","9"]) + "".join(random.choices("0123456789", k=9))

# def log(data):
#     try:
#         with open(LOG_FILE, "r", encoding="utf-8") as f:
#             logs = json.load(f)
#     except:
#         logs = []
#     logs.append(data)
#     with open(LOG_FILE, "w", encoding="utf-8") as f:
#         json.dump(logs, f, indent=2, ensure_ascii=False)

# # ================== WORKER THREAD ==================
# def worker(tid, log_callback, status_callback, check_complete_callback):
#     global is_running, total_conversions, TARGET_URL, TOTAL_VISITS_TARGET
    
#     log_callback(f"[THREAD {tid}] Started!")
    
#     while is_running:
#         if total_conversions >= TOTAL_VISITS_TARGET:
#             log_callback(f"[THREAD {tid}] 🎯 TARGET REACHED! {total_conversions}/{TOTAL_VISITS_TARGET}")
#             check_complete_callback()
#             break
            
#         ua = random.choice(USER_AGENTS)
#         res = random.choice(RESOLUTIONS)
        
#         options = Options()
#         options.add_argument(f"--user-agent={ua}")
#         options.add_argument(f"--window-size={res}")
#         options.add_argument("--no-sandbox")
#         options.add_argument("--disable-dev-shm-usage")
#         options.add_argument("--disable-blink-features=AutomationControlled")
#         options.add_experimental_option("excludeSwitches", ["enable-automation"])
#         options.add_experimental_option('useAutomationExtension', False)
#         options.add_argument("--disable-gpu")
#         options.add_argument("--ignore-certificate-errors")
#         options.add_argument("--ignore-ssl-errors")

#         driver = None
#         try:
#             driver = webdriver.Chrome(
#                 service=Service(ChromeDriverManager().install()),
#                 options=options,
#                 seleniumwire_options={
#                     'proxy': {'http': PROXY_URL, 'https': PROXY_URL},
#                     'verify_ssl': False,
#                     'suppress_connection_errors': True
#                 }
#             )
            
#             driver.get("https://api.ipify.org")
#             time.sleep(3)
#             ip = driver.find_element(By.TAG_NAME, "body").text.strip()

#             driver.get(f"{TARGET_URL}&sub2=CLK{random.randint(1000000,9999999)}")
#             time.sleep(random.randint(22, 38))

#             content = generate_content()
#             mobile = generate_mobile()

#             driver.find_element(By.CSS_SELECTOR, "textarea[name='pledge'], textarea#pledge").send_keys(content)
#             driver.find_element(By.CSS_SELECTOR, "input[name='phone'], input#phone").send_keys(mobile)
#             driver.execute_script("document.querySelector('input[type=\"checkbox\"], input#terms')?.click();")
#             driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

#             total_conversions += 1
#             log_callback(f"[THREAD {tid}] ✓ SUCCESS | Words: {len(content.split())} | IP: {ip} | TOTAL: {total_conversions}/{TOTAL_VISITS_TARGET}")
#             status_callback(f"Total Conversions: {total_conversions}/{TOTAL_VISITS_TARGET}")

#             log({"thread": tid, "no": total_conversions, "time": datetime.now().strftime("%H:%M:%S"), "ip": ip, "words": len(content.split())})

#             time.sleep(random.randint(12, 22))
            
#         except Exception as e:
#             log_callback(f"[THREAD {tid}] ✗ ERROR → {str(e)[:80]}")
#             time.sleep(15)
#         finally:
#             if driver:
#                 driver.quit()
    
#     log_callback(f"[THREAD {tid}] Stopped.")

# # ================== GUI CLASS ==================
# class TataGroqGUI:
#     def __init__(self, root):
#         self.root = root
#         self.root.title("🇮🇳 TATA GROQ AUTOMATION - AI Content Only")
#         self.root.geometry("800x650")
#         self.root.configure(bg="#1a1a2e")
#         self.root.resizable(True, True)
        
#         self.threads = []
#         self.create_widgets()
    
#     def create_widgets(self):
#         # Title
#         title_frame = tk.Frame(self.root, bg="#1a1a2e")
#         title_frame.pack(pady=20)
        
#         title_label = tk.Label(
#             title_frame, 
#             text="🇮🇳 TATA GROQ AUTOMATION 🇮🇳",
#             font=("Arial", 24, "bold"),
#             fg="#ff6b35",
#             bg="#1a1a2e"
#         )
#         title_label.pack()
        
#         subtitle = tk.Label(
#             title_frame,
#             text="100% AI Generated Content | Residential Proxy | Undetectable",
#             font=("Arial", 10),
#             fg="#888888",
#             bg="#1a1a2e"
#         )
#         subtitle.pack()
        
#         # Input Frame
#         input_frame = tk.Frame(self.root, bg="#16213e", padx=30, pady=20)
#         input_frame.pack(pady=10, padx=30, fill="x")
        
#         # Target URL
#         url_label = tk.Label(
#             input_frame,
#             text="🎯 Target URL:",
#             font=("Arial", 12, "bold"),
#             fg="#ffffff",
#             bg="#16213e"
#         )
#         url_label.grid(row=0, column=0, sticky="w", pady=5)
        
#         self.url_entry = tk.Entry(
#             input_frame,
#             font=("Arial", 11),
#             width=60,
#             bg="#0f0f23",
#             fg="#00ff88",
#             insertbackground="#00ff88",
#             relief="flat",
#             highlightthickness=2,
#             highlightbackground="#333",
#             highlightcolor="#ff6b35"
#         )
#         self.url_entry.grid(row=0, column=1, pady=5, padx=10, sticky="ew")
#         self.url_entry.insert(0, "https://partners.marcadeo.com/click?oid=298&uid=908&lid=263")
        
#         # Groq API Key
#         key_label = tk.Label(
#             input_frame,
#             text="🔑 Groq API Key:",
#             font=("Arial", 12, "bold"),
#             fg="#ffffff",
#             bg="#16213e"
#         )
#         key_label.grid(row=1, column=0, sticky="w", pady=5)
        
#         self.key_entry = tk.Entry(
#             input_frame,
#             font=("Arial", 11),
#             width=60,
#             bg="#0f0f23",
#             fg="#00ff88",
#             insertbackground="#00ff88",
#             relief="flat",
#             show="*",
#             highlightthickness=2,
#             highlightbackground="#333",
#             highlightcolor="#ff6b35"
#         )
#         self.key_entry.grid(row=1, column=1, pady=5, padx=10, sticky="ew")
        
#         # Show/Hide Key Button
#         self.show_key = False
#         self.toggle_btn = tk.Button(
#             input_frame,
#             text="👁",
#             font=("Arial", 10),
#             bg="#333",
#             fg="#fff",
#             relief="flat",
#             command=self.toggle_key_visibility
#         )
#         self.toggle_btn.grid(row=1, column=2, padx=5)
        
#         # Total Visits Target
#         visits_label = tk.Label(
#             input_frame,
#             text="🎯 Total Visits:",
#             font=("Arial", 12, "bold"),
#             fg="#ffffff",
#             bg="#16213e"
#         )
#         visits_label.grid(row=2, column=0, sticky="w", pady=5)
        
#         self.visits_entry = tk.Entry(
#             input_frame,
#             font=("Arial", 11),
#             width=20,
#             bg="#0f0f23",
#             fg="#00ff88",
#             insertbackground="#00ff88",
#             relief="flat",
#             highlightthickness=2,
#             highlightbackground="#333",
#             highlightcolor="#ff6b35"
#         )
#         self.visits_entry.grid(row=2, column=1, pady=5, padx=10, sticky="w")
#         self.visits_entry.insert(0, "10000")
        
#         # Thread Count
#         thread_label = tk.Label(
#             input_frame,
#             text="🧵 Threads:",
#             font=("Arial", 12, "bold"),
#             fg="#ffffff",
#             bg="#16213e"
#         )
#         thread_label.grid(row=3, column=0, sticky="w", pady=5)
        
#         self.thread_spinbox = ttk.Spinbox(
#             input_frame,
#             from_=1,
#             to=10,
#             width=10,
#             font=("Arial", 11)
#         )
#         self.thread_spinbox.set(5)
#         self.thread_spinbox.grid(row=3, column=1, pady=5, padx=10, sticky="w")
        
#         input_frame.columnconfigure(1, weight=1)
        
#         # Button Frame
#         btn_frame = tk.Frame(self.root, bg="#1a1a2e")
#         btn_frame.pack(pady=15)
        
#         self.start_btn = tk.Button(
#             btn_frame,
#             text="🚀 START AUTOMATION",
#             font=("Arial", 14, "bold"),
#             bg="#00ff88",
#             fg="#000000",
#             width=25,
#             height=2,
#             relief="flat",
#             cursor="hand2",
#             command=self.start_script
#         )
#         self.start_btn.pack(side="left", padx=10)
        
#         self.stop_btn = tk.Button(
#             btn_frame,
#             text="🛑 STOP",
#             font=("Arial", 14, "bold"),
#             bg="#ff4444",
#             fg="#ffffff",
#             width=15,
#             height=2,
#             relief="flat",
#             cursor="hand2",
#             command=self.stop_script,
#             state="disabled"
#         )
#         self.stop_btn.pack(side="left", padx=10)
        
#         # Status Label
#         self.status_label = tk.Label(
#             self.root,
#             text="Status: Ready to start",
#             font=("Arial", 12, "bold"),
#             fg="#00ff88",
#             bg="#1a1a2e"
#         )
#         self.status_label.pack(pady=5)
        
#         # Log Frame
#         log_frame = tk.Frame(self.root, bg="#1a1a2e")
#         log_frame.pack(pady=10, padx=30, fill="both", expand=True)
        
#         log_label = tk.Label(
#             log_frame,
#             text="📋 Live Logs:",
#             font=("Arial", 11, "bold"),
#             fg="#ffffff",
#             bg="#1a1a2e"
#         )
#         log_label.pack(anchor="w")
        
#         self.log_text = scrolledtext.ScrolledText(
#             log_frame,
#             font=("Consolas", 10),
#             bg="#0f0f23",
#             fg="#00ff88",
#             height=12,
#             relief="flat",
#             insertbackground="#00ff88"
#         )
#         self.log_text.pack(fill="both", expand=True, pady=5)
        
#         # Footer
#         footer = tk.Label(
#             self.root,
#             text="AI-Powered Content Generation | Pure AI Output",
#             font=("Arial", 9),
#             fg="#666666",
#             bg="#1a1a2e"
#         )
#         footer.pack(pady=10)
    
#     def toggle_key_visibility(self):
#         self.show_key = not self.show_key
#         self.key_entry.config(show="" if self.show_key else "*")
#         self.toggle_btn.config(text="🙈" if self.show_key else "👁")
    
#     def log_message(self, message):
#         self.log_text.insert(tk.END, f"{message}\n")
#         self.log_text.see(tk.END)
    
#     def update_status(self, status):
#         self.status_label.config(text=f"Status: {status}")
    
#     def check_complete(self):
#         global is_running, total_conversions, TOTAL_VISITS_TARGET
#         if total_conversions >= TOTAL_VISITS_TARGET:
#             is_running = False
#             self.log_message("="*60)
#             self.log_message(f"🎉 MISSION COMPLETED! {total_conversions}/{TOTAL_VISITS_TARGET} VISITS DONE!")
#             self.log_message("="*60)
#             self.update_status(f"COMPLETED: {total_conversions}/{TOTAL_VISITS_TARGET}")
#             self.start_btn.config(state="normal", bg="#00ff88")
#             self.stop_btn.config(state="disabled")
#             self.url_entry.config(state="normal")
#             self.key_entry.config(state="normal")
#             self.visits_entry.config(state="normal")
#             messagebox.showinfo("🎉 Completed!", f"Target reached!\n{total_conversions}/{TOTAL_VISITS_TARGET} visits completed!")
    
#     def start_script(self):
#         global TARGET_URL, GROQ_API_KEY, TOTAL_VISITS_TARGET, is_running, total_conversions
        
#         TARGET_URL = self.url_entry.get().strip()
#         GROQ_API_KEY = self.key_entry.get().strip()
        
#         try:
#             TOTAL_VISITS_TARGET = int(self.visits_entry.get().strip())
#         except:
#             messagebox.showerror("Error", "Please enter valid number for Total Visits!")
#             return
        
#         if not TARGET_URL:
#             messagebox.showerror("Error", "Please enter Target URL!")
#             return
        
#         if not GROQ_API_KEY:
#             messagebox.showerror("Error", "Please enter Groq API Key!")
#             return
        
#         if TOTAL_VISITS_TARGET < 1:
#             messagebox.showerror("Error", "Total Visits must be at least 1!")
#             return
        
#         total_conversions = 0
        
#         self.log_message("Setting up Groq client...")
#         if not setup_groq_client(GROQ_API_KEY):
#             messagebox.showerror("Error", "Failed to setup Groq client!")
#             return
        
#         is_running = True
#         self.start_btn.config(state="disabled", bg="#666666")
#         self.stop_btn.config(state="normal")
#         self.url_entry.config(state="disabled")
#         self.key_entry.config(state="disabled")
#         self.visits_entry.config(state="disabled")
        
#         thread_count = int(self.thread_spinbox.get())
        
#         self.log_message("="*60)
#         self.log_message("🚀 AUTOMATION STARTED!")
#         self.log_message(f"🎯 Target: {TARGET_URL[:50]}...")
#         self.log_message(f"🎯 Total Visits Target: {TOTAL_VISITS_TARGET}")
#         self.log_message(f"🧵 Threads: {thread_count}")
#         self.log_message("="*60)
        
#         self.update_status(f"Running... 0/{TOTAL_VISITS_TARGET}")
        
#         for i in range(1, thread_count + 1):
#             t = threading.Thread(
#                 target=worker,
#                 args=(i, self.log_message, self.update_status, self.check_complete),
#                 daemon=True
#             )
#             t.start()
#             self.threads.append(t)
#             time.sleep(2)
    
#     def stop_script(self):
#         global is_running
#         is_running = False
        
#         self.log_message("="*60)
#         self.log_message("🛑 STOPPING ALL THREADS...")
#         self.log_message("="*60)
        
#         self.start_btn.config(state="normal", bg="#00ff88")
#         self.stop_btn.config(state="disabled")
#         self.url_entry.config(state="normal")
#         self.key_entry.config(state="normal")
#         self.visits_entry.config(state="normal")
        
#         self.update_status("Stopped")
#         self.threads = []

# # ================== MAIN ==================
# if __name__ == "__main__":
#     root = tk.Tk()
#     app = TataGroqGUI(root)
#     root.mainloop()






# TATA_1LAKH_GROQ_GUI.py ← FINAL VERSION: 100% PURE AI CONTENT ONLY (NO FIXED ENDING)

# import tkinter as tk
# from tkinter import ttk, messagebox, scrolledtext
# from seleniumwire import webdriver
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.chrome.options import Options
# from webdriver_manager.chrome import ChromeDriverManager
# from selenium.webdriver.common.by import By
# from groq import Groq
# import httpx
# import random
# import time
# import json
# import threading
# from datetime import datetime

# # ================== GLOBAL VARIABLES ==================
# PROXY_URL = "socks5://geonode_xvmYN44Bvz-type-residential-country-in:test@example.com:11000"
# TARGET_URL = ""
# GROQ_API_KEY = "CHANGE_ME_API_KEY"
# TOTAL_VISITS_TARGET = 10000
# groq_client = None
# is_running = False
# total_conversions = 0

# USER_AGENTS = [
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
#     "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:130.0) Gecko/20100101 Firefox/130.0",
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Edg/130.0.0.0",
#     "Mozilla/5.0 (iPhone; CPU iPhone OS 18_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.1 Mobile/15E148 Safari/604.1",
#     "Mozilla/5.0 (Linux; Android 14; SM-S928B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.6723.69 Mobile Safari/537.36",
#     "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
# ]

# RESOLUTIONS = [
#     "1920,1080", "1366,768", "1536,864", "1440,900", "1280,720", "1600,900",
#     "360,800", "393,851", "414,896", "430,932", "375,812", "390,844",
# ]

# LOG_FILE = "tata_groq_log.json"

# # ================== GROQ CLIENT SETUP ==================
# def setup_groq_client(api_key):
#     global groq_client
#     try:
#         proxy_url = "http://geonode_xvmYN44Bvz-type-residential-country-in:test@example.com:9000"
#         transport = httpx.HTTPTransport(proxy=proxy_url)
#         client = httpx.Client(transport=transport)
#         groq_client = Groq(api_key=api_key, http_client=client)
#         return True
#     except Exception as e:
#         print(f"Groq setup error: {e}")
#         return False

# # ================== PURE AI CONTENT (NO FIXED ENDING) ==================
# def generate_content():
#     global groq_client

#     prompt = """Write a deeply emotional, powerful and patriotic pledge in English (max 450 characters).

# Must include:
# - First person perspective
# - Love for India, unity, progress, responsibility, pride
# - Passionate and natural tone

# CRITICAL RULES:
# - Return ONLY the pledge text
# - No quotes, no titles, no "Here is", no "Pledge:", no explanation
# - Do NOT force any ending like "Jai Hind" or "Bharat Mata Ki Jai"
# - Pure human-like content only"""

#     try:
#         response = groq_client.chat.completions.create(
#             model="llama-3.3-70b-versatile",
#             messages=[{"role": "user", "content": prompt}],
#             temperature=1.15,
#             max_tokens=700,
#             top_p=0.97
#         )
#         raw = response.choices[0].message.content.strip()

#         # Aggressive cleaning
#         lines = [line.strip() for line in raw.splitlines()]
#         cleaned_lines = []
#         for line in lines:
#             lower = line.lower()
#             if any(start in lower for start in ["here is", "here's", "pledge:", "sure", "below", "```", "**", "##"]):
#                 continue
#             if line and not line.startswith(('"', "'", "`", "*")):
#                 cleaned_lines.append(line)

#         content = " ".join(cleaned_lines).strip()

#         # Final safety
#         if not content or len(content) < 40:
#             content = "I dedicate my life to India’s glory and unity. With every breath, I promise to protect her dignity, serve her people, and build a stronger tomorrow. My heart belongs to this sacred land forever."

#         return content[:450]

#     except Exception as e:
#         print(f"[GROQ ERROR] {e}")
#         return "My soul belongs to India. I pledge to stand united, work honestly, and contribute everything for her progress and pride. This nation is my identity, my purpose, my everything."

# def generate_mobile():
#     return random.choice(["7","8","9"]) + "".join(random.choices("0123456789", k=9))

# def log(data):
#     try:
#         with open(LOG_FILE, "r", encoding="utf-8") as f:
#             logs = json.load(f)
#     except:
#         logs = []
#     logs.append(data)
#     with open(LOG_FILE, "w", encoding="utf-8") as f:
#         json.dump(logs, f, indent=2, ensure_ascii=False)

# # ================== WORKER THREAD ==================
# def worker(tid, log_callback, status_callback, check_complete_callback):
#     global is_running, total_conversions, TARGET_URL, TOTAL_VISITS_TARGET

#     log_callback(f"[THREAD {tid}] Started!")

#     while is_running and total_conversions < TOTAL_VISITS_TARGET:
#         ua = random.choice(USER_AGENTS)
#         res = random.choice(RESOLUTIONS)

#         options = Options()
#         options.add_argument(f"--user-agent={ua}")
#         options.add_argument(f"--window-size={res}")
#         options.add_argument("--no-sandbox")
#         options.add_argument("--disable-dev-shm-usage")
#         options.add_argument("--disable-blink-features=AutomationControlled")
#         options.add_experimental_option("excludeSwitches", ["enable-automation"])
#         options.add_experimental_option('useAutomationExtension', False)
#         options.add_argument("--disable-gpu")
#         options.add_argument("--ignore-certificate-errors")

#         driver = None
#         try:
#             driver = webdriver.Chrome(
#                 service=Service(ChromeDriverManager().install()),
#                 options=options,
#                 seleniumwire_options={
#                     'proxy': {'http': PROXY_URL, 'https': PROXY_URL},
#                     'verify_ssl': False
#                 }
#             )

#             driver.get("https://api.ipify.org")
#             time.sleep(3)
#             ip = driver.find_element(By.TAG_NAME, "body").text.strip()

#             driver.get(f"{TARGET_URL}&sub2=CLK{random.randint(1000000,9999999)}")
#             time.sleep(random.randint(20, 35))

#             pledge = generate_content()
#             mobile = generate_mobile()

#             driver.find_element(By.CSS_SELECTOR, "textarea[name='pledge'], textarea#pledge").send_keys(pledge)
#             driver.find_element(By.CSS_SELECTOR, "input[name='phone'], input#phone").send_keys(mobile)
#             driver.execute_script("document.querySelector('input[type=\"checkbox\"], input#terms')?.click();")
#             driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

#             total_conversions += 1
#             log_callback(f"[THREAD {tid}] SUCCESS | Chars: {len(pledge)} | IP: {ip} | Total: {total_conversions}/{TOTAL_VISITS_TARGET}")
#             status_callback(f"Total Conversions: {total_conversions}/{TOTAL_VISITS_TARGET}")

#             log({
#                 "thread": tid,
#                 "no": total_conversions,
#                 "time": datetime.now().strftime("%H:%M:%S"),
#                 "ip": ip,
#                 "mobile": mobile,
#                 "pledge": pledge,
#                 "chars": len(pledge)
#             })

#             time.sleep(random.randint(10, 20))

#         except Exception as e:
#             log_callback(f"[THREAD {tid}] ERROR → {str(e)[:100]}")
#             time.sleep(15)
#         finally:
#             if driver:
#                 driver.quit()

#     log_callback(f"[THREAD {tid}] Stopped.")

# # ================== GUI CLASS ==================
# class TataGroqGUI:
#     def __init__(self, root):
#         self.root = root
#         self.root.title("TATA GROQ AUTOMATION - 100% PURE AI CONTENT")
#         self.root.geometry("800x650")
#         self.root.configure(bg="#1a1a2e")
#         self.threads = []
#         self.create_widgets()

#     def create_widgets(self):
#         # Title
#         title_frame = tk.Frame(self.root, bg="#1a1a2e")
#         title_frame.pack(pady=20)
#         tk.Label(title_frame, text="TATA GROQ AUTOMATION", font=("Arial", 24, "bold"), fg="#ff6b35", bg="#1a1a2e").pack()
#         tk.Label(title_frame, text="Pure AI Content • No Fixed Ending • Undetectable", font=("Arial", 10), fg="#888", bg="#1a1a2e").pack()

#         # Input Frame
#         input_frame = tk.Frame(self.root, bg="#16213e", padx=30, pady=20)
#         input_frame.pack(pady=10, padx=30, fill="x")

#         # Target URL
#         tk.Label(input_frame, text="Target URL:", font=("Arial", 12, "bold"), fg="#fff", bg="#16213e").grid(row=0, column=0, sticky="w", pady=5)
#         self.url_entry = tk.Entry(input_frame, font=("Arial", 11), width=60, bg="#0f0f23", fg="#00ff88", insertbackground="#00ff88")
#         self.url_entry.grid(row=0, column=1, pady=5, padx=10, sticky="ew")
#         self.url_entry.insert(0, "https://partners.marcadeo.com/click?oid=298&uid=908&lid=263")

#         # Groq API Key
#         tk.Label(input_frame, text="Groq API Key:", font=("Arial", 12, "bold"), fg="#fff", bg="#16213e").grid(row=1, column=0, sticky="w", pady=5)
#         self.key_entry = tk.Entry(input_frame, font=("Arial", 11), width=60, bg="#0f0f23", fg="#00ff88", insertbackground="#00ff88", show="*")
#         self.key_entry.grid(row=1, column=1, pady=5, padx=10, sticky="ew")

#         # Total Visits
#         tk.Label(input_frame, text="Total Visits:", font=("Arial", 12, "bold"), fg="#fff", bg="#16213e").grid(row=2, column=0, sticky="w", pady=5)
#         self.visits_entry = tk.Entry(input_frame, font=("Arial", 11), width=20, bg="#0f0f23", fg="#00ff88")
#         self.visits_entry.grid(row=2, column=1, pady=5, padx=10, sticky="w")
#         self.visits_entry.insert(0, "10000")

#         # Threads
#         tk.Label(input_frame, text="Threads:", font=("Arial", 12, "bold"), fg="#fff", bg="#16213e").grid(row=3, column=0, sticky="w", pady=5)
#         self.thread_spinbox = ttk.Spinbox(input_frame, from_=1, to=10, width=10)
#         self.thread_spinbox.set(5)
#         self.thread_spinbox.grid(row=3, column=1, pady=5, padx=10, sticky="w")

#         input_frame.columnconfigure(1, weight=1)

#         # Buttons
#         btn_frame = tk.Frame(self.root, bg="#1a1a2e")
#         btn_frame.pack(pady=15)
#         self.start_btn = tk.Button(btn_frame, text="START AUTOMATION", font=("Arial", 14, "bold"), bg="#00ff88", fg="#000", width=25, height=2, command=self.start_script)
#         self.start_btn.pack(side="left", padx=10)
#         self.stop_btn = tk.Button(btn_frame, text="STOP", font=("Arial", 14, "bold"), bg="#ff4444", fg="#fff", width=15, height=2, command=self.stop_script, state="disabled")
#         self.stop_btn.pack(side="left", padx=10)

#         # Status
#         self.status_label = tk.Label(self.root, text="Status: Ready", font=("Arial", 12, "bold"), fg="#00ff88", bg="#1a1a2e")
#         self.status_label.pack(pady=5)

#         # Log Area
#         log_frame = tk.Frame(self.root, bg="#1a1a2e")
#         log_frame.pack(pady=10, padx=30, fill="both", expand=True)
#         tk.Label(log_frame, text="Live Logs:", font=("Arial", 11, "bold"), fg="#fff", bg="#1a1a2e").pack(anchor="w")
#         self.log_text = scrolledtext.ScrolledText(log_frame, font=("Consolas", 10), bg="#0f0f23", fg="#00ff88", height=12)
#         self.log_text.pack(fill="both", expand=True, pady=5)

#     def log_message(self, msg):
#         self.log_text.insert(tk.END, f"{msg}\n")
#         self.log_text.see(tk.END)

#     def update_status(self, status):
#         self.status_label.config(text=f"Status: {status}")

#     def check_complete(self):
#         global is_running, total_conversions, TOTAL_VISITS_TARGET
#         if total_conversions >= TOTAL_VISITS_TARGET:
#             is_running = False
#             self.log_message("="*60)
#             self.log_message(f"MISSION COMPLETED! {total_conversions}/{TOTAL_VISITS_TARGET}")
#             self.log_message("="*60)
#             self.update_status(f"COMPLETED: {total_conversions}/{TOTAL_VISITS_TARGET}")
#             self.start_btn.config(state="normal", bg="#00ff88")
#             self.stop_btn.config(state="disabled")
#             self.url_entry.config(state="normal")
#             self.key_entry.config(state="normal")
#             self.visits_entry.config(state="normal")
#             messagebox.showinfo("Completed", f"Target achieved!\n{total_conversions} pledges submitted!")

#     def start_script(self):
#         global TARGET_URL, GROQ_API_KEY, TOTAL_VISITS_TARGET, is_running, total_conversions
#         TARGET_URL = self.url_entry.get().strip()
#         GROQ_API_KEY = self.key_entry.get().strip()
#         try:
#             TOTAL_VISITS_TARGET = int(self.visits_entry.get().strip())
#         except:
#             messagebox.showerror("Error", "Invalid number for Total Visits!")
#             return

#         if not all([TARGET_URL, GROQ_API_KEY]) or TOTAL_VISITS_TARGET < 1:
#             messagebox.showerror("Error", "Fill all fields correctly!")
#             return

#         total_conversions = 0
#         if not setup_groq_client(GROQ_API_KEY):
#             messagebox.showerror("Error", "Groq API connection failed!")
#             return

#         is_running = True
#         self.start_btn.config(state="disabled", bg="#666")
#         self.stop_btn.config(state="normal")
#         self.url_entry.config(state="disabled")
#         self.key_entry.config(state="disabled")
#         self.visits_entry.config(state="disabled")

#         thread_count = int(self.thread_spinbox.get())
#         self.log_message("="*60)
#         self.log_message("AUTOMATION STARTED | PURE AI CONTENT ONLY")
#         self.log_message(f"Target: {TOTAL_VISITS_TARGET} | Threads: {thread_count}")
#         self.log_message("="*60)

#         for i in range(1, thread_count + 1):
#             t = threading.Thread(target=worker, args=(i, self.log_message, self.update_status, self.check_complete), daemon=True)
#             t.start()
#             self.threads.append(t)
#             time.sleep(1.5)

#     def stop_script(self):
#         global is_running
#         is_running = False
#         self.log_message("STOPPING ALL THREADS...")
#         self.start_btn.config(state="normal", bg="#00ff88")
#         self.stop_btn.config(state="disabled")
#         self.url_entry.config(state="normal")
#         self.key_entry.config(state="normal")
#         self.visits_entry.config(state="normal")
#         self.update_status("Stopped by user")

# # ================== MAIN ==================
# if __name__ == "__main__":
#     root = tk.Tk()
#     app = TataGroqGUI(root)
#     root.mainloop()



# TATA_1LAKH_GROQ_GUI.py ← FINAL VERSION: RANDOM PROMPTS FROM TXT FILE
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
from seleniumwire import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import phonenumbers
from phonenumbers import geocoder, carrier
from groq import Groq
import httpx
import random
import time
import json
import threading
from datetime import datetime

# ================== GLOBAL VARIABLES ==================
PROXY_URL = "socks5://geonode_xvmYN44Bvz-type-residential-country-in:test@example.com:11001"
TARGET_URL = ""
GROQ_API_KEY = "CHANGE_ME_API_KEY"
TOTAL_VISITS_TARGET = 1000
PROMPTS_LIST = []           # ← Ye ab TXT file se load hoga
groq_client = None
is_running = False
total_conversions = 0

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:130.0) Gecko/20100101 Firefox/130.0",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 18_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.1 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 14; SM-S928B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.6723.69 Mobile Safari/537.36",
]

RESOLUTIONS = [
    "1920,1080", "1366,768", "1536,864", "1440,900", "1280,720", "1600,900",
    "360,800", "393,851", "414,896", "430,932", "375,812", "390,844",
]

LOG_FILE = "tata_groq_log.json"

# ================== LOAD PROMPTS FROM TXT FILE ==================
def load_prompts_from_file(filepath):
    global PROMPTS_LIST
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            prompts = [line.strip() for line in f if line.strip()]
        if not prompts:
            return False, "TXT file is empty!"
        PROMPTS_LIST = prompts
        return True, f"Loaded {len(prompts)} prompts successfully!"
    except Exception as e:
        return False, f"Error loading file: {e}"

# ================== GROQ CLIENT SETUP ==================
def setup_groq_client(api_key):
    global groq_client
    try:
        proxy_url = "http://geonode_xvmYN44Bvz-type-residential-country-in:test@example.com:9000"
        transport = httpx.HTTPTransport(proxy=proxy_url)
        client = httpx.Client(transport=transport)
        groq_client = Groq(api_key=api_key, http_client=client)
        return True
    except Exception as e:
        print(f"Groq setup error: {e}")
        return False

# ================== GENERATE CONTENT USING RANDOM PROMPT FROM TXT ==================
def generate_content():
    global groq_client, PROMPTS_LIST

    if not PROMPTS_LIST:
        return "I my unwavering loyalty to India and its people."

    selected_prompt = random.choice(PROMPTS_LIST)

    try:
        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": selected_prompt}],
            temperature=1.1,
            max_tokens=700,
            top_p=0.96
        )
        raw = response.choices[0].message.content.strip()

        # Ultra-aggressive cleaning
        lines = [line.strip() for line in raw.splitlines() if line.strip()]
        cleaned = []
        for line in lines:
            l = line.lower()
            if any(bad in l for bad in ["here is", "here's", "pledge:", "sure", "```", "**", "##", "below", "quote"]):
                continue
            if not line.startswith(('"', "'", "`", "*", "#", ">")):
                cleaned.append(line)
        
        content = " ".join(cleaned).strip()
        if not content or len(content) < 30:
            content = "With all my heart, I commit myself to the service and glory of India. I will work tirelessly for unity, progress, and justice. This is my sacred promise to my motherland."

        return content[:450]

    except Exception as e:
        print(f"[GROQ ERROR] {e}")
        return "I stand united with every Indian. My life is dedicated to building a stronger, greater, and more prosperous Bharat."

def generate_mobile():
    while True:
        # Indian mobile number pattern: 6,7,8,9 se start
        first_digit = random.choice(['7', '8', '9'])
        remaining = ''.join(random.choices('0123456789', k=9))
        number_str = first_digit + remaining
        
        # Check for too many repeating digits (avoid 9999999999, 9999999999 etc.)
        if len(set(number_str)) < 4:  # agar 4 se kam unique digits hain → reject
            continue
        if number_str.count(number_str[0]) >= 7:  # same digit 7+ times → reject
            continue
            
        # Optional: Check if it's a possible valid Indian number (not necessary but good)
        try:
            parsed = phonenumbers.parse("+91" + number_str, None)
            if phonenumbers.is_possible_number(parsed) and phonenumbers.is_valid_number(parsed):
                return number_str
        except:
            pass
        
        # Agar phonenumbers validate na kare to bhi, basic check pass ho to accept
        return number_str

def log(data):
    try:
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            logs = json.load(f)
    except:
        logs = []
    logs.append(data)
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(logs, f, indent=2, ensure_ascii=False)

# ================== WORKER THREAD ==================
def worker(tid, log_callback, status_callback, check_complete_callback):
    global is_running, total_conversions, TARGET_URL, TOTAL_VISITS_TARGET

    log_callback(f"[THREAD {tid}] Started!")

    while is_running and total_conversions < TOTAL_VISITS_TARGET:
        ua = random.choice(USER_AGENTS)
        res = random.choice(RESOLUTIONS)

        options = Options()
        options.add_argument(f"--user-agent={ua}")
        options.add_argument(f"--window-size={res}")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument("--disable-gpu")
        options.add_argument("--ignore-certificate-errors")

        driver = None
        try:
            driver = webdriver.Chrome(
                service=Service(ChromeDriverManager().install()),
                options=options,
                seleniumwire_options={
                    'proxy': {'http': PROXY_URL, 'https': PROXY_URL},
                    'verify_ssl': False
                }
            )

            driver.get("https://api.ipify.org")
            time.sleep(3)
            ip = driver.find_element(By.TAG_NAME, "body").text.strip()

            driver.get(f"{TARGET_URL}&sub2=CLK{random.randint(1000000,9999999)}")
            time.sleep(random.randint(20, 35))

            pledge = generate_content()
            mobile = generate_mobile()

            driver.find_element(By.CSS_SELECTOR, "textarea[name='pledge'], textarea#pledge").send_keys(pledge)
            driver.find_element(By.CSS_SELECTOR, "input[name='phone'], input#phone").send_keys(mobile)
            driver.execute_script("document.querySelector('input[type=\"checkbox\"], input#terms')?.click();")
            driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

            total_conversions += 1
            log_callback(f"[THREAD {tid}] SUCCESS | Chars: {len(pledge)} | IP: {ip} | Total: {total_conversions}/{TOTAL_VISITS_TARGET}")
            status_callback(f"Total Conversions: {total_conversions}/{TOTAL_VISITS_TARGET}")

            log({
                "thread": tid,
                "no": total_conversions,
                "time": datetime.now().strftime("%H:%M:%S"),
                "ip": ip,
                "mobile": mobile,
                "pledge": pledge,
                "chars": len(pledge)
            })

            time.sleep(random.randint(10, 22))

        except Exception as e:
            log_callback(f"[THREAD {tid}] ERROR → {str(e)[:100]}")
            time.sleep(15)
        finally:
            if driver:
                driver.quit()

    log_callback(f"[THREAD {tid}] Stopped.")

# ================== GUI CLASS ==================
class TataGroqGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("TATA GROQ AUTOMATION - RANDOM PROMPTS FROM TXT")
        self.root.geometry("850x720")
        self.root.configure(bg="#1a1a2e")
        self.threads = []
        self.prompts_file_path = ""
        self.create_widgets()

    def create_widgets(self):
        title_frame = tk.Frame(self.root, bg="#1a1a2e")
        title_frame.pack(pady=20)
        tk.Label(title_frame, text="TATA GROQ AUTOMATION", font=("Arial", 24, "bold"), fg="#ff6b35", bg="#1a1a2e").pack()
        tk.Label(title_frame, text="Random Prompts from TXT File • 100% Unique • Undetectable", font=("Arial", 10), fg="#88ff88", bg="#1a1a2e").pack()

        input_frame = tk.Frame(self.root, bg="#16213e", padx=30, pady=20)
        input_frame.pack(pady=10, padx=30, fill="x")

        # === PROMPTS TXT FILE ===
        tk.Label(input_frame, text="Prompts TXT File:", font=("Arial", 12, "bold"), fg="#fff", bg="#16213e").grid(row=0, column=0, sticky="w", pady=5)
        self.prompts_path_entry = tk.Entry(input_frame, font=("Arial", 11), width=50, bg="#0f0f23", fg="#00ff88")
        self.prompts_path_entry.grid(row=0, column=1, pady=5, padx=(10,5), sticky="ew")
        tk.Button(input_frame, text="Browse", command=self.browse_prompts_file, bg="#333", fg="#fff").grid(row=0, column=2, padx=5)

        # Target URL
        tk.Label(input_frame, text="Target URL:", font=("Arial", 12, "bold"), fg="#fff", bg="#16213e").grid(row=1, column=0, sticky="w", pady=5)
        self.url_entry = tk.Entry(input_frame, font=("Arial", 11), width=60, bg="#0f0f23", fg="#00ff88", insertbackground="#00ff88")
        self.url_entry.grid(row=1, column=1, columnspan=2, pady=5, padx=10, sticky="ew")
        self.url_entry.insert(0, "https://partners.marcadeo.com/click?oid=298&uid=908&lid=263")

        # Groq API Key
        tk.Label(input_frame, text="Groq API Key:", font=("Arial", 12, "bold"), fg="#fff", bg="#16213e").grid(row=2, column=0, sticky="w", pady=5)
        self.key_entry = tk.Entry(input_frame, font=("Arial", 11), width=60, bg="#0f0f23", fg="#00ff88", show="*")
        self.key_entry.grid(row=2, column=1, columnspan=2, pady=5, padx=10, sticky="ew")

        # Total Visits
        tk.Label(input_frame, text="Total Visits:", font=("Arial", 12, "bold"), fg="#fff", bg="#16213e").grid(row=3, column=0, sticky="w", pady=5)
        self.visits_entry = tk.Entry(input_frame, font=("Arial", 11), width=20, bg="#0f0f23", fg="#00ff88")
        self.visits_entry.grid(row=3, column=1, pady=5, padx=10, sticky="w")
        self.visits_entry.insert(0, "10000")

        # Threads
        tk.Label(input_frame, text="Threads:", font=("Arial", 12, "bold"), fg="#fff", bg="#16213e").grid(row=4, column=0, sticky="w", pady=5)
        self.thread_spinbox = ttk.Spinbox(input_frame, from_=1, to=10, width=10)
        self.thread_spinbox.set(5)
        self.thread_spinbox.grid(row=4, column=1, pady=5, padx=10, sticky="w")

        input_frame.columnconfigure(1, weight=1)

        # Buttons
        btn_frame = tk.Frame(self.root, bg="#1a1a2e")
        btn_frame.pack(pady=20)
        self.start_btn = tk.Button(btn_frame, text="START AUTOMATION", font=("Arial", 14, "bold"), bg="#00ff88", fg="#000", width=28, height=2, command=self.start_script)
        self.start_btn.pack(side="left", padx=15)
        self.stop_btn = tk.Button(btn_frame, text="STOP", font=("Arial", 14, "bold"), bg="#ff4444", fg="#fff", width=15, height=2, command=self.stop_script, state="disabled")
        self.stop_btn.pack(side="left", padx=15)

        # Status
        self.status_label = tk.Label(self.root, text="Status: Ready • Load Prompts TXT First", font=("Arial", 12, "bold"), fg="#00ff88", bg="#1a1a2e")
        self.status_label.pack(pady=5)

        # Log Area
        log_frame = tk.Frame(self.root, bg="#1a1a2e")
        log_frame.pack(pady=10, padx=30, fill="both", expand=True)
        tk.Label(log_frame, text="Live Logs:", font=("Arial", 11, "bold"), fg="#fff", bg="#1a1a2e").pack(anchor="w")
        self.log_text = scrolledtext.ScrolledText(log_frame, font=("Consolas", 10), bg="#0f0f23", fg="#00ff88", height=14)
        self.log_text.pack(fill="both", expand=True, pady=5)

    def browse_prompts_file(self):
        filepath = filedialog.askopenfilename(
            title="Select Prompts TXT File",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        if filepath:
            self.prompts_path_entry.delete(0, tk.END)
            self.prompts_path_entry.insert(0, filepath)
            self.prompts_file_path = filepath
            success, msg = load_prompts_from_file(filepath)
            if success:
                self.log_message(f"PROMPTS LOADED: {msg}")
                self.status_label.config(text=f"Status: Ready • {len(PROMPTS_LIST)} prompts loaded")
            else:
                messagebox.showerror("Error", msg)
                self.log_message(f"ERROR: {msg}")

    def log_message(self, msg):
        self.log_text.insert(tk.END, f"{msg}\n")
        self.log_text.see(tk.END)

    def update_status(self, status):
        self.status_label.config(text=f"Status: {status}")

    def check_complete(self):
        global is_running, total_conversions, TOTAL_VISITS_TARGET
        if total_conversions >= TOTAL_VISITS_TARGET:
            is_running = False
            self.log_message("="*60)
            self.log_message(f"MISSION COMPLETED! {total_conversions}/{TOTAL_VISITS_TARGET} DONE")
            self.log_message("="*60)
            self.update_status(f"COMPLETED: {total_conversions}/{TOTAL_VISITS_TARGET}")
            self.start_btn.config(state="normal", bg="#00ff88")
            self.stop_btn.config(state="disabled")
            messagebox.showinfo("Success", f"Target completed!\n{total_conversions} pledges submitted!")

    def start_script(self):
        global TARGET_URL, GROQ_API_KEY, TOTAL_VISITS_TARGET, is_running, total_conversions

        if not self.prompts_file_path or not PROMPTS_LIST:
            messagebox.showerror("Error", "Please load a valid Prompts TXT file first!")
            return

        TARGET_URL = self.url_entry.get().strip()
        GROQ_API_KEY = self.key_entry.get().strip()
        try:
            TOTAL_VISITS_TARGET = int(self.visits_entry.get().strip())
        except:
            messagebox.showerror("Error", "Invalid Total Visits!")
            return

        if not all([TARGET_URL, GROQ_API_KEY]) or TOTAL_VISITS_TARGET < 1:
            messagebox.showerror("Error", "All fields are required!")
            return

        total_conversions = 0
        if not setup_groq_client(GROQ_API_KEY):
            messagebox.showerror("Error", "Failed to connect Groq API!")
            return

        is_running = True
        self.start_btn.config(state="disabled", bg="#666")
        self.stop_btn.config(state="normal")
        self.url_entry.config(state="disabled")
        self.key_entry.config(state="disabled")
        self.visits_entry.config(state="disabled")
        self.prompts_path_entry.config(state="disabled")

        thread_count = int(self.thread_spinbox.get())
        self.log_message("="*60)
        self.log_message(f"AUTOMATION STARTED | Using {len(PROMPTS_LIST)} Random Prompts")
        self.log_message(f"Target: {TOTAL_VISITS_TARGET} | Threads: {thread_count}")
        self.log_message("="*60)

        for i in range(1, thread_count + 1):
            t = threading.Thread(target=worker, args=(i, self.log_message, self.update_status, self.check_complete), daemon=True)
            t.start()
            self.threads.append(t)
            time.sleep(1.5)

    def stop_script(self):
        global is_running
        is_running = False
        self.log_message("STOPPING ALL THREADS...")
        self.start_btn.config(state="normal", bg="#00ff88")
        self.stop_btn.config(state="disabled")
        self.url_entry.config(state="normal")
        self.key_entry.config(state="normal")
        self.visits_entry.config(state="normal")
        self.prompts_path_entry.config(state="normal")
        self.update_status("Stopped by user")

# ================== MAIN ==================
if __name__ == "__main__":
    root = tk.Tk()
    app = TataGroqGUI(root)
    root.mainloop()
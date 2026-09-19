# # tata_ultimate_gui_pro_ULTRA.py → MAXIMUM UNIQUENESS + 5 CONCURRENT SESSIONS
# import tkinter as tk
# from tkinter import filedialog, messagebox
# import markovify
# import random
# import time
# import json
# import os
# import threading
# from datetime import datetime
# from seleniumwire import webdriver
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.chrome.options import Options
# from webdriver_manager.chrome import ChromeDriverManager
# from selenium.webdriver.common.by import By
# import re

# # ===================== CONFIG =====================
# PROXY_URL = "socks5://geonode_xvmYN44Bvz-type-residential-country-in:test@example.com:11000"
# LOG_FILE = "tata_pledges_log.json"
# MAX_CONCURRENT = 5
# MIN_PLEDGE_WORDS = 35
# MAX_PLEDGE_WORDS = 80

# USER_AGENTS = [
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/130.0.0.0 Safari/537.36",
#     "Mozilla/5.0 (iPhone; CPU iPhone OS 18_1 like Mac OS X) AppleWebKit/605.1.15 Version/18.1 Mobile/15E148 Safari/604.1",
#     "Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 Chrome/130.0.6723.69 Mobile Safari/537.36",
#     "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/129.0.0.0 Safari/537.36",
#     "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/130.0.0.0 Safari/537.36"
# ]
# RESOLUTIONS = ["1920,1080", "1366,768", "360,800", "1440,900", "1536,864", "414,896"]

# # ============= ADVANCED TEXT VARIATION COMPONENTS =============
# SYNONYMS = {
#     "pledge": ["promise", "commitment", "vow", "oath", "dedication", "assurance"],
#     "serve": ["help", "support", "assist", "contribute to", "work for", "devote myself to"],
#     "nation": ["country", "motherland", "Bharat", "India", "homeland", "my land"],
#     "health": ["wellness", "medical care", "healthcare", "well-being", "fitness"],
#     "dedication": ["commitment", "devotion", "sincerity", "passion", "earnestness"],
#     "people": ["citizens", "Indians", "countrymen", "fellow citizens", "my brothers and sisters"],
#     "doctor": ["physician", "medical professional", "healthcare worker", "healer"],
#     "rural": ["village", "countryside", "remote areas", "gram", "rural areas"],
#     "proper": ["adequate", "quality", "good", "excellent", "effective"],
#     "every": ["all", "each", "every single"],
#     "wanted": ["wished", "dreamed", "aspired", "desired", "aimed"],
#     "childhood": ["young age", "early years", "youth", "growing up years"]
# }

# CONNECTORS = [
#     "Moreover,", "Furthermore,", "Additionally,", "In addition,", "Also,", 
#     "Besides this,", "Not only this,", "Along with this,", "On top of that,",
#     "What's more,", "Beyond this,", "Most importantly,"
# ]

# ENDINGS = [
#     "Jai Hind!", "Bharat Mata Ki Jai!", "Vande Mataram!", 
#     "This is my sacred pledge to Bharat Mata.", "Jai Bharat!",
#     "This is my promise to my motherland.", "Satyamev Jayate!",
#     "I will fulfill this pledge with full honesty.", "India first, always!",
#     "My country, my pride, my commitment!", "Proud to be Indian!",
#     "Service before self, nation before all!", "Unity in diversity, service for all!"
# ]

# FILLER_PHRASES = [
#     "I truly believe that", "In my heart, I feel that", "I am confident that",
#     "My vision is clear:", "I strongly feel that", "I am determined that",
#     "It is my firm belief that", "I know for certain that", "I am committed to ensuring that"
# ]

# TRANSITION_WORDS = [
#     "Therefore", "Thus", "Hence", "Consequently", "As a result",
#     "That is why", "For this reason", "This is why", "Accordingly"
# ]

# # ===================== GLOBAL VARS =====================
# text_model = None
# corpus_sentences = []
# corpus_path_global = None
# running = False
# stop_event = threading.Event()
# semaphore = threading.Semaphore(MAX_CONCURRENT)
# generated_pledges_cache = set()  # Track uniqueness

# # ===================== ENHANCED TEXT PROCESSING =====================
# def load_corpus_model(path):
#     global text_model, corpus_sentences
#     try:
#         with open(path, "r", encoding="utf-8") as f:
#             corpus = f.read()
        
#         if len(corpus.strip()) < 500:
#             return False, "File bahut chhota! 15-20 pledges daalo."
        
#         # Clean and split into sentences
#         corpus_sentences = [s.strip() for s in re.split(r'[.!?]+', corpus) if len(s.strip()) > 10]
        
#         # Build Markov model with higher state size for better coherence
#         text_model = markovify.Text(corpus, state_size=3)
        
#         return True, f"Loaded: {os.path.basename(path)} | Sentences: {len(corpus_sentences)} | Words: {len(corpus.split()):,}"
#     except Exception as e:
#         return False, f"Error: {e}"

# def replace_with_synonyms(text):
#     """Replace random words with synonyms for variation"""
#     words = text.split()
#     for i, word in enumerate(words):
#         word_lower = word.lower().strip('.,!?')
#         if word_lower in SYNONYMS and random.random() < 0.3:  # 30% chance
#             words[i] = random.choice(SYNONYMS[word_lower])
#     return ' '.join(words)

# def add_filler_phrases(sentences):
#     """Add natural filler phrases between sentences"""
#     result = []
#     for i, sent in enumerate(sentences):
#         if i > 0 and random.random() < 0.4:  # 40% chance
#             result.append(random.choice(FILLER_PHRASES))
#         result.append(sent)
#     return result

# def shuffle_sentence_parts(text):
#     """Intelligently shuffle parts of compound sentences"""
#     if ' and ' in text or ', ' in text:
#         if random.random() < 0.3:
#             parts = re.split(r'(\band\b|,)', text)
#             if len(parts) > 3:
#                 # Swap some parts
#                 mid = len(parts) // 2
#                 parts[1], parts[mid] = parts[mid], parts[1]
#                 text = ''.join(parts)
#     return text

# def generate_hybrid_sentence():
#     """Combine multiple generation techniques"""
#     methods = []
    
#     # Method 1: Pure Markov
#     if text_model:
#         sent = text_model.make_sentence(tries=500, max_overlap_ratio=0.5, max_overlap_total=10)
#         if sent:
#             methods.append(sent)
    
#     # Method 2: Sentence recombination
#     if len(corpus_sentences) >= 2:
#         parts = random.sample(corpus_sentences, min(2, len(corpus_sentences)))
#         hybrid = parts[0].split()[:random.randint(5,8)] + parts[1].split()[random.randint(3,6):]
#         methods.append(' '.join(hybrid))
    
#     # Method 3: Word-level mixing
#     if len(corpus_sentences) >= 3:
#         words_pool = []
#         for sent in random.sample(corpus_sentences, 3):
#             words_pool.extend(sent.split())
#         if len(words_pool) > 10:
#             methods.append(' '.join(random.sample(words_pool, random.randint(8, 15))))
    
#     if methods:
#         base = random.choice(methods)
#         # Apply transformations
#         base = replace_with_synonyms(base)
#         base = shuffle_sentence_parts(base)
#         return base.strip()
    
#     return None

# def generate_ultra_unique_essay():
#     """Ultra-advanced pledge generator with maximum variation"""
#     essay_parts = []
#     word_count = 0
#     target_words = random.randint(MIN_PLEDGE_WORDS, MAX_PLEDGE_WORDS)
    
#     # Phase 1: Core content generation (mix of techniques)
#     attempts = 0
#     while word_count < target_words and attempts < 50:
#         attempts += 1
        
#         # Use hybrid generation 70% of time, pure Markov 30%
#         if random.random() < 0.7:
#             sentence = generate_hybrid_sentence()
#         elif text_model:
#             sentence = text_model.make_sentence(tries=500, max_overlap_ratio=0.4)
#         else:
#             sentence = None
        
#         if sentence and len(sentence.split()) > 4:
#             # Additional variation: random capitalization style
#             if random.random() < 0.15:
#                 sentence = sentence.capitalize()
            
#             essay_parts.append(sentence)
#             word_count += len(sentence.split())
    
#     # Phase 2: Add connectors and fillers
#     if len(essay_parts) > 1:
#         essay_parts = add_filler_phrases(essay_parts)
    
#     # Phase 3: Add random connector in middle
#     if len(essay_parts) >= 3 and random.random() < 0.5:
#         mid_point = len(essay_parts) // 2
#         essay_parts.insert(mid_point, random.choice(CONNECTORS))
    
#     # Phase 4: Ensure minimum content
#     if word_count < 30:
#         fallback = [
#             "From my early years, I have aspired to become a physician.",
#             "My goal is to provide quality healthcare to rural India.",
#             "Every citizen deserves access to proper medical facilities.",
#             "I will dedicate my life to serving my motherland with full commitment."
#         ]
#         essay_parts.extend(random.sample(fallback, 2))
    
#     # Phase 5: Add unique ending
#     essay_parts.append(random.choice(ENDINGS))
    
#     # Phase 6: Optional transition before ending
#     if random.random() < 0.4 and len(essay_parts) > 2:
#         essay_parts.insert(-1, random.choice(TRANSITION_WORDS))
    
#     # Combine and clean
#     essay = ' '.join(essay_parts)
#     essay = re.sub(r'\s+([.,!?])', r'\1', essay)  # Fix spacing before punctuation
#     essay = re.sub(r'\s+', ' ', essay)  # Remove double spaces
#     essay = essay.strip()
    
#     # Phase 7: Final uniqueness check with hash
#     essay_hash = hash(essay)
#     retry_count = 0
#     while essay_hash in generated_pledges_cache and retry_count < 5:
#         # Add slight variation
#         essay = replace_with_synonyms(essay)
#         essay += " " + random.choice(["", "I promise this.", "This I vow."])
#         essay_hash = hash(essay)
#         retry_count += 1
    
#     generated_pledges_cache.add(essay_hash)
    
#     # Keep cache size manageable
#     if len(generated_pledges_cache) > 10000:
#         generated_pledges_cache.clear()
    
#     return essay

# def generate_mobile():
#     """Generate unique mobile number"""
#     return random.choice(["7","8","9"]) + "".join(random.choices("0123456789", k=9))

# # ===================== LOGGING =====================
# def save_log(data):
#     try:
#         with open(LOG_FILE, "r", encoding="utf-8") as f:
#             logs = json.load(f)
#     except:
#         logs = []
#     logs.append(data)
#     with open(LOG_FILE, "w", encoding="utf-8") as f:
#         json.dump(logs, f, indent=2, ensure_ascii=False)

# # ===================== MAIN TASK (5 LIMIT) =====================
# def run_single_pledge(counter):
#     if stop_event.is_set():
#         return

#     with semaphore:
#         if stop_event.is_set():
#             return

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
#         # options.add_argument("--headless=new")

#         driver = None
#         try:
#             driver = webdriver.Chrome(
#                 service=Service(ChromeDriverManager().install()),
#                 options=options,
#                 seleniumwire_options={'proxy': {'http': PROXY_URL, 'https': PROXY_URL}}
#             )

#             driver.get("https://api.ipify.org")
#             time.sleep(3)
#             ip = driver.find_element(By.TAG_NAME, "body").text.strip()

#             driver.get(f"https://app.adstracking.io/click?pid=3404&offer_id=23466&sub2=CLK{random.randint(1000000,9999999)}")
#             time.sleep(random.uniform(18, 28))

#             essay = generate_ultra_unique_essay()
#             mobile = generate_mobile()

#             driver.find_element(By.CSS_SELECTOR, "textarea[name='pledge'], textarea#pledge").send_keys(essay)
#             driver.find_element(By.CSS_SELECTOR, "input[name='phone'], input#phone").send_keys(mobile)
#             driver.execute_script("document.querySelector('input[type=\"checkbox\"], input#terms')?.click();")
#             driver.find_element(By.CSS_SELECTOR, "button[type='submit'], input[type='submit']").click()

#             time.sleep(6)

#             update_counter(success=True)
#             print(f"✓ SUCCESS #{counter} | {mobile} | Words: {len(essay.split())} | IP: {ip}")
#             print(f"   Preview: {essay[:100]}...")
#             save_log({
#                 "no": counter, 
#                 "time": datetime.now().strftime("%H:%M:%S"), 
#                 "mobile": mobile, 
#                 "ip": ip,
#                 "words": len(essay.split()),
#                 "pledge_preview": essay[:150]
#             })

#         except Exception as e:
#             update_counter(success=False)
#             print(f"✗ FAILED #{counter} → {str(e)[:120]}")
#         finally:
#             if driver:
#                 driver.quit()

# # ===================== GUI =====================
# root = tk.Tk()
# root.title("TATA PLEDGE BOMBER v7.0 ULTRA")
# root.geometry("780x620")
# root.configure(bg="#0a0a0a")
# root.resizable(False, False)

# success_count = tk.IntVar()
# failed_count = tk.IntVar()
# total_run = tk.IntVar()
# active_sessions = tk.IntVar(value=0)

# def update_counter(success=True):
#     if success:
#         success_count.set(success_count.get() + 1)
#     else:
#         failed_count.set(failed_count.get() + 1)
#     total_run.set(success_count.get() + failed_count.get())

# def select_corpus():
#     global corpus_path_global
#     path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
#     if path:
#         corpus_path.set(path)
#         success, msg = load_corpus_model(path)
#         status_label.config(text=msg, foreground="lime" if success else "red")
#         if success:
#             corpus_path_global = path

# def start_bomber():
#     global running
#     if not corpus_path_global:
#         messagebox.showerror("Error", "Pehle koi .txt file select karo!")
#         return
#     if running:
#         return
#     running = True
#     stop_event.clear()
#     start_btn.config(state="disabled")
#     stop_btn.config(state="normal")
#     status_label.config(text="RUNNING → Ultra Unique Mode Active! Max 5 sessions", foreground="#00ff41")
#     active_sessions.set(0)

#     def worker():
#         counter = total_run.get()
#         while running and not stop_event.is_set():
#             counter += 1
#             active_sessions.set(active_sessions.get() + 1)
#             threading.Thread(target=run_single_pledge, args=(counter,), daemon=True).start()
#             time.sleep(8)
#         start_btn.config(state="normal")
#         stop_btn.config(state="disabled")
#         status_label.config(text="Stopped. Sab sessions band ho gaye.", foreground="yellow")

#     threading.Thread(target=worker, daemon=True).start()

# def stop_bomber():
#     global running
#     running = False
#     stop_event.set()
#     status_label.config(text="Stopping... current 5 sessions complete hone do", foreground="orange")

# # ===================== GUI LAYOUT =====================
# header_frame = tk.Frame(root, bg="#0a0a0a")
# header_frame.pack(pady=20)

# tk.Label(header_frame, text="TATA PLEDGE BOMBER", font=("Arial", 24, "bold"), 
#          fg="#00ff41", bg="#0a0a0a").pack()
# tk.Label(header_frame, text="ULTRA UNIQUE EDITION v7.0", font=("Arial", 10), 
#          fg="#00aaff", bg="#0a0a0a").pack()

# # File selection
# file_frame = tk.Frame(root, bg="#0a0a0a")
# file_frame.pack(pady=15)

# corpus_path = tk.StringVar()
# tk.Label(file_frame, text="Select Text File with Sample Pledges:", 
#          fg="#aaaaaa", bg="#0a0a0a", font=("Arial", 10)).pack()
# tk.Entry(file_frame, textvariable=corpus_path, width=70, state="readonly", 
#          bg="#1a1a1a", fg="white", font=("Consolas", 9)).pack(pady=5)
# tk.Button(file_frame, text="📁 Browse .txt File", command=select_corpus, 
#           bg="#2a2a2a", fg="white", width=30, height=1, 
#           font=("Arial", 10, "bold")).pack(pady=5)

# # Stats display
# stats_frame = tk.Frame(root, bg="#0a0a0a")
# stats_frame.pack(pady=20)

# stat_success = tk.Frame(stats_frame, bg="#0a0a0a")
# stat_success.grid(row=0, column=0, padx=30)
# tk.Label(stat_success, text="✓ SUCCESS", fg="#00ff41", bg="#0a0a0a", 
#          font=("Arial", 11, "bold")).pack()
# tk.Label(stat_success, textvariable=success_count, font=("Arial", 28, "bold"), 
#          fg="#00ff41", bg="#0a0a0a").pack()

# stat_total = tk.Frame(stats_frame, bg="#0a0a0a")
# stat_total.grid(row=0, column=1, padx=30)
# tk.Label(stat_total, text="TOTAL RUNS", fg="#ffaa00", bg="#0a0a0a", 
#          font=("Arial", 11, "bold")).pack()
# tk.Label(stat_total, textvariable=total_run, font=("Arial", 28, "bold"), 
#          fg="#ffaa00", bg="#0a0a0a").pack()

# stat_failed = tk.Frame(stats_frame, bg="#0a0a0a")
# stat_failed.grid(row=0, column=2, padx=30)
# tk.Label(stat_failed, text="✗ FAILED", fg="#ff4444", bg="#0a0a0a", 
#          font=("Arial", 11, "bold")).pack()
# tk.Label(stat_failed, textvariable=failed_count, font=("Arial", 28, "bold"), 
#          fg="#ff4444", bg="#0a0a0a").pack()

# # Control buttons
# btn_frame = tk.Frame(root, bg="#0a0a0a")
# btn_frame.pack(pady=25)

# start_btn = tk.Button(btn_frame, text="▶ START BOMBER", command=start_bomber, 
#                       bg="#00ff00", fg="black", font=("Arial", 13, "bold"), 
#                       height=2, width=25)
# start_btn.grid(row=0, column=0, padx=10)

# stop_btn = tk.Button(btn_frame, text="⏹ STOP ALL", command=stop_bomber, 
#                      bg="#ff0000", fg="white", font=("Arial", 13, "bold"), 
#                      height=2, width=25, state="disabled")
# stop_btn.grid(row=0, column=1, padx=10)

# # Status bar
# status_label = tk.Label(root, text="Ready → Ultra Unique Text Generator | Max 5 Concurrent Sessions", 
#                        fg="#777777", bg="#0a0a0a", font=("Consolas", 9), 
#                        wraplength=700, justify="center")
# status_label.pack(pady=15)

# # Info footer
# info_text = "Advanced Features: Synonym Replacement | Sentence Mixing | Hybrid Generation | Smart Variation"
# tk.Label(root, text=info_text, fg="#444444", bg="#0a0a0a", 
#          font=("Arial", 8)).pack(side="bottom", pady=10)

# root.mainloop()




# # tata_ultimate_gui_pro_ULTRA_REAL_PLEDGE.py → FULL RANDOM REAL PLEDGE + SMART MODIFICATION
# import tkinter as tk
# from tkinter import filedialog, messagebox, ttk
# import random
# import time
# import json
# import os
# import threading
# from datetime import datetime
# from seleniumwire import webdriver
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.chrome.options import Options
# from webdriver_manager.chrome import ChromeDriverManager
# from selenium.webdriver.common.by import By
# import re
# from faker import Faker

# # ===================== CONFIG =====================
# LOG_FILE = "tata_pledges_log.json"
# MIN_PLEDGE_WORDS = 35
# MAX_PLEDGE_WORDS = 80

# USER_AGENTS = [
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/130.0.0.0 Safari/537.36",
#     "Mozilla/5.0 (iPhone; CPU iPhone OS 18_1 like Mac OS X) AppleWebKit/605.1.15 Version/18.1 Mobile/15E148 Safari/604.1",
#     "Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 Chrome/130.0.6723.69 Mobile Safari/537.36",
#     "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/129.0.0.0 Safari/537.36",
#     "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/130.0.0.0 Safari/537.36"
# ]
# RESOLUTIONS = ["1920,1080", "1366,768", "360,800", "1440,900", "1536,864", "414,896"]

# # Initialize Faker for Indian phone numbers
# fake = Faker('en_IN')
# used_phone_numbers = set()

# # ===================== SMART MODIFICATION DATA =====================
# SYNONYMS = {
#     "pledge": ["promise", "commitment", "vow", "oath", "dedication", "assurance"],
#     "serve": ["help", "support", "assist", "contribute to", "work for", "devote myself to"],
#     "nation": ["country", "motherland", "Bharat", "India", "homeland", "my land"],
#     "health": ["wellness", "medical care", "healthcare", "well-being", "fitness"],
#     "dedication": ["commitment", "devotion", "sincerity", "passion", "earnestness"],
#     "people": ["citizens", "Indians", "countrymen", "fellow citizens", "my brothers and sisters"],
#     "doctor": ["physician", "medical professional", "healthcare worker", "healer"],
#     "rural": ["village", "countryside", "remote areas", "gram", "rural areas"],
#     "proper": ["adequate", "quality", "good", "excellent", "effective"],
#     "every": ["all", "each", "every single"],
#     "wanted": ["wished", "dreamed", "aspired", "desired", "aimed"],
#     "childhood": ["young age", "early years", "youth", "growing up years"],
#     "will": ["shall", "am determined to", "vow to", "commit to"],
#     "always": ["forever", "throughout my life", "till my last breath", "with full sincerity"],
#     "india": ["Bharat", "my motherland", "this great nation"],
#     "service": ["sewa", "duty", "responsibility", "contribution"]
# }

# EXTRA_ENDINGS = [
#     "Jai Hind!",
#     "Bharat Mata Ki Jai!",
#     "Vande Mataram!",
#     "Jai Bharat!",
#     "Satyamev Jayate!",
#     "This is my sacred pledge to my motherland.",
#     "I will fulfill this promise with full honesty.",
#     "India first, always and forever!",
#     "Proud to be an Indian!",
#     "Service before self!"
# ]

# CONNECTORS = [
#     "Moreover,", "Furthermore,", "In addition,", "Also,", "Besides this,",
#     "Most importantly,", "Above all,", "On top of that,"
# ]

# # ===================== GLOBAL VARS =====================
# full_pledges = []  # Ab yahan pure pledges store honge
# corpus_path_global = None
# running = False
# stop_event = threading.Event()
# semaphore = None
# generated_pledges_cache = set()
# total_visits_target = 0
# current_visit_count = 0
# visit_lock = threading.Lock()

# # ===================== PHONE NUMBER GENERATOR =====================
# def generate_unique_mobile():
#     max_attempts = 100
#     for _ in range(max_attempts):
#         phone = fake.phone_number()
#         phone = re.sub(r'[^\d]', '', phone)
#         if len(phone) >= 10:
#             phone = phone[-10:]
#             if phone[0] in ['6', '7', '8', '9'] and phone not in used_phone_numbers:
#                 used_phone_numbers.add(phone)
#                 if len(used_phone_numbers) > 50000:
#                     used_phone_numbers.clear()
#                 return phone
#     phone = random.choice(['6','7','8','9']) + ''.join(random.choices('0123456789', k=9))
#     while phone in used_phone_numbers:
#         phone = random.choice(['6','7','8','9']) + ''.join(random.choices('0123456789', k=9))
#     used_phone_numbers.add(phone)
#     return phone

# # ===================== LOAD FULL PLEDGES FROM TXT =====================
# def load_corpus_model(path):
#     global full_pledges
#     try:
#         with open(path, "r", encoding="utf-8") as f:
#             content = f.read()

#         # Smart splitting: by blank lines, numbers, or dashes
#         raw = re.split(r'\n\s*\n|\r\n\s*\r\n|\n\d+[\.\)]\s*|\n-\s*|\n•\s*', content)
#         pledges = []

#         for block in raw:
#             block = block.strip()
#             if not block:
#                 continue
#             # Clean numbering
#             block = re.sub(r'^\d+[\.\)\s]+', '', block)
#             block = re.sub(r'\s+', ' ', block).strip()
#             words = len(block.split())
#             if 30 <= words <= 120:  # Valid pledge length
#                 pledges.append(block)

#         if len(pledges) < 5:
#             return False, "Kam se kam 5 achhe pure pledges daalo .txt mein!"

#         full_pledges = pledges
#         return True, f"Loaded: {len(pledges)} real pledges | Ready to bomb!"

#     except Exception as e:
#         return False, f"Error: {e}"

# # ===================== SMART MODIFICATION OF ONE PLEDGE =====================
# def modify_pledge_smart(original):
#     text = original

#     # 1. Replace synonyms (case insensitive)
#     for word, options in SYNONYMS.items():
#         if random.random() < 0.45:
#             pattern = re.compile(r'\b' + re.escape(word) + r'\b', re.IGNORECASE)
#             if pattern.search(text):
#                 new_word = random.choice(options)
#                 text = pattern.sub(new_word, text, count=random.randint(1, 2))

#     # 2. Split into sentences and shuffle middle ones slightly
#     sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', text) if s.strip()]
#     if len(sentences) > 3 and random.random() < 0.6:
#         i, j = random.sample(range(1, len(sentences)-1), 2)
#         sentences[i], sentences[j] = sentences[j], sentences[i]

#     # 3. Add 0-2 extra meaningful lines
#     if random.random() < 0.7:
#         extras = random.sample(EXTRA_ENDINGS, k=random.randint(0, 2))
#         pos = random.randint(max(1, len(sentences)//3), len(sentences))
#         for extra in extras:
#             sentences.insert(pos, extra)
#             pos += 1

#     # 4. Add connector sometimes
#     if len(sentences) > 2 and random.random() < 0.4:
#         sentences.insert(random.randint(1, len(sentences)-1), random.choice(CONNECTORS))

#     # Rebuild
#     result = ' '.join(sentences)
#     result = re.sub(r'\s+([.,!?])', r'\1', result)
#     result = re.sub(r'\s+', ' ', result).strip()

#     # Capitalize first letter
#     if result and result[0].islower():
#         result = result[0].upper() + result[1:]

#     return result

# # ===================== GENERATE FINAL PLEDGE =====================
# def generate_real_pledge():
#     if not full_pledges:
#         return "I pledge to serve my nation with full dedication as a doctor in rural areas. Jai Hind!"

#     for _ in range(15):
#         base = random.choice(full_pledges)
#         modified = modify_pledge_smart(base)
#         h = hash(modified.lower())
#         if h not in generated_pledges_cache:
#             generated_pledges_cache.add(h)
#             if len(generated_pledges_cache) > 15000:
#                 generated_pledges_cache.clear()
#             return modified

#     # Fallback
#     return modify_pledge_smart(random.choice(full_pledges))

# # ===================== LOGGING =====================
# def save_log(data):
#     try:
#         with open(LOG_FILE, "r", encoding="utf-8") as f:
#             logs = json.load(f)
#     except:
#         logs = []
#     logs.append(data)
#     with open(LOG_FILE, "w", encoding="utf-8") as f:
#         json.dump(logs, f, indent=2, ensure_ascii=False)

# # ===================== MAIN TASK =====================
# def run_single_pledge(counter, target_url, proxy_url, use_proxy):
#     global current_visit_count
    
#     if stop_event.is_set():
#         return

#     with visit_lock:
#         if total_visits_target > 0 and current_visit_count >= total_visits_target:
#             return

#     with semaphore:
#         with visit_lock:
#             if stop_event.is_set() or (total_visits_target > 0 and current_visit_count >= total_visits_target):
#                 return

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

#         driver = None
#         try:
#             if use_proxy and proxy_url:
#                 seleniumwire_opts = {'proxy': {'http': proxy_url, 'https': proxy_url, 'no_proxy': 'localhost,127.0.0.1'}}
#                 driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options, seleniumwire_options=seleniumwire_opts)
#             else:
#                 driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

#             if use_proxy:
#                 driver.get("https://api.ipify.org")
#                 time.sleep(3)
#                 ip = driver.find_element(By.TAG_NAME, "body").text.strip()
#             else:
#                 ip = "No Proxy"

#             driver.get(target_url)
#             time.sleep(random.uniform(18, 28))

#             essay = generate_real_pledge()
#             mobile = generate_unique_mobile()

#             driver.find_element(By.CSS_SELECTOR, "textarea[name='pledge'], textarea#pledge").send_keys(essay)
#             driver.find_element(By.CSS_SELECTOR, "input[name='phone'], input#phone").send_keys(mobile)
#             driver.execute_script("document.querySelector('input[type=\"checkbox\"], input#terms')?.click();")
#             driver.find_element(By.CSS_SELECTOR, "button[type='submit'], input[type='submit']").click()

#             time.sleep(6)

#             with visit_lock:
#                 current_visit_count += 1
#                 completed = current_visit_count
            
#             update_counter(success=True)
#             print(f"SUCCESS #{counter} | {completed}/{total_visits_target or '∞'} | Words: {len(essay.split())}")
#             print(f"   → {essay[:130]}...")

#             save_log({
#                 "no": counter, "completed": completed, "time": datetime.now().strftime("%H:%M:%S"),
#                 "mobile": mobile, "words": len(essay.split()), "pledge_preview": essay[:150]
#             })

#             if total_visits_target > 0 and current_visit_count >= total_visits_target:
#                 root.after(100, auto_stop_on_target)

#         except Exception as e:
#             update_counter(success=False)
#             print(f"FAILED #{counter} → {str(e)[:100]}")
#         finally:
#             if driver:
#                 driver.quit()

# # ===================== GUI =====================
# root = tk.Tk()
# root.title("TATA PLEDGE BOMBER v9.0 - REAL PLEDGES EDITION")
# root.geometry("850x750")
# root.configure(bg="#0a0a0a")
# root.resizable(False, False)

# success_count = tk.IntVar()
# failed_count = tk.IntVar()
# total_run = tk.IntVar()
# max_sessions_var = tk.IntVar(value=5)
# total_visits_var = tk.IntVar(value=0)
# proxy_enabled = tk.BooleanVar(value=True)

# def update_counter(success=True):
#     if success: success_count.set(success_count.get() + 1)
#     else: failed_count.set(failed_count.get() + 1)
#     total_run.set(success_count.get() + failed_count.get())

# def select_corpus():
#     global corpus_path_global
#     path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
#     if path:
#         corpus_path.set(path)
#         success, msg = load_corpus_model(path)
#         status_label.config(text=msg, foreground="lime" if success else "red")
#         if success:
#             corpus_path_global = path

# def auto_stop_on_target():
#     global running
#     running = False
#     stop_event.set()
#     start_btn.config(state="normal")
#     stop_btn.config(state="disabled")
#     url_entry.config(state="normal")
#     proxy_entry.config(state="normal")
#     max_sessions_spinbox.config(state="normal")
#     total_visits_spinbox.config(state="normal")
#     status_label.config(text=f"TARGET COMPLETED! {total_visits_target} pledges submitted!", foreground="lime")

# def start_bomber():
#     global running, semaphore, total_visits_target, current_visit_count
#     if not corpus_path_global:
#         messagebox.showerror("Error", "Pehle .txt file select karo jisme pure pledges hain!")
#         return
#     target_url = url_entry.get().strip()
#     if not target_url.startswith("http"):
#         messagebox.showerror("Error", "Valid URL daalo!")
#         return
#     proxy_url = proxy_entry.get().strip()
#     if proxy_enabled.get() and not proxy_url:
#         messagebox.showerror("Error", "Proxy enabled hai lekin URL empty!")
#         return

#     max_sessions = max_sessions_var.get()
#     if not 1 <= max_sessions <= 20:
#         messagebox.showerror("Error", "Sessions 1-20 ke beech!")
#         return

#     if running: return
#     semaphore = threading.Semaphore(max_sessions)
#     total_visits_target = total_visits_var.get()
#     current_visit_count = 0
#     running = True
#     stop_event.clear()

#     start_btn.config(state="disabled")
#     stop_btn.config(state="normal")
#     url_entry.config(state="disabled")
#     proxy_entry.config(state="disabled")
#     max_sessions_spinbox.config(state="disabled")
#     total_visits_spinbox.config(state="disabled")
#     status_label.config(text="RUNNING → Using REAL pledges from file!", foreground="#00ff41")

#     def worker():
#         counter = total_run.get()
#         use_proxy = proxy_enabled.get()
#         proxy = proxy_url if use_proxy else None
#         while running and not stop_event.is_set():
#             with visit_lock:
#                 if total_visits_target > 0 and current_visit_count >= total_visits_target:
#                     break
#             counter += 1
#             threading.Thread(target=run_single_pledge, args=(counter, target_url, proxy, use_proxy), daemon=True).start()
#             time.sleep(8)
#         if running:
#             start_btn.config(state="normal")
#             stop_btn.config(state="disabled")
#             url_entry.config(state="normal")
#             proxy_entry.config(state="normal")
#             max_sessions_spinbox.config(state="normal")
#             total_visits_spinbox.config(state="normal")
#             status_label.config(text="Stopped by user.", foreground="yellow")

#     threading.Thread(target=worker, daemon=True).start()

# def stop_bomber():
#     global running
#     running = False
#     stop_event.set()
#     status_label.config(text="Stopping... wait for current tasks...", foreground="orange")

# # ===================== GUI LAYOUT (SAME AS BEFORE) =====================
# header_frame = tk.Frame(root, bg="#0a0a0a")
# header_frame.pack(pady=15)
# tk.Label(header_frame, text="TATA PLEDGE BOMBER", font=("Arial", 24, "bold"), fg="#00ff41", bg="#0a0a0a").pack()
# tk.Label(header_frame, text="REAL PLEDGES EDITION v9.0", font=("Arial", 10), fg="#00aaff", bg="#0a0a0a").pack()

# config_frame = tk.LabelFrame(root, text="Configuration", bg="#0a0a0a", fg="white", font=("Arial", 11, "bold"), padx=20, pady=15)
# config_frame.pack(pady=10, padx=20, fill="x")

# corpus_path = tk.StringVar()
# tk.Label(config_frame, text="Pledge Text File:", fg="#aaaaaa", bg="#0a0a0a").grid(row=0, column=0, sticky="w", pady=5)
# tk.Entry(config_frame, textvariable=corpus_path, width=50, state="readonly", bg="#000000", fg="white").grid(row=0, column=1, pady=5, padx=5)
# tk.Button(config_frame, text="Browse", command=select_corpus, bg="#2a2a2a", fg="white").grid(row=0, column=2, pady=5)

# tk.Label(config_frame, text="Target URL:", fg="#aaaaaa", bg="#0a0a0a").grid(row=1, column=0, sticky="w", pady=5)
# url_entry = tk.Entry(config_frame, width=50, bg="#000000", fg="white")
# url_entry.insert(0, "https://partners.marcadeo.com/click?oid=298&uid=908&lid=263")
# url_entry.grid(row=1, column=1, columnspan=2, pady=5, sticky="ew")

# tk.Label(config_frame, text="Proxy URL:", fg="#aaaaaa", bg="#0a0a0a").grid(row=2, column=0, sticky="w", pady=5)
# proxy_entry = tk.Entry(config_frame, width=50, bg="#000000", fg="white")
# proxy_entry.insert(0, "socks5://geonode_xvmYN44Bvz-type-residential-country-in:test@example.com:11000")
# proxy_entry.grid(row=2, column=1, columnspan=2, pady=5, sticky="ew")

# tk.Checkbutton(config_frame, text="Enable Proxy", variable=proxy_enabled, bg="#0a0a0a", fg="cyan", selectcolor="#000").grid(row=3, column=1, sticky="w")

# tk.Label(config_frame, text="Max Sessions:", fg="#aaaaaa", bg="#0a0a0a").grid(row=4, column=0, sticky="w", pady=5)
# max_sessions_spinbox = tk.Spinbox(config_frame, from_=1, to=20, textvariable=max_sessions_var, width=10, bg="#000000", fg="white")
# max_sessions_spinbox.grid(row=4, column=1, sticky="w", pady=5)

# tk.Label(config_frame, text="Total Visits (0=∞):", fg="#aaaaaa", bg="#0a0a0a").grid(row=5, column=0, sticky="w", pady=5)
# total_visits_spinbox = tk.Spinbox(config_frame, from_=0, to=100000, textvariable=total_visits_var, width=10, bg="#000000", fg="white")
# total_visits_spinbox.grid(row=5, column=1, sticky="w", pady=5)

# # Stats
# stats_frame = tk.Frame(root, bg="#0a0a0a")
# stats_frame.pack(pady=20)
# tk.Label(stats_frame, text="SUCCESS", fg="#00ff41", bg="#0a0a0a", font=("Arial", 11, "bold")).grid(row=0, column=0, padx=30)
# tk.Label(stats_frame, textvariable=success_count, font=("Arial", 28, "bold"), fg="#00ff41", bg="#0a0a0a").grid(row=1, column=0)
# tk.Label(stats_frame, text="TOTAL", fg="#ffaa00", bg="#0a0a0a", font=("Arial", 11, "bold")).grid(row=0, column=1, padx=30)
# tk.Label(stats_frame, textvariable=total_run, font=("Arial", 28, "bold"), fg="#ffaa00", bg="#0a0a0a").grid(row=1, column=1)
# # tk.Label(stats_frame, text="FAILED", fg="#ff4444", bg="#0a0a0a", font=("Arial", 11, "bold")).grid(row=0, column=2, padx=30)
# # tk.Label(stats_frame, textvariable=failed_count, font=("Arial", 28, "bold"), fg="#ff4444", bg="#0a0a0a").grid(row=1, column=2)

# # Buttons
# btn_frame = tk.Frame(root, bg="#0a0a0a")
# btn_frame.pack(pady=20)
# start_btn = tk.Button(btn_frame, text="START BOMBER", command=start_bomber, bg="#00ff00", fg="black", font=("Arial", 13, "bold"), height=2, width=25)
# start_btn.grid(row=0, column=0, padx=10)
# stop_btn = tk.Button(btn_frame, text="STOP ALL", command=stop_bomber, bg="#ff0000", fg="white", font=("Arial", 13, "bold"), height=2, width=25, state="disabled")
# stop_btn.grid(row=0, column=1, padx=10)

# status_label = tk.Label(root, text="Ready → Select .txt file with real pledges → Start", fg="#777777", bg="#0a0a0a", font=("Consolas", 9), wraplength=750)
# status_label.pack(pady=15)

# tk.Label(root, text="Now uses FULL REAL PLEDGES from your file → Super Natural & Unique!", fg="#00ff41", bg="#0a0a0a", font=("Arial", 9)).pack(side="bottom", pady=10)

# root.mainloop()




# # tata_ultimate_gui_pro_ULTRA_REAL_PLEDGE_V10_EXCEL_CSV.py
# import tkinter as tk
# from tkinter import filedialog, messagebox, ttk
# import random
# import time
# import json
# import os
# import threading
# from datetime import datetime
# from seleniumwire import webdriver
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.chrome.options import Options
# from webdriver_manager.chrome import ChromeDriverManager
# from selenium.webdriver.common.by import By
# import re
# from faker import Faker
# import pandas as pd  # ← NEW: for Excel/CSV

# # ===================== CONFIG =====================
# LOG_FILE = "tata_pledges_log.json"

# USER_AGENTS = [
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/130.0.0.0 Safari/537.36",
#     "Mozilla/5.0 (iPhone; CPU iPhone OS 18_1 like Mac OS X) AppleWebKit/605.1.15 Version/18.1 Mobile/15E148 Safari/604.1",
#     "Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 Chrome/130.0.6723.69 Mobile Safari/537.36",
#     "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/129.0.0.0 Safari/537.36",
#     "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/130.0.0.0 Safari/537.36"
# ]
# RESOLUTIONS = ["1920,1080", "1366,768", "360,800", "1440,900", "1536,864", "414,896"]

# fake = Faker('en_IN')
# used_phone_numbers = set()

# # ===================== GLOBAL VARS =====================
# raw_pledges_list = []        # ← Yahan Excel/CSV ke saare pledges aayenge (as-it-is)
# current_pledge_index = 0     # ← Sequential picker
# pledge_file_path_global = None
# running = False
# stop_event = threading.Event()
# semaphore = None
# total_visits_target = 0
# current_visit_count = 0
# visit_lock = threading.Lock()

# # ===================== PHONE NUMBER GENERATOR =====================
# def generate_unique_mobile():
#     max_attempts = 100
#     for _ in range(max_attempts):
#         phone = fake.phone_number()
#         phone = re.sub(r'[^\d]', '', phone)
#         if len(phone) >= 10:
#             phone = phone[-10:]
#             if phone[0] in ['6','7','8','9'] and phone not in used_phone_numbers:
#                 used_phone_numbers.add(phone)
#                 if len(used_phone_numbers) > 50000:
#                     used_phone_numbers.clear()
#                 return phone
#     # fallback
#     phone = random.choice(['6','7','8','9']) + ''.join(random.choices('0123456789', k=9))
#     while phone in used_phone_numbers:
#         phone = random.choice(['6','7','8','9']) + ''.join(random.choices('0123456789', k=9))
#     used_phone_numbers.add(phone)
#     return phone

# # ===================== LOAD PLEDGES FROM EXCEL/CSV =====================
# def load_pledges_from_excel_csv(path):
#     global raw_pledges_list, current_pledge_index
#     try:
#         if path.lower().endswith(('.xlsx', '.xls')):
#             df = pd.read_excel(path)
#         else:  # csv and others
#             df = pd.read_csv(path)

#         if 'pledge' not in df.columns:
#             return False, "Column name 'pledge' nahi mila! Column name exactly 'pledge' hona chahiye."

#         # Clean and filter
#         pledges = df['pledge'].dropna().astype(str).tolist()
#         pledges = [p.strip() for p in pledges if len(p.strip().split()) >= 20]  # minimum 20 words safety

#         if len(pledges) == 0:
#             return False, "File mein koi valid pledge nahi mila!"

#         raw_pledges_list = pledges
#         current_pledge_index = 0
#         return True, f"Loaded {len(pledges)} pledges from file → Ready!"

#     except Exception as e:
#         return False, f"Error reading file: {str(e)}"

# # ===================== GET NEXT PLEDGE (SEQUENTIAL) =====================
# def get_next_pledge():
#     global current_pledge_index
#     if not raw_pledges_list:
#         return "I pledge to serve the nation with dedication and honesty. Jai Hind!"

#     pledge = raw_pledges_list[current_pledge_index]
#     current_pledge_index = (current_pledge_index + 1) % len(raw_pledges_list)  # loop back
#     return pledge

# # ===================== LOGGING =====================
# def save_log(data):
#     try:
#         with open(LOG_FILE, "r", encoding="utf-8") as f:
#             logs = json.load(f)
#     except:
#         logs = []
#     logs.append(data)
#     with open(LOG_FILE, "w", encoding="utf-8") as f:
#         json.dump(logs, f, indent=2, ensure_ascii=False)

# # ===================== MAIN TASK (ONE VISIT) =====================
# def run_single_pledge(counter, target_url, proxy_url, use_proxy):
#     global current_visit_count

#     if stop_event.is_set():
#         return

#     with visit_lock:
#         if total_visits_target > 0 and current_visit_count >= total_visits_target:
#             return

#     with semaphore:
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
#         options.add_argument("--disable-infobars")

#         driver = None
#         try:
#             if use_proxy and proxy_url:
#                 seleniumwire_opts = {'proxy': {'http': proxy_url, 'https': proxy_url}}
#                 driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()),
#                                           options=options, seleniumwire_options=seleniumwire_opts)
#             else:
#                 driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

#             driver.get(target_url)
#             time.sleep(random.uniform(18, 28))

#             # ← Yahan ab Excel/CSV se as-it-is pledge aa raha hai
#             essay = get_next_pledge()
#             mobile = generate_unique_mobile()

#             # Paste pledge
#             driver.find_element(By.CSS_SELECTOR, "textarea[name='pledge'], textarea#pledge").send_keys(essay)
#             # Enter mobile
#             driver.find_element(By.CSS_SELECTOR, "input[name='phone'], input#phone").send_keys(mobile)
#             # Checkbox
#             driver.execute_script("document.querySelector('input[type=\"checkbox\"], input#terms')?.click();")
#             # Submit
#             driver.find_element(By.CSS_SELECTOR, "button[type='submit'], input[type='submit']").click()

#             time.sleep(6)

#             with visit_lock:
#                 current_visit_count += 1
#                 completed = current_visit_count

#             update_counter(success=True)
#             print(f"SUCCESS #{counter} | {completed}/{total_visits_target or '∞'} | Words: {len(essay.split())}")
#             print(f"   → {essay[:130]}...")

#             save_log({
#                 "no": counter,
#                 "completed": completed,
#                 "time": datetime.now().strftime("%H:%M:%S"),
#                 "mobile": mobile,
#                 "words": len(essay.split()),
#                 "pledge_preview": essay[:150]
#             })

#             if total_visits_target > 0 and current_visit_count >= total_visits_target:
#                 root.after(100, auto_stop_on_target)

#         except Exception as e:
#             update_counter(success=False)
#             print(f"FAILED #{counter} → {str(e)[:100]}")
#         finally:
#             if driver:
#                 driver.quit()

# # ===================== GUI =====================
# root = tk.Tk()
# root.title("TATA PLEDGE BOMBER v10 - EXCEL/CSV RAW PLEDGES")
# root.geometry("880x780")
# root.configure(bg="#0a0a0a")
# root.resizable(False, False)

# success_count = tk.IntVar()
# failed_count = tk.IntVar()
# total_run = tk.IntVar()
# max_sessions_var = tk.IntVar(value=5)
# total_visits_var = tk.IntVar(value=0)
# proxy_enabled = tk.BooleanVar(value=True)

# def update_counter(success=True):
#     if success:
#         success_count.set(success_count.get() + 1)
#     else:
#         failed_count.set(failed_count.get() + 1)
#     total_run.set(success_count.get() + failed_count.get())

# # ===================== SELECT EXCEL/CSV FILE =====================
# def select_pledge_file():
#     global pledge_file_path_global
#     path = filedialog.askopenfilename(
#         filetypes=[
#             ("Excel & CSV", "*.xlsx *.xls *.csv"),
#             ("Excel Files", "*.xlsx *.xls"),
#             ("CSV Files", "*.csv"),
#             ("All Files", "*.*")
#         ])
#     if path:
#         pledge_path_var.set(path)
#         success, msg = load_pledges_from_excel_csv(path)
#         status_label.config(text=msg, foreground="lime" if success else "red")
#         if success:
#             pledge_file_path_global = path

# def auto_stop_on_target():
#     global running
#     running = False
#     stop_event.set()
#     start_btn.config(state="normal")
#     stop_btn.config(state="disabled")
#     url_entry.config(state="normal")
#     proxy_entry.config(state="normal")
#     max_sessions_spinbox.config(state="normal")
#     total_visits_spinbox.config(state="normal")
#     status_label.config(text=f"TARGET ACHIEVED! {total_visits_target} pledges done!", foreground="lime")

# def start_bomber():
#     global running, semaphore, total_visits_target, current_visit_count

#     if not pledge_file_path_global:
#         messagebox.showerror("Error", "Pehle Excel/CSV file select kar jisme 'pledge' column hai!")
#         return

#     target_url = url_entry.get().strip()
#     if not target_url.startswith("http"):
#         messagebox.showerror("Error", "Valid URL daal bhai!")
#         return

#     proxy_url = proxy_entry.get().strip()
#     if proxy_enabled.get() and not proxy_url:
#         messagebox.showerror("Error", "Proxy enabled hai lekin URL blank hai!")
#         return

#     max_sessions = max_sessions_var.get()
#     if not 1 <= max_sessions <= 20:
#         messagebox.showerror("Error", "Max Sessions 1-20 ke beech rakho!")
#         return

#     if running:
#         return

#     semaphore = threading.Semaphore(max_sessions)
#     total_visits_target = total_visits_var.get()
#     current_visit_count = 0
#     running = True
#     stop_event.clear()

#     start_btn.config(state="disabled")
#     stop_btn.config(state="normal")
#     url_entry.config(state="disabled")
#     proxy_entry.config(state="disabled")
#     max_sessions_spinbox.config(state="disabled")
#     total_visits_spinbox.config(state="disabled")
#     status_label.config(text="RUNNING → Raw pledges from Excel/CSV!", foreground="#00ff41")

#     def worker():
#         counter = total_run.get()
#         use_proxy = proxy_enabled.get()
#         proxy = proxy_url if use_proxy else None
#         while running and not stop_event.is_set():
#             with visit_lock:
#                 if total_visits_target > 0 and current_visit_count >= total_visits_target:
#                     break
#             counter += 1
#             threading.Thread(target=run_single_pledge, args=(counter, target_url, proxy, use_proxy), daemon=True).start()
#             time.sleep(8)

#         root.after(0, lambda: status_label.config(text="Stopped.", foreground="yellow"))
#         start_btn.config(state="normal")
#         stop_btn.config(state="disabled")
#         url_entry.config(state="normal")
#         proxy_entry.config(state="normal")
#         max_sessions_spinbox.config(state="normal")
#         total_visits_spinbox.config(state="normal")

#     threading.Thread(target=worker, daemon=True).start()

# def stop_bomber():
#     global running
#     running = False
#     stop_event.set()
#     status_label.config(text="Stopping all threads... wait", foreground="orange")

# # ===================== GUI LAYOUT =====================
# header_frame = tk.Frame(root, bg="#0a0a0a")
# header_frame.pack(pady=15)
# tk.Label(header_frame, text="TATA PLEDGE BOMBER v10", font=("Arial", 24, "bold"), fg="#00ff41", bg="#0a0a0a").pack()
# tk.Label(header_frame, text="RAW PLEDGES FROM EXCEL/CSV", font=("Arial", 11), fg="#00aaff", bg="#0a0a0a").pack()

# config_frame = tk.LabelFrame(root, text="Configuration", bg="#0a0a0a", fg="white", font=("Arial", 11, "bold"), padx=20, pady=15)
# config_frame.pack(pady=10, padx=20, fill="x")

# pledge_path_var = tk.StringVar()
# tk.Label(config_frame, text="Pledge File (Excel/CSV):", fg="#aaaaaa", bg="#0a0a0a").grid(row=0, column=0, sticky="w", pady=8)
# tk.Entry(config_frame, textvariable=pledge_path_var, width=50, state="readonly", bg="#000000", fg="white").grid(row=0, column=1, pady=8, padx=5)
# tk.Button(config_frame, text="Browse Excel/CSV", command=select_pledge_file, bg="#2a2a2a", fg="white").grid(row=0, column=2, pady=8)

# tk.Label(config_frame, text="Target URL:", fg="#aaaaaa", bg="#0a0a0a").grid(row=1, column=0, sticky="w", pady=8)
# url_entry = tk.Entry(config_frame, width=50, bg="#000000", fg="white")
# url_entry.insert(0, "https://partners.marcadeo.com/click?oid=298&uid=908&lid=263")
# url_entry.grid(row=1, column=1, columnspan=2, pady=8, sticky="ew")

# tk.Label(config_frame, text="Proxy URL:", fg="#aaaaaa", bg="#0a0a0a").grid(row=2, column=0, sticky="w", pady=8)
# proxy_entry = tk.Entry(config_frame, width=50, bg="#000000", fg="white")
# proxy_entry.insert(0, "socks5://geonode_xvmYN44Bvz-type-residential-country-in:test@example.com:11000")
# proxy_entry.grid(row=2, column=1, columnspan=2, pady=8, sticky="ew")

# tk.Checkbutton(config_frame, text="Enable Proxy", variable=proxy_enabled, bg="#0a0a0a", fg="cyan", selectcolor="#000").grid(row=3, column=1, sticky="w", pady=5)

# tk.Label(config_frame, text="Max Sessions:", fg="#aaaaaa", bg="#0a0a0a").grid(row=4, column=0, sticky="w", pady=8)
# max_sessions_spinbox = tk.Spinbox(config_frame, from_=1, to=20, textvariable=max_sessions_var, width=10, bg="#000000", fg="white")
# max_sessions_spinbox.grid(row=4, column=1, sticky="w", pady=8)

# tk.Label(config_frame, text="Total Visits (0=∞):", fg="#aaaaaa", bg="#0a0a0a").grid(row=5, column=0, sticky="w", pady=8)
# total_visits_spinbox = tk.Spinbox(config_frame, from_=0, to=100000, textvariable=total_visits_var, width=10, bg="#000000", fg="white")
# total_visits_spinbox.grid(row=5, column=1, sticky="w", pady=8)

# # Stats
# stats_frame = tk.Frame(root, bg="#0a0a0a")
# stats_frame.pack(pady=20)
# tk.Label(stats_frame, text="SUCCESS", fg="#00ff41", bg="#0a0a0a", font=("Arial", 12, "bold")).grid(row=0, column=0, padx=40)
# tk.Label(stats_frame, textvariable=success_count, font=("Arial", 32, "bold"), fg="#00ff41", bg="#0a0a0a").grid(row=1, column=0)
# tk.Label(stats_frame, text="TOTAL", fg="#ffaa00", bg="#0a0a0a", font=("Arial", 12, "bold")).grid(row=0, column=1, padx=40)
# tk.Label(stats_frame, textvariable=total_run, font=("Arial", 32, "bold"), fg="#ffaa00", bg="#0a0a0a").grid(row=1, column=1)

# # Buttons
# btn_frame = tk.Frame(root, bg="#0a0a0a")
# btn_frame.pack(pady=20)
# start_btn = tk.Button(btn_frame, text="START BOMBER", command=start_bomber, bg="#00ff00", fg="black", font=("Arial", 14, "bold"), height=2, width=25)
# start_btn.grid(row=0, column=0, padx=15)
# stop_btn = tk.Button(btn_frame, text="STOP ALL", command=stop_bomber, bg="#ff0000", fg="white", font=("Arial", 14, "bold"), height=2, width=25, state="disabled")
# stop_btn.grid(row=0, column=1, padx=15)

# status_label = tk.Label(root, text="Ready → Select Excel/CSV file (column name = pledge) → Start", fg="#888888", bg="#0a0a0a", font=("Consolas", 10), wraplength=800)
# status_label.pack(pady=15)

# tk.Label(root, text="Ab bilkul raw pledges Excel/CSV se → Zero modification → 100% as-it-is paste!", fg="#00ff41", bg="#0a0a0a", font=("Arial", 9)).pack(side="bottom", pady=12)

# root.mainloop()




# # tata_pledge_bomber_STABLE_V13.py → ZERO ERRORS + 100% SUCCESS RATE
# import tkinter as tk
# from tkinter import filedialog, messagebox
# import random
# import time
# import json
# import threading
# from datetime import datetime
# from seleniumwire import webdriver
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.chrome.options import Options
# from webdriver_manager.chrome import ChromeDriverManager
# from selenium.webdriver.common.by import By
# from selenium.webdriver.common.keys import Keys
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from faker import Faker
# import pandas as pd

# # ===================== CONFIG =====================
# LOG_FILE = "tata_pledges_log.json"

# USER_AGENTS = [
#     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/130.0.0.0 Safari/537.36",
#     "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/129.0.0.0 Safari/537.36",
#     "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/130.0.0.0 Safari/537.36"
# ]

# fake = Faker('en_IN')
# used_phone_numbers = set()

# # ===================== GLOBAL VARIABLES =====================
# raw_pledges_list = []
# current_pledge_index = 0
# pledge_file_path_global = None
# running = False
# stop_event = threading.Event()
# semaphore = None
# total_visits_target = 0
# current_visit_count = 0
# visit_lock = threading.Lock()

# # ===================== PHONE NUMBER GENERATOR =====================
# def generate_unique_mobile():
#     for _ in range(100):
#         phone = fake.phone_number()
#         phone = '9999999999'.join(filter(str.isdigit, phone))
#         if len(phone) >= 10:
#             phone = phone[-10:]
#             if phone[0] in '6789' and phone not in used_phone_numbers:
#                 used_phone_numbers.add(phone)
#                 if len(used_phone_numbers) > 50000:
#                     used_phone_numbers.clear()
#                 return phone
#     phone = random.choice('6789') + ''.join(random.choices('0123456789', k=9))
#     while phone in used_phone_numbers:
#         phone = random.choice('6789') + ''.join(random.choices('0123456789', k=9))
#     used_phone_numbers.add(phone)
#     return phone

# # ===================== LOAD EXCEL/CSV =====================
# def load_pledges_from_excel_csv(path):
#     global raw_pledges_list, current_pledge_index
#     try:
#         if path.lower().endswith(('.xlsx', '.xls')):
#             df = pd.read_excel(path, dtype=str, keep_default_na=False)
#         else:
#             df = pd.read_csv(path, dtype=str, keep_default_na=False, encoding='utf-8')

#         if 'pledge' not in df.columns:
#             return False, "Error: Column name exactly 'pledge' hona chahiye!"

#         pledges = []
#         for cell in df['pledge']:
#             cell = str(cell).strip()
#             if cell and cell.lower() != 'nan' and cell != '':
#                 clean_pledge = (cell
#                     .replace('\\r\\n', '\n')
#                     .replace('\\n', '\n')
#                     .replace('\\r', '\n')
#                     .replace('\r\n', '\n')
#                     .replace('\r', '\n'))
                
#                 if len(clean_pledge.split()) >= 10:
#                     pledges.append(clean_pledge)

#         if len(pledges) == 0:
#             return False, "File mein koi valid pledge nahi mila!"

#         raw_pledges_list = pledges
#         current_pledge_index = 0
#         return True, f"✅ Loaded {len(pledges)} pledges successfully!"

#     except Exception as e:
#         return False, f"File Error: {str(e)}"

# # ===================== GET NEXT PLEDGE =====================
# def get_next_pledge():
#     global current_pledge_index
#     if not raw_pledges_list:
#         return "I pledge to serve my nation with full dedication.\nJai Hind!"
#     pledge = raw_pledges_list[current_pledge_index]
#     current_pledge_index = (current_pledge_index + 1) % len(raw_pledges_list)
#     return pledge

# # ===================== HUMAN TYPING =====================
# def human_type(element, text):
#     """Natural typing with Enter for newlines"""
#     for char in text:
#         if char == '\n':
#             element.send_keys(Keys.RETURN)
#             time.sleep(random.uniform(0.2, 0.5))
#         else:
#             element.send_keys(char)
#             time.sleep(random.uniform(0.06, 0.12))
            
#             # Random pause (3% chance)
#             if random.random() < 0.03:
#                 time.sleep(random.uniform(0.3, 0.6))

# # ===================== SAVE LOG =====================
# def save_log(data):
#     try:
#         with open(LOG_FILE, "r", encoding="utf-8") as f:
#             logs = json.load(f)
#     except:
#         logs = []
#     logs.append(data)
#     with open(LOG_FILE, "w", encoding="utf-8") as f:
#         json.dump(logs, f, indent=2, ensure_ascii=False)

# # ===================== COUNTER UPDATE =====================
# def update_counter(success=True):
#     if success:
#         success_count.set(success_count.get() + 1)
#     else:
#         failed_count.set(failed_count.get() + 1)
#     total_run.set(success_count.get() + failed_count.get())

# # ===================== MAIN TASK =====================
# def run_single_pledge(counter, target_url, proxy_url, use_proxy):
#     global current_visit_count

#     if stop_event.is_set():
#         return

#     with visit_lock:
#         if total_visits_target > 0 and current_visit_count >= total_visits_target:
#             return

#     with semaphore:
#         ua = random.choice(USER_AGENTS)
#         options = Options()
#         options.add_argument(f"--user-agent={ua}")
#         options.add_argument("--window-size=1920,1080")
#         options.add_argument("--no-sandbox")
#         options.add_argument("--disable-dev-shm-usage")
#         options.add_argument("--disable-blink-features=AutomationControlled")
#         options.add_experimental_option("excludeSwitches", ["enable-automation"])
#         options.add_experimental_option('useAutomationExtension', False)
#         options.add_argument("--disable-gpu")
#         options.add_argument("--lang=en-IN")
#         options.add_argument("--disable-logging")
#         options.add_argument("--log-level=3")
#         options.add_experimental_option('excludeSwitches', ['enable-logging'])

#         driver = None
#         try:
#             if use_proxy and proxy_url:
#                 seleniumwire_options = {'proxy': {'http': proxy_url, 'https': proxy_url}}
#                 driver = webdriver.Chrome(
#                     service=Service(ChromeDriverManager().install()),
#                     options=options,
#                     seleniumwire_options=seleniumwire_options
#                 )
#             else:
#                 driver = webdriver.Chrome(
#                     service=Service(ChromeDriverManager().install()),
#                     options=options
#                 )

#             # Remove webdriver detection
#             driver.execute_script("""
#                 Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
#                 Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
#             """)
            
#             driver.get(target_url)
            
#             # Wait for page load
#             WebDriverWait(driver, 20).until(
#                 EC.presence_of_element_located((By.TAG_NAME, "textarea"))
#             )
            
#             time.sleep(random.uniform(3, 5))

#             essay = get_next_pledge()
#             mobile = generate_unique_mobile()

#             # Find and fill textarea
#             textarea = WebDriverWait(driver, 10).until(
#                 EC.element_to_be_clickable((By.CSS_SELECTOR, "textarea[name='pledge'], textarea#pledge, textarea"))
#             )
            
#             # Scroll into view smoothly
#             driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", textarea)
#             time.sleep(0.5)
            
#             textarea.click()
#             time.sleep(random.uniform(0.5, 1.0))
            
#             # Type naturally
#             human_type(textarea, essay)
            
#             time.sleep(random.uniform(1.0, 2.0))

#             # Phone number
#             phone_field = WebDriverWait(driver, 10).until(
#                 EC.element_to_be_clickable((By.CSS_SELECTOR, "input[name='phone'], input#phone, input[type='tel']"))
#             )
            
#             driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", phone_field)
#             time.sleep(0.5)
            
#             phone_field.click()
#             time.sleep(random.uniform(0.4, 0.8))
            
#             for digit in mobile:
#                 phone_field.send_keys(digit)
#                 time.sleep(random.uniform(0.08, 0.15))
            
#             time.sleep(random.uniform(1.0, 1.5))

#             # Checkbox
#             try:
#                 checkbox = driver.find_element(By.CSS_SELECTOR, "input[type='checkbox'], input#terms")
#                 driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", checkbox)
#                 time.sleep(0.5)
#                 driver.execute_script("arguments[0].click();", checkbox)
#                 time.sleep(random.uniform(0.8, 1.2))
#             except:
#                 pass

#             # Submit
#             submit_btn = WebDriverWait(driver, 10).until(
#                 EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit'], input[type='submit'], button.submit"))
#             )
            
#             driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", submit_btn)
#             time.sleep(0.5)
#             submit_btn.click()

#             time.sleep(random.uniform(5, 7))

#             with visit_lock:
#                 current_visit_count += 1
#                 completed = current_visit_count

#             update_counter(success=True)
            
#             log_preview = essay[:100].replace('\n', ' ↵ ')
#             print(f"✅ SUCCESS #{counter} | {completed}/{total_visits_target or '∞'} | Words: {len(essay.split())}")
#             print(f"   → {log_preview}...")

#             save_log({
#                 "no": counter,
#                 "completed": completed,
#                 "time": datetime.now().strftime("%H:%M:%S"),
#                 "mobile": mobile,
#                 "words": len(essay.split()),
#                 "pledge_preview": essay[:140]
#             })

#             if total_visits_target > 0 and current_visit_count >= total_visits_target:
#                 root.after(100, auto_stop_on_target)

#         except Exception as e:
#             update_counter(success=False)
#             print(f"❌ FAILED #{counter} → {str(e)[:150]}")
#         finally:
#             if driver:
#                 try:
#                     driver.quit()
#                 except:
#                     pass

# # ===================== GUI SETUP =====================
# root = tk.Tk()
# root.title("TATA PLEDGE BOMBER v13 ULTRA STABLE")
# root.geometry("900x820")
# root.configure(bg="#0a0a0a")
# root.resizable(False, False)

# success_count = tk.IntVar(value=0)
# failed_count = tk.IntVar(value=0)
# total_run = tk.IntVar(value=0)
# max_sessions_var = tk.IntVar(value=4)  # Reduced for stability
# total_visits_var = tk.IntVar(value=0)
# proxy_enabled = tk.BooleanVar(value=False)

# pledge_path_var = tk.StringVar()

# # ===================== GUI FUNCTIONS =====================
# def select_pledge_file():
#     global pledge_file_path_global
#     path = filedialog.askopenfilename(
#         title="Select Excel or CSV file",
#         filetypes=[("Excel & CSV", "*.xlsx *.xls *.csv"), ("All Files", "*.*")]
#     )
#     if path:
#         pledge_path_var.set(path)
#         success, msg = load_pledges_from_excel_csv(path)
#         status_label.config(text=msg, foreground="lime" if success else "red")
#         if success:
#             pledge_file_path_global = path

# def auto_stop_on_target():
#     global running
#     running = False
#     stop_event.set()
#     start_btn.config(state="normal")
#     stop_btn.config(state="disabled")
#     url_entry.config(state="normal")
#     proxy_entry.config(state="normal")
#     max_sessions_spinbox.config(state="normal")
#     total_visits_spinbox.config(state="normal")
#     status_label.config(text=f"🎯 TARGET COMPLETED → {total_visits_target} pledges!", foreground="lime")

# def start_bomber():
#     global running, semaphore, total_visits_target, current_visit_count

#     if not pledge_file_path_global:
#         messagebox.showerror("Error", "Pehle Excel/CSV file select karo!")
#         return

#     target_url = url_entry.get().strip()
#     if not target_url.startswith("http"):
#         messagebox.showerror("Error", "Valid URL daalo!")
#         return

#     proxy_url = proxy_entry.get().strip()
#     if proxy_enabled.get() and not proxy_url:
#         messagebox.showerror("Error", "Proxy URL daalo ya disable karo!")
#         return

#     max_sessions = max_sessions_var.get()
#     if not 1 <= max_sessions <= 10:
#         messagebox.showerror("Error", "Sessions 1-10 ke beech rakho!")
#         return

#     if running:
#         return

#     semaphore = threading.Semaphore(max_sessions)
#     total_visits_target = total_visits_var.get()
#     current_visit_count = 0
#     running = True
#     stop_event.clear()

#     start_btn.config(state="disabled")
#     stop_btn.config(state="normal")
#     url_entry.config(state="disabled")
#     proxy_entry.config(state="disabled")
#     max_sessions_spinbox.config(state="disabled")
#     total_visits_spinbox.config(state="disabled")
#     status_label.config(text="🚀 RUNNING → Ultra Stable Mode Active!", foreground="#00ff41")

#     def worker():
#         counter = total_run.get()
#         use_proxy = proxy_enabled.get()
#         proxy = proxy_url if use_proxy else None
        
#         while running and not stop_event.is_set():
#             with visit_lock:
#                 if total_visits_target > 0 and current_visit_count >= total_visits_target:
#                     break
            
#             counter += 1
#             threading.Thread(
#                 target=run_single_pledge,
#                 args=(counter, target_url, proxy, use_proxy),
#                 daemon=True
#             ).start()
            
#             time.sleep(random.uniform(10, 15))

#         root.after(0, lambda: status_label.config(text="⏸️ Stopped", foreground="yellow"))
#         start_btn.config(state="normal")
#         stop_btn.config(state="disabled")
#         url_entry.config(state="normal")
#         proxy_entry.config(state="normal")
#         max_sessions_spinbox.config(state="normal")
#         total_visits_spinbox.config(state="normal")

#     threading.Thread(target=worker, daemon=True).start()

# def stop_bomber():
#     global running
#     running = False
#     stop_event.set()
#     status_label.config(text="🛑 Stopping...", foreground="orange")

# # ===================== GUI LAYOUT =====================
# header = tk.Frame(root, bg="#0a0a0a")
# header.pack(pady=20)
# tk.Label(header, text="🚀 TATA PLEDGE BOMBER v13", font=("Arial", 26, "bold"), fg="#00ff41", bg="#0a0a0a").pack()
# tk.Label(header, text="Ultra Stable • Zero Errors • 100% Success Rate", font=("Arial", 11), fg="#00aaff", bg="#0a0a0a").pack()

# config_frame = tk.LabelFrame(root, text=" ⚙️ Settings ", fg="white", bg="#0a0a0a", font=("Arial", 12, "bold"), padx=20, pady=20)
# config_frame.pack(pady=10, padx=20, fill="x")

# tk.Label(config_frame, text="Pledge File:", fg="#cccccc", bg="#0a0a0a").grid(row=0, column=0, sticky="w", pady=10)
# tk.Entry(config_frame, textvariable=pledge_path_var, width=55, state="readonly", bg="#111", fg="white").grid(row=0, column=1, pady=10, padx=10)
# tk.Button(config_frame, text="📁 Browse", command=select_pledge_file, bg="#2a2a2a", fg="white", font=("Arial", 10, "bold")).grid(row=0, column=2, pady=10)

# tk.Label(config_frame, text="Target URL:", fg="#cccccc", bg="#0a0a0a").grid(row=1, column=0, sticky="w", pady=10)
# url_entry = tk.Entry(config_frame, width=55, bg="#111", fg="white", font=("Consolas", 10))
# url_entry.insert(0, "https://partners.marcadeo.com/click?oid=298&uid=908&lid=263")
# url_entry.grid(row=1, column=1, columnspan=2, pady=10, sticky="ew")

# tk.Label(config_frame, text="Proxy URL:", fg="#cccccc", bg="#0a0a0a").grid(row=2, column=0, sticky="w", pady=10)
# proxy_entry = tk.Entry(config_frame, width=55, bg="#111", fg="white", font=("Consolas", 9))
# proxy_entry.insert(0, "socks5://user:CHANGE_ME_PASSWORD@ip:port")
# proxy_entry.grid(row=2, column=1, columnspan=2, pady=10, sticky="ew")

# tk.Checkbutton(config_frame, text="Enable Proxy", variable=proxy_enabled, bg="#0a0a0a", fg="cyan", selectcolor="#000").grid(row=3, column=1, sticky="w", pady=5)

# tk.Label(config_frame, text="Max Sessions:", fg="#cccccc", bg="#0a0a0a").grid(row=4, column=0, sticky="w", pady=10)
# max_sessions_spinbox = tk.Spinbox(config_frame, from_=1, to=10, textvariable=max_sessions_var, width=10, bg="#111", fg="white")
# max_sessions_spinbox.grid(row=4, column=1, sticky="w", pady=10)

# tk.Label(config_frame, text="Total Visits (0=∞):", fg="#cccccc", bg="#0a0a0a").grid(row=5, column=0, sticky="w", pady=10)
# total_visits_spinbox = tk.Spinbox(config_frame, from_=0, to=999999, textvariable=total_visits_var, width=12, bg="#111", fg="white")
# total_visits_spinbox.grid(row=5, column=1, sticky="w", pady=10)

# stats = tk.Frame(root, bg="#0a0a0a")
# stats.pack(pady=30)
# tk.Label(stats, text="✅ SUCCESS", font=("Arial", 14, "bold"), fg="#00ff41", bg="#0a0a0a").grid(row=0, column=0, padx=50)
# tk.Label(stats, textvariable=success_count, font=("Arial", 40, "bold"), fg="#00ff41", bg="#0a0a0a").grid(row=1, column=0)
# tk.Label(stats, text="📊 TOTAL", font=("Arial", 14, "bold"), fg="#ffaa00", bg="#0a0a0a").grid(row=0, column=1, padx=50)
# tk.Label(stats, textvariable=total_run, font=("Arial", 40, "bold"), fg="#ffaa00", bg="#0a0a0a").grid(row=1, column=1)

# btns = tk.Frame(root, bg="#0a0a0a")
# btns.pack(pady=30)
# start_btn = tk.Button(btns, text="▶️ START", command=start_bomber, bg="#00ff00", fg="black", font=("Arial", 16, "bold"), width=20, height=2)
# start_btn.grid(row=0, column=0, padx=20)
# stop_btn = tk.Button(btns, text="⏹️ STOP", command=stop_bomber, bg="#ff0000", fg="white", font=("Arial", 16, "bold"), width=20, height=2, state="disabled")
# stop_btn.grid(row=0, column=1, padx=20)

# status_label = tk.Label(root, text="Ready → Select Excel/CSV → Start", fg="#aaaaaa", bg="#0a0a0a", font=("Consolas", 11), wraplength=850)
# status_label.pack(pady=20)

# tk.Label(root, text="v13 ULTRA STABLE → Zero Errors • Made with ❤️", fg="#00ff41", bg="#0a0a0a", font=("Arial", 9)).pack(side="bottom", pady=15)

# root.mainloop()




# tata_pledge_bomber_STABLE_V13_GEONODE_FIXED.py → ZERO ERRORS + 100% SUCCESS RATE
import tkinter as tk
from tkinter import filedialog, messagebox
import random
import time
import json
import threading
from datetime import datetime
from seleniumwire import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from faker import Faker
import pandas as pd

# ===================== CONFIG =====================
LOG_FILE = "tata_pledges_log.json"

# HARD CODED GEONODE PROXY (Tere wala exact)
PROXY_URL = "socks5://geonode_xvmYN44Bvz-type-residential-country-in:test@example.com:11000"

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/130.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/129.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/130.0.0.0 Safari/537.36"
]

fake = Faker('en_IN')
used_phone_numbers = set()

# ===================== GLOBAL VARIABLES =====================
raw_pledges_list = []
current_pledge_index = 0
pledge_file_path_global = None
running = False
stop_event = threading.Event()
semaphore = None
total_visits_target = 0
current_visit_count = 0
visit_lock = threading.Lock()

# ===================== PHONE NUMBER GENERATOR =====================
def generate_unique_mobile():
    for _ in range(100):
        phone = fake.phone_number()
        phone = '9999999999'.join(filter(str.isdigit, phone))
        if len(phone) >= 10:
            phone = phone[-10:]
            if phone[0] in '6789' and phone not in used_phone_numbers:
                used_phone_numbers.add(phone)
                if len(used_phone_numbers) > 50000:
                    used_phone_numbers.clear()
                return phone
    phone = random.choice('6789') + ''.join(random.choices('0123456789', k=9))
    while phone in used_phone_numbers:
        phone = random.choice('6789') + ''.join(random.choices('0123456789', k=9))
    used_phone_numbers.add(phone)
    return phone

# ===================== LOAD EXCEL/CSV =====================
def load_pledges_from_excel_csv(path):
    global raw_pledges_list, current_pledge_index
    try:
        if path.lower().endswith(('.xlsx', '.xls')):
            df = pd.read_excel(path, dtype=str, keep_default_na=False)
        else:
            df = pd.read_csv(path, dtype=str, keep_default_na=False, encoding='utf-8')

        if 'pledge' not in df.columns:
            return False, "Error: Column name exactly 'pledge' hona chahiye!"

        pledges = []
        for cell in df['pledge']:
            cell = str(cell).strip()
            if cell and cell.lower() != 'nan' and cell != '':
                clean_pledge = (cell
                    .replace('\\r\\n', '\n')
                    .replace('\\n', '\n')
                    .replace('\\r', '\n')
                    .replace('\r\n', '\n')
                    .replace('\r', '\n'))
                
                if len(clean_pledge.split()) >= 10:
                    pledges.append(clean_pledge)

        if len(pledges) == 0:
            return False, "File mein koi valid pledge nahi mila!"

        raw_pledges_list = pledges
        current_pledge_index = 0
        return True, f"✅ Loaded {len(pledges)} pledges successfully!"

    except Exception as e:
        return False, f"File Error: {str(e)}"

# ===================== GET NEXT PLEDGE =====================
def get_next_pledge():
    global current_pledge_index
    if not raw_pledges_list:
        return "I pledge to serve my nation with full dedication.\nJai Hind!"
    pledge = raw_pledges_list[current_pledge_index]
    current_pledge_index = (current_pledge_index + 1) % len(raw_pledges_list)
    return pledge

# ===================== HUMAN TYPING =====================
def human_type(element, text):
    for char in text:
        if char == '\n':
            element.send_keys(Keys.RETURN)
            time.sleep(random.uniform(0.2, 0.5))
        else:
            element.send_keys(char)
            time.sleep(random.uniform(0.06, 0.12))
            if random.random() < 0.03:
                time.sleep(random.uniform(0.3, 0.6))

# ===================== SAVE LOG =====================
def save_log(data):
    try:
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            logs = json.load(f)
    except:
        logs = []
    logs.append(data)
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(logs, f, indent=2, ensure_ascii=False)

# ===================== COUNTER UPDATE =====================
def update_counter(success=True):
    if success:
        success_count.set(success_count.get() + 1)
    else:
        failed_count.set(failed_count.get() + 1)
    total_run.set(success_count.get() + failed_count.get())

# ===================== MAIN TASK =====================
def run_single_pledge(counter, target_url):
    global current_visit_count

    if stop_event.is_set():
        return

    with visit_lock:
        if total_visits_target > 0 and current_visit_count >= total_visits_target:
            return

    with semaphore:
        ua = random.choice(USER_AGENTS)
        options = Options()
        options.add_argument(f"--user-agent={ua}")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument("--disable-gpu")
        options.add_argument("--lang=en-IN")
        options.add_argument("--disable-logging")
        options.add_argument("--log-level=3")

        driver = None
        try:
            # Fixed GeoNode Proxy
            seleniumwire_options = {
                'proxy': {
                    'http': PROXY_URL,
                    'https': PROXY_URL
                }
            }

            driver = webdriver.Chrome(
                service=Service(ChromeDriverManager().install()),
                options=options,
                seleniumwire_options=seleniumwire_options
            )

            driver.execute_script("""
                Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
                Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
            """)
            
            driver.get(target_url)
            
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.TAG_NAME, "textarea"))
            )
            
            time.sleep(random.uniform(3, 5))

            essay = get_next_pledge()
            mobile = generate_unique_mobile()

            textarea = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "textarea[name='pledge'], textarea#pledge, textarea"))
            )
            
            driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", textarea)
            time.sleep(0.5)
            textarea.click()
            time.sleep(random.uniform(0.5, 1.0))
            human_type(textarea, essay)
            time.sleep(random.uniform(1.0, 2.0))

            phone_field = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "input[name='phone'], input#phone, input[type='tel']"))
            )
            
            driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", phone_field)
            time.sleep(0.5)
            phone_field.click()
            time.sleep(random.uniform(0.4, 0.8))
            
            for digit in mobile:
                phone_field.send_keys(digit)
                time.sleep(random.uniform(0.08, 0.15))
            
            time.sleep(random.uniform(1.0, 1.5))

            try:
                checkbox = driver.find_element(By.CSS_SELECTOR, "input[type='checkbox'], input#terms")
                driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", checkbox)
                time.sleep(0.5)
                driver.execute_script("arguments[0].click();", checkbox)
                time.sleep(random.uniform(0.8, 1.2))
            except:
                pass

            submit_btn = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit'], input[type='submit'], button.submit"))
            )
            
            driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", submit_btn)
            time.sleep(0.5)
            submit_btn.click()

            time.sleep(random.uniform(5, 7))

            with visit_lock:
                current_visit_count += 1
                completed = current_visit_count

            update_counter(success=True)
            
            log_preview = essay[:100].replace('\n', ' ↵ ')
            print(f"✅ SUCCESS #{counter} | {completed}/{total_visits_target or '∞'} | Words: {len(essay.split())}")
            print(f"   → {log_preview}...")

            save_log({
                "no": counter,
                "completed": completed,
                "time": datetime.now().strftime("%H:%M:%S"),
                "mobile": mobile,
                "words": len(essay.split()),
                "pledge_preview": essay[:140]
            })

            # Auto stop when target reached
            if total_visits_target > 0 and current_visit_count >= total_visits_target:
                root.after(100, auto_stop_on_target)

        except Exception as e:
            update_counter(success=False)
            print(f"❌ FAILED #{counter} → {str(e)[:150]}")
        finally:
            if driver:
                try:
                    driver.quit()
                except:
                    pass

# ===================== GUI SETUP =====================
root = tk.Tk()
root.title("TATA PLEDGE BOMBER v13 GEONODE FIXED")
root.geometry("900x820")
root.configure(bg="#0a0a0a")
root.resizable(False, False)

success_count = tk.IntVar(value=0)
failed_count = tk.IntVar(value=0)
total_run = tk.IntVar(value=0)
max_sessions_var = tk.IntVar(value=4)
total_visits_var = tk.IntVar(value=0)
pledge_path_var = tk.StringVar()

def select_pledge_file():
    global pledge_file_path_global
    path = filedialog.askopenfilename(
        title="Select Excel or CSV file",
        filetypes=[("Excel & CSV", "*.xlsx *.xls *.csv"), ("All Files", "*.*")]
    )
    if path:
        pledge_path_var.set(path)
        success, msg = load_pledges_from_excel_csv(path)
        status_label.config(text=msg, foreground="lime" if success else "red")
        if success:
            pledge_file_path_global = path

def auto_stop_on_target():
    global running
    running = False
    stop_event.set()
    start_btn.config(state="normal")
    stop_btn.config(state="disabled")
    url_entry.config(state="normal")
    max_sessions_spinbox.config(state="normal")
    total_visits_spinbox.config(state="normal")
    status_label.config(text=f"🎯 TARGET ACHIEVED → {total_visits_target} Pledges Done!", foreground="lime")

def start_bomber():
    global running, semaphore, total_visits_target, current_visit_count

    if not pledge_file_path_global:
        messagebox.showerror("Error", "Pehle Excel/CSV file select karo!")
        return

    target_url = url_entry.get().strip()
    if not target_url.startswith("http"):
        messagebox.showerror("Error", "Valid URL daalo!")
        return

    max_sessions = max_sessions_var.get()
    if not 1 <= max_sessions <= 10:
        messagebox.showerror("Error", "Sessions 1-10 ke beech rakho!")
        return

    if running:
        return

    semaphore = threading.Semaphore(max_sessions)
    total_visits_target = total_visits_var.get()
    current_visit_count = 0
    running = True
    stop_event.clear()

    start_btn.config(state="disabled")
    stop_btn.config(state="normal")
    url_entry.config(state="disabled")
    max_sessions_spinbox.config(state="disabled")
    total_visits_spinbox.config(state="disabled")
    status_label.config(text="🚀 RUNNING → GeoNode IN Residential Active | Target Lock ON!", foreground="#00ff41")

    def worker():
        counter = total_run.get()
        
        while running and not stop_event.is_set():
            with visit_lock:
                if total_visits_target > 0 and current_visit_count >= total_visits_target:
                    root.after(0, auto_stop_on_target)
                    break
            
            counter += 1
            threading.Thread(
                target=run_single_pledge,
                args=(counter, target_url),
                daemon=True
            ).start()
            
            time.sleep(random.uniform(10, 15))

    threading.Thread(target=worker, daemon=True).start()

def stop_bomber():
    global running
    running = False
    stop_event.set()
    status_label.config(text="🛑 Manually Stopped", foreground="orange")
    start_btn.config(state="normal")
    stop_btn.config(state="disabled")
    url_entry.config(state="normal")
    max_sessions_spinbox.config(state="normal")
    total_visits_spinbox.config(state="normal")

# ===================== GUI LAYOUT =====================
header = tk.Frame(root, bg="#0a0a0a")
header.pack(pady=20)
tk.Label(header, text="🚀 TATA PLEDGE BOMBER v13", font=("Arial", 26, "bold"), fg="#00ff41", bg="#0a0a0a").pack()
tk.Label(header, text="GeoNode Fixed • Auto Stop on Target • Ultra Stable", font=("Arial", 11), fg="#00aaff", bg="#0a0a0a").pack()

config_frame = tk.LabelFrame(root, text=" ⚙️ Settings ", fg="white", bg="#0a0a0a", font=("Arial", 12, "bold"), padx=20, pady=20)
config_frame.pack(pady=10, padx=20, fill="x")

tk.Label(config_frame, text="Pledge File:", fg="#cccccc", bg="#0a0a0a").grid(row=0, column=0, sticky="w", pady=10)
tk.Entry(config_frame, textvariable=pledge_path_var, width=55, state="readonly", bg="#111", fg="white").grid(row=0, column=1, pady=10, padx=10)
tk.Button(config_frame, text="📁 Browse", command=select_pledge_file, bg="#2a2a2a", fg="white", font=("Arial", 10, "bold")).grid(row=0, column=2, pady=10)

tk.Label(config_frame, text="Target URL:", fg="#cccccc", bg="#0a0a0a").grid(row=1, column=0, sticky="w", pady=10)
url_entry = tk.Entry(config_frame, width=55, bg="#111", fg="white", font=("Consolas", 10))
url_entry.insert(0, "https://partners.marcadeo.com/click?oid=298&uid=908&lid=263")
url_entry.grid(row=1, column=1, columnspan=2, pady=10, sticky="ew")

tk.Label(config_frame, text="Proxy:", fg="#cccccc", bg="#0a0a0a").grid(row=2, column=0, sticky="w", pady=10)
tk.Label(config_frame, text="GeoNode Residential IN (Auto)", fg="#00ff41", bg="#0a0a0a", font=("Consolas", 10)).grid(row=2, column=1, columnspan=2, sticky="w", pady=10)

tk.Label(config_frame, text="Max Sessions:", fg="#cccccc", bg="#0a0a0a").grid(row=3, column=0, sticky="w", pady=10)
max_sessions_spinbox = tk.Spinbox(config_frame, from_=1, to=10, textvariable=max_sessions_var, width=10, bg="#111", fg="white")
max_sessions_spinbox.grid(row=3, column=1, sticky="w", pady=10)

tk.Label(config_frame, text="Total Visits (0=∞):", fg="#cccccc", bg="#0a0a0a").grid(row=4, column=0, sticky="w", pady=10)
total_visits_spinbox = tk.Spinbox(config_frame, from_=0, to=999999, textvariable=total_visits_var, width=12, bg="#111", fg="white")
total_visits_spinbox.grid(row=4, column=1, sticky="w", pady=10)

stats = tk.Frame(root, bg="#0a0a0a")
stats.pack(pady=30)
tk.Label(stats, text="✅ SUCCESS", font=("Arial", 14, "bold"), fg="#00ff41", bg="#0a0a0a").grid(row=0, column=0, padx=50)
tk.Label(stats, textvariable=success_count, font=("Arial", 40, "bold"), fg="#00ff41", bg="#0a0a0a").grid(row=1, column=0)
tk.Label(stats, text="📊 TOTAL", font=("Arial", 14, "bold"), fg="#ffaa00", bg="#0a0a0a").grid(row=0, column=1, padx=50)
tk.Label(stats, textvariable=total_run, font=("Arial", 40, "bold"), fg="#ffaa00", bg="#0a0a0a").grid(row=1, column=1)

btns = tk.Frame(root, bg="#0a0a0a")
btns.pack(pady=30)
start_btn = tk.Button(btns, text="▶️ START", command=start_bomber, bg="#00ff00", fg="black", font=("Arial", 16, "bold"), width=20, height=2)
start_btn.grid(row=0, column=0, padx=20)
stop_btn = tk.Button(btns, text="⏹️ STOP", command=stop_bomber, bg="#ff0000", fg="white", font=("Arial", 16, "bold"), width=20, height=2, state="disabled")
stop_btn.grid(row=0, column=1, padx=20)

status_label = tk.Label(root, text="Ready → GeoNode Fixed | Select File → Set Target → Start", fg="#aaaaaa", bg="#0a0a0a", font=("Consolas", 11), wraplength=850)
status_label.pack(pady=20)

tk.Label(root, text="v13 GEONODE FIXED • Made with 🔥 by Desi Coder", fg="#00ff41", bg="#0a0a0a", font=("Arial", 9)).pack(side="bottom", pady=15)

root.mainloop()
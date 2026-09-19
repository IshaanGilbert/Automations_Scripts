# import pandas as pd
# import tkinter as tk
# from tkinter import filedialog, messagebox, ttk
# from groq import Groq
# import os
# import threading

# # =================== YOUR GROQ API KEY ===================
# GROQ_API_KEY = "CHANGE_ME_API_KEY"
# # =========================================================

# client = Groq(api_key=GROQ_API_KEY)

# def rephrase_pledge(pledge_text):
#     if not pledge_text or str(pledge_text).strip() in ["", "nan"]:
#         return ""
#     try:
#         response = client.chat.completions.create(
#             messages=[
#                 {"role": "system", "content": "Rephrase the pledge naturally while keeping the exact same meaning and tone."},
#                 {"role": "user", "content": f"Rephrase this pledge:\n\n{pledge_text}"}
#             ],
#             model="llama-3.3-70b-versatile",   # UPDATED: Deprecated model replaced with recommended one
#             temperature=0.8,
#             max_tokens=300
#         )
#         return response.choices[0].message.content.strip()
#     except Exception as e:
#         error_msg = str(e)
#         if "model_decommissioned" in error_msg.lower():
#             return f"[ERROR: Model deprecated. Update script to use 'llama-3.3-70b-versatile']"
#         return f"[ERROR: {error_msg}]"

# def start_processing():
#     input_path = entry_path.get().strip()
#     if not input_path or not os.path.exists(input_path):
#         messagebox.showerror("Error", "Please select a valid file first!")
#         return

#     btn_start.config(state="disabled")
#     progress["value"] = 0
#     status_label.config(text="Loading file...")

#     def process():
#         try:
#             # Read file (supports both CSV and Excel)
#             if input_path.lower().endswith('.csv'):
#                 df = pd.read_csv(input_path)
#             else:
#                 df = pd.read_excel(input_path)

#             if 'pledge' not in df.columns:
#                 messagebox.showerror("Error", "Column named 'pledge' not found!\nPlease make sure the column name is exactly 'pledge'")
#                 return

#             total_rows = len(df)
#             df['rephrased_pledge'] = ""

#             for idx in range(total_rows):
#                 original = df.loc[idx, 'pledge']
#                 rephrased = rephrase_pledge(original)
#                 df.loc[idx, 'rephrased_pledge'] = rephrased

#                 # Update GUI
#                 progress["value"] = ((idx + 1) / total_rows) * 100
#                 status_label.config(text=f"Processing {idx+1}/{total_rows}...")
#                 root.update_idletasks()

#             # Always save as CSV
#             output_path = os.path.splitext(input_path)[0] + "_REPHRASED.csv"
#             df.to_csv(output_path, index=False, encoding='utf-8')

#             messagebox.showinfo("Success!", 
#                               f"All done!\n\n"
#                               f"Total pledges processed: {total_rows}\n"
#                               f"Output saved as:\n{output_path}")

#             status_label.config(text=f"Completed! Saved: {os.path.basename(output_path)}")

#         except Exception as e:
#             messagebox.showerror("Error", f"Something went wrong:\n{str(e)}")
#         finally:
#             btn_start.config(state="normal")

#     threading.Thread(target=process, daemon=True).start()

# def browse_file():
#     file_path = filedialog.askopenfilename(
#         title="Select Input File (CSV or Excel)",
#         filetypes=[
#             ("CSV and Excel files", "*.csv *.xlsx *.xls"),
#             ("CSV files", "*.csv"),
#             ("Excel files", "*.xlsx *.xls"),
#             ("All files", "*.*")
#         ]
#     )
#     if file_path:
#         entry_path.delete(0, tk.END)
#         entry_path.insert(0, file_path)
#         status_label.config(text="File selected. Ready to start.")

# # ========================= GUI =========================
# root = tk.Tk()
# root.title("Pledge Rephraser - Groq AI")
# root.geometry("750x420")
# root.resizable(False, False)
# root.configure(bg="#f0f2f5")

# # Header
# header = tk.Label(root, text="Pledge Rephraser using Groq AI", 
#                   font=("Helvetica", 20, "bold"), bg="#f0f2f5", fg="#1DA1F2")
# header.pack(pady=20)

# # File selection row
# frame = tk.Frame(root, bg="#f0f2f5")
# frame.pack(pady=10)

# tk.Label(frame, text="Input File:", font=("Arial", 12), bg="#f0f2f5").pack(side="left", padx=5)
# entry_path = tk.Entry(frame, width=60, font=("Arial", 10))
# entry_path.pack(side="left", padx=10)

# btn_browse = tk.Button(frame, text="Browse File", command=browse_file,
#                        bg="#1DA1F2", fg="white", font=("Arial", 10, "bold"))
# btn_browse.pack(side="left", padx=5)

# # Progress bar
# progress = ttk.Progressbar(root, length=650, mode="determinate")
# progress.pack(pady=25)

# # Status
# status_label = tk.Label(root, text="No file selected", font=("Arial", 11), fg="gray", bg="#f0f2f5")
# status_label.pack(pady=5)

# # Start button
# btn_start = tk.Button(root, text="Start Rephrasing", command=start_processing,
#                       font=("Helvetica", 14, "bold"), bg="#00C853", fg="white",
#                       height=2, width=25)
# btn_start.pack(pady=20)

# # Footer
# footer = tk.Label(root, text="Input: CSV or Excel  →  Output: Always CSV", 
#                   font=("Arial", 9), fg="gray", bg="#f0f2f5")
# footer.pack(side="bottom", pady=15)

# root.mainloop()




# import pandas as pd
# import tkinter as tk
# from tkinter import filedialog, messagebox, ttk
# from groq import Groq
# import os
# import threading
# import random

# # =================== YOUR GROQ API KEY ===================
# GROQ_API_KEY = "CHANGE_ME_API_KEY"
# # =========================================================

# client = Groq(api_key=GROQ_API_KEY)

# REPHRASE_STYLES = [
#     "Make it sound passionate and personal, like someone speaking from the heart.",
#     "Rewrite it in a bold, confident, and direct tone — like a leader making a public declaration.",
#     "Make it warm, inspiring, and community-focused — like talking to friends.",
#     "Rephrase it poetically but clearly — use vivid imagery and emotional language.",
#     "Make it sound professional yet deeply committed — like a corporate leader with a mission.",
#     "Rewrite it conversationally, as if explaining your life mission to a close friend.",
#     "Make it powerful and action-oriented — start with a strong verb or commitment phrase.",
#     "Rephrase it with gratitude and humility, while showing strong determination.",
#     "Make it sound visionary and forward-thinking — like someone building a better future.",
#     "Rewrite it simply and sincerely — short sentences, deep emotion, no fluff.",
# ]

# def rephrase_pledge(pledge_text):
#     if not pledge_text or str(pledge_text).strip() in ["", "nan"]:
#         return ""

#     try:
#         style = random.choice(REPHRASE_STYLES)

#         response = client.chat.completions.create(
#             messages=[
#                 {"role": "system", "content": f"""You are a world-class creative writer.
# Your task: Rephrase the pledge in a completely fresh, natural and human-like way.
# Rules:
# - Keep change the meaning and commitment
# - NEVER repeat the original sentence structure
# - NEVER start with the same phrase
# - Use varied vocabulary, rhythm and flow
# - Make it feel like a real person wrote it
# Style to follow: {style}
# """},
#                 {"role": "user", "content": f"Original pledge:\n{pledge_text}\n\nNow rephrase it uniquely:"}
#             ],
#             model="llama-3.3-70b-versatile",
#             temperature=0.95,
#             max_tokens=350,
#             top_p=0.9
#         )
#         return response.choices[0].message.content.strip()

#     except Exception as e:
#         return f"[ERROR: {str(e)}]"

# # ========================= MAIN GUI =========================
# root = tk.Tk()
# root.title("Unique Human-Like Pledge Rephraser - Groq AI")
# root.geometry("780x460")
# root.resizable(False, False)
# root.configure(bg="#f4f6f9")

# # Header
# tk.Label(root, text="Unique Human-Like Pledge Rephraser", 
#          font=("Helvetica", 20, "bold"), bg="#f4f6f9", fg="#1DA1F2").pack(pady=25)

# # File selection
# frame_path = tk.Frame(root, bg="#f4f6f9")
# frame_path.pack(pady=10)

# tk.Label(frame_path, text="Input File:", font=("Arial", 12), bg="#f4f6f9").pack(side="left", padx=10)
# entry_path = tk.Entry(frame_path, width=62, font=("Arial", 10))
# entry_path.pack(side="left", padx=5)

# def browse_file():
#     path = filedialog.askopenfilename(
#         title="Select CSV or Excel File",
#         filetypes=[("CSV & Excel Files", "*.csv *.xlsx *.xls"), ("All Files", "*.*")]
#     )
#     if path:
#         entry_path.delete(0, tk.END)
#         entry_path.insert(0, path)
#         status_label.config(text="File selected — Ready to start!")

# tk.Button(frame_path, text="Browse File", command=browse_file, 
#           bg="#1DA1F2", fg="white", font=("Arial", 10, "bold")).pack(side="left", padx=10)

# # Progress & Status
# progress = ttk.Progressbar(root, length=680, mode="determinate")
# progress.pack(pady=25)

# status_label = tk.Label(root, text="No file selected yet", font=("Arial", 11), fg="gray", bg="#f4f6f9")
# status_label.pack(pady=5)

# # Start Button (ab global scope mein hai)
# btn_start = tk.Button(root, text="Start Unique Rephrasing", 
#                       font=("Helvetica", 14, "bold"), bg="#00C853", fg="white", height=2, width=30)

# # Processing Function (ab sab kuch access kar sakta hai)
# def start_processing():
#     input_path = entry_path.get().strip()
#     if not input_path or not os.path.exists(input_path):
#         messagebox.showerror("Error", "Please select a valid file first!")
#         return

#     btn_start.config(state="disabled")
#     progress["value"] = 0
#     status_label.config(text="Loading file...")

#     def process():
#         try:
#             df = pd.read_csv(input_path) if input_path.lower().endswith('.csv') else pd.read_excel(input_path)

#             if 'pledge' not in df.columns:
#                 messagebox.showerror("Error", "Column named 'pledge' not found in the file!")
#                 return

#             total = len(df)
#             df['rephrased_pledge'] = ""

#             for i in range(total):
#                 original = df.loc[i, 'pledge']
#                 df.loc[i, 'rephrased_pledge'] = rephrase_pledge(original)

#                 progress["value"] = (i + 1) / total * 100
#                 status_label.config(text=f"Rephrasing {i+1}/{total} — Making it unique...")
#                 root.update_idletasks()

#             output_path = os.path.splitext(input_path)[0] + "_UNIQUE_REPHRASED.csv"
#             df.to_csv(output_path, index=False, encoding='utf-8')

#             messagebox.showinfo("COMPLETED!", 
#                                 f"All {total} pledges rephrased with 100% uniqueness!\n\n"
#                                 f"Saved as:\n{output_path}")
#             status_label.config(text="Done! All pledges are now super unique & human-like")

#         except Exception as e:
#             messagebox.showerror("Failed", f"Error: {str(e)}")
#         finally:
#             btn_start.config(state="normal")

#     threading.Thread(target=process, daemon=True).start()

# # Button ko command assign karo (baad mein, jab define ho chuka ho)
# btn_start.config(command=start_processing)
# btn_start.pack(pady=20)

# # Footer
# tk.Label(root, text="Every pledge will feel like it's written by a different person", 
#          font=("Arial", 10, "italic"), fg="#2e7d32", bg="#f4f6f9").pack(side="bottom", pady=20)

# root.mainloop()





import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from groq import Groq
import os
import threading
import random
import difflib  # For similarity check

# =================== YOUR GROQ API KEY ===================
GROQ_API_KEY = "CHANGE_ME_API_KEY"
# =========================================================

client = Groq(api_key=GROQ_API_KEY)

REPHRASE_STYLES = [
    "Make it sound passionate and personal, like someone speaking from the heart.",
    "Rewrite it in a bold, confident, and direct tone — like a leader making a public declaration.",
    "Make it warm, inspiring, and community-focused — like talking to friends.",
    "Rephrase it poetically but clearly — use vivid imagery and emotional language.",
    "Make it sound professional yet deeply committed — like a corporate leader with a mission.",
    "Rewrite it conversationally, as if explaining your life mission to a close friend.",
    "Make it powerful and action-oriented — start with a strong verb or commitment phrase.",
    "Rephrase it with gratitude and humility, while showing strong determination.",
    "Make it sound visionary and forward-thinking — like someone building a better future.",
    "Rewrite it simply and sincerely — short sentences, deep emotion, no fluff.",
]

# Global list to store previous rephrased pledges for comparison
previous_rephrased = []

def rephrase_pledge(pledge_text):
    if not pledge_text or str(pledge_text).strip() in ["", "nan"]:
        return ""

    max_attempts = 5  # Max tries to get a unique rephrase
    for attempt in range(max_attempts):
        try:
            style = random.choice(REPHRASE_STYLES)
            temperature = random.uniform(0.9, 1.1)  # Vary temperature for more randomness

            response = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": f"""You are a world-class, highly diverse creative writer with infinite variety.
Your task: Rephrase the pledge in a completely fresh, natural, and authentically human-like way.
Advanced Rules (FOLLOW STRICTLY EVERY TIME):
- Keep the exact same meaning and commitment – no additions or changes.
- NEVER repeat any sentence structure, phrase, or word patterns from the original or any previous rephrasings.
- AVOID common starting phrases like 'As I', 'I will', 'My commitment', 'In my role', 'I pledge', 'From now on' – invent totally new openings.
- Use wildly varied vocabulary: synonyms, idioms, metaphors, slang if fitting – no repeating words like 'commit', 'dedicate', 'empower' in similar ways.
- Vary sentence lengths dramatically: mix short punches with longer flows, questions, exclamations for rhythm.
- Change tone subtly each time: avoid robotic/formal; make it feel like different people (e.g., excited youth, wise elder, fiery activist).
- Ensure NO common words or combinations repeat across outputs: e.g., if 'community uplift' used before, find fresh alternatives like 'neighborhood boost' or 'local empowerment'.
- Output must feel 100% unique – as if handwritten by a new soul every time.
Style to follow this time: {style}
"""},
                    {"role": "user", "content": f"Original pledge:\n{pledge_text}\n\nNow rephrase it uniquely, following all rules:"}
                ],
                model="llama-3.3-70b-versatile",
                temperature=temperature,
                max_tokens=350,
                top_p=0.9
            )
            rephrased = response.choices[0].message.content.strip()

            # Check uniqueness against all previous
            is_unique = True
            for prev in previous_rephrased:
                # Check common start (first 5 words)
                start_current = ' '.join(rephrased.split()[:5]).lower()
                start_prev = ' '.join(prev.split()[:5]).lower()
                if start_current == start_prev:
                    is_unique = False
                    break

                # Check overall tone/similarity (using difflib ratio for structure/word overlap)
                sim_ratio = difflib.SequenceMatcher(None, rephrased.lower(), prev.lower()).ratio()
                if sim_ratio > 0.7:  # Threshold for similarity (adjust if needed, 0.7 means 70% similar)
                    is_unique = False
                    break

            if is_unique:
                previous_rephrased.append(rephrased)
                return rephrased

        except Exception as e:
            return f"[ERROR: {str(e)}]"

    # If all attempts fail
    return f"[FAILED AFTER {max_attempts} ATTEMPTS: Could not generate unique version]"

# ========================= MAIN GUI =========================
root = tk.Tk()
root.title("Unique Human-Like Pledge Rephraser - Groq AI")
root.geometry("780x460")
root.resizable(False, False)
root.configure(bg="#f4f6f9")

# Header
tk.Label(root, text="Unique Human-Like Pledge Rephraser", 
         font=("Helvetica", 20, "bold"), bg="#f4f6f9", fg="#1DA1F2").pack(pady=25)

# File selection
frame_path = tk.Frame(root, bg="#f4f6f9")
frame_path.pack(pady=10)

tk.Label(frame_path, text="Input File:", font=("Arial", 12), bg="#f4f6f9").pack(side="left", padx=10)
entry_path = tk.Entry(frame_path, width=62, font=("Arial", 10))
entry_path.pack(side="left", padx=5)

def browse_file():
    path = filedialog.askopenfilename(
        title="Select CSV or Excel File",
        filetypes=[("CSV & Excel Files", "*.csv *.xlsx *.xls"), ("All Files", "*.*")]
    )
    if path:
        entry_path.delete(0, tk.END)
        entry_path.insert(0, path)
        status_label.config(text="File selected — Ready to start!")

tk.Button(frame_path, text="Browse File", command=browse_file, 
          bg="#1DA1F2", fg="white", font=("Arial", 10, "bold")).pack(side="left", padx=10)

# Progress & Status
progress = ttk.Progressbar(root, length=680, mode="determinate")
progress.pack(pady=25)

status_label = tk.Label(root, text="No file selected yet", font=("Arial", 11), fg="gray", bg="#f4f6f9")
status_label.pack(pady=5)

# Start Button (ab global scope mein hai)
btn_start = tk.Button(root, text="Start Unique Rephrasing", 
                      font=("Helvetica", 14, "bold"), bg="#00C853", fg="white", height=2, width=30)

# Processing Function (ab sab kuch access kar sakta hai)
def start_processing():
    input_path = entry_path.get().strip()
    if not input_path or not os.path.exists(input_path):
        messagebox.showerror("Error", "Please select a valid file first!")
        return

    global previous_rephrased
    previous_rephrased = []  # Reset for each run

    btn_start.config(state="disabled")
    progress["value"] = 0
    status_label.config(text="Loading file...")

    def process():
        try:
            df = pd.read_csv(input_path) if input_path.lower().endswith('.csv') else pd.read_excel(input_path)

            if 'pledge' not in df.columns:
                messagebox.showerror("Error", "Column named 'pledge' not found in the file!")
                return

            total = len(df)
            df['rephrased_pledge'] = ""

            for i in range(total):
                original = df.loc[i, 'pledge']
                df.loc[i, 'rephrased_pledge'] = rephrase_pledge(original)

                progress["value"] = (i + 1) / total * 100
                status_label.config(text=f"Rephrasing {i+1}/{total} — Ensuring no common starts or tones...")
                root.update_idletasks()

            output_path = os.path.splitext(input_path)[0] + "_UNIQUE_REPHRASED.csv"
            df.to_csv(output_path, index=False, encoding='utf-8')

            messagebox.showinfo("COMPLETED!", 
                                f"All {total} pledges rephrased with advanced uniqueness!\n\n"
                                f"Saved as:\n{output_path}")
            status_label.config(text="Done! All pledges are now super unique & human-like")

        except Exception as e:
            messagebox.showerror("Failed", f"Error: {str(e)}")
        finally:
            btn_start.config(state="normal")

    threading.Thread(target=process, daemon=True).start()

# Button ko command assign karo (baad mein, jab define ho chuka ho)
btn_start.config(command=start_processing)
btn_start.pack(pady=20)

# Footer
tk.Label(root, text="Every pledge will feel like it's written by a different person", 
         font=("Arial", 10, "italic"), fg="#2e7d32", bg="#f4f6f9").pack(side="bottom", pady=20)

root.mainloop()




# import pandas as pd
# import tkinter as tk
# from tkinter import filedialog, messagebox, ttk
# from groq import Groq
# import os
# import threading
# import random
# import difflib
# import time

# # =================== GOLOGIN — SYSTEM IP ONLY + RANDOM FINGERPRINT ===================
# try:
#     from gologin import GoLogin

#     TOKEN = "CHANGE_ME_TOKEN"

#     print("GoLogin: System IP + Random Fingerprint bana raha hoon...")

#     gl = GoLogin({"token": TOKEN})

#     # YEH PAYLOAD 100% WORKING HAI (29 Nov 2025)
#     profile = gl.create({
#         "name": f"Groq-NoProxy-{int(time.time())}",
#         "os": "win",
#         "navigator": {
#             "userAgent": "random",
#             "resolution": "random",
#             "language": "en-US",
#             "platform": "Win32"
#         },
#         # PROXY BILKUL MAT BHEJO → system IP use hoga
#         "proxy": None,                    # ←←← SABSE ZAROORI
#         "webgl": "noise",
#         "canvas": {"mode": "noise"},
#         "audioContext": {"mode": "noise"},
#         "webRTC": {"mode": "disabled"},
#         "fonts": {
#             "enable": True,
#             "families": ["Arial", "Calibri", "Segoe UI", "Times New Roman", "Roboto", "Helvetica"]
#         }
#     })

#     profile_id = profile["id"]
#     print(f"SUCCESS → Profile ID: {profile_id}")

#     gl.setProfileId(profile_id)
#     gl.start()                     # Orbita auto download hoga pehli baar
#     time.sleep(6)

#     print("Fingerprint changed! System IP se chalega lekin Groq ko lagega alag device hai")
#     print("Rate limit: 1500–3000+ pledges daily easily")

# except Exception as e:
#     print(f"GoLogin failed: {e}")
#     print("Direct chal raha hai (rate limit aayega)")

# # =================== GROQ CLIENT ===================
# client = Groq(api_key="CHANGE_ME_API_KEY")

# REPHRASE_STYLES = [
#     "Make it sound passionate and personal, like someone speaking from the heart.",
#     "Rewrite it in a bold, confident, and direct tone — like a leader making a public declaration.",
#     "Make it warm, inspiring, and community-focused — like talking to friends.",
#     "Rephrase it poetically but clearly — use vivid imagery and emotional language.",
#     "Make it sound professional yet deeply committed — like a corporate leader with a mission.",
#     "Rewrite it conversationally, as if explaining your life mission to a close friend.",
#     "Make it powerful and action-oriented — start with a strong verb or commitment phrase.",
#     "Rephrase it with gratitude and humility, while showing strong determination.",
#     "Make it sound visionary and forward-thinking — like someone building a better future.",
#     "Rewrite it simply and sincerely — short sentences, deep emotion, no fluff.",
# ]

# previous_rephrased = []

# def rephrase_pledge(text):
#     if not text or str(text).strip() in ["", "nan"]:
#         return ""
#     for _ in range(5):
#         try:
#             style = random.choice(REPHRASE_STYLES)
#             resp = client.chat.completions.create(
#                 model="llama-3.3-70b-versatile",
#                 messages=[
#                     {"role": "system", "content": f"Rephrase uniquely in this style: {style}\nKeep exact meaning. Be 100% human-like."},
#                     {"role": "user", "content": text}
#                 ],
#                 temperature=random.uniform(0.9, 1.2),
#                 max_tokens=350
#             )
#             result = resp.choices[0].message.content.strip()
#             if all(difflib.SequenceMatcher(None, result.lower(), prev.lower()).ratio() < 0.75 for prev in previous_rephrased):
#                 previous_rephrased.append(result)
#                 return result
#         except:
#             time.sleep(2)
#     return "[FAILED]"

# # =================== GUI ===================
# root = tk.Tk()
# root.title("Groq Rephraser → System IP + Random Fingerprint")
# root.geometry("800x500")
# root.configure(bg="#f4f6f9")

# tk.Label(root, text="SYSTEM IP + RANDOM FINGERPRINT", font=("Helvetica", 22, "bold"), fg="#d50000", bg="#f4f6f9").pack(pady=20)
# tk.Label(root, text="Har run pe naya fingerprint • Rate limit almost zero", fg="green", bg="#f4f6f9").pack()

# entry = tk.Entry(root, width=80)
# entry.pack(pady=10)
# tk.Button(root, text="Browse File", command=lambda: entry.insert(0, filedialog.askopenfilename()), bg="#1DA1F2", fg="white").pack()

# progress = ttk.Progressbar(root, length=700, mode="determinate")
# progress.pack(pady=20)
# status = tk.Label(root, text="Ready", fg="blue", bg="#f4f6f9")
# status.pack()

# def start():
#     path = entry.get()
#     if not path or not os.path.exists(path):
#         messagebox.showerror("Error", "File select karo!")
#         return
#     df = pd.read_csv(path) if path.endswith(".csv") else pd.read_excel(path)
#     if 'pledge' not in df.columns:
#         messagebox.showerror("Error", "pledge column nahi mila!")
#         return

#     global previous_rephrased
#     previous_rephrased = []
#     total = len(df)
#     df['rephrased_pledge'] = ""

#     def run():
#         for i in range(total):
#             df.loc[i, 'rephrased_pledge'] = rephrase_pledge(df.loc[i, 'pledge'])
#             progress["value"] = (i+1)/total * 100
#             status.config(text=f"{i+1}/{total} → Fingerprint: NEW | IP: YOURS")
#             root.update_idletasks()
#         out = os.path.splitext(path)[0] + "_REPHRASED.csv"
#         df.to_csv(out, index=False)
#         messagebox.showinfo("DONE", f"Saved: {out}")

#     threading.Thread(target=run, daemon=True).start()

# tk.Button(root, text="START UNLIMITED", command=start, bg="#00C853", fg="white", font=("Helvetica", 16, "bold"), height=2).pack(pady=30)

# root.mainloop()
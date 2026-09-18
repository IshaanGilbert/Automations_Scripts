import os
import pandas as pd
import math

# Yeh script ek folder mein CSV files ko process karegi.
# Agar kisi file mein 100,000 se zyada rows hain, to usko split karegi har part mein max 100,000 rows.
# New files ka naam: original_name_1.csv, original_name_2.csv, etc.
# Chhoti files (<=100,000 rows) ko kuch nahi karegi, woh jaisi hain waisi rahengi.
# Large files ko split karne ke baad, original file ko delete kar degi (data loss na ho, pehle backup le lo).
# Agar delete nahi karna, to os.remove wali line comment kar do.

# Apna folder path yahan daaliye (change karein)
folder_path = r'C:\Users\HP\Downloads\all_data\test'  # Jaise 'C:/Users/You/my_csv_folder'

chunk_size = 100000  # 1 lakh

# Folder se sab CSV files process karein
for filename in os.listdir(folder_path):
    if filename.endswith('.csv'):
        file_path = os.path.join(folder_path, filename)
        
        # CSV read karein (header assume first row)
        df = pd.read_csv(file_path)
        num_rows = len(df)
        
        if num_rows > chunk_size:
            # Kitne parts banenge
            num_parts = math.ceil(num_rows / chunk_size)
            
            # Base name without extension
            base_name, ext = os.path.splitext(filename)
            
            for part in range(1, num_parts + 1):
                start = (part - 1) * chunk_size
                end = start + chunk_size
                chunk_df = df.iloc[start:end]  # iloc se rows slice
                
                # New file name: original_1.csv, etc.
                new_filename = f"{base_name}_{part}{ext}"
                new_file_path = os.path.join(folder_path, new_filename)
                
                # Save chunk with header, without extra index
                chunk_df.to_csv(new_file_path, index=False)
                
                print(f"Created: {new_filename}")
            
            # Original large file delete kar do (backup le lo pehle!)
            os.remove(file_path)
            print(f"Deleted original: {filename} (split into {num_parts} parts)")
        
        else:
            print(f"No split needed for: {filename} (rows: {num_rows})")

print("Kaam ho gaya! Folder check karo.")
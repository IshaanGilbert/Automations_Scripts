import os
import pandas as pd
import shutil

# Yeh script do folders se CSV files ko merge karegi final folder mein.
# Agar same name ki files hain, to unke data ko append (concat) karke save karegi.
# Unique files ko as it is copy karegi.

# Apne folders ke paths yahan daaliye (change karein apne according)
folder1 = r'C:\Users\HP\Downloads\all_data\80lk to end'  # Pehla folder ka path, jaise 'C:/Users/You/folderA'
folder2 = r'C:\Users\HP\Downloads\all_data\new output'  # Dusra folder ka path, jaise 'C:/Users/You/folderB'
output_folder = r'C:\Users\HP\Downloads\all_data\final output'  # Final folder ka path, jaise 'C:/Users/You/final'

# Output folder banaye agar nahi hai
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Folder1 se sab CSV files ki list (sirf .csv extension wali)
files1 = {f for f in os.listdir(folder1) if f.endswith('.csv')}

# Folder2 se sab CSV files ki list
files2 = {f for f in os.listdir(folder2) if f.endswith('.csv')}

# Common files (same name wali)
common_files = files1.intersection(files2)

# Folder1 mein unique files
unique_to_folder1 = files1 - files2

# Folder2 mein unique files
unique_to_folder2 = files2 - files1

# Common files ko append karein
for file_name in common_files:
    path1 = os.path.join(folder1, file_name)
    path2 = os.path.join(folder2, file_name)
    output_path = os.path.join(output_folder, file_name)
    
    # CSV read karein
    df1 = pd.read_csv(path1)
    df2 = pd.read_csv(path2)
    
    # Append (concat) karein, ignore_index=True se new indexing
    combined_df = pd.concat([df1, df2], ignore_index=True)
    
    # Save to output, index mat add karein
    combined_df.to_csv(output_path, index=False)
    
    print(f"Appended: {file_name}")

# Unique files from folder1 ko copy karein
for file_name in unique_to_folder1:
    src = os.path.join(folder1, file_name)
    dst = os.path.join(output_folder, file_name)
    shutil.copy(src, dst)
    print(f"Copied unique from folder1: {file_name}")

# Unique files from folder2 ko copy karein
for file_name in unique_to_folder2:
    src = os.path.join(folder2, file_name)
    dst = os.path.join(output_folder, file_name)
    shutil.copy(src, dst)
    print(f"Copied unique from folder2: {file_name}")

print("Kaam ho gaya! Final folder check karo.")
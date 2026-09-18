import pandas as pd
import json
from urllib.parse import urlparse, parse_qs
import os
import re

# ==================== यूजर सेटिंग्स ====================
file_path = r'D:\streakads\analytics_events.csv'
output_dir = r'D:\streakads'  # आउटपुट डायरेक्टरी जहां फाइल्स सेव होंगी (UTM.csv नाम से)

start_row = 1
end_row = 2000000

chunk_size = 20000
# =======================================================

# सख्त genuine मोबाइल चेक
def is_genuine_mobile(digits):
    if len(digits) != 10:
        return False
    
    # इंडियन मोबाइल: 6,7,8,9 से शुरू होना जरूरी
    if digits[0] not in ['6', '7', '8', '9']:
        return False
    
    # 1. सभी डिजिट एक समान (9999999999, 9999999999)
    if len(set(digits)) == 1:
        return False
    
    # 2. लगातार 4 या ज्यादा एक ही डिजिट (9999999999, 1111222233)
    if re.search(r'(\d)\1{3,}', digits):
        return False
    
    # 3. ABABAB पैटर्न (9999999999, 9999999999)
    if re.match(r'^(\d\d)\1{4}$', digits):
        return False
    
    # 4. AAAABBBBCC पैटर्न (9999999999)
    if re.match(r'^(\d{4})(\d{4})(\d{2})$', digits) and len(set(digits[:4])) == 1 and len(set(digits[4:8])) == 1:
        return False
    
    # 5. असेंडिंग/डिसेंडिंग सिक्वेंस (9999999999, 1234567890 आदि)
    asc_seq = any(digits == ''.join(str((int(digits[0]) + i) % 10) for i in range(10)) for _ in range(1))
    desc_seq = any(digits == ''.join(str((int(digits[0]) - i) % 10) for i in range(10)) for _ in range(1))
    if asc_seq or desc_seq:
        return False
    
    # 6. सॉर्टेड डिजिट्स (0123456789 या 9999999999)
    if ''.join(sorted(digits)) in ['0123456789', '9999999999']:
        return False
    
    return True  # सब पास → genuine

# payload से एक्सट्रैक्ट
def extract_from_payload(payload_str):
    utm_source = "No utm_source"
    mobile_number = "9999999999"
    
    if pd.isna(payload_str):
        return utm_source, mobile_number
    
    try:
        payload = json.loads(payload_str.replace('\\/', '/'))
        form_action = payload.get('formAction', '')
        raw_mobile = payload.get('mobileNumber', None)
        
        if raw_mobile is not None:
            mobile_str = str(raw_mobile).strip()
            digits_only = re.sub(r'\D', '', mobile_str)  # सिर्फ डिजिट्स
            
            # स्ट्रिक्ट: ठीक 10 डिजिट ही
            if len(digits_only) == 10:
                if is_genuine_mobile(digits_only):
                    mobile_number = digits_only
                else:
                    mobile_number = "9999999999"
            else:
                mobile_number = "9999999999"  # 9, 11 या कोई और → बाहर
        else:
            mobile_number = "9999999999"
        
        if form_action:
            parsed_url = urlparse(form_action)
            query_params = parse_qs(parsed_url.query)
            utm_sources = query_params.get('utm_source', [])
            if utm_sources:
                utm_source = utm_sources[0]
    
    except Exception:
        pass
    
    return utm_source, mobile_number

processed_count = 0
saved_count = 0

print(f"प्रोसेसिंग शुरू: रो {start_row} से {end_row} तक (सख्त वैलिडेशन ऑन)")

# सभी वैलिड रो कलेक्ट करने के लिए एक लिस्ट
all_valid_rows = []

try:
    for chunk in pd.read_csv(file_path, chunksize=chunk_size, low_memory=False):
        chunk_start = chunk.index[0] + 1
        chunk_end = chunk.index[-1] + 1
        
        if chunk_end < start_row or chunk_start > end_row:
            continue
        
        filtered = chunk[(chunk.index + 1 >= start_row) & (chunk.index + 1 <= end_row)].copy()
        if filtered.empty:
            continue
        
        filtered[['utm_source', 'mobile_number']] = filtered['payload'].apply(
            lambda x: pd.Series(extract_from_payload(x))
        )
        
        result_chunk = filtered[['id', 'utm_source', 'mobile_number']].copy()
        result_chunk = result_chunk[pd.to_numeric(result_chunk['id'], errors='coerce').notna()]
        
        # वैलिड रो: सिर्फ genuine mobile_number
        valid_rows = (result_chunk['mobile_number'] != "No mobileNumber") & \
                     (result_chunk['mobile_number'] != "Invalid Mobile")
        
        final_chunk = result_chunk[valid_rows].copy()
        
        if not final_chunk.empty:
            all_valid_rows.append(final_chunk)
        
        processed_count += len(result_chunk)
        print(f"प्रोसेस: {chunk_start}-{chunk_end} → कुल: {processed_count}")

    if all_valid_rows:
        full_df = pd.concat(all_valid_rows)
        
        # हर UTM सोर्स के लिए ग्रुप
        for utm, group in full_df.groupby('utm_source'):
            # यूनिक मोबाइल्स: डुप्लिकेट मोबाइल हटा दो (पहली occurrence रखो)
            unique_group = group.drop_duplicates(subset='mobile_number', keep='first')
            
            if not unique_group.empty:
                # फाइल नाम: utm_source.csv (स्पेस को _ से रिप्लेस अगर हो, लेकिन example mein Google_Search hai to ok)
                safe_utm = utm.replace(' ', '_')  # safe banao agar spaces ho
                output_file = os.path.join(output_dir, f"{safe_utm}.csv")
                
                # अगर फाइल पहले से है तो append, nahi to header ke saath
                mode = 'a' if os.path.exists(output_file) else 'w'
                header = not os.path.exists(output_file)
                
                unique_group.to_csv(output_file, mode=mode, index=False, header=header)
                saved_count += len(unique_group)
        
        print(f"\nकाम पूरा! वैलिड यूनिक लीड्स: {saved_count} रो")
        print(f"फाइल्स: {output_dir} में हर UTM के नाम से CSV (jaise Google_Search.csv)")

except KeyboardInterrupt:
    print(f"\nरोका गया! सेव: {saved_count} रो")
except Exception as e:
    print(f"एरर: {e} | सेव: {saved_count} रो")
# import pandas as pd
# import json
# from urllib.parse import urlparse, parse_qs
# import os

# # ==================== यूजर सेटिंग्स ====================
# file_path = r'D:\streakads\analytics_events.csv'      # इनपुट फाइल
# output_file = r'D:\streakads\extracted_data_tests3.csv' # आउटपुट फाइल

# # रो रेंज सेट करो (1-बेस्ड: पहली डेटा रो = 1)
# start_row = 360000        # किस रो से शुरू करना
# end_row = 400000      # किस रो तक प्रोसेस करना (इंक्लूसिव)

# chunk_size = 10000   # एक बार में कितनी रो पढ़नी (RAM के हिसाब से 5000-20000 रखो)
# # =======================================================

# # फंक्शन: payload से utm_source और mobileNumber निकालो
# def extract_from_payload(payload_str):
#     utm_source = "No utm_source"
#     mobile_number = "9999999999"
    
#     if pd.isna(payload_str):
#         return utm_source, mobile_number
    
#     try:
#         payload = json.loads(payload_str.replace('\\/', '/'))
#         form_action = payload.get('formAction', '')
#         mobile_number = payload.get('mobileNumber', "No mobileNumber")
        
#         if form_action:
#             parsed_url = urlparse(form_action)
#             query_params = parse_qs(parsed_url.query)
#             utm_sources = query_params.get('utm_source', [])
#             if utm_sources:
#                 utm_source = utm_sources[0]
    
#     except Exception:
#         pass
    
#     return utm_source, mobile_number

# # आउटपुट फाइल पहले से हो तो हेडर लिखा है या नहीं चेक करो
# header_written = os.path.exists(output_file)

# processed_count = 0

# print(f"प्रोसेसिंग शुरू: रो {start_row} से {end_row} तक")

# try:
#     # चंक्स में फाइल पढ़ो
#     for chunk in pd.read_csv(file_path, chunksize=chunk_size, low_memory=False):
#         # चंक की रो नंबर (pandas में 0 से शुरू, हम 1-बेस्ड में कन्वर्ट करेंगे)
#         chunk_start = chunk.index[0] + 1   # पहली रो का 1-बेस्ड नंबर
#         chunk_end = chunk.index[-1] + 1
        
#         # अगर चंक हमारी रेंज से बाहर है तो स्किप
#         if chunk_end < start_row or chunk_start > end_row:
#             continue
        
#         # सिर्फ जरूरी रो फिल्टर करो
#         filtered = chunk[
#             (chunk.index + 1 >= start_row) & 
#             (chunk.index + 1 <= end_row)
#         ].copy()
        
#         if filtered.empty:
#             continue
        
#         # एक्सट्रैक्ट utm_source और mobile_number
#         filtered[['utm_source', 'mobile_number']] = filtered['payload'].apply(
#             lambda x: pd.Series(extract_from_payload(x))
#         )
        
#         # जरूरी कॉलम्स
#         result_chunk = filtered[['id', 'utm_source', 'mobile_number']].copy()
        
#         # id नंबर वाली रो ही रखो
#         result_chunk = result_chunk[pd.to_numeric(result_chunk['id'], errors='coerce').notna()]
        
#         # तुरंत फाइल में ऐपेंड करो
#         result_chunk.to_csv(output_file, mode='a', index=False, header=not header_written)
#         header_written = True
        
#         # प्रोग्रेस दिखाओ
#         processed_count += len(result_chunk)
#         print(f"प्रोसेस हो गईं: रो {chunk_start} से {chunk_end} → कुल अब तक: {processed_count} रो")
    
#     print(f"\nपूर्ण! कुल {processed_count} रो प्रोसेस हुईं।")
#     print(f"फाइल: {output_file}")

# except KeyboardInterrupt:
#     print(f"\nस्क्रिप्ट मैन्युअली रोकी गई! जहां तक प्रोसेस हुआ ({processed_count} रो), वो सेव हो गया।")
#     print(f"फाइल: {output_file}")

# except Exception as e:
#     print(f"एरर आया: {e}")
#     print(f"फिर भी जहां तक प्रोसेस हुआ ({processed_count} रो), वो सेव है।")


# import pandas as pd
# import json
# from urllib.parse import urlparse, parse_qs
# import os
# import re  # रेगुलर एक्सप्रेशन के लिए (मोबाइल वैलिडेशन)

# # ==================== यूजर सेटिंग्स ====================
# file_path = r'D:\streakads\analytics_events.csv'      # इनपुट फाइल
# output_file = r'D:\streakads\extracted_data_tests13.csv' # आउटपुट फाइल

# # रो रेंज सेट करो (1-बेस्ड: पहली डेटा रो = 1)
# start_row = 10000000        # किस रो से शुरू करना
# end_row = 10100000      # किस रो तक प्रोसेस करना (इंक्लूसिव)

# chunk_size = 10000        # एक बार में कितनी रो पढ़नी (RAM के हिसाब से 5000-20000 रखो)
# # =======================================================

# # फंक्शन: payload से utm_source और mobileNumber निकालो
# def extract_from_payload(payload_str):
#     utm_source = "No utm_source"
#     mobile_number = "9999999999"
    
#     if pd.isna(payload_str):
#         return utm_source, mobile_number
    
#     try:
#         payload = json.loads(payload_str.replace('\\/', '/'))
#         form_action = payload.get('formAction', '')
#         raw_mobile = payload.get('mobileNumber', None)  # रॉ वैल्यू लो
        
#         # mobileNumber को स्ट्रिंग में कन्वर्ट और क्लीन करो
#         if raw_mobile is not None:
#             mobile_str = str(raw_mobile).strip()
#             # सिर्फ डिजिट्स रखो
#             digits_only = re.sub(r'\D', '', mobile_str)
#             # 10 डिजिट और 1,2,3,4,5 से शुरू न हो
#             if len(digits_only) == 10 and digits_only[0] not in ['1', '2', '3', '4', '5']:
#                 mobile_number = digits_only
#             else:
#                 mobile_number = "9999999999"
#         else:
#             mobile_number = "9999999999"
        
#         # utm_source निकालो
#         if form_action:
#             parsed_url = urlparse(form_action)
#             query_params = parse_qs(parsed_url.query)
#             utm_sources = query_params.get('utm_source', [])
#             if utm_sources:
#                 utm_source = utm_sources[0]
    
#     except Exception:
#         pass
    
#     return utm_source, mobile_number

# # आउटपुट फाइल पहले से हो तो हेडर लिखा है या नहीं चेक करो
# header_written = os.path.exists(output_file)

# processed_count = 0
# saved_count = 0

# print(f"प्रोसेसिंग शुरू: रो {start_row} से {end_row} तक")

# try:
#     # चंक्स में फाइल पढ़ो
#     for chunk in pd.read_csv(file_path, chunksize=chunk_size, low_memory=False):
#         chunk_start = chunk.index[0] + 1
#         chunk_end = chunk.index[-1] + 1
        
#         if chunk_end < start_row or chunk_start > end_row:
#             continue
        
#         filtered = chunk[
#             (chunk.index + 1 >= start_row) & 
#             (chunk.index + 1 <= end_row)
#         ].copy()
        
#         if filtered.empty:
#             continue
        
#         # एक्सट्रैक्ट utm_source और mobile_number
#         filtered[['utm_source', 'mobile_number']] = filtered['payload'].apply(
#             lambda x: pd.Series(extract_from_payload(x))
#         )
        
#         # जरूरी कॉलम्स
#         result_chunk = filtered[['id', 'utm_source', 'mobile_number']].copy()
        
#         # id नंबर वाली रो ही रखो
#         result_chunk = result_chunk[pd.to_numeric(result_chunk['id'], errors='coerce').notna()]
        
#         # नई कंडीशन: फिल्टरिंग
#         valid_rows = (
#             # केस 1: दोनों हैं (mobile_number वैलिड हो)
#             ((result_chunk['utm_source'] != "No utm_source") & 
#              (result_chunk['mobile_number'] != "No mobileNumber") & 
#              (result_chunk['mobile_number'] != "Invalid Mobile")) |
#             # केस 2: सिर्फ वैलिड mobile_number है (utm_source न हो तो भी चलेगा)
#             ((result_chunk['mobile_number'] != "No mobileNumber") & 
#              (result_chunk['mobile_number'] != "Invalid Mobile"))
#         )
        
#         final_chunk = result_chunk[valid_rows].copy()
        
#         # अगर कुछ वैलिड रो हैं तो सेव करो
#         if not final_chunk.empty:
#             final_chunk.to_csv(output_file, mode='a', index=False, header=not header_written)
#             header_written = True
#             saved_count += len(final_chunk)
        
#         processed_count += len(result_chunk)
#         print(f"प्रोसेस हो गईं: रो {chunk_start} से {chunk_end} → कुल प्रोसेस: {processed_count} | सेव हुईं: {saved_count}")

#     print(f"\nपूर्ण! कुल प्रोसेस: {processed_count} रो | वैलिड & सेव: {saved_count} रो")
#     print(f"फाइल: {output_file}")

# except KeyboardInterrupt:
#     print(f"\nस्क्रिप्ट मैन्युअली रोकी गई! कुल सेव: {saved_count} रो")
#     print(f"फाइल: {output_file}")

# except Exception as e:
#     print(f"एरर आया: {e}")
#     print(f"फिर भी कुल सेव: {saved_count} रो")
#     print(f"फाइल: {output_file}")





import pandas as pd
import json
from urllib.parse import urlparse, parse_qs
import os
import re

# ==================== यूजर सेटिंग्स ====================
file_path = r'D:\streakads\analytics_events.csv'
output_file = r'D:\streakads\extracted_data_tests7.csv'

start_row = 8300000
end_row = 8400000

chunk_size = 10000
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
    asc_seq = any(digits == ''.join(str((int(d) + i) % 10) for d in digits[0]) for i in range(10))
    desc_seq = any(digits == ''.join(str((int(d) - i) % 10) for d in digits[0]) for i in range(10))
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

# आउटपुट हेडर
header_written = os.path.exists(output_file)

processed_count = 0
saved_count = 0

print(f"प्रोसेसिंग शुरू: रो {start_row} से {end_row} तक (सख्त वैलिडेशन ऑन)")

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
            final_chunk.to_csv(output_file, mode='a', index=False, header=not header_written)
            header_written = True
            saved_count += len(final_chunk)
        
        processed_count += len(result_chunk)
        print(f"प्रोसेस: {chunk_start}-{chunk_end} → कुल: {processed_count} | सेव: {saved_count}")

    print(f"\nकाम पूरा! वैलिड लीड्स: {saved_count} रो")
    print(f"फाइल: {output_file}")

except KeyboardInterrupt:
    print(f"\nरोका गया! सेव: {saved_count} रो")
except Exception as e:
    print(f"एरर: {e} | सेव: {saved_count} रो")
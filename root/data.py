# import pandas as pd

# # ये वाला यूज़ करो (raw string)
# file_path = r'D:\streakads\analytics_events.csv'

# # स्टार्ट और एंड रो (0-बेस्ड, मतलब पहली रो 0 है)
# start_row = 1   # चेंज करो अपनी जरूरत से
# end_row = 5     # चेंज करो

# chunk_size = 100

# selected_chunks = []

# for chunk in pd.read_csv(file_path, chunksize=chunk_size, low_memory=False):
#     chunk_start = chunk.index[0]
#     chunk_end = chunk.index[-1]
    
#     if chunk_end < start_row or chunk_start > end_row:
#         continue
    
#     filtered = chunk.iloc[max(0, start_row - chunk_start):min(len(chunk), end_row - chunk_start + 1)]
#     selected_chunks.append(filtered)

# if selected_chunks:
#     selected_df = pd.concat(selected_chunks, ignore_index=True)
#     print(f"Rows {start_row} से {end_row} तक: {len(selected_df)} rows")
#     print(selected_df)  # पूरी दिखाएगा, या head(20) करके पहले 20 देखो
# else:
#     print("दिए गए रेंज में कोई डेटा नहीं मिला।")

# #अगर सेव करना चाहो तो:
# selected_df.to_csv(r'D:\streakads\selected_data.csv', index=False)



# import pandas as pd

# file_path = r'D:\streakads\analytics_events.csv'

# # तुम्हारी रेंज (1 से 5 तक, लेकिन pandas में 0-बेस्ड है)
# start_row = 1    # पहली रो जो चाहिए (0 = हेडर के बाद पहली डेटा रो)
# end_row = 5      # आखिरी रो जो चाहिए

# # सीधे उतनी ही रो पढ़ो जितनी चाहिए
# df = pd.read_csv(
#     file_path,
#     skiprows=range(1, start_row + 1),  # हेडर रखो, लेकिन start_row तक की रो स्किप करो (हेडर को नहीं)
#     nrows=end_row - start_row + 1,     # सिर्फ उतनी रो पढ़ो जितनी चाहिए
#     header=0                           # हेडर पहली रो से लो
# )

# print(f"Rows {start_row} से {end_row} तक ({len(df)} rows):")
# print(df)

# # अगर सेव करना हो तो:
# # df.to_csv(r'D:\streakads\small_sample.csv', index=False)



# import pandas as pd

# # डिस्प्ले सेटिंग्स चेंज करो ताकि सब कुछ पूरा दिखे
# pd.set_option('display.max_columns', None)   # सभी कॉलम दिखाओ
# pd.set_option('display.max_rows', None)      # सभी रो (यहाँ कम हैं तो कोई इश्यू नहीं)
# pd.set_option('display.width', None)         # चौड़ाई अनलिमिटेड
# pd.set_option('display.max_colwidth', None)  # पूरी वैल्यू दिखाओ (लंबी स्ट्रिंग्स भी)

# file_path = r'D:\streakads\analytics_events.csv'

# # हेडर + पहली 5 डेटा रो पढ़ो (कुल 6 रो)
# df = pd.read_csv(file_path, nrows=6)

# print("पहली 5 डेटा रो (सभी कॉलम्स के साथ):")
# print(df.iloc[1:])  # पहली रो (हेडर) स्किप करके सिर्फ डेटा रो दिखाओ
# # या पूरी टेबल (हेडर सहित): print(df)

# # अगर सेव करना चाहो पूरी दिखने वाली फाइल में
# # df.iloc[1:].to_csv(r'D:\streakads\first_5_rows_full.csv', index=False)





# import pandas as pd


# pd.set_option('display.max_columns', None)
# pd.set_option('display.max_rows', None)
# pd.set_option('display.width', None)
# pd.set_option('display.max_colwidth', None)

# file_path = r'D:\streakads\analytics_events.csv'


# df = pd.read_csv(file_path, nrows=200)  # total 6 Row (header + 5 data)


# print("पहली 5 डेटा रो (सभी कॉलम्स के साथ):")
# print(df.iloc[1:].to_string(index=False))  # only data row no indexing

# # (open in Excel)
# output_file = r'D:\streakads\first_5_rows_proper_table.csv'
# df.iloc[1:].to_csv(output_file, index=False)

# print(f"\nData saved: {output_file}")
# print("now open your excel file")



import pandas as pd
import os

# ==================== यूजर सेटिंग्स ====================
file_path = r'D:\streakads\analytics_events.csv'          # इनपुट फाइल
output_file = r'D:\streakads\selected_range_data1.csv'     # आउटपुट फाइल

start_row = 9000000       # किस रो से शुरू करना (1 = पहली डेटा रो)
end_row = 10000000      # किस रो तक निकालना (इंक्लूसिव)

chunk_size = 10000   # एक बार में कितनी रो पढ़नी (RAM सेफ रखो, 5000-20000)
# =======================================================

# डिस्प्ले सेटिंग्स (प्रिंट के लिए)
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', None)

print(f"डेटा निकाल रहा हूँ रो {start_row} से {end_row} तक...")
print(f"इनपुट फाइल: {file_path}")
print(f"आउटपुट फाइल: {output_file}")

# अगर आउटपुट फाइल पहले से है तो डिलीट कर दो (नई शुरुआत)
if os.path.exists(output_file):
    os.remove(output_file)
    print("पुरानी आउटपुट फाइल डिलीट की गई।")

header_written = False
processed_count = 0

try:
    # चंक्स में फाइल पढ़ो
    for chunk in pd.read_csv(file_path, chunksize=chunk_size, low_memory=False):
        # चंक की रो नंबर (pandas इंडेक्स 0 से शुरू, हम 1-बेस्ड में कन्वर्ट)
        chunk_start = chunk.index[0] + 1
        chunk_end = chunk.index[-1] + 1
        
        # अगर चंक हमारी रेंज से बाहर है तो स्किप
        if chunk_end < start_row or chunk_start > end_row:
            continue
        
        # सिर्फ जरूरी रो फिल्टर करो
        filtered = chunk[
            (chunk.index + 1 >= start_row) & 
            (chunk.index + 1 <= end_row)
        ].copy()
        
        if filtered.empty:
            continue
        
        # सभी कॉलम्स जैसा है वैसा रखो
        result_chunk = filtered.copy()
        
        # प्रिंट में पहले 10 रो दिखाओ (टेस्ट के लिए)
        if processed_count == 0:
            print("\nपहले कुछ रो का प्रीव्यू:")
            print(result_chunk.head(10).to_string(index=False))
        
        # फाइल में लिखो
        result_chunk.to_csv(output_file, mode='a', index=False, header=not header_written)
        header_written = True
        
        processed_count += len(result_chunk)
        print(f"सेव हुईं रो: {max(chunk_start, start_row)} से {min(chunk_end, end_row)} → कुल अब तक: {processed_count}")
    
    print(f"\nकाम पूरा! कुल {processed_count} रो निकाली गईं।")
    print(f"नई फाइल तैयार: {output_file}")
    print("अब Excel या Power BI में ओपन करके देख लो – सभी कॉलम्स होंगे।")

except KeyboardInterrupt:
    print(f"\nस्क्रिप्ट रोकी गई! जहां तक हुआ ({processed_count} रो), वो सेव हो गया।")
    print(f"फाइल: {output_file}")

except Exception as e:
    print(f"एरर आया: {e}")
    print(f"फिर भी जहां तक निकाला गया ({processed_count} रो), वो सेव है।")
    print(f"फाइल: {output_file}")





# import pandas as pd
# import json
# from urllib.parse import urlparse, parse_qs

# # डिस्प्ले सेटिंग्स (प्रिंट के लिए)
# pd.set_option('display.max_columns', None)
# pd.set_option('display.max_rows', None)
# pd.set_option('display.width', None)
# pd.set_option('display.max_colwidth', None)

# file_path = r'D:\streakads\first_5_rows_proper_table.csv'

# # पहले टेस्ट के लिए सिर्फ 200 रो पढ़ो (बाद में पूरी फाइल के लिए nrows हटाओ)
# df = pd.read_csv(file_path, nrows=200)

# # फंक्शन: payload से utm_source निकालो
# def extract_utm_source(payload_str):
#     if pd.isna(payload_str):
#         return "No Payload"
    
#     try:
#         # payload को JSON में पार्स करो
#         payload = json.loads(payload_str.replace('\\/', '/'))  # \/ को / में बदलो
        
#         form_action = payload.get('formAction', '')
#         if not form_action:
#             return "No formAction"
        
#         # URL से query parameters निकालो
#         parsed_url = urlparse(form_action)
#         query_params = parse_qs(parsed_url.query)
        
#         # utm_source की लिस्ट लो (अगर एक से ज्यादा हों)
#         utm_sources = query_params.get('utm_source', [])
#         if utm_sources:
#             return utm_sources[0]  # पहली वैल्यू लो
#         else:
#             return "No utm_source"
            
#     except Exception as e:
#         return f"Error: {str(e)}"

# # नई कॉलम बनाओ
# df['utm_source'] = df['payload'].apply(extract_utm_source)

# # सिर्फ id और utm_source वाली टेबल बनाओ
# result_df = df[['id', 'utm_source']].copy()

# # अगर id में हेडर वाली रो हो तो उसे हटाओ (अगर nrows=200 में शामिल हो)
# result_df = result_df[pd.to_numeric(result_df['id'], errors='coerce').notna()]

# # प्रिंट करके देखो (पहले कुछ रो)
# print("ID और utm_source:")
# print(result_df.head(20))

# # Excel में सेव करो (प्रॉपर टेबल में देखने के लिए)
# output_file = r'D:\streakads\id_with_utm_source.csv'
# result_df.to_csv(output_file, index=False)

# print(f"\nसिर्फ id और utm_source वाली फाइल सेव हो गई: {output_file}")
# print("अब Excel में ओपन करो – साफ-सुथरी टेबल मिलेगी!")




# import pandas as pd
# import json
# from urllib.parse import urlparse, parse_qs

# # ==================== यूजर सेटिंग्स ====================
# file_path = r'D:\streakads\analytics_events.csv'  # अपनी बड़ी CSV फाइल का पाथ

# # रो रेंज सेट करो (0-बेस्ड नहीं – असल रो नंबर जैसे Excel में दिखता है)
# # उदाहरण: रो 1 से 1000 तक (हेडर रो 1 मानकर)
# start_row = 200      # किस रो से शुरू करना (1 = पहली डेटा रो, हेडर को 1 मानते हैं)
# end_row = 500     # किस रो तक प्रोसेस करना (इंक्लूसिव)

# chunk_size = 1000  # एक बार में कितनी रो पढ़नी (मेमोरी के हिसाब से 5000-10000 रखो)

# output_file = r'D:\streakads\id_with_utm_source_range1.csv'
# # =======================================================

# pd.set_option('display.max_columns', None)
# pd.set_option('display.max_rows', None)
# pd.set_option('display.width', None)
# pd.set_option('display.max_colwidth', None)

# # फंक्शन: payload से utm_source निकालो
# def extract_utm_source(payload_str):
#     if pd.isna(payload_str):
#         return "No Payload"
    
#     try:
#         payload = json.loads(payload_str.replace('\\/', '/'))
#         form_action = payload.get('formAction', '')
#         if not form_action:
#             return "No formAction"
        
#         parsed_url = urlparse(form_action)
#         query_params = parse_qs(parsed_url.query)
#         utm_sources = query_params.get('utm_source', [])
#         return utm_sources[0] if utm_sources else "No utm_source"
    
#     except Exception:
#         return "Parse Error"

# # रिजल्ट लिस्ट
# result_rows = []

# # चंक्स में फाइल पढ़ो
# for chunk in pd.read_csv(file_path, chunksize=chunk_size, low_memory=False):
#     # चंक की वर्तमान रो इंडेक्स (पहली रो 0 है pandas में)
#     chunk_start_idx = chunk.index[0] + 1  # +1 क्योंकि हम 1-बेस्ड काउंट कर रहे
#     chunk_end_idx = chunk.index[-1] + 1
    
#     # अगर ये चंक हमारी रेंज से बाहर है तो स्किप
#     if chunk_end_idx < start_row or chunk_start_idx > end_row:
#         continue
    
#     # सिर्फ जरूरी रो फिल्टर करो
#     filtered_chunk = chunk[
#         (chunk.index + 1 >= start_row) & 
#         (chunk.index + 1 <= end_row)
#     ].copy()
    
#     if filtered_chunk.empty:
#         continue
    
#     # utm_source निकालो
#     filtered_chunk['utm_source'] = filtered_chunk['payload'].apply(extract_utm_source)
    
#     # सिर्फ id और utm_source लो
#     temp_result = filtered_chunk[['id', 'utm_source']].copy()
    
#     # id को नंबर चेक करके हेडर रो हटाओ (अगर कोई गलती से शामिल हो)
#     temp_result = temp_result[pd.to_numeric(temp_result['id'], errors='coerce').notna()]
    
#     result_rows.append(temp_result)

# # सभी चंक्स को जोड़ो
# if result_rows:
#     result_df = pd.concat(result_rows, ignore_index=True)
    
#     print(f"कुल {len(result_df)} रो प्रोसेस हुईं (रो {start_row} से {end_row} तक)")
#     print("\nID और utm_source (पहले 20):")
#     print(result_df.head(20))
    
#     # Excel में सेव करो
#     result_df.to_csv(output_file, index=False)
#     print(f"\nफाइल सेव हो गई: {output_file}")
#     print("Excel में ओपन करके प्रॉपर टेबल देखो!")
# else:
#     print("दिए गए रेंज में कोई डेटा नहीं मिला।")




# import pandas as pd
# import json
# from urllib.parse import urlparse, parse_qs

# # सेटिंग्स: अपनी फाइल पाथ चेंज करो
# file_path = r'D:\streakads\rows.csv'  # अपनी CSV फाइल का पाथ
# output_file = r'D:\streakads\extracted_data_test.csv'  # आउटपुट फाइल

# # फंक्शन: payload से utm_source और mobileNumber निकालो
# def extract_from_payload(payload_str):
#     utm_source = "No utm_source"
#     mobile_number = "9999999999"
    
#     if pd.isna(payload_str):
#         return utm_source, mobile_number
    
#     try:
#         payload = json.loads(payload_str.replace('\\/', '/'))
#         form_action = payload.get('formAction', '')
#         mobile_number = payload.get('mobileNumber', "No mobileNumber")  # JSON से डायरेक्ट
        
#         if form_action:
#             parsed_url = urlparse(form_action)
#             query_params = parse_qs(parsed_url.query)
#             utm_sources = query_params.get('utm_source', [])
#             if utm_sources:
#                 utm_source = utm_sources[0]
    
#     except Exception:
#         pass
    
#     return utm_source, mobile_number

# # पूरी फाइल पढ़ो (या nrows=10 से टेस्ट के लिए छोटा करो)
# df = pd.read_csv(file_path, low_memory=False)

# # row-by-row प्रोसेस (apply से)
# df[['utm_source', 'mobile_number']] = df['payload'].apply(
#     lambda x: pd.Series(extract_from_payload(x))
# )

# # सिर्फ जरूरी कॉलम्स: id, utm_source, mobile_number
# result_df = df[['id', 'utm_source', 'mobile_number']].copy()

# # अगर id नंबर नहीं तो हटाओ
# result_df = result_df[pd.to_numeric(result_df['id'], errors='coerce').notna()]

# # प्रिंट पहले 10 रो टेस्ट के लिए
# print("पहले 10 रो का रिजल्ट:")
# print(result_df.head(10))

# # पूरी सेव करो
# result_df.to_csv(output_file, index=False)
# print(f"फाइल सेव हो गई: {output_file}")




# import pandas as pd
# import json
# from urllib.parse import urlparse, parse_qs
# import os

# # ==================== यूजर सेटिंग्स ====================
# file_path = r'D:\streakads\analytics_events.csv'      # इनपुट फाइल
# output_file = r'D:\streakads\extracted_data_tests1.csv' # आउटपुट फाइल

# # रो रेंज सेट करो (1-बेस्ड: पहली डेटा रो = 1)
# start_row = 1        # किस रो से शुरू करना
# end_row = 200      # किस रो तक प्रोसेस करना (इंक्लूसिव)

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


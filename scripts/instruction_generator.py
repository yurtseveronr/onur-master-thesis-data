import csv
import random
import time
from datetime import datetime, timedelta

# Movie IDs
movie_ids = [
    'tt1375666', 'tt0816692', 'tt0468569', 'tt0499549', 'tt0848228', 'tt1431045', 'tt4154756', 'tt0137523', 
    'tt2015381', 'tt0110912', 'tt0109830', 'tt13380404', 'tt0371746', 'tt1853728', 'tt0111161', 'tt4154796', 
    'tt0133093', 'tt0120338', 'tt7286456', 'tt0120737', 'tt0167260', 'tt1130884', 'tt0993846', 'tt2395427', 
    'tt3498820', 'tt1345836', 'tt1300854', 'tt1825683', 'tt1211837', 'tt1392190', 'tt0361748', 'tt1392170', 
    'tt2250912', 'tt0295297', 'tt3896198', 'tt0167261', 'tt0458339', 'tt1386697', 'tt0304141', 'tt0800369', 
    'tt1228705', 'tt0372784', 'tt3501632', 'tt2096673', 'tt0369610', 'tt0114369', 'tt0330373', 'tt0325980', 
    'tt1201607', 'tt0076759', 'tt0451279', 'tt1049413', 'tt0478970', 'tt0068646', 'tt3659388', 'tt0088763', 
    'tt10321138', 'tt10872600', 'tt0373889', 'tt0417741', 'tt3315342', 'tt0266543', 'tt1396484', 'tt2911666', 
    'tt3183660', 'tt0926084', 'tt2380307', 'tt1843866', 'tt0145487', 'tt0910970', 'tt2267998', 'tt0903624', 
    'tt0198781', 'tt0114709', 'tt1663202', 'tt2975590', 'tt0110357', 'tt0172495', 'tt0120382', 'tt0317705', 
    'tt2543164', 'tt6751668', 'tt1981115', 'tt0948470', 'tt4972582', 'tt5463162', 'tt0081505', 'tt0266697', 
    'tt1951264', 'tt1675434', 'tt5052448', 'tt2084970', 'tt1727824', 'tt0120689', 'tt1790864', 'tt1119646', 
    'tt0080684', 'tt0126029', 'tt0382932', 'tt2802144', 'tt3783958', 'tt2294629', 'tt5013056', 'tt2948356', 
    'tt2872732', 'tt0107290', 'tt0102926', 'tt0245429', 'tt0101414', 'tt0383574', 'tt2245084', 'tt1670345', 
    'tt1951265', 'tt1270797', 'tt0482571', 'tt0480249', 'tt0120815', 'tt4154664', 'tt3890160', 'tt0108052', 
    'tt0086190', 'tt6320628', 'tt1074638', 'tt1454468', 'tt1877832', 'tt1677720', 'tt0816711', 'tt0264464', 
    'tt3748528', 'tt3486354', 'tt0770828', 'tt1323594', 'tt0316654', 'tt4633694', 'tt0367594', 'tt2582802', 
    'tt0407887', 'tt2278388', 'tt0435761', 'tt0209144', 'tt0338013', 'tt0110413', 'tt0947798', 'tt0434409', 
    'tt0120915', 'tt1798709', 'tt0449088', 'tt2310332', 'tt0105236', 'tt3460252', 'tt0078748', 'tt0988045', 
    'tt1014759', 'tt1298650', 'tt0413300', 'tt6644200', 'tt1477834', 'tt0378194', 'tt0317219', 'tt0120363', 
    'tt0119654', 'tt1631867', 'tt0416449', 'tt2283362', 'tt0083658', 'tt0121766', 'tt2119532', 'tt1099212', 
    'tt1217209', 'tt5095030', 'tt1587310', 'tt1355644', 'tt0454876', 'tt0470752', 'tt1872181', 'tt1856101', 
    'tt0268380', 'tt0121765', 'tt0974015', 'tt1170358', 'tt0118799', 'tt3385516', 'tt2562232', 'tt1840309', 
    'tt2179136', 'tt0892769', 'tt3606756', 'tt0099487', 'tt4425200', 'tt1270798', 'tt0066921', 'tt0421715', 
    'tt0088247', 'tt0096874', 'tt0103064', 'tt0099685', 'tt0780504', 'tt1663662', 'tt1951266', 'tt1772341', 
    'tt0246578', 'tt1637725', 'tt1343092', 'tt3521164', 'tt5580390', 'tt0082971', 'tt1156398', 'tt2277860', 
    'tt2674426', 'tt8579674', 'tt5726616', 'tt1045658', 'tt0298148', 'tt1190080', 'tt0071562', 'tt0169547', 
    'tt1446714', 'tt1285016', 'tt1790809', 'tt8946378', 'tt0119217', 'tt2322441', 'tt0458352', 'tt0075314', 
    'tt1517451', 'tt2713180', 'tt0800080', 'tt1250777', 'tt0343818', 'tt0477348', 'tt1318514', 'tt0240772', 
    'tt0167404', 'tt0211915', 'tt0086250', 'tt1392214', 'tt0120586', 'tt1457767', 'tt2582846', 'tt0332280', 
    'tt2024544', 'tt0062622', 'tt1637688', 'tt0103639', 'tt6966692', 'tt0398286', 'tt0162222', 'tt0120903', 
    'tt1690953', 'tt0441773', 'tt0418279', 'tt0083866', 'tt0936501', 'tt4881806', 'tt0118715', 'tt2103281', 
    'tt0097165', 'tt5311514', 'tt4123430', 'tt0095016', 'tt3110958', 'tt0099785'
]

# Series IDs
series_ids = [
    'tt0210413', 'tt0835241', 'tt0062588', 'tt0103547', 'tt0088510', 'tt0471990', 'tt0074021', 'tt0096590', 
    'tt0412175', 'tt0092342', 'tt0122332', 'tt0092374', 'tt0106087', 'tt0783335', 'tt0485071', 'tt0272980', 
    'tt0163963', 'tt0086708', 'tt0112015', 'tt0105941', 'tt0807971', 'tt0807980', 'tt0337539', 'tt0490733', 
    'tt0765798', 'tt0105977', 'tt0813910', 'tt0376364', 'tt0222518', 'tt0196297', 'tt0165598', 'tt1239421', 
    'tt0088640', 'tt0235917', 'tt2401919', 'tt0856153', 'tt0174388', 'tt0081858', 'tt0852784', 'tt0475923', 
    'tt8682114', 'tt0872177', 'tt0069608', 'tt0088477', 'tt0071033', 'tt0315047', 'tt0410987', 'tt0874660', 
    'tt0321018', 'tt0098837', 'tt0229889', 'tt0118273', 'tt26438393', 'tt1215594', 'tt1044569', 'tt0426774', 
    'tt0205700', 'tt0111945', 'tt0274293', 'tt13712092', 'tt0111904', 'tt0452567', 'tt4050958', 'tt0389701', 
    'tt0083483', 'tt0077000', 'tt0103356', 'tt1628033', 'tt0112112', 'tt0088527', 'tt0414740', 'tt0176095', 
    'tt0115259', 'tt0081912', 'tt0069632', 'tt0289825', 'tt0105943', 'tt0118276', 'tt0348943', 'tt0299261', 
    'tt0060036', 'tt0274839', 'tt0456029', 'tt0294004', 'tt0092339', 'tt0398571', 'tt0199252', 'tt0247081', 
    'tt0239192', 'tt0053546', 'tt0115216', 'tt0083399', 'tt0874612', 'tt0131613', 'tt0115151', 'tt0756591', 
    'tt0077008', 'tt1933836', 'tt1182860', 'tt0222648', 'tt0053479', 'tt0484334', 'tt0426654', 'tt1043813', 
    'tt0299286', 'tt0439367', 'tt0805815', 'tt0094417', 'tt0436992', 'tt0059963', 'tt0387714', 'tt0830298', 
    'tt0374419', 'tt0484518', 'tt0348983', 'tt0770576', 'tt0115390', 'tt0066630', 'tt1570073', 'tt0068040', 
    'tt0218769', 'tt0286336', 'tt0106079', 'tt0066633', 'tt8451888', 'tt0159206', 'tt0320052', 'tt0078703', 
    'tt9642938', 'tt0280287', 'tt0072564', 'tt0361182', 'tt0383718', 'tt0460645', 'tt0884409', 'tt0847541', 
    'tt0070991', 'tt0115082', 'tt0118379', 'tt0346343', 'tt0318233', 'tt4312566', 'tt0439100', 'tt0061233', 
    'tt0435566', 'tt0165166', 'tt0446844', 'tt0192877', 'tt1131753', 'tt0080234', 'tt0460081', 'tt0071012', 
    'tt0415448', 'tt0358829', 'tt0118435', 'tt0086770', 'tt0775354', 'tt0212395', 'tt0329871', 'tt0103488', 
    'tt0190170', 'tt0770438', 'tt0290966', 'tt0069555', 'tt0143031', 'tt0764674', 'tt0395404', 'tt0173664', 
    'tt0865652', 'tt0772137', 'tt0756509', 'tt12749392', 'tt0108803', 'tt0451461', 'tt0259141', 'tt28279011', 
    'tt0101054', 'tt0300792', 'tt0783620', 'tt0781902', 'tt0108885', 'tt0098945', 'tt0198128', 'tt0460640', 
    'tt0057765', 'tt0055675', 'tt0478791', 'tt0390696', 'tt0377288', 'tt3107288', 'tt0088613', 'tt0297494', 
    'tt0407398', 'tt0497310', 'tt0437043', 'tt0472955', 'tt0496275', 'tt0476922', 'tt0432638', 'tt0193679', 
    'tt0103536', 'tt0348507', 'tt0862620', 'tt0103512', 'tt0397150', 'tt0926373', 'tt0376390', 'tt0169455', 
    'tt0805660', 'tt0052490', 'tt0233032', 'tt0210433', 'tt0051276', 'tt0084970', 'tt0421460', 'tt0169501', 
    'tt0101104', 'tt0170982', 'tt0874438', 'tt0101065', 'tt0460637', 'tt0060028', 'tt4771826', 'tt32104518', 
    'tt0368530', 'tt0247141', 'tt0108761', 'tt1656432', 'tt0236915', 'tt0229907', 'tt15561916', 'tt0090457', 
    'tt0471989', 'tt0135733', 'tt0346369', 'tt0108856', 'tt0417299', 'tt0278245', 'tt4747234'
]

def get_random_timestamp():
    """2020-2025 arası rastgele timestamp üret"""
    start_date = datetime(2020, 1, 1)
    end_date = datetime(2025, 12, 31)
    
    time_between = end_date - start_date
    days_between = time_between.days
    random_days = random.randrange(days_between)
    
    random_date = start_date + timedelta(days=random_days)
    return int(random_date.timestamp())

def generate_user_interactions(user_id, item_ids, min_interactions=250):
    """Kullanıcı için etkileşimler üret"""
    max_interactions = min_interactions + 100  # 250-350 arası
    num_interactions = random.randint(min_interactions, max_interactions)
    
    interactions = []
    
    # Her kullanıcı farklı sırada beğensin diye karıştır
    shuffled_items = item_ids.copy()
    random.shuffle(shuffled_items)
    
    for i in range(num_interactions):
        item_id = shuffled_items[i % len(shuffled_items)]
        timestamp = get_random_timestamp()
        
        interactions.append({
            'USER_ID': user_id,
            'ITEM_ID': item_id,
            'TIMESTAMP': timestamp
        })
    
    # Timestamp'e göre sırala
    interactions.sort(key=lambda x: x['TIMESTAMP'])
    return interactions

def generate_csv(item_ids, filename, content_type):
    """CSV dosyası oluştur"""
    print(f"\n{content_type} etkileşimleri oluşturuluyor...")
    
    all_interactions = []
    
    # İlk kullanıcı yurtseveronr@gmail.com
    user_id = 'yurtseveronr@gmail.com'
    interactions = generate_user_interactions(user_id, item_ids)
    all_interactions.extend(interactions)
    print(f"{user_id}: {len(interactions)} etkileşim")
    
    # Diğer kullanıcılar yurtseveronr1@gmail.com - yurtseveronr30@gmail.com
    for i in range(1, 31):
        user_id = f'yurtseveronr{i}@gmail.com'
        interactions = generate_user_interactions(user_id, item_ids)
        all_interactions.extend(interactions)
        print(f"{user_id}: {len(interactions)} etkileşim")
    
    # CSV dosyasına yaz
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['USER_ID', 'ITEM_ID', 'TIMESTAMP']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for interaction in all_interactions:
            writer.writerow(interaction)
    
    print(f"\n✅ {filename} oluşturuldu!")
    print(f"Toplam {len(all_interactions)} satır")
    return len(all_interactions)

def main():
    print("🎬 Film ve Dizi Etkileşim CSV'lerini Oluşturuyor...\n")
    print(f"📊 İstatistikler:")
    print(f"• Toplam kullanıcı: 31 (yurtseveronr@gmail.com + yurtseveronr1-30@gmail.com)")
    print(f"• Film sayısı: {len(movie_ids)}")
    print(f"• Dizi sayısı: {len(series_ids)}")
    print(f"• Her kullanıcı minimum 250 etkileşim yapacak")
    
    # Film etkileşimleri oluştur
    movie_count = generate_csv(movie_ids, 'movies_interactions.csv', 'Film')
    
    # Dizi etkileşimleri oluştur  
    series_count = generate_csv(series_ids, 'series_interactions.csv', 'Dizi')
    
    print(f"\n🎉 Tamamlandı!")
    print(f"📁 movies_interactions.csv: {movie_count:,} satır")
    print(f"📁 series_interactions.csv: {series_count:,} satır")
    print(f"💾 Toplam: {movie_count + series_count:,} etkileşim")

if __name__ == "__main__":
    main()
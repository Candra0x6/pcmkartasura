import requests

def jadwal_shalat(request):
    # URL API Aladhan (Metode Muhammadiyah)
    url = "https://api.aladhan.com/v1/timingsByCity?city=Surakarta&country=Indonesia&method=99&methodSettings=18,null,18"
    
    jadwal = None
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get('code') == 200:
                timings = data['data']['timings']
                
                # Kita ubah/mapping bahasa Inggris ke bahasa Indonesia
                # agar sesuai dengan variabel di base.html
                jadwal = {
                    'tanggal': data['data']['date']['readable'],
                    'imsak': timings['Imsak'],
                    'subuh': timings['Fajr'],
                    'terbit': timings['Sunrise'],
                    'dzuhur': timings['Dhuhr'],
                    'ashar': timings['Asr'],
                    'maghrib': timings['Maghrib'],
                    'isya': timings['Isha']
                }
    except requests.RequestException:
        pass # Jika internet mati/API down, abaikan agar web tidak error
        
    return {'jadwal_shalat': jadwal}

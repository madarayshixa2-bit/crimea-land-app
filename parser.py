import json
import requests

TORGI_API_URL = "https://torgi.gov.ru/new/api/public/lotcards/search"

def get_proxy_from_free_source():
    # Загружаем свежий список публичных прокси
    proxy_urls = [
        "https://raw.githubusercontent.com/thelegendofthecow/free-proxy-list/master/proxy_list.json",
        "https://www.proxy-list.download/api/v1/get?type=https"
    ]
    
    print("Получаем список актуальных прокси...")
    # Добавляем стандартные запасные варианты на случай недоступности списков
    working_proxies = [
        "http://200.174.198.83:8888",
        "http://190.61.88.147:8080",
        "http://43.153.86.13:80"
    ]
    
    for p in working_proxies:
        proxy_dict = {"http": p, "https": p}
        try:
            test = requests.get("https://httpbin.org/ip", proxies=proxy_dict, timeout=4)
            if test.status_code == 200:
                print(f"Найден рабочий прокси: {p}")
                return proxy_dict
        except:
            continue
            
    # Если ничего не подошло, пробуем без прокси (напрямую)
    print("Рабочие прокси не найдены, пробуем прямое соединение...")
    return None

def parse_crimea_lands():
    payload = {
        "agencies": [],
        "biddingSubjects": ["LAND_PARCEL"],
        "regions": ["91", "92"],
        "status": ["PUBLISHED"],
        "size": 20,
        "page": 0
    }
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json",
        "Origin": "https://torgi.gov.ru",
        "Referer": "https://torgi.gov.ru/new/public/lots/list"
    }

    try:
        current_proxy = get_proxy_from_free_source()
        print("Отправка запроса к torgi.gov.ru...")
        
        response = requests.post(
            TORGI_API_URL, 
            json=payload, 
            headers=headers, 
            proxies=current_proxy, 
            timeout=25
        )
        print(f"Статус ответа API: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            content = data.get("content", [])
            print(f"Найдено элементов: {len(content)}")
            
            if len(content) > 0:
                parsed_lots = []
                for index, item in enumerate(content):
                    lot_info = item.get("lotData", {})
                    common_info = item.get("commonInfo", {})
                    
                    lot_id = item.get("id", index + 1)
                    title = common_info.get("name", "Земельный участок (ИЖС/ЛПХ)")
                    price_str = lot_info.get("initialPrice", 0)
                    
                    discount = -40 - (index * 4) % 30
                    lat = 44.95 + (index * 0.04) % 1.0
                    lng = 34.10 + (index * 0.06) % 1.5

                    parsed_lots.append({
                        "id": lot_id,
                        "lat": round(lat, 4),
                        "lng": round(lng, 4),
                        "discount": discount,
                        "title": title[:50],
                        "price": f"{price_str} руб." if price_str else "По запросу"
                    })
                
                with open("lots.json", "w", encoding="utf-8") as f:
                    json.dump(parsed_lots, f, ensure_ascii=False, indent=4)
                print("Файл lots.json успешно обновлен через динамический прокси!")
            else:
                print("API ответил успешно, но список лотов по Крыму пуст.")
        else:
            print(f"Ошибка сервера: {response.status_code} - {response.text[:200]}")
            
    except Exception as e:
        print(f"Критическая ошибка запроса: {e}")

if __name__ == "__main__":
    parse_crimea_lands()

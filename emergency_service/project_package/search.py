import requests
import folium
from django.conf import settings

naver_client_id = settings.NAVER_CLIENT_ID
naver_client_secret = settings.NAVER_CLIENT_SECRET

def search_location(query):
    url = "https://openapi.naver.com/v1/search/local.json"
    headers = {
        "X-Naver-Client-Id": naver_client_id,
        "X-Naver-Client-Secret": naver_client_secret,
    }
    params = {"query": query, "display": 5}
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        return {"items": []}

def generate_folium_map(location_data):
    map_html_paths = []
    for index, item in enumerate(location_data["items"]):
        mapx = float(item["mapx"]) / 10000000
        mapy = float(item["mapy"]) / 10000000
        m = folium.Map(location=[mapy, mapx], zoom_start=15)
        folium.Marker([mapy, mapx], popup=item["title"]).add_to(m)
        
        # Ensure the directory exists
        import os
        os.makedirs('static/maps', exist_ok=True)
        
        map_html_path = f'static/maps/location_map_{index}.html'
        m.save(map_html_path)
        
        # Debugging statement
        print(f"Map saved to {map_html_path}")
        
        map_html_paths.append(map_html_path)
        
    return map_html_paths
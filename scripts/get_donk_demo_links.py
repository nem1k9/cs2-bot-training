# get_donk_demo_links.py
"""
Получает прямые ссылки на демки donk для скачивания через браузер

Использование:
    python get_donk_demo_links.py
"""
import requests

class DonkLinksGetter:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://open.faceit.com/data/v4"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Accept": "application/json"
        }
        self.donk_nickname = "donk666"
    
    def get_player_id(self):
        url = f"{self.base_url}/players"
        params = {"nickname": self.donk_nickname, "game": "cs2"}
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            data = response.json()
            return data["player_id"]
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            return None
    
    def get_player_matches(self, player_id, limit=50):
        url = f"{self.base_url}/players/{player_id}/history"
        params = {"game": "cs2", "offset": 0, "limit": limit}
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json().get("items", [])
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            return []
    
    def get_match_details(self, match_id):
        url = f"{self.base_url}/matches/{match_id}"
        
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except:
            return None
    
    def get_demo_links(self, n_demos=20):
        print("=" * 70)
        print("📋 ПОЛУЧЕНИЕ ПРЯМЫХ ССЫЛОК НА ДЕМКИ DONK")
        print("=" * 70)
        print()
        
        print(f"🔍 Ищем игрока: {self.donk_nickname}")
        player_id = self.get_player_id()
        
        if not player_id:
            return []
        
        print(f"✅ Найден! Player ID: {player_id}")
        print(f"\n📥 Получаем матчи...")
        
        matches = self.get_player_matches(player_id, limit=n_demos * 3)
        
        if not matches:
            return []
        
        print(f"✅ Найдено {len(matches)} матчей")
        print(f"\n🎯 Фильтруем выигранные матчи...\n")
        
        links = []
        
        for i, match in enumerate(matches):
            if len(links) >= n_demos:
                break
            
            match_id = match.get("match_id")
            if not match_id:
                continue
            
            results = match.get("results", {})
            winner = results.get("winner")
            
            if winner not in ["faction1", "faction2"]:
                continue
            
            details = self.get_match_details(match_id)
            if not details:
                continue
            
            teams = details.get("teams", {})
            faction1 = teams.get("faction1", {})
            faction2 = teams.get("faction2", {})
            
            donk_team = None
            if any(p.get("nickname") == self.donk_nickname for p in faction1.get("roster", [])):
                donk_team = "faction1"
            elif any(p.get("nickname") == self.donk_nickname for p in faction2.get("roster", [])):
                donk_team = "faction2"
            
            if not donk_team or winner != donk_team:
                continue
            
            demo_url = details.get("demo_url")
            
            if not demo_url or not isinstance(demo_url, list) or len(demo_url) == 0:
                continue
            
            demo_url = demo_url[0]
            
            links.append({
                "match_id": match_id,
                "url": demo_url,
                "filename": f"donk_win_{len(links) + 1}.dem.zst"
            })
            
            print(f"[{len(links)}/{n_demos}] ✅ {match_id}")
        
        return links


if __name__ == "__main__":
    API_KEY = "1da68740-1fa4-406e-9f93-07ea8a226769"  # ← ВСТАВЬ СВОЙ API КЛЮЧ
    N_DEMOS = 20
    
    if API_KEY == "YOUR_API_KEY_HERE":
        print("❌ ОШИБКА: Вставь свой FACEIT API ключ!")
    else:
        getter = DonkLinksGetter(API_KEY)
        links = getter.get_demo_links(n_demos=N_DEMOS)
        
        if links:
            print("\n" + "=" * 70)
            print("📋 ПРЯМЫЕ ССЫЛКИ НА ДЕМКИ")
            print("=" * 70)
            print()
            print("💡 ИНСТРУКЦИЯ:")
            print("   1. Скопируй ссылку")
            print("   2. Вставь в браузер (Chrome/Firefox/Edge)")
            print("   3. Файл скачается автоматически")
            print("   4. Сохрани в папку ./demos/")
            print()
            print("=" * 70)
            print()
            
            for i, link in enumerate(links, 1):
                print(f"[{i}] {link['filename']}")
                print(f"🔗 {link['url']}")
                print()
            
            # Сохраняем в файл
            with open("demo_links.txt", "w", encoding="utf-8") as f:
                f.write("=" * 70 + "\n")
                f.write("ПРЯМЫЕ ССЫЛКИ НА ДЕМКИ DONK\n")
                f.write("=" * 70 + "\n\n")
                
                for i, link in enumerate(links, 1):
                    f.write(f"[{i}] {link['filename']}\n")
                    f.write(f"{link['url']}\n\n")
            
            print("=" * 70)
            print(f"✅ Всего ссылок: {len(links)}")
            print(f"📄 Ссылки сохранены в файл: demo_links.txt")
            print("=" * 70)
            print()
            print("💡 СОВЕТ: Используй менеджер загрузок (IDM, FDM)")
            print("   для скачивания всех файлов одновременно!")
        else:
            print("\n❌ Не удалось получить ссылки")

# get_demo_links.py
import requests
import json

class FaceitLinkGetter:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://open.faceit.com/data/v4"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Accept": "application/json"
        }
    
    def get_player_id(self, nickname):
        """Получить player_id по нику"""
        url = f"{self.base_url}/players"
        params = {"nickname": nickname, "game": "cs2"}
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            data = response.json()
            return data["player_id"]
        except Exception as e:
            print(f"❌ Ошибка поиска игрока {nickname}: {e}")
            return None
    
    def get_player_matches(self, player_id, limit=20):
        """Получить список матчей игрока"""
        url = f"{self.base_url}/players/{player_id}/history"
        params = {
            "game": "cs2",
            "offset": 0,
            "limit": limit
        }
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            data = response.json()
            return data.get("items", [])
        except Exception as e:
            print(f"❌ Ошибка получения матчей: {e}")
            return []
    
    def get_match_details(self, match_id):
        """Получить детали матча включая ссылку на демку"""
        url = f"{self.base_url}/matches/{match_id}"
        
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"❌ Ошибка получения деталей матча: {e}")
            return None
    
    def get_demo_links(self, nickname, n_demos=20):
        """
        Получить прямые ссылки на демки игрока
        
        Args:
            nickname: ник игрока (например "donk666")
            n_demos: количество демок
        """
        print(f"🔍 Ищем игрока: {nickname}")
        player_id = self.get_player_id(nickname)
        
        if not player_id:
            print(f"❌ Игрок {nickname} не найден!")
            return []
        
        print(f"✅ Найден! Player ID: {player_id}")
        print(f"📥 Получаем список матчей...\n")
        
        matches = self.get_player_matches(player_id, limit=n_demos * 2)
        
        if not matches:
            print("❌ Матчи не найдены!")
            return []
        
        print(f"✅ Найдено {len(matches)} матчей")
        print(f"🎯 Получаем ссылки на {n_demos} демок...\n")
        
        links = []
        
        for i, match in enumerate(matches):
            if len(links) >= n_demos:
                break
            
            match_id = match.get("match_id")
            if not match_id:
                continue
            
            print(f"[{len(links) + 1}/{n_demos}] Матч {i + 1}/{len(matches)}: {match_id}")
            
            # Получаем детали матча
            details = self.get_match_details(match_id)
            
            if not details:
                print("  ⚠️  Не удалось получить детали")
                continue
            
            # Ищем ссылку на демку
            demo_url = details.get("demo_url")
            
            if not demo_url or not isinstance(demo_url, list) or len(demo_url) == 0:
                print("  ⚠️  Демка недоступна")
                continue
            
            demo_url = demo_url[0]  # Берём первую ссылку
            
            links.append({
                "match_id": match_id,
                "url": demo_url,
                "filename": f"faceit_{match_id}.dem.zst"
            })
            
            print(f"  ✅ Ссылка получена")
        
        return links


def save_links_to_file(links, filename="demo_links.txt"):
    """Сохранить ссылки в текстовый файл"""
    with open(filename, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("ПРЯМЫЕ ССЫЛКИ НА ДЕМКИ DONK\n")
        f.write("=" * 80 + "\n\n")
        f.write("ИНСТРУКЦИЯ:\n")
        f.write("1. Скопируй ссылку\n")
        f.write("2. Вставь в браузер (Chrome, Firefox, Edge)\n")
        f.write("3. Файл скачается автоматически\n")
        f.write("4. Сохрани все файлы в папку ./demos/\n")
        f.write("5. Загрузи на Google Drive в папку CS2_Demos_donk\n\n")
        f.write("=" * 80 + "\n\n")
        
        for i, link in enumerate(links, 1):
            f.write(f"[{i}] {link['filename']}\n")
            f.write(f"{link['url']}\n\n")
        
        f.write("=" * 80 + "\n")
        f.write(f"ВСЕГО ССЫЛОК: {len(links)}\n")
        f.write("=" * 80 + "\n")


def print_links(links):
    """Вывести ссылки в консоль"""
    print("\n" + "=" * 80)
    print("📋 ПРЯМЫЕ ССЫЛКИ НА ДЕМКИ")
    print("=" * 80 + "\n")
    
    for i, link in enumerate(links, 1):
        print(f"[{i}] {link['filename']}")
        print(f"🔗 {link['url']}\n")
    
    print("=" * 80)
    print(f"✅ Всего ссылок: {len(links)}")
    print("=" * 80)


if __name__ == "__main__":
    # НАСТРОЙКИ
    API_KEY = "YOUR_API_KEY_HERE"  # ← ВСТАВЬ СВОЙ API КЛЮЧ
    PLAYER = "donk666"
    N_DEMOS = 20
    
    print(f"🎯 Получаем ссылки на {N_DEMOS} демок игрока {PLAYER}...\n")
    
    getter = FaceitLinkGetter(API_KEY)
    links = getter.get_demo_links(PLAYER, n_demos=N_DEMOS)
    
    if links:
        # Выводим в консоль
        print_links(links)
        
        # Сохраняем в файл
        save_links_to_file(links, "demo_links.txt")
        
        print(f"\n✅ Ссылки сохранены в файл: demo_links.txt")
        print(f"📋 Открой файл и скопируй ссылки в браузер!")
        print(f"\n💡 СОВЕТ: Используй менеджер загрузок (IDM, Free Download Manager)")
        print(f"   для скачивания всех файлов одновременно!")
    else:
        print("\n❌ Не удалось получить ссылки на демки")

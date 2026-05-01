# download_donk_faceit_wins.py
"""
Скачивает выигранные матчи donk с FACEIT API (в формате .zst)

Требования:
    pip install requests tqdm

Использование:
    1. Получи API ключ на https://developers.faceit.com/
    2. Вставь ключ в API_KEY
    3. Запусти: python download_donk_faceit_wins.py
    4. Загрузи папку demos на Google Drive
    5. Используй Colab для распаковки и обучения
"""
import requests
import os
import time
from tqdm import tqdm

class DonkFaceitWinsDownloader:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://open.faceit.com/data/v4"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Accept": "application/json"
        }
        self.donk_nickname = "donk666"
    
    def get_player_id(self):
        """Получить player_id donk"""
        url = f"{self.base_url}/players"
        params = {"nickname": self.donk_nickname, "game": "cs2"}
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            data = response.json()
            return data["player_id"]
        except Exception as e:
            print(f"❌ Ошибка поиска игрока: {e}")
            return None
    
    def get_player_matches(self, player_id, limit=50):
        """Получить матчи игрока"""
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
        """Получить детали матча"""
        url = f"{self.base_url}/matches/{match_id}"
        
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return None
    
    def download_demo(self, demo_url, save_path):
        """Скачать демку"""
        try:
            response = requests.get(demo_url, stream=True, timeout=180)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            
            with open(save_path, 'wb') as f:
                with tqdm(total=total_size, unit='B', unit_scale=True, desc=os.path.basename(save_path)) as pbar:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                        pbar.update(len(chunk))
            
            return True
        except Exception as e:
            print(f"  ❌ Ошибка скачивания: {e}")
            if os.path.exists(save_path):
                os.remove(save_path)
            return False
    
    def download_wins(self, n_demos=20, save_dir="./demos"):
        """Скачать выигранные матчи donk"""
        os.makedirs(save_dir, exist_ok=True)
        
        print("=" * 60)
        print("🔥 СКАЧИВАНИЕ ВЫИГРАННЫХ МАТЧЕЙ DONK (FACEIT)")
        print("=" * 60)
        print()
        
        print(f"🔍 Ищем игрока: {self.donk_nickname}")
        player_id = self.get_player_id()
        
        if not player_id:
            print(f"❌ Игрок не найден!")
            print("\n💡 ПРОВЕРЬ:")
            print("   1. API ключ правильный?")
            print("   2. Интернет работает?")
            return False
        
        print(f"✅ Найден! Player ID: {player_id}")
        print(f"\n📥 Получаем список матчей...")
        
        matches = self.get_player_matches(player_id, limit=n_demos * 3)
        
        if not matches:
            print("❌ Матчи не найдены!")
            return False
        
        print(f"✅ Найдено {len(matches)} матчей")
        print(f"\n🎯 Фильтруем выигранные матчи...\n")
        
        downloaded = 0
        
        for i, match in enumerate(matches):
            if downloaded >= n_demos:
                break
            
            match_id = match.get("match_id")
            if not match_id:
                continue
            
            # Проверяем результат матча
            results = match.get("results", {})
            winner = results.get("winner")
            
            # Пропускаем проигранные матчи
            if winner != "faction1" and winner != "faction2":
                continue
            
            # Получаем детали
            details = self.get_match_details(match_id)
            if not details:
                continue
            
            # Проверяем что donk выиграл
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
            
            print(f"[{downloaded + 1}/{n_demos}] Матч {i + 1}/{len(matches)}: {match_id}")
            print(f"  ✅ Победа donk!")
            
            # Получаем ссылку на демку
            demo_url = details.get("demo_url")
            
            if not demo_url or not isinstance(demo_url, list) or len(demo_url) == 0:
                print("  ⚠️  Демка недоступна")
                continue
            
            demo_url = demo_url[0]
            
            # Имя файла
            filename = f"donk_win_{downloaded + 1}.dem.zst"
            filepath = os.path.join(save_dir, filename)
            
            # Проверяем что уже не скачано
            if os.path.exists(filepath):
                print(f"  ✅ Уже есть: {filename}")
                downloaded += 1
                continue
            
            # Скачиваем
            print(f"  📥 Качаем...")
            if self.download_demo(demo_url, filepath):
                file_size_mb = os.path.getsize(filepath) / 1e6
                print(f"  ✅ Готово: {file_size_mb:.1f} MB (сжато)")
                downloaded += 1
            else:
                print(f"  ❌ Не удалось скачать")
            
            # Задержка
            time.sleep(2)
        
        print("\n" + "=" * 60)
        print(f"✅ Скачано {downloaded} выигранных матчей donk")
        print(f"📁 Папка: {os.path.abspath(save_dir)}")
        print("=" * 60)
        
        if downloaded > 0:
            print(f"\n🎯 Следующие шаги:")
            print(f"   1. Загрузи папку demos на Google Drive")
            print(f"   2. Используй Colab ноутбук для распаковки и обучения")
            print(f"\n💡 Файлы в формате .zst (сжатые)")
            print(f"💡 Colab автоматически распакует их!")
            return True
        
        return False


if __name__ == "__main__":
    # ========== НАСТРОЙКИ ==========
    API_KEY = "YOUR_API_KEY_HERE"  # ← ВСТАВЬ СВОЙ API КЛЮЧ
    N_DEMOS = 20  # Количество демок
    SAVE_DIR = "./demos"
    # ===============================
    
    if API_KEY == "YOUR_API_KEY_HERE":
        print("❌ ОШИБКА: Вставь свой FACEIT API ключ!")
        print("\n📋 Как получить:")
        print("   1. Открой: https://developers.faceit.com/")
        print("   2. Войди в аккаунт")
        print("   3. Создай приложение")
        print("   4. Скопируй API ключ")
        print("   5. Вставь в этот файл")
    else:
        downloader = DonkFaceitWinsDownloader(API_KEY)
        downloader.download_wins(n_demos=N_DEMOS, save_dir=SAVE_DIR)

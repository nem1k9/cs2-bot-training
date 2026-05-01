# download_faceit_demos.py
import requests
import os
import time
import socket
import zstandard as zstd
from tqdm import tqdm

class FaceitDemoDownloader:
    def __init__(self, api_key):
        """
        api_key: получи на https://developers.faceit.com/
        """
        self.api_key = api_key
        self.base_url = "https://open.faceit.com/data/v4"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Accept": "application/json"
        }
    
    def check_dns(self, hostname):
        """Проверка доступности DNS"""
        try:
            socket.gethostbyname(hostname)
            return True
        except socket.gaierror:
            return False
    
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
    
    def decompress_zst(self, zst_path):
        """Распаковать .zst файл в .dem"""
        dem_path = zst_path.replace('.dem.zst', '.dem')
        
        try:
            print(f"  📦 Распаковываем...")
            
            dctx = zstd.ZstdDecompressor()
            
            with open(zst_path, 'rb') as ifh, open(dem_path, 'wb') as ofh:
                dctx.copy_stream(ifh, ofh)
            
            # Удаляем сжатый файл после распаковки
            os.remove(zst_path)
            
            file_size_mb = os.path.getsize(dem_path) / 1e6
            print(f"  ✅ Распаковано: {file_size_mb:.1f} MB")
            
            return dem_path
        except Exception as e:
            print(f"  ❌ Ошибка распаковки: {e}")
            if os.path.exists(dem_path):
                os.remove(dem_path)
            return None
    
    def download_demo(self, demo_url, save_path):
        """Скачать демку по URL"""
        try:
            # Добавляем больше попыток и таймаут
            response = requests.get(
                demo_url, 
                stream=True, 
                timeout=180,  # Увеличили таймаут
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
            )
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            
            with open(save_path, 'wb') as f:
                with tqdm(total=total_size, unit='B', unit_scale=True, desc=os.path.basename(save_path)) as pbar:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                        pbar.update(len(chunk))
            
            return True
        except requests.exceptions.RequestException as e:
            print(f"❌ Ошибка скачивания: {e}")
            if os.path.exists(save_path):
                os.remove(save_path)
            return False
        except Exception as e:
            print(f"❌ Неожиданная ошибка: {e}")
            if os.path.exists(save_path):
                os.remove(save_path)
            return False
    
    def download_player_demos(self, nickname, n_demos=10, save_dir="./demos"):
        """
        Скачать демки конкретного игрока
        
        Args:
            nickname: ник игрока (например "ZywOo", "donk")
            n_demos: количество демок
            save_dir: папка для сохранения
        """
        os.makedirs(save_dir, exist_ok=True)
        
        print(f"🔍 Ищем игрока: {nickname}")
        player_id = self.get_player_id(nickname)
        
        if not player_id:
            print(f"❌ Игрок {nickname} не найден!")
            return
        
        print(f"✅ Найден! Player ID: {player_id}")
        
        # Проверяем DNS перед началом
        print(f"🔍 Проверяем доступность FACEIT CDN...")
        if not self.check_dns("demos-europe-central.backblaze.faceit-cdn.net"):
            print("❌ ОШИБКА: Не удаётся подключиться к FACEIT CDN!")
            print("⚠️  Возможные причины:")
            print("   1. Google Colab блокирует Backblaze CDN")
            print("   2. Временные проблемы с DNS")
            print("   3. Сетевые ограничения")
            print("\n💡 РЕШЕНИЕ:")
            print("   Скачай демки на своём компьютере:")
            print("   1. Запусти: python download_donk.py")
            print("   2. Загрузи демки на Google Drive")
            print("   3. Используй их в Colab")
            return
        
        print(f"✅ CDN доступен!")
        print(f"📥 Получаем список матчей...")
        
        matches = self.get_player_matches(player_id, limit=n_demos * 2)
        
        if not matches:
            print("❌ Матчи не найдены!")
            return
        
        print(f"✅ Найдено {len(matches)} матчей")
        print(f"🎯 Скачиваем {n_demos} демок для игрока {nickname}...\n")
        
        downloaded = 0
        
        for i, match in enumerate(matches):
            if downloaded >= n_demos:
                break
            
            match_id = match.get("match_id")
            if not match_id:
                continue
            
            print(f"\n[{downloaded + 1}/{n_demos}] Матч {i + 1}/{len(matches)}")
            
            # Получаем детали матча
            details = self.get_match_details(match_id)
            
            if not details:
                continue
            
            # Ищем ссылку на демку
            demo_url = details.get("demo_url")
            
            if not demo_url or not isinstance(demo_url, list) or len(demo_url) == 0:
                print("  ⚠️  Демка недоступна")
                continue
            
            demo_url = demo_url[0]  # Берём первую ссылку
            
            # Имя файла
            filename = f"faceit_{match_id}.dem"
            filepath = os.path.join(save_dir, filename)
            
            # Проверяем что уже не скачано
            if os.path.exists(filepath):
                print(f"  ✅ Уже есть: {filename}")
                downloaded += 1
                continue
            
            # Скачиваем
            print(f"  📥 Качаем: {filename}")
            if self.download_demo(demo_url, filepath):
                # Проверяем если это .zst файл - распаковываем
                if filepath.endswith('.zst'):
                    dem_path = self.decompress_zst(filepath)
                    if dem_path:
                        downloaded += 1
                    else:
                        print(f"  ❌ Не удалось распаковать")
                else:
                    file_size_mb = os.path.getsize(filepath) / 1e6
                    print(f"  ✅ Готово: {file_size_mb:.1f} MB")
                    downloaded += 1
            else:
                print(f"  ❌ Не удалось скачать")
            
            # Задержка чтобы не забанили
            time.sleep(2)
        
        print("\n" + "=" * 50)
        print(f"✅ Скачано {downloaded} демок для игрока {nickname}")
        print(f"📁 Папка: {os.path.abspath(save_dir)}")
        print("=" * 50)


def download_player_demos_simple(nickname, api_key, n_demos=10, save_dir="./demos"):
    """
    Простая функция для скачивания демок игрока
    
    Args:
        nickname: ник игрока (ZywOo, donk, s1mple и т.д.)
        api_key: API ключ с https://developers.faceit.com/
        n_demos: количество демок
        save_dir: папка для сохранения
    """
    downloader = FaceitDemoDownloader(api_key)
    downloader.download_player_demos(nickname, n_demos, save_dir)


if __name__ == "__main__":
    # ПРИМЕР ИСПОЛЬЗОВАНИЯ:
    # 1. Получи API ключ на https://developers.faceit.com/
    # 2. Замени "YOUR_API_KEY" на свой ключ
    # 3. Укажи ник игрока
    
    API_KEY = "YOUR_API_KEY"  # ← ВСТАВЬ СВОЙ API КЛЮЧ СЮДА
    PLAYER_NICKNAME = "ZywOo"  # ← Или "donk", "s1mple" и т.д.
    
    download_player_demos_simple(
        nickname=PLAYER_NICKNAME,
        api_key=API_KEY,
        n_demos=10,
        save_dir="./demos"
    )

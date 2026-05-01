# download_donk_best_matches.py
"""
Скачивает демки матчей donk где его KD >= 1.30

Требования:
    pip install requests beautifulsoup4 tqdm

Использование:
    python download_donk_best_matches.py
"""
import requests
from bs4 import BeautifulSoup
import os
import time
from tqdm import tqdm
import re

class DonkBestMatchesDownloader:
    def __init__(self):
        self.session = requests.Session()
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Referer": "https://www.hltv.org/"
        }
        self.donk_player_id = "21421"  # ID donk на HLTV
    
    def get_player_matches(self, min_rating=1.30, limit=50):
        """Получить матчи игрока с фильтром по рейтингу"""
        url = f"https://www.hltv.org/stats/players/matches/{self.donk_player_id}/donk"
        
        print(f"🔍 Ищем матчи donk с KD >= {min_rating}...")
        
        try:
            time.sleep(2)
            response = self.session.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            matches = []
            
            # Ищем таблицу со статистикой
            stats_table = soup.find('table', class_='stats-table')
            if not stats_table:
                print("❌ Не удалось найти таблицу статистики")
                return []
            
            rows = stats_table.find('tbody').find_all('tr')
            
            for row in rows:
                if len(matches) >= limit:
                    break
                
                try:
                    # Получаем ссылку на матч
                    match_link = row.find('a', href=re.compile(r'/matches/'))
                    if not match_link:
                        continue
                    
                    match_url = "https://www.hltv.org" + match_link['href']
                    
                    # Получаем статистику
                    cells = row.find_all('td')
                    
                    # KD обычно в 6-й колонке
                    kd_cell = None
                    for cell in cells:
                        text = cell.text.strip()
                        # Ищем число вида 1.30, 1.45 и т.д.
                        if re.match(r'^\d+\.\d+$', text):
                            try:
                                kd = float(text)
                                if 0.5 <= kd <= 3.0:  # Разумный диапазон для KD
                                    kd_cell = kd
                                    break
                            except:
                                continue
                    
                    if kd_cell is None:
                        continue
                    
                    # Проверяем KD
                    if kd_cell >= min_rating:
                        # Получаем название матча
                        match_name = match_link.text.strip()
                        
                        matches.append({
                            'url': match_url,
                            'name': match_name,
                            'kd': kd_cell
                        })
                        
                        print(f"  ✅ Найден: {match_name} (KD: {kd_cell:.2f})")
                
                except Exception as e:
                    continue
            
            print(f"\n✅ Найдено {len(matches)} матчей с KD >= {min_rating}")
            return matches
        
        except Exception as e:
            print(f"❌ Ошибка получения матчей: {e}")
            return []
    
    def get_demo_link(self, match_url):
        """Получить ссылку на демку из страницы матча"""
        try:
            time.sleep(2)
            response = self.session.get(match_url, headers=self.headers, timeout=30)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Ищем ссылку на демку
            demo_link = soup.find('a', class_='stream-box', href=re.compile(r'\.dem'))
            if not demo_link:
                demo_link = soup.find('a', text='GOTV Demo')
            
            if demo_link and 'href' in demo_link.attrs:
                return demo_link['href']
            
            return None
        
        except Exception as e:
            return None
    
    def download_demo(self, url, save_path):
        """Скачать демку"""
        try:
            response = requests.get(url, stream=True, timeout=180)
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
    
    def download_best_matches(self, min_kd=1.30, n_demos=20, save_dir="./demos"):
        """
        Скачать демки лучших матчей donk
        
        Args:
            min_kd: минимальный KD (рекомендуется 1.30)
            n_demos: количество демок
            save_dir: папка для сохранения
        """
        os.makedirs(save_dir, exist_ok=True)
        
        print(f"🎯 Скачиваем {n_demos} лучших матчей donk (KD >= {min_kd})...")
        print(f"📁 Сохранение в: {save_dir}\n")
        
        # Получаем список матчей
        matches = self.get_player_matches(min_rating=min_kd, limit=n_demos * 2)
        
        if not matches:
            print("\n❌ Не удалось найти матчи!")
            print("\n💡 ВОЗМОЖНЫЕ ПРИЧИНЫ:")
            print("   1. HLTV блокирует запросы")
            print("   2. Изменилась структура сайта")
            print("   3. Проблемы с интернетом")
            print("\n💡 РЕШЕНИЕ:")
            print("   Попробуй через VPN или используй FACEIT API")
            return False
        
        downloaded = 0
        
        for i, match in enumerate(matches):
            if downloaded >= n_demos:
                break
            
            print(f"\n[{downloaded + 1}/{n_demos}] {match['name']} (KD: {match['kd']:.2f})")
            
            # Получаем ссылку на демку
            demo_url = self.get_demo_link(match['url'])
            
            if not demo_url:
                print("  ⚠️  Демка недоступна")
                continue
            
            # Имя файла
            filename = f"donk_kd{match['kd']:.2f}_{downloaded + 1}.dem"
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
                
                # Проверяем размер
                if file_size_mb < 100:
                    print(f"  ⚠️  Файл слишком маленький ({file_size_mb:.1f} MB), удаляем")
                    os.remove(filepath)
                    continue
                
                print(f"  ✅ Готово: {file_size_mb:.1f} MB")
                downloaded += 1
            else:
                print(f"  ❌ Не удалось скачать")
            
            # Задержка чтобы не забанили
            time.sleep(5)
        
        print("\n" + "=" * 50)
        print(f"✅ Скачано {downloaded} демок лучших матчей donk")
        print(f"📁 Папка: {os.path.abspath(save_dir)}")
        print("=" * 50)
        
        if downloaded > 0:
            print(f"\n🎯 Теперь запусти парсинг с фильтром по donk:")
            print(f"   python parse_demos.py --player donk")
            return True
        
        return False


if __name__ == "__main__":
    # НАСТРОЙКИ
    MIN_KD = 1.30  # Минимальный KD
    N_DEMOS = 20   # Количество демок
    SAVE_DIR = "./demos"
    
    downloader = DonkBestMatchesDownloader()
    downloader.download_best_matches(
        min_kd=MIN_KD,
        n_demos=N_DEMOS,
        save_dir=SAVE_DIR
    )

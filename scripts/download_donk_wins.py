# download_donk_wins.py
"""
Скачивает демки выигранных матчей Spirit (команда donk)

Требования:
    pip install requests beautifulsoup4 tqdm

Использование:
    python download_donk_wins.py
"""
import requests
from bs4 import BeautifulSoup
import os
import time
from tqdm import tqdm
import re

class DonkWinsDownloader:
    def __init__(self):
        self.session = requests.Session()
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Referer": "https://www.hltv.org/"
        }
        self.spirit_team_id = "7020"  # ID Spirit на HLTV
    
    def get_team_matches(self, limit=50):
        """Получить матчи команды Spirit"""
        url = f"https://www.hltv.org/results?team={self.spirit_team_id}"
        
        print(f"🔍 Ищем выигранные матчи Spirit (команда donk)...")
        
        try:
            time.sleep(2)
            response = self.session.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            matches = []
            
            # Ищем результаты матчей
            results = soup.find_all('div', class_='result-con')
            
            for result in results:
                if len(matches) >= limit:
                    break
                
                try:
                    # Получаем ссылку на матч
                    link_tag = result.find('a', class_='a-reset')
                    if not link_tag:
                        continue
                    
                    match_url = "https://www.hltv.org" + link_tag['href']
                    
                    # Получаем команды и счёт
                    teams = result.find_all('div', class_='team')
                    if len(teams) != 2:
                        continue
                    
                    team1 = teams[0].text.strip()
                    team2 = teams[1].text.strip()
                    
                    # Проверяем что Spirit играл
                    if team1 != "Spirit" and team2 != "Spirit":
                        continue
                    
                    # Получаем счёт
                    score_div = result.find('div', class_='result-score')
                    if not score_div:
                        continue
                    
                    score_text = score_div.text.strip()
                    
                    # Парсим счёт (например "2 - 0" или "16 - 14")
                    score_match = re.search(r'(\d+)\s*-\s*(\d+)', score_text)
                    if not score_match:
                        continue
                    
                    score1 = int(score_match.group(1))
                    score2 = int(score_match.group(2))
                    
                    # Определяем победителя
                    spirit_won = False
                    if team1 == "Spirit" and score1 > score2:
                        spirit_won = True
                    elif team2 == "Spirit" and score2 > score1:
                        spirit_won = True
                    
                    # Добавляем только выигранные матчи
                    if spirit_won:
                        matches.append({
                            'url': match_url,
                            'team1': team1,
                            'team2': team2,
                            'score': f"{score1}-{score2}"
                        })
                        
                        print(f"  ✅ {team1} vs {team2} ({score1}-{score2})")
                
                except Exception as e:
                    continue
            
            print(f"\n✅ Найдено {len(matches)} выигранных матчей Spirit")
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
    
    def download_wins(self, n_demos=20, save_dir="./demos"):
        """
        Скачать демки выигранных матчей Spirit
        
        Args:
            n_demos: количество демок
            save_dir: папка для сохранения
        """
        os.makedirs(save_dir, exist_ok=True)
        
        print(f"🎯 Скачиваем {n_demos} выигранных матчей Spirit (donk)...")
        print(f"📁 Сохранение в: {save_dir}\n")
        
        # Получаем список матчей
        matches = self.get_team_matches(limit=n_demos * 2)
        
        if not matches:
            print("\n❌ Не удалось найти матчи!")
            print("\n💡 ВОЗМОЖНЫЕ ПРИЧИНЫ:")
            print("   1. HLTV блокирует запросы")
            print("   2. Изменилась структура сайта")
            print("   3. Проблемы с интернетом")
            print("\n💡 РЕШЕНИЕ:")
            print("   Попробуй через VPN или позже")
            return False
        
        downloaded = 0
        
        for i, match in enumerate(matches):
            if downloaded >= n_demos:
                break
            
            print(f"\n[{downloaded + 1}/{n_demos}] {match['team1']} vs {match['team2']} ({match['score']})")
            
            # Получаем ссылку на демку
            demo_url = self.get_demo_link(match['url'])
            
            if not demo_url:
                print("  ⚠️  Демка недоступна")
                continue
            
            # Имя файла
            filename = f"spirit_win_{downloaded + 1}.dem"
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
        print(f"✅ Скачано {downloaded} демок выигранных матчей Spirit")
        print(f"📁 Папка: {os.path.abspath(save_dir)}")
        print("=" * 50)
        
        if downloaded > 0:
            print(f"\n🎯 Теперь запусти парсинг с фильтром по donk:")
            print(f"   python parse_demos.py")
            print(f"\n💡 В парсере будет установлен target_player='donk'")
            return True
        
        return False


if __name__ == "__main__":
    # НАСТРОЙКИ
    N_DEMOS = 20   # Количество демок
    SAVE_DIR = "./demos"
    
    print("=" * 50)
    print("🔥 СКАЧИВАНИЕ ВЫИГРАННЫХ МАТЧЕЙ SPIRIT (DONK)")
    print("=" * 50)
    print()
    print("Что делает:")
    print("  ✅ Находит выигранные матчи Spirit")
    print("  ✅ Скачивает демки")
    print("  ✅ Готовит для анализа donk")
    print()
    print("=" * 50)
    print()
    
    downloader = DonkWinsDownloader()
    success = downloader.download_wins(
        n_demos=N_DEMOS,
        save_dir=SAVE_DIR
    )
    
    if success:
        print("\n🎉 УСПЕХ!")
        print("\n📋 Следующие шаги:")
        print("   1. Загрузи папку demos на Google Drive")
        print("   2. Или запусти парсинг локально:")
        print("      python parse_demos.py")
        print("\n💡 Парсер автоматически будет анализировать только donk!")

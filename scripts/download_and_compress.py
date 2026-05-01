# download_and_compress.py
"""
Скачивает демки топовых команд с HLTV и сжимает в ZIP архив

Требования:
    pip install requests beautifulsoup4 tqdm

Использование:
    python download_and_compress.py
"""
import requests
from bs4 import BeautifulSoup
import os
import time
import zipfile
from tqdm import tqdm

# Топовые команды (обе команды должны быть из списка)
TOP_TEAMS = [
    "Vitality", "FaZe", "Spirit", "MOUZ", "Natus Vincere",
    "FURIA", "Falcons", "The MongolZ", "G2", "Astralis",
    "3DMAX", "FUT", "PARIVISION", "Aurora"
]

def get_recent_matches(n_matches=20):
    """Получить список недавних матчей с HLTV"""
    url = "https://www.hltv.org/results"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    print(f"🔍 Ищем матчи на HLTV...")
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        matches = []
        for result in soup.find_all('div', class_='result-con'):
            if len(matches) >= n_matches * 3:  # Берём с запасом
                break
            
            # Получаем ссылку на матч
            link_tag = result.find('a', class_='a-reset')
            if not link_tag:
                continue
            
            match_url = "https://www.hltv.org" + link_tag['href']
            
            # Получаем команды
            teams = result.find_all('div', class_='team')
            if len(teams) != 2:
                continue
            
            team1 = teams[0].text.strip()
            team2 = teams[1].text.strip()
            
            # Проверяем что обе команды топовые
            if team1 in TOP_TEAMS and team2 in TOP_TEAMS:
                matches.append({
                    'url': match_url,
                    'team1': team1,
                    'team2': team2
                })
        
        print(f"✅ Найдено {len(matches)} матчей топовых команд")
        return matches
    
    except Exception as e:
        print(f"❌ Ошибка получения матчей: {e}")
        return []


def get_demo_link(match_url):
    """Получить ссылку на демку из страницы матча"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    try:
        response = requests.get(match_url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Ищем ссылку на демку
        demo_link = soup.find('a', text='GOTV Demo')
        if demo_link and 'href' in demo_link.attrs:
            return demo_link['href']
        
        return None
    
    except Exception as e:
        return None


def download_demo(url, save_path):
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
        print(f"  ❌ Ошибка: {e}")
        if os.path.exists(save_path):
            os.remove(save_path)
        return False


def compress_demos(demo_dir, output_zip):
    """Сжать все демки в ZIP архив с максимальным сжатием"""
    print(f"\n📦 Сжимаем демки в архив...")
    
    dem_files = [f for f in os.listdir(demo_dir) if f.endswith('.dem')]
    
    if not dem_files:
        print("❌ Нет демок для сжатия!")
        return False
    
    # Создаём ZIP с максимальным сжатием
    with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as zipf:
        for dem_file in tqdm(dem_files, desc="Сжатие"):
            file_path = os.path.join(demo_dir, dem_file)
            zipf.write(file_path, dem_file)
    
    # Статистика сжатия
    original_size = sum(os.path.getsize(os.path.join(demo_dir, f)) for f in dem_files)
    compressed_size = os.path.getsize(output_zip)
    ratio = (1 - compressed_size / original_size) * 100
    
    print(f"\n✅ Архив создан: {output_zip}")
    print(f"📊 Оригинальный размер: {original_size / 1e9:.2f} GB")
    print(f"📊 Сжатый размер: {compressed_size / 1e9:.2f} GB")
    print(f"📊 Сжатие: {ratio:.1f}%")
    
    return True


def download_and_compress_demos(n_demos=20, demo_dir="./demos", output_zip="demos_compressed.zip"):
    """
    Скачать демки с HLTV и сжать в ZIP архив
    
    Args:
        n_demos: количество демок
        demo_dir: папка для временного хранения
        output_zip: имя выходного архива
    """
    os.makedirs(demo_dir, exist_ok=True)
    
    print(f"🎯 Скачиваем {n_demos} демок с HLTV...")
    print(f"📁 Временная папка: {demo_dir}")
    print(f"📦 Выходной архив: {output_zip}\n")
    
    # Получаем список матчей
    matches = get_recent_matches(n_matches=n_demos)
    
    if not matches:
        print("❌ Не удалось найти матчи!")
        return False
    
    downloaded = 0
    
    for i, match in enumerate(matches):
        if downloaded >= n_demos:
            break
        
        print(f"\n[{downloaded + 1}/{n_demos}] {match['team1']} vs {match['team2']}")
        
        # Получаем ссылку на демку
        demo_url = get_demo_link(match['url'])
        
        if not demo_url:
            print("  ⚠️  Демка недоступна")
            continue
        
        # Имя файла
        filename = f"demo_{downloaded + 1}.dem"
        filepath = os.path.join(demo_dir, filename)
        
        # Проверяем что уже не скачано
        if os.path.exists(filepath):
            print(f"  ✅ Уже есть: {filename}")
            downloaded += 1
            continue
        
        # Скачиваем
        print(f"  📥 Качаем...")
        if download_demo(demo_url, filepath):
            file_size_mb = os.path.getsize(filepath) / 1e6
            
            # Проверяем размер (должно быть >100MB)
            if file_size_mb < 100:
                print(f"  ⚠️  Файл слишком маленький ({file_size_mb:.1f} MB), удаляем")
                os.remove(filepath)
                continue
            
            print(f"  ✅ Готово: {file_size_mb:.1f} MB")
            downloaded += 1
        else:
            print(f"  ❌ Не удалось скачать")
        
        # Задержка чтобы не забанили
        time.sleep(3)
    
    print("\n" + "=" * 50)
    print(f"✅ Скачано {downloaded} демок")
    print("=" * 50)
    
    if downloaded == 0:
        print("❌ Нет демок для сжатия!")
        return False
    
    # Сжимаем в архив
    success = compress_demos(demo_dir, output_zip)
    
    if success:
        print(f"\n🎉 ГОТОВО!")
        print(f"📦 Архив: {output_zip}")
        print(f"📤 Загрузи этот файл на Google Drive!")
        print(f"\n💡 СОВЕТ: Можешь удалить папку {demo_dir} чтобы освободить место")
        print(f"   Все демки сохранены в архиве!")
    
    return success


if __name__ == "__main__":
    # НАСТРОЙКИ
    N_DEMOS = 20  # Количество демок
    DEMO_DIR = "./demos"  # Временная папка
    OUTPUT_ZIP = "cs2_demos_compressed.zip"  # Имя архива
    
    download_and_compress_demos(
        n_demos=N_DEMOS,
        demo_dir=DEMO_DIR,
        output_zip=OUTPUT_ZIP
    )

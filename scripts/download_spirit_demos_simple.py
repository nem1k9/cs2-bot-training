# download_spirit_demos_simple.py
"""
Простой скрипт для скачивания демок Spirit через прямые ссылки

Использование:
    python download_spirit_demos_simple.py
"""
import requests
import os
from tqdm import tqdm

# Прямые ссылки на демки Spirit (последние матчи)
# Эти ссылки работают без блокировок
DEMO_LINKS = [
    # Добавь сюда прямые ссылки на демки
    # Формат: ("название", "url")
]

def download_demo(url, filename, save_dir="./demos"):
    """Скачать демку по прямой ссылке"""
    os.makedirs(save_dir, exist_ok=True)
    filepath = os.path.join(save_dir, filename)
    
    if os.path.exists(filepath):
        print(f"✅ Уже есть: {filename}")
        return True
    
    try:
        print(f"📥 Качаем: {filename}")
        response = requests.get(url, stream=True, timeout=180)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        
        with open(filepath, 'wb') as f:
            with tqdm(total=total_size, unit='B', unit_scale=True) as pbar:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
                    pbar.update(len(chunk))
        
        print(f"✅ Готово: {filename}")
        return True
    
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        if os.path.exists(filepath):
            os.remove(filepath)
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("📥 СКАЧИВАНИЕ ДЕМОК SPIRIT")
    print("=" * 60)
    print()
    
    if not DEMO_LINKS:
        print("❌ Нет ссылок на демки!")
        print()
        print("💡 РЕШЕНИЕ:")
        print("   Используй один из методов:")
        print()
        print("   1. VPN + download_donk_faceit_wins.py")
        print("   2. Смени DNS на 1.1.1.1")
        print("   3. Скачай демки вручную с HLTV")
        print()
        print("📋 Как скачать вручную:")
        print("   1. Открой https://www.hltv.org/team/7020/spirit")
        print("   2. Перейди в Matches")
        print("   3. Открой матч")
        print("   4. Нажми 'GOTV Demo'")
        print("   5. Сохрани в папку ./demos/")
    else:
        downloaded = 0
        for name, url in DEMO_LINKS:
            if download_demo(url, name):
                downloaded += 1
        
        print()
        print("=" * 60)
        print(f"✅ Скачано {downloaded}/{len(DEMO_LINKS)} демок")
        print("=" * 60)

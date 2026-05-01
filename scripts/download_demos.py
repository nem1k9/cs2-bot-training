import cloudscraper
from bs4 import BeautifulSoup
import os, time, random
import shutil  # для проверки места на диске

scraper = cloudscraper.create_scraper(
    browser={"browser": "chrome", "platform": "windows", "mobile": False}
)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Referer": "https://www.hltv.org/",
}

# Только топовые команды (обе команды должны быть из этого списка)
TOP_TEAMS = [
    "Vitality",      # чемпионы, ZywOo
    "FaZe",          # финалисты, broky, rain
    "Spirit",        # donk
    "MOUZ",          # torzsi, xertioN
    "Natus Vincere", # b1t, iM (полное название!)
    "FURIA",         # kscerato, yuurih
    "Falcons",       # zonic
    "The MongolZ",   # 0IQTESTINGV2
    "G2",            # NiKo, m0NESY
    "Astralis",      # device, blameF
    "3DMAX",         # Djoko
    "FUT",           # MAJ3R
    "PARIVISION",    # n0rb3r7
    "Aurora",        # deko
]

def get_demo_links(pages=3, max_matches=50):
    """
    pages: сколько страниц парсить (1 страница = ~50 матчей)
    max_matches: максимум матчей для скачивания
    """
    links = []

    for page in range(0, pages * 100, 100):
        if len(links) >= max_matches:
            break
            
        # stars=2 = только крупные турниры (Major, ESL, BLAST)
        url = f"https://www.hltv.org/results?offset={page}&stars=2"
        print(f"Страница {page//100 + 1}/{pages}... (найдено {len(links)} матчей)")

        try:
            resp = scraper.get(url, headers=HEADERS, timeout=15)
            soup = BeautifulSoup(resp.text, "html.parser")

            for result in soup.select(".result-con"):
                teams = result.select(".team-cell .team")
                team_names = [t.text.strip() for t in teams]

                # ОБЕ команды должны быть из TOP_TEAMS
                if len(team_names) == 2 and all(t in TOP_TEAMS for t in team_names):
                    a = result.select_one("a.a-reset")
                    if a:
                        match_url = "https://www.hltv.org" + a["href"]
                        links.append(match_url)
                        print(f"  + {' vs '.join(team_names)}")

        except Exception as e:
            print(f"  Ошибка страницы: {e}")

        time.sleep(random.uniform(3, 6))

    links = list(set(links))[:max_matches]  # ограничиваем количество
    print(f"\nВсего матчей найдено: {len(links)}")
    return links


def get_demo_url(match_url):
    try:
        resp = scraper.get(match_url, headers=HEADERS, timeout=15)
        soup = BeautifulSoup(resp.text, "html.parser")

        selectors = [
            "a.stream-box[href*='.dem']",
            "a[href*='mydemos']",
            "a[data-demo-link]",
            "a[href*='demo']",
        ]

        for sel in selectors:
            btn = soup.select_one(sel)
            if btn:
                href = btn.get("href") or btn.get("data-demo-link", "")
                if href:
                    return href if href.startswith("http") else "https://www.hltv.org" + href

    except Exception as e:
        print(f"  Ошибка получения ссылки: {e}")

    return None


def download_demo(url, save_dir="./demos"):
    os.makedirs(save_dir, exist_ok=True)

    filename = url.split("/")[-1].split("?")[0]
    if not filename.endswith(".dem"):
        filename += ".dem"

    filepath = os.path.join(save_dir, filename)
    if os.path.exists(filepath):
        print(f"  Уже есть: {filename}")
        return filepath

    try:
        print(f"  Качаем: {filename}")
        resp = scraper.get(url, headers=HEADERS, stream=True, timeout=60)

        with open(filepath, "wb") as f:
            downloaded = 0
            for chunk in resp.iter_content(chunk_size=8192):
                f.write(chunk)
                downloaded += len(chunk)
                print(f"\r  {downloaded/1e6:.1f} MB...", end="", flush=True)

        file_size_mb = os.path.getsize(filepath) / 1e6
        print(f"\r  Готово: {file_size_mb:.1f} MB")
        
        # Проверка: нормальная демка CS2 весит минимум 100 MB
        if file_size_mb < 100:
            print(f"  ⚠️  Файл слишком маленький ({file_size_mb:.1f} MB), возможно битый")
            os.remove(filepath)
            return None
        
        return filepath

    except Exception as e:
        print(f"\n  Ошибка скачивания: {e}")
        if os.path.exists(filepath):
            os.remove(filepath)
        return None


def download_all(n_demos=10, save_dir="./demos"):
    # Проверка уже скачанных демок
    os.makedirs(save_dir, exist_ok=True)
    existing_demos = len([f for f in os.listdir(save_dir) if f.endswith('.dem')])
    
    if existing_demos >= n_demos:
        print("=" * 50)
        print(f"✅ Уже скачано {existing_demos} демок!")
        print(f"Папка: {os.path.abspath(save_dir)}")
        print("=" * 50)
        return
    
    demos_needed = n_demos - existing_demos
    
    # Проверка свободного места
    free_space_gb = shutil.disk_usage(os.path.dirname(os.path.abspath(save_dir))).free / (1024**3)
    required_space_gb = demos_needed * 1.0  # ~1 GB на демку
    
    print("=" * 50)
    print(f"Уже есть: {existing_demos} демок")
    print(f"Нужно скачать: {demos_needed} демок (~{required_space_gb:.0f} GB)")
    print(f"Свободно на диске: {free_space_gb:.1f} GB")
    
    if free_space_gb < required_space_gb + 5:  # +5 GB запас
        print(f"⚠️  ВНИМАНИЕ: Может не хватить места!")
        print(f"   Рекомендуется: {required_space_gb + 5:.0f} GB")
        response = input("Продолжить? (y/n): ")
        if response.lower() != 'y':
            print("Отменено")
            return
    
    print("Команды: " + ", ".join(TOP_TEAMS))
    print("Турниры: Major, ESL, BLAST (только Tier-1)")
    print("=" * 50)

    # Парсим только столько страниц, сколько нужно (с запасом x2)
    pages_needed = max(2, (demos_needed * 2) // 50 + 1)
    match_links = get_demo_links(pages=pages_needed, max_matches=demos_needed * 2)

    if not match_links:
        print("Матчи не найдены! Возможно HLTV заблокировал.")
        print("Подожди 10 минут и попробуй снова.")
        return

    print(f"\n💡 Найдено {len(match_links)} матчей (с запасом)")
    print(f"   Будет скачано только {demos_needed} демок\n")

    downloaded = 0
    failed = 0

    for i, match_url in enumerate(match_links):
        if downloaded >= demos_needed:
            print(f"\n✅ Достигнута цель: {n_demos} демок!")
            break

        print(f"\n[{existing_demos + downloaded + 1}/{n_demos}] Проверяем матч {i+1}...")

        demo_url = get_demo_url(match_url)

        if demo_url:
            result = download_demo(demo_url, save_dir)
            if result:
                downloaded += 1
            else:
                failed += 1
        else:
            print("  Демка не найдена")
            failed += 1

        # Останавливаемся если достигли цели
        if downloaded >= demos_needed:
            break
            
        time.sleep(random.uniform(5, 10))

    total_demos = existing_demos + downloaded
    print("\n" + "=" * 50)
    print(f"Всего демок: {total_demos} (было {existing_demos}, скачано {downloaded})")
    print(f"Размер: ~{total_demos * 1.0:.0f} GB")
    print(f"Не удалось: {failed}")
    print(f"Папка: {os.path.abspath(save_dir)}")
    print("=" * 50)


if __name__ == "__main__":
    # ВНИМАНИЕ: 1 демка ≈ 1 GB!
    # 10 демок = ~10 GB (минимум для теста)
    # 20 демок = ~20 GB (базовое обучение)
    # 50 демок = ~50 GB (полный датасет)
    download_all(n_demos=10, save_dir="./demos")
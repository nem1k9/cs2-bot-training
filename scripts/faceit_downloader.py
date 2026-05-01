import requests
import os
import time

API_KEY = "ВАШ_КЛЮЧ_СЮДА"

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Accept": "application/json",
}

BASE = "https://open.faceit.com/data/v4"

TARGET_PLAYERS = [
    "donk",
    "ZywOo",
    "NiKo",
    "broky",
    "b1t",
]


def get_faceit_player_id(nickname):
    resp = requests.get(f"{BASE}/players?nickname={nickname}", headers=HEADERS)
    if resp.status_code == 200:
        return resp.json().get("player_id")
    print(f"  Игрок {nickname} не найден: {resp.status_code}")
    return None


def get_player_matches(faceit_id, limit=20):
    matches = []
    offset = 0
    while len(matches) < limit:
        resp = requests.get(
            f"{BASE}/players/{faceit_id}/history",
            headers=HEADERS,
            params={"game": "cs2", "offset": offset, "limit": min(20, limit - len(matches))}
        )
        if resp.status_code != 200:
            break
        data = resp.json().get("items", [])
        if not data:
            break
        matches.extend(data)
        offset += len(data)
        time.sleep(0.5)
    return matches


def get_demo_url(match_id):
    resp = requests.get(f"{BASE}/matches/{match_id}", headers=HEADERS)
    if resp.status_code != 200:
        return None
    data = resp.json()
    demo_url = data.get("demo_url", [])
    if isinstance(demo_url, list) and demo_url:
        return demo_url[0]
    if isinstance(demo_url, str) and demo_url:
        return demo_url
    return None


def download_demo(url, save_path):
    if os.path.exists(save_path):
        print(f"  Уже есть: {os.path.basename(save_path)}")
        return True
    try:
        resp = requests.get(url, stream=True, timeout=60)
        if resp.status_code != 200:
            print(f"  Ошибка: {resp.status_code}")
            return False
        with open(save_path, "wb") as f:
            downloaded = 0
            for chunk in resp.iter_content(chunk_size=8192):
                f.write(chunk)
                downloaded += len(chunk)
                print(f"\r  {downloaded/1e6:.1f} MB...", end="", flush=True)
        print(f"\r  Готово: {os.path.getsize(save_path)/1e6:.1f} MB")
        return True
    except Exception as e:
        print(f"\n  Ошибка: {e}")
        if os.path.exists(save_path):
            os.remove(save_path)
        return False


def download_player_demos(nickname, n_demos=10, save_dir="../demos"):
    os.makedirs(save_dir, exist_ok=True)
    print(f"\n{'='*50}")
    print(f"Игрок: {nickname} | Цель: {n_demos} демок")
    print(f"{'='*50}")
    faceit_id = get_faceit_player_id(nickname)
    if not faceit_id:
        return 0
    print(f"Faceit ID: {faceit_id}")
    matches = get_player_matches(faceit_id, limit=n_demos * 2)
    print(f"Матчей найдено: {len(matches)}")
    downloaded = 0
    for match in matches:
        if downloaded >= n_demos:
            break
        match_id = match.get("match_id") or match.get("matchId")
        if not match_id:
            continue
        print(f"\n[{downloaded+1}/{n_demos}] {match_id}")
        demo_url = get_demo_url(match_id)
        if not demo_url:
            print("  Демка недоступна")
            continue
        save_path = os.path.join(save_dir, f"{nickname}_{match_id}.dem")
        if download_demo(demo_url, save_path):
            downloaded += 1
        time.sleep(1)
    print(f"\nСкачано для {nickname}: {downloaded}")
    return downloaded


if __name__ == "__main__":
    download_player_demos("donk", n_demos=20, save_dir="../demos")

# parse_demos.py
from awpy import Demo
import pandas as pd
import numpy as np
import os
from tqdm import tqdm

def parse_single_demo(path, target_player=None):
    """
    Расширенный парсинг с отслеживанием:
    - Движения и позиционирования
    - Пиков и агрессивной игры
    - Стрельбы и точности
    - Использования гранат (смоки, флешки, молотовы)
    - Тактических решений
    
    target_player: ник игрока (например "ZywOo", "donk", "s1mple")
                   Если None - берём всех игроков
    """
    demo = Demo(path, parse_frames=True)
    rows = []

    for round_num, round_data in enumerate(demo.rounds):
        prev_states = {}  # запоминаем прошлый тик для вычисления дельты

        for tick in round_data.frames:
            for player in tick.players:
                if not player.is_alive:
                    continue
                
                # Фильтр по игроку
                if target_player and player.name != target_player:
                    continue

                pid = player.steam_id
                cur = {
                    # Базовая позиция
                    "x": player.x, "y": player.y, "z": player.z,
                    "yaw": player.yaw, "pitch": player.pitch,
                    
                    # Состояние игрока
                    "hp": player.hp / 100.0,
                    "armor": player.armor / 100.0,
                    "helmet": float(player.has_helmet) if hasattr(player, 'has_helmet') else 0.0,
                    
                    # Оружие и боеприпасы
                    "weapon": player.active_weapon_id,
                    "ammo": min(player.ammo_clip, 30) / 30.0 if player.ammo_clip else 0.0,
                    "total_ammo": min(player.ammo_reserve, 120) / 120.0 if player.ammo_reserve else 0.0,
                    
                    # Гранаты
                    "has_flash": float(player.flash_grenades > 0) if hasattr(player, 'flash_grenades') else 0.0,
                    "has_smoke": float(player.smoke_grenades > 0) if hasattr(player, 'smoke_grenades') else 0.0,
                    "has_he": float(player.he_grenades > 0) if hasattr(player, 'he_grenades') else 0.0,
                    "has_molotov": float(player.molotov_grenades > 0 or player.incendiary_grenades > 0) if hasattr(player, 'molotov_grenades') else 0.0,
                    
                    # Тактическая информация
                    "team": 1 if player.team == "CT" else 0,
                    "is_ducking": float(player.is_ducking) if hasattr(player, 'is_ducking') else 0.0,
                    "is_scoped": float(player.is_scoped) if hasattr(player, 'is_scoped') else 0.0,
                    "velocity": player.velocity if hasattr(player, 'velocity') else 0.0,
                    
                    # Контекст раунда
                    "round": round_num,
                    "tick": tick.tick,
                    "money": min(player.money, 16000) / 16000.0 if hasattr(player, 'money') else 0.0,
                }

                # Враги (топ-3 ближайших) - для пиков и позиционирования
                enemies = sorted(
                    [p for p in tick.players if p.team != player.team and p.is_alive],
                    key=lambda e: (e.x - player.x)**2 + (e.y - player.y)**2
                )[:3]

                for i in range(3):
                    if i < len(enemies):
                        e = enemies[i]
                        dist = ((e.x - player.x)**2 + (e.y - player.y)**2)**0.5
                        cur[f"e{i}_dx"] = (e.x - player.x) / 1000.0
                        cur[f"e{i}_dy"] = (e.y - player.y) / 1000.0
                        cur[f"e{i}_dz"] = (e.z - player.z) / 500.0
                        cur[f"e{i}_dist"] = min(dist / 3000.0, 1.0)  # нормализованная дистанция
                        cur[f"e{i}_vis"] = float(e.spotted) if hasattr(e, 'spotted') else 0.0
                        cur[f"e{i}_hp"] = e.hp / 100.0
                    else:
                        cur[f"e{i}_dx"] = 0.0
                        cur[f"e{i}_dy"] = 0.0
                        cur[f"e{i}_dz"] = 0.0
                        cur[f"e{i}_dist"] = 1.0
                        cur[f"e{i}_vis"] = 0.0
                        cur[f"e{i}_hp"] = 0.0

                # Вычисляем действия (дельты) - как игрок двигается и стреляет
                if pid in prev_states:
                    prev = prev_states[pid]

                    # Прицеливание (aim)
                    dyaw = cur["yaw"] - prev["yaw"]
                    dyaw = dyaw - 360 * round(dyaw / 360)  # нормализуем в -180..180
                    dpitch = cur["pitch"] - prev["pitch"]
                    dpitch = max(-89, min(89, dpitch))

                    # Движение
                    dx = cur["x"] - prev["x"]
                    dy = cur["y"] - prev["y"]
                    dz = cur["z"] - prev["z"]
                    speed = (dx**2 + dy**2)**0.5

                    # Стрельба (по изменению патронов)
                    is_shooting = float(cur["ammo"] < prev["ammo"])
                    
                    # Использование гранат
                    used_flash = float(cur["has_flash"] < prev["has_flash"])
                    used_smoke = float(cur["has_smoke"] < prev["has_smoke"])
                    used_he = float(cur["has_he"] < prev["has_he"])
                    used_molotov = float(cur["has_molotov"] < prev["has_molotov"])

                    rows.append({
                        # Состояние (state)
                        **{f"s_{k}": v for k, v in cur.items()},
                        
                        # Действия (actions)
                        "a_dyaw":   np.clip(dyaw / 20.0, -1, 1),
                        "a_dpitch": np.clip(dpitch / 10.0, -1, 1),
                        "a_moving": float(speed > 2.0),
                        "a_dx":     np.clip(dx / 200.0, -1, 1),
                        "a_dy":     np.clip(dy / 200.0, -1, 1),
                        "a_dz":     np.clip(dz / 100.0, -1, 1),
                        "a_speed":  np.clip(speed / 250.0, 0, 1),
                        
                        # Боевые действия
                        "a_shooting": is_shooting,
                        "a_reload": float(cur["ammo"] > prev["ammo"] and not is_shooting),
                        
                        # Использование гранат
                        "a_use_flash": used_flash,
                        "a_use_smoke": used_smoke,
                        "a_use_he": used_he,
                        "a_use_molotov": used_molotov,
                        
                        # Тактические действия
                        "a_duck": float(cur["is_ducking"] > prev["is_ducking"]),
                        "a_scope": float(cur["is_scoped"] > prev["is_scoped"]),
                        
                        # Метаданные
                        "demo": os.path.basename(path),
                        "player": pid,
                        "player_name": player.name if hasattr(player, 'name') else "unknown",
                    })

                prev_states[pid] = cur

    return pd.DataFrame(rows)


def build_dataset(demo_dir="./demos", out_path="./dataset.parquet", target_player=None):
    """
    target_player: ник игрока для обучения (например "ZywOo", "donk", "s1mple")
                   Если None - берём всех игроков
    """
    dem_files = [f for f in os.listdir(demo_dir) if f.endswith(".dem")]
    
    if target_player:
        print(f"🎯 Парсим {len(dem_files)} демок для игрока: {target_player}")
    else:
        print(f"Парсим {len(dem_files)} демок (все игроки)...")

    all_dfs = []
    for f in tqdm(dem_files):
        try:
            df = parse_single_demo(os.path.join(demo_dir, f), target_player=target_player)
            if len(df) > 100:
                all_dfs.append(df)
        except Exception as e:
            print(f"Ошибка {f}: {e}")

    result = pd.concat(all_dfs, ignore_index=True)
    result.to_parquet(out_path)
    
    if target_player:
        print(f"✅ Датасет для {target_player}: {len(result):,} тиков → {out_path}")
    else:
        print(f"Датасет: {len(result):,} тиков → {out_path}")
    
    print(f"Размер файла: {os.path.getsize(out_path)/1e6:.0f} MB")
    return result


if __name__ == "__main__":
    build_dataset()
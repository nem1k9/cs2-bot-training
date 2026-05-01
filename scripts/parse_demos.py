# parse_demos.py
from awpy import Demo
import pandas as pd
import numpy as np
import os
from tqdm import tqdm

def parse_single_demo(path):
    demo = Demo(path, parse_frames=True)
    rows = []

    for round_num, round_data in enumerate(demo.rounds):
        prev_states = {}  # запоминаем прошлый тик для вычисления дельты

        for tick in round_data.frames:
            for player in tick.players:
                if not player.is_alive:
                    continue

                pid = player.steam_id
                cur = {
                    "x": player.x, "y": player.y, "z": player.z,
                    "yaw": player.yaw, "pitch": player.pitch,
                    "hp": player.hp / 100.0,
                    "armor": player.armor / 100.0,
                    "weapon": player.active_weapon_id,
                    "ammo": min(player.ammo_clip, 30) / 30.0,
                    "team": 1 if player.team == "CT" else 0,
                    "round": round_num,
                    "tick": tick.tick,
                }

                # Враги (топ-3 ближайших)
                enemies = sorted(
                    [p for p in tick.players if p.team != player.team and p.is_alive],
                    key=lambda e: (e.x - player.x)**2 + (e.y - player.y)**2
                )[:3]

                for i in range(3):
                    if i < len(enemies):
                        e = enemies[i]
                        cur[f"e{i}_dx"] = (e.x - player.x) / 1000.0
                        cur[f"e{i}_dy"] = (e.y - player.y) / 1000.0
                        cur[f"e{i}_dz"] = (e.z - player.z) / 500.0
                        cur[f"e{i}_vis"] = float(e.spotted)
                    else:
                        cur[f"e{i}_dx"] = 0.0
                        cur[f"e{i}_dy"] = 0.0
                        cur[f"e{i}_dz"] = 0.0
                        cur[f"e{i}_vis"] = 0.0

                # Вычисляем действия (дельты)
                if pid in prev_states:
                    prev = prev_states[pid]

                    dyaw = cur["yaw"] - prev["yaw"]
                    # Нормализуем в -180..180
                    dyaw = dyaw - 360 * round(dyaw / 360)

                    dpitch = cur["pitch"] - prev["pitch"]
                    dpitch = max(-89, min(89, dpitch))

                    dx = cur["x"] - prev["x"]
                    dy = cur["y"] - prev["y"]

                    rows.append({
                        **{f"s_{k}": v for k, v in cur.items()},
                        "a_dyaw":   np.clip(dyaw / 20.0, -1, 1),
                        "a_dpitch": np.clip(dpitch / 10.0, -1, 1),
                        "a_moving": float(abs(dx) + abs(dy) > 2.0),
                        "a_dx":     np.clip(dx / 200.0, -1, 1),
                        "a_dy":     np.clip(dy / 200.0, -1, 1),
                        "demo": os.path.basename(path),
                        "player": pid,
                    })

                prev_states[pid] = cur

    return pd.DataFrame(rows)


def build_dataset(demo_dir="./demos", out_path="./dataset.parquet"):
    dem_files = [f for f in os.listdir(demo_dir) if f.endswith(".dem")]
    print(f"Парсим {len(dem_files)} демок...")

    all_dfs = []
    for f in tqdm(dem_files):
        try:
            df = parse_single_demo(os.path.join(demo_dir, f))
            if len(df) > 100:
                all_dfs.append(df)
        except Exception as e:
            print(f"Ошибка {f}: {e}")

    result = pd.concat(all_dfs, ignore_index=True)
    result.to_parquet(out_path)
    print(f"Датасет: {len(result):,} тиков → {out_path}")
    print(f"Размер файла: {os.path.getsize(out_path)/1e6:.0f} MB")
    return result


if __name__ == "__main__":
    build_dataset()
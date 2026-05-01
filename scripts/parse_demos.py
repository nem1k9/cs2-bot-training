from awpy import Demo
import pandas as pd
import numpy as np
import os
from tqdm import tqdm

STATE_COLS = [
    "s_x", "s_y", "s_z", "s_yaw", "s_pitch",
    "s_hp", "s_armor", "s_weapon", "s_ammo", "s_team",
    "s_e0_dx", "s_e0_dy", "s_e0_dz", "s_e0_vis",
    "s_e1_dx", "s_e1_dy", "s_e1_dz", "s_e1_vis",
    "s_e2_dx", "s_e2_dy", "s_e2_dz", "s_e2_vis",
]


def parse_single_demo(path):
    demo = Demo(path, parse_frames=True)
    rows = []
    for round_num, round_data in enumerate(demo.rounds):
        prev_states = {}
        for tick in round_data.frames:
            for player in tick.players:
                if not player.is_alive:
                    continue
                pid = player.steam_id
                cur = {
                    "x": player.x, "y": player.y, "z": player.z,
                    "yaw": player.yaw, "pitch": player.pitch,
                    "hp": player.hp / 100.0, "armor": player.armor / 100.0,
                    "weapon": player.active_weapon_id,
                    "ammo": min(player.ammo_clip, 30) / 30.0,
                    "team": 1 if player.team == "CT" else 0,
                }
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
                if pid in prev_states:
                    prev = prev_states[pid]
                    dyaw = cur["yaw"] - prev["yaw"]
                    dyaw = dyaw - 360 * round(dyaw / 360)
                    dpitch = float(np.clip(cur["pitch"] - prev["pitch"], -89, 89))
                    dx = cur["x"] - prev["x"]
                    dy = cur["y"] - prev["y"]
                    rows.append({
                        "s_x": cur["x"], "s_y": cur["y"], "s_z": cur["z"],
                        "s_yaw": cur["yaw"] / 180.0, "s_pitch": cur["pitch"] / 90.0,
                        "s_hp": cur["hp"], "s_armor": cur["armor"],
                        "s_weapon": cur["weapon"], "s_ammo": cur["ammo"],
                        "s_team": cur["team"],
                        "s_e0_dx": cur["e0_dx"], "s_e0_dy": cur["e0_dy"],
                        "s_e0_dz": cur["e0_dz"], "s_e0_vis": cur["e0_vis"],
                        "s_e1_dx": cur["e1_dx"], "s_e1_dy": cur["e1_dy"],
                        "s_e1_dz": cur["e1_dz"], "s_e1_vis": cur["e1_vis"],
                        "s_e2_dx": cur["e2_dx"], "s_e2_dy": cur["e2_dy"],
                        "s_e2_dz": cur["e2_dz"], "s_e2_vis": cur["e2_vis"],
                        "a_dyaw": float(np.clip(dyaw / 20.0, -1, 1)),
                        "a_dpitch": float(np.clip(dpitch / 10.0, -1, 1)),
                        "a_moving": float(abs(dx) + abs(dy) > 2.0),
                        "a_dx": float(np.clip(dx / 200.0, -1, 1)),
                        "a_dy": float(np.clip(dy / 200.0, -1, 1)),
                        "player": pid, "round": round_num,
                        "demo": os.path.basename(path),
                    })
                prev_states[pid] = cur
    return pd.DataFrame(rows)


def build_dataset(demo_dir="../demos", out_path="../dataset.parquet"):
    dem_files = [f for f in os.listdir(demo_dir) if f.endswith(".dem")]
    print(f"Парсим {len(dem_files)} демок...")
    all_dfs = []
    for f in tqdm(dem_files):
        try:
            df = parse_single_demo(os.path.join(demo_dir, f))
            if len(df) > 100:
                all_dfs.append(df)
                print(f"  {f}: {len(df):,} тиков")
        except Exception as e:
            print(f"  Ошибка {f}: {e}")
    result = pd.concat(all_dfs, ignore_index=True)
    result.to_parquet(out_path)
    print(f"\nДатасет: {len(result):,} тиков -> {out_path}")
    return result


if __name__ == "__main__":
    build_dataset()

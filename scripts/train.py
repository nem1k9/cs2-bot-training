# train.py
import torch
import torch.nn as nn
import pandas as pd
import numpy as np
from torch.utils.data import Dataset, DataLoader
from tqdm import tqdm
import os

SEQ_LEN = 32  # помним 32 тика назад (~0.5 сек)

STATE_COLS = [
    "s_x", "s_y", "s_z", "s_yaw", "s_pitch",
    "s_hp", "s_armor", "s_weapon", "s_ammo", "s_team",
    "s_e0_dx","s_e0_dy","s_e0_dz","s_e0_vis",
    "s_e1_dx","s_e1_dy","s_e1_dz","s_e1_vis",
    "s_e2_dx","s_e2_dy","s_e2_dz","s_e2_vis",
]

class DemoDataset(Dataset):
    def __init__(self, parquet_path):
        df = pd.read_parquet(parquet_path).fillna(0)

        # Нормализация позиций
        for col in ["s_x","s_y","s_z"]:
            m, s = df[col].mean(), df[col].std() + 1e-8
            df[col] = (df[col] - m) / s
        df["s_yaw"]   /= 180.0
        df["s_pitch"] /= 90.0

        self.seqs, self.labels = [], []

        for (player, demo), grp in tqdm(
            df.groupby(["player","demo"]),
            desc="Строим последовательности"
        ):
            grp = grp.sort_values("s_tick").reset_index(drop=True)
            if len(grp) < SEQ_LEN + 1:
                continue

            states = grp[STATE_COLS].values.astype(np.float32)
            labels = grp[["a_dyaw","a_dpitch","a_moving","a_dx","a_dy"]]\
                       .values.astype(np.float32)

            for i in range(SEQ_LEN, len(grp)):
                self.seqs.append(states[i-SEQ_LEN:i])
                self.labels.append(labels[i])

        print(f"Примеров: {len(self.seqs):,}")

    def __len__(self): return len(self.seqs)

    def __getitem__(self, idx):
        return (
            torch.tensor(self.seqs[idx]),
            torch.tensor(self.labels[idx])
        )


def train():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Устройство: {device}")

    dataset = DemoDataset("./dataset.parquet")
    loader  = DataLoader(dataset, batch_size=512, shuffle=True,
                         num_workers=4, pin_memory=True)

    # Импортируем модель из прошлого шага
    from model import CS2BotModel
    model = CS2BotModel(state_dim=len(STATE_COLS)).to(device)
    print(f"Параметров: {sum(p.numel() for p in model.parameters()):,}")

    optimizer = torch.optim.AdamW(model.parameters(), lr=3e-4, weight_decay=1e-4)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=80)

    ckpt_path = "./checkpoint.pt"
    start_epoch = 0

    if os.path.exists(ckpt_path):
        ckpt = torch.load(ckpt_path, map_location=device)
        model.load_state_dict(ckpt["model"])
        optimizer.load_state_dict(ckpt["optimizer"])
        start_epoch = ckpt["epoch"] + 1
        print(f"Возобновляем с эпохи {start_epoch}")

    aim_loss_fn  = nn.MSELoss()
    move_loss_fn = nn.BCELoss()
    reg_loss_fn  = nn.MSELoss()

    for epoch in range(start_epoch, 100):
        model.train()
        total_loss = 0
        lstm_hidden = None

        for states, labels in tqdm(loader, desc=f"Epoch {epoch+1}"):
            states = states.to(device)
            aim_target  = labels[:, :2].to(device)   # dyaw, dpitch
            move_target = labels[:, 2:3].to(device)  # moving flag
            reg_target  = labels[:, 3:].to(device)   # dx, dy

            optimizer.zero_grad()
            preds, _ = model(states)

            loss = (
                aim_loss_fn(preds["aim"], aim_target) * 3.0 +
                move_loss_fn(preds["move"][:, :1], move_target) +
                reg_loss_fn(preds["move"][:, 1:3], reg_target)
            )

            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()
            total_loss += loss.item()

        scheduler.step()
        avg = total_loss / len(loader)
        print(f"Epoch {epoch+1} | Loss: {avg:.4f} | LR: {scheduler.get_last_lr()[0]:.6f}")

        # Сохраняем каждые 5 эпох
        if (epoch + 1) % 5 == 0:
            torch.save({
                "epoch": epoch,
                "model": model.state_dict(),
                "optimizer": optimizer.state_dict(),
                "loss": avg,
            }, ckpt_path)
            print(f"Чекпоинт сохранён!")

    torch.save(model.state_dict(), "./cs2bot_final.pt")
    print("Готово! Модель сохранена в cs2bot_final.pt")


if __name__ == "__main__":
    train()
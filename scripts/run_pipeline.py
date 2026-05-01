# run_pipeline.py — всё в одном
import os

print("=" * 50)
print("ШАГ 1: Скачиваем демки с HLTV")
print("=" * 50)
if len(os.listdir("./demos")) < 5:
    from download_demos import download_all
    download_all(n_demos=10, save_dir="./demos")  # 10 демок = ~10 GB
else:
    print("Демки уже есть, пропускаем")

print("\n" + "=" * 50)
print("ШАГ 2: Парсим демки в датасет")
print("=" * 50)
if not os.path.exists("./dataset.parquet"):
    from parse_demos import build_dataset
    build_dataset()
else:
    print("Датасет уже есть, пропускаем")

print("\n" + "=" * 50)
print("ШАГ 3: Обучаем модель")
print("=" * 50)
from train import train
train()
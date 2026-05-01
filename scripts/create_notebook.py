import json

nb = {
 "nbformat": 4,
 "nbformat_minor": 0,
 "metadata": {
  "kernelspec": {"display_name": "Python 3", "name": "python3"},
  "language_info": {"name": "python"},
  "accelerator": "GPU",
  "colab": {"provenance": []}
 },
 "cells": [
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": ["# CS2 Bot Training\n", "Запускай ячейки по порядку!"]
  },
  {
   "cell_type": "code", "metadata": {}, "execution_count": None, "outputs": [],
   "source": [
    "!git clone https://github.com/nem1k9/cs2-bot-training.git\n",
    "import os, sys\n",
    "sys.path.append('/content/cs2-bot-training/scripts')\n",
    "os.chdir('/content/cs2-bot-training/scripts')\n",
    "!pip install awpy pandas pyarrow tqdm requests -q\n",
    "print('Готово!')"
   ]
  },
  {
   "cell_type": "code", "metadata": {}, "execution_count": None, "outputs": [],
   "source": [
    "from google.colab import drive\n",
    "drive.mount('/content/drive')\n",
    "import os\n",
    "os.makedirs('/content/drive/MyDrive/cs2bot/demos', exist_ok=True)\n",
    "print('Drive подключён!')"
   ]
  },
  {
   "cell_type": "code", "metadata": {}, "execution_count": None, "outputs": [],
   "source": [
    "import sys\n",
    "sys.path.append('/content/cs2-bot-training/scripts')\n",
    "import faceit_downloader as fd\n",
    "fd.API_KEY = 'ВАШ_FACEIT_КЛЮЧ'\n",
    "fd.HEADERS['Authorization'] = f'Bearer {fd.API_KEY}'\n",
    "fd.download_player_demos(nickname='donk', n_demos=20, save_dir='/content/drive/MyDrive/cs2bot/demos')"
   ]
  },
  {
   "cell_type": "code", "metadata": {}, "execution_count": None, "outputs": [],
   "source": [
    "import os\n",
    "dataset_path = '/content/drive/MyDrive/cs2bot/dataset.parquet'\n",
    "if os.path.exists(dataset_path):\n",
    "    print('Датасет уже есть')\n",
    "else:\n",
    "    from parse_demos import build_dataset\n",
    "    build_dataset(demo_dir='/content/drive/MyDrive/cs2bot/demos', out_path=dataset_path)"
   ]
  },
  {
   "cell_type": "code", "metadata": {}, "execution_count": None, "outputs": [],
   "source": [
    "import torch, os\n",
    "print(f'GPU: {torch.cuda.get_device_name(0)}')\n",
    "os.chdir('/content/cs2-bot-training/scripts')\n",
    "from train import train\n",
    "train(\n",
    "    dataset_path='/content/drive/MyDrive/cs2bot/dataset.parquet',\n",
    "    checkpoint_path='/content/drive/MyDrive/cs2bot/checkpoint.pt',\n",
    "    output_path='/content/drive/MyDrive/cs2bot/cs2bot_final.pt'\n",
    ")"
   ]
  },
  {
   "cell_type": "code", "metadata": {}, "execution_count": None, "outputs": [],
   "source": [
    "from google.colab import files\n",
    "files.download('/content/drive/MyDrive/cs2bot/cs2bot_final.pt')\n",
    "print('Модель скачана!')"
   ]
  }
 ]
}

with open("CS2_Bot_Training.ipynb", "w", encoding="utf-8") as f:
    json.dump(nb, f, ensure_ascii=False, indent=1)
print("Файл создан!")

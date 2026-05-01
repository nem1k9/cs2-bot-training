# 🎮 CS2 AI Bot Training

Обучение AI-бота для Counter-Strike 2 на профессиональных демо-записях с HLTV.org

## 🚀 Быстрый старт

### Рекомендуемый путь: ПК → Google Drive → Colab

1. **Скачай демки на ПК** (один раз)
   ```bash
   pip install cloudscraper beautifulsoup4
   python download_demos.py  # 10 демок, ~10 GB
   ```

2. **Загрузи на Google Drive**
   - Создай папку `cs2_demos` в Drive
   - Перетащи все *.dem файлы
   - Или используй Google Drive Desktop для быстрой синхронизации

3. **Загрузи код на GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git push
   ```

4. **Обучай в Colab с GPU**
   - Открой `CS2_Bot_Training.ipynb` в Colab
   - Включи T4 GPU (Runtime → Change runtime type)
   - Запускай ячейки по порядку

📖 **[Подробная инструкция →](SETUP_GUIDE.md)**

### Альтернатива: Всё в Colab

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/YOUR_USERNAME/cs2-bot-training/blob/main/CS2_Bot_Training.ipynb)

Можно скачивать демки прямо в Colab, но они удалятся после сессии.

## 📦 Локальная установка

```bash
pip install cloudscraper beautifulsoup4 awpy pandas pyarrow tqdm torch
```

## 🎯 Архитектура

- **TCN** (Temporal Convolutional Network) — краткосрочные паттерны
- **LSTM** — долгосрочная память
- **3 выходных головы**: движение (WASD), прицеливание (yaw/pitch), действия (стрельба, прыжок)

## 📊 Датасет

Скачиваются демки только с топовыми командами:
- Vitality, FaZe, Spirit, MOUZ, Natus Vincere
- FURIA, Falcons, The MongolZ, G2, Astralis
- Только Major, ESL, BLAST турниры

**Размеры:**
- 1 демка ≈ 1 GB
- 10 демок ≈ 10 GB (минимум для теста)
- 20 демок ≈ 20 GB (базовое обучение)

## 🔧 Использование

### Вариант 1: Полный пайплайн
```python
python run_pipeline.py
```

### Вариант 2: По шагам
```python
# Шаг 1: Скачать демки
from download_demos import download_all
download_all(n_demos=10, save_dir="./demos")

# Шаг 2: Парсинг
from parse_demos import build_dataset
build_dataset(demo_dir="./demos", out_path="./dataset.parquet")

# Шаг 3: Обучение
from train import train
train()
```

## ⚠️ Важно

- **Демки весят ~1 GB каждая!** Проверь свободное место
- Для GitHub используй `.gitignore` (демки не загружаются)
- Для хранения демок используй Google Drive (15 GB бесплатно)
- Обучение требует GPU (в Colab бесплатно)

## 📁 Структура проекта

```
cs2-bot-training/
├── download_demos.py    # Скачивание с HLTV
├── parse_demos.py       # Парсинг в датасет
├── model.py             # Архитектура нейросети
├── train.py             # Обучение
├── run_pipeline.py      # Полный пайплайн
├── CS2_Bot_Training.ipynb  # Colab ноутбук
└── demos/               # Демки (не в git)
```

## 🎓 Результаты

После обучения получишь:
- `cs2bot_final.pt` — финальная модель
- `checkpoint.pt` — чекпоинт для продолжения обучения
- `dataset.parquet` — обработанный датасет

## 📝 Лицензия

MIT

# 📖 Пошаговая инструкция: Скачать демки → Drive → Colab

## 🎯 План действий

1. **Скачать демки на ПК** (один раз)
2. **Залить на Google Drive** (15 GB бесплатно)
3. **Загрузить код на GitHub** (без демок)
4. **Обучить в Colab** с GPU

---

## 📥 Шаг 1: Скачать демки на ПК

```bash
# Установи зависимости
pip install cloudscraper beautifulsoup4

# Скачай 10 демок (~10 GB, займёт 30-60 минут)
python download_demos.py
```

**Результат:** папка `demos/` с 10 файлами *.dem (~1 GB каждый)

---

## ☁️ Шаг 2: Загрузить демки на Google Drive

### Вариант А: Через браузер
1. Открой [Google Drive](https://drive.google.com)
2. Создай папку `cs2_demos`
3. Перетащи все *.dem файлы из папки `demos/`
4. Дождись загрузки (может занять 1-2 часа)

### Вариант Б: Через Google Drive Desktop (быстрее!)
1. Установи [Google Drive для ПК](https://www.google.com/drive/download/)
2. Скопируй папку `demos/` в `Google Drive/cs2_demos/`
3. Синхронизация пройдёт автоматически

**Проверка:** в Drive должна быть папка `cs2_demos/` с 10 файлами *.dem

---

## 🐙 Шаг 3: Загрузить код на GitHub

```bash
# Инициализация git
git init
git add .
git commit -m "Initial commit: CS2 bot training"

# Создай репозиторий на GitHub.com
# Затем:
git remote add origin https://github.com/YOUR_USERNAME/cs2-bot-training.git
git branch -M main
git push -u origin main
```

**Важно:** Демки НЕ загрузятся (они в `.gitignore`) — это правильно!

---

## 🚀 Шаг 4: Обучение в Google Colab

### 4.1 Открой ноутбук
1. Перейди в свой репозиторий на GitHub
2. Открой файл `CS2_Bot_Training.ipynb`
3. Нажми кнопку **"Open in Colab"** (или скопируй ссылку)

### 4.2 Включи GPU
1. В Colab: **Runtime → Change runtime type**
2. Выбери **T4 GPU**
3. Нажми **Save**

### 4.3 Запусти ячейки по порядку

**Ячейка 1:** Проверка GPU
```python
!nvidia-smi
```
Должно показать: `Tesla T4` или `Tesla V100`

**Ячейка 2:** Установка зависимостей
```python
!pip install -q cloudscraper beautifulsoup4 awpy pandas pyarrow tqdm torch
```

**Ячейка 3:** Клонирование репозитория
```python
!git clone https://github.com/YOUR_USERNAME/cs2-bot-training.git
%cd cs2-bot-training
```

**Ячейка 4:** Подключение Drive
```python
from google.colab import drive
drive.mount('/content/drive')
```
Разреши доступ к Drive (появится окно авторизации)

**Ячейка 5:** Копирование демок из Drive
```python
!mkdir -p ./demos
!cp /content/drive/MyDrive/cs2_demos/*.dem ./demos/
!ls -lh ./demos
```
Должно показать 10 файлов *.dem

**Ячейка 6:** Парсинг демок
```python
from parse_demos import build_dataset
build_dataset(demo_dir="./demos", out_path="./dataset.parquet")
```
Займёт 10-30 минут

**Ячейка 7:** Обучение модели
```python
from train import train
train()
```
Займёт 2-4 часа (100 эпох)

**Ячейка 8:** Сохранение результатов на Drive
```python
!mkdir -p /content/drive/MyDrive/cs2_bot_results
!cp cs2bot_final.pt /content/drive/MyDrive/cs2_bot_results/
!cp checkpoint.pt /content/drive/MyDrive/cs2_bot_results/
!cp dataset.parquet /content/drive/MyDrive/cs2_bot_results/
```

---

## 🎉 Готово!

После обучения на твоём Drive будет папка `cs2_bot_results/` с:
- ✅ `cs2bot_final.pt` — обученная модель
- ✅ `checkpoint.pt` — чекпоинт для продолжения
- ✅ `dataset.parquet` — обработанный датасет

**Теперь можешь удалить всё с ПК!** Всё сохранено в облаке.

---

## 💡 Полезные советы

### Если Colab отключился
Чекпоинты сохраняются каждые 5 эпох. Просто запусти обучение заново:
```python
from train import train
train()  # продолжит с последнего чекпоинта
```

### Если нужно больше демок
1. Скачай ещё на ПК: `download_all(n_demos=20)`
2. Добавь в Drive в ту же папку `cs2_demos/`
3. В Colab пересоздай датасет

### Если закончилось место в Drive (15 GB)
- Удали старые демки после парсинга (датасет весит меньше)
- Или используй Google One (100 GB за $2/месяц)

### Мониторинг обучения
В Colab можно смотреть графики loss в реальном времени:
```python
# Добавь в train.py
from torch.utils.tensorboard import SummaryWriter
writer = SummaryWriter()
```

---

## ❓ Частые проблемы

**Q: Colab пишет "Out of memory"**  
A: Уменьши `batch_size` в `train.py` с 512 до 256

**Q: Демки не копируются из Drive**  
A: Проверь путь: `!ls /content/drive/MyDrive/` и найди свою папку

**Q: Парсинг падает с ошибкой**  
A: Некоторые демки могут быть битыми, это нормально. Скрипт пропустит их.

**Q: Обучение слишком долгое**  
A: Уменьши количество эпох в `train.py` со 100 до 50

---

## 📞 Поддержка

Если что-то не работает, проверь:
1. ✅ GPU включен в Colab
2. ✅ Drive подключен
3. ✅ Демки скопированы в `./demos/`
4. ✅ Все зависимости установлены

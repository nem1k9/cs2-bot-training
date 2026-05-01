# 🚀 Быстрый старт - CS2 Bot Training

## ✅ Рекомендуемый метод: Сжатые демки

### Шаг 1: Установи библиотеки

```bash
pip install requests beautifulsoup4 tqdm
```

### Шаг 2: Скачай и сожми демки

```bash
python download_and_compress.py
```

⏱️ Время: ~30-60 минут  
📦 Результат: `cs2_demos_compressed.zip` (~10-15 GB)

### Шаг 3: Загрузи на Google Drive

1. Открой [Google Drive](https://drive.google.com)
2. Загрузи файл `cs2_demos_compressed.zip`
3. Запомни путь (например: `/MyDrive/cs2_demos_compressed.zip`)

### Шаг 4: Запусти обучение в Colab

**Открой в Colab:**
```
https://colab.research.google.com/github/nem1k9/cs2-bot-training/blob/main/CS2_Bot_Training_Compressed.ipynb
```

**Настрой GPU:**
- Runtime → Change runtime type → T4 GPU → Save

**Запусти:**
- Нажми "Выполнить все" (Run all)
- Или запускай ячейки по порядку

⏱️ Время обучения: ~2-4 часа

---

## 📋 Что получишь:

- ✅ Обученная модель AI бота
- ✅ Датасет с действиями про-игроков
- ✅ Чекпоинты для продолжения обучения

Всё сохраняется на Google Drive автоматически!

---

## 💡 Дополнительно

### Фильтрация по игроку

Если хочешь обучить на конкретном игроке (например, donk):

В Colab ноутбуке измени:
```python
PLAYER = "donk"  # Или "ZywOo", "s1mple" и т.д.
```

### Изменить количество демок

В `download_and_compress.py`:
```python
N_DEMOS = 20  # Измени на 10, 15, 30 и т.д.
```

---

## 🔧 Проблемы?

### Не скачиваются демки
- Проверь интернет
- Попробуй VPN
- Смени DNS на 1.1.1.1

### Нет места на Drive
- Уменьши количество демок: `N_DEMOS = 10`
- Или купи больше места ($1.99/мес за 100GB)

### Ошибка в Colab
- Проверь что выбран GPU (T4)
- Проверь путь к архиву на Drive
- Перезапусти Runtime

---

## 📚 Подробная документация

- [COMPRESSED_WORKFLOW.md](COMPRESSED_WORKFLOW.md) - Полная инструкция
- [README.md](README.md) - Общая информация о проекте
- [SETUP_GUIDE.md](SETUP_GUIDE.md) - Локальная установка

---

**Готово! Теперь запускай и обучай своего AI бота!** 🎮🔥

# 📥 Руководство по ручному скачиванию демок donk

## ❌ Проблема: Backblaze CDN недоступен

Если ты видишь ошибку `DNS_PROBE_FINISHED_NXDOMAIN`, это значит что:
- Твой провайдер блокирует Backblaze CDN
- DNS не может найти домен
- Автоматическое скачивание не работает

## ✅ Решение: Скачай демки вручную

### Способ 1: Через FACEIT (рекомендуется)

**Время:** 10-15 минут для 10-15 демок

1. **Открой:** https://www.faceit.com/en/players/donk666
2. **Войди** в свой FACEIT аккаунт (если нет - создай)
3. **Перейди:** Stats → Match History
4. **Фильтруй:**
   - Game: CS2
   - Result: Won (только победы)
5. **Для каждого матча:**
   - Открой матч
   - Нажми "Download Demo" или иконку скачивания
   - Сохрани в папку `C:\Users\illia\cs2bot\scripts\demos\`
6. **Повтори** для 10-20 матчей

**Результат:** Файлы `.dem.zst` в папке `demos`

---

### Способ 2: Через HLTV

**Время:** 15-20 минут

1. **Открой:** https://www.hltv.org/team/7020/spirit
2. **Перейди:** Matches
3. **Фильтруй:** только победы Spirit
4. **Для каждого матча:**
   - Открой матч
   - Нажми "GOTV Demo"
   - Сохрани в папку `demos`
5. **Повтори** для 10-20 матчей

**Результат:** Файлы `.dem` в папке `demos`

---

### Способ 3: Используй VPN

Если хочешь автоматическое скачивание:

1. **Скачай VPN:**
   - Proton VPN (бесплатный): https://protonvpn.com/
   - Windscribe (бесплатный): https://windscribe.com/
2. **Включи VPN**
3. **Запусти:**
   ```bash
   python download_donk_faceit_wins.py
   ```

VPN обойдёт блокировку провайдера!

---

## 📤 После скачивания:

### Вариант А: Обучение на ПК

```bash
python parse_demos.py
python train.py
```

### Вариант Б: Обучение в Colab

1. **Загрузи** папку `demos` на Google Drive
2. **Открой:** https://colab.research.google.com/github/nem1k9/cs2-bot-training/blob/main/scripts/CS2_Bot_Training_Compressed.ipynb
3. **Установи:**
   ```python
   USE_ZIP = False
   DRIVE_FOLDER_PATH = "/content/drive/MyDrive/demos"
   PLAYER = "donk"
   ```
4. **Запусти** все ячейки

---

## 💡 Рекомендация:

**Используй Способ 1 (FACEIT)** - это:
- ✅ Быстро (10-15 минут)
- ✅ Надёжно (без блокировок)
- ✅ Только выигранные матчи donk
- ✅ Файлы уже сжаты (.zst)

Просто открой FACEIT, войди в аккаунт и скачай демки вручную!

---

## 🔧 Если нужна помощь с DNS:

### Смена DNS на Google DNS:

**Windows 11:**
1. Win + I → Сеть и Интернет
2. Выбери подключение (Wi-Fi или Ethernet)
3. Назначение DNS-сервера → Изменить
4. Вручную → IPv4 включить
5. Предпочитаемый: `8.8.8.8`
6. Альтернативный: `8.8.4.4`
7. Сохранить

**Очистка кэша:**
```bash
ipconfig /flushdns
```

**Проверка:**
```bash
nslookup demos-europe-central.backblaze.faceit-cdn.net 8.8.8.8
```

Если выдаёт IP - DNS работает!
Если нет - используй VPN или ручное скачивание.

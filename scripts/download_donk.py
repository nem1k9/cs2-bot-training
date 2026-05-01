from download_faceit_demos import download_player_demos_simple

# НАСТРОЙКИ
API_KEY = "YOUR_API_KEY_HERE"  # ← ВСТАВЬ СВОЙ API КЛЮЧ
PLAYER = "donk666"
N_DEMOS = 20  # Количество демок

print(f"🎯 Скачиваем {N_DEMOS} демок игрока {PLAYER} с FACEIT...")
print(f"📁 Сохранение в: ./demos/\n")

download_player_demos_simple(
    nickname=PLAYER,
    api_key=API_KEY,
    n_demos=N_DEMOS,
    save_dir="./demos"
)

print(f"\n✅ Готово! Демки сохранены в ./demos/")
print(f"📤 Теперь загрузи их на Google Drive!")

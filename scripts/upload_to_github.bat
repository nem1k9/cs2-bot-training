@echo off
echo ========================================
echo Загрузка проекта на GitHub
echo ========================================

REM Инициализация git
git init

REM Добавление всех файлов (кроме demos, они в .gitignore)
git add .

REM Первый коммит
git commit -m "Initial commit: CS2 bot training project"

REM Добавление удалённого репозитория
echo.
echo ВАЖНО: Замени YOUR_USERNAME на своё имя пользователя GitHub!
echo Пример: git remote add origin https://github.com/illia/cs2-bot-training.git
echo.
set /p REPO_URL="Введи URL репозитория: "
git remote add origin %REPO_URL%

REM Отправка на GitHub
git branch -M main
git push -u origin main

echo.
echo ========================================
echo Готово! Проект загружен на GitHub
echo ========================================
pause

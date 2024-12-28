# Tg-bot
Запуск *Tg-bot*: <br>
1. Установить Docker и Docker-Compose <br>
    Убедитесь, что на вашем компьютере установлены Docker и Docker-Compose <br>

2. Клонировать репозиторий с GitHub <br>
    git clone https://github.com/Pr0tuberanec/Tg-bot.git <br>
    cd Tg-bot <br>

3. Создать файл с токеном <br>
    Найдите @BotFather в телеграмм, создайте своего собственного бота и получите его токен <br>
    Создайте файл bot_token_secret в корневой директории проекта и вставьте в него ваш токен <br>

4. Запустить сборку и контейнеры через Docker-Compose <br>
        docker-compose up --build <br>

5. Проверить работу бота <br>
    Если бот начал вам отвечать, то вы всё сделали правильно <br>

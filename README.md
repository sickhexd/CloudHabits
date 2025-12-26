# 🌟 CloudHabits

<div align="center">

**Веб-приложение для отслеживания привычек с интеграцией Telegram Mini Apps**  
**Habit tracking web application with Telegram Mini Apps integration**

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-green.svg)](https://fastapi.tiangolo.com/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0.23-orange.svg)](https://www.sqlalchemy.org/)
[![License](https://img.shields.io/badge/license-Non--Commercial-red.svg)](LICENSE)

**[🇷🇺 Русский](#-о-проекте) | [🇬🇧 English](#-about-the-project)**

</div>

---

# 🇷🇺 Русский

## 📖 О проекте

**CloudHabits** — это современное веб-приложение для отслеживания ежедневных привычек, разработанное специально для работы в Telegram Mini Apps. Приложение помогает пользователям формировать полезные привычки, отслеживать прогресс и анализировать статистику выполнения.

### 🎯 Зачем нужен CloudHabits?

- ✅ **Простота использования** — интуитивный интерфейс, доступный прямо из Telegram
- 📊 **Визуализация прогресса** — календарные представления и детальная статистика
- 🔥 **Мотивация через стрики** — отслеживание текущих и максимальных серий выполнений
- 📱 **Мобильная оптимизация** — адаптивный дизайн для комфортной работы на любых устройствах
- 🔒 **Безопасность** — аутентификация через Telegram, изолированные данные для каждого пользователя
- ⚡ **Производительность** — быстрая работа благодаря оптимизированным запросам к базе данных

---

## ✨ Основные возможности

### 📅 Календарные представления
- **Недельный вид** — быстрый обзор текущей недели с возможностью отмечать выполнение привычек
- **Месячный календарь** — полный обзор месяца с визуализацией прогресса по дням

### 📈 Отчеты и статистика
- **Процент выполнения** — показывает, как часто вы выполняете каждую привычку
- **Текущий стрик** — количество дней подряд без пропусков
- **Максимальный стрик** — ваш лучший результат
- **Графики прогресса** — визуализация динамики за выбранный период (7 дней, 30 дней, 90 дней)

### 🎨 Управление привычками
- Создание новых привычек с автоматическим назначением цветов
- Удаление привычек
- Отслеживание выполнения по дням
- История всех выполнений

### 🔐 Аутентификация
- Интеграция с Telegram Mini Apps
- Автоматическое определение пользователя через Telegram WebApp API
- Изолированные данные для каждого пользователя

---

## 🛠 Технологический стек

- **Backend Framework**: [FastAPI](https://fastapi.tiangolo.com/) — современный, быстрый веб-фреймворк для Python
- **Database**: SQLite (с возможностью перехода на PostgreSQL)
- **ORM**: SQLAlchemy 2.0 — мощный инструмент для работы с базами данных
- **Templates**: Jinja2 — шаблонизатор для HTML
- **Server**: Gunicorn + Uvicorn — production-ready сервер
- **Authentication**: Telegram Mini Apps API

---

## 📱 Использование

### Для разработки

1. Запустите приложение локально
2. Откройте в браузере: `http://localhost:8000/?user_id=demo_user`

### Для Telegram Mini App

1. Создайте бота через [@BotFather](https://t.me/botfather)
2. Настройте Mini App в настройках бота
3. Укажите URL вашего приложения
4. Пользователи смогут открыть приложение прямо из Telegram

### Основные страницы

- **`/`** — Главная страница с недельным календарем
- **`/calendar`** — Месячный календарь
- **`/reports`** — Отчеты и статистика
- **`/habits-list`** — Список привычек (для синхронизации)

---

## 📁 Структура проекта

```
CloudHabits/
├── app/                    # Основное приложение
│   ├── __init__.py
│   ├── main.py            # Точка входа, маршруты FastAPI
│   ├── database.py        # Модели базы данных и запросы
│   ├── services.py        # Бизнес-логика (стрики, статистика)
│   ├── telegram_auth.py  # Аутентификация через Telegram
│   ├── templates_helpers.py # Вспомогательные функции для шаблонов
│   └── utils.py           # Утилиты (календарь, форматирование)
├── config/
│   └── env.example        # Пример файла с переменными окружения
├── scripts/
│   └── migrate_db.py      # Скрипт миграции базы данных
├── templates/             # HTML шаблоны
│   ├── index.html         # Главная страница (недельный календарь)
│   ├── calendar.html      # Месячный календарь
│   ├── reports.html       # Страница отчетов
│   └── habits_list.html   # Список привычек
├── requirements.txt       # Зависимости проекта
├── requirements-dev.txt   # Зависимости для разработки
├── pyproject.toml         # Конфигурация инструментов разработки
├── gunicorn_config.py     # Конфигурация Gunicorn
├── wsgi.py                # WSGI точка входа
└── habits.db              # База данных SQLite (создается автоматически)
```

---

## 🔧 API Endpoints

### GET `/`
Главная страница с недельным календарем привычек.

**Параметры:**
- `user_id` (query) — ID пользователя Telegram

### GET `/calendar`
Месячный календарь с визуализацией прогресса.

**Параметры:**
- `user_id` (query) — ID пользователя Telegram
- `year` (query, optional) — год
- `month` (query, optional) — месяц

### GET `/reports`
Страница с отчетами и статистикой.

**Параметры:**
- `user_id` (query) — ID пользователя Telegram
- `period` (query, default: "7days") — период: "7days", "30days", "90days"

### POST `/habits`
Создание новой привычки.

**Параметры формы:**
- `name` — название привычки
- `user_id` — ID пользователя

### DELETE `/habits/{habit_id}`
Удаление привычки.

### POST `/completions`
Переключение статуса выполнения привычки на определенную дату.

**Параметры формы:**
- `habit_id` — ID привычки
- `date` — дата в формате YYYY-MM-DD
- `user_id` — ID пользователя
- `context` — контекст ("week" или "month")

---

## 🎨 Особенности реализации

- **Оптимизированные запросы** — использование batch-запросов для получения данных о выполнении привычек
- **HTMX интеграция** — динамическое обновление интерфейса без перезагрузки страницы
- **Цветовая кодировка** — автоматическое назначение уникальных цветов для каждой привычки
- **Расчет стриков** — эффективный алгоритм подсчета текущих и максимальных серий выполнений
- **Адаптивный дизайн** — современный UI, оптимизированный для мобильных устройств

---

## 🔒 Безопасность

- Аутентификация через Telegram Mini Apps API
- Изоляция данных по пользователям на уровне базы данных
- Валидация всех входных данных
- Защита от SQL-инъекций через SQLAlchemy ORM

---

## 📝 Лицензия

Этот проект распространяется под лицензией **Non-Commercial License**. 

**Важно:** Коммерческое использование, продажа и монетизация этого проекта запрещены. Проект предназначен только для личного и образовательного использования. Подробности см. в файле [LICENSE](LICENSE).

---

## 🤝 Вклад в проект

Мы приветствуем вклад в развитие проекта! Пожалуйста, создавайте issues для багов и feature requests, или отправляйте pull requests с улучшениями.

---

## 📧 Контакты

Если у вас есть вопросы или предложения, создайте issue в репозитории проекта.

---

# 🇬🇧 English

## 📖 About the Project

**CloudHabits** is a modern web application for tracking daily habits, specifically designed to work with Telegram Mini Apps. The application helps users build useful habits, track progress, and analyze completion statistics.

### 🎯 Why CloudHabits?

- ✅ **Ease of use** — intuitive interface accessible directly from Telegram
- 📊 **Progress visualization** — calendar views and detailed statistics
- 🔥 **Motivation through streaks** — tracking current and maximum completion streaks
- 📱 **Mobile optimization** — responsive design for comfortable use on any device
- 🔒 **Security** — authentication via Telegram, isolated data for each user
- ⚡ **Performance** — fast operation thanks to optimized database queries

---

## ✨ Key Features

### 📅 Calendar Views
- **Weekly view** — quick overview of the current week with ability to mark habit completion
- **Monthly calendar** — full month overview with day-by-day progress visualization

### 📈 Reports and Statistics
- **Completion percentage** — shows how often you complete each habit
- **Current streak** — number of consecutive days without missing
- **Maximum streak** — your best result
- **Progress charts** — visualization of dynamics for selected period (7 days, 30 days, 90 days)

### 🎨 Habit Management
- Create new habits with automatic color assignment
- Delete habits
- Track completion by days
- History of all completions

### 🔐 Authentication
- Integration with Telegram Mini Apps
- Automatic user identification via Telegram WebApp API
- Isolated data for each user

---

## 🛠 Technology Stack

- **Backend Framework**: [FastAPI](https://fastapi.tiangolo.com/) — modern, fast web framework for Python
- **Database**: SQLite (with ability to switch to PostgreSQL)
- **ORM**: SQLAlchemy 2.0 — powerful tool for database operations
- **Templates**: Jinja2 — HTML templating engine
- **Server**: Gunicorn + Uvicorn — production-ready server
- **Authentication**: Telegram Mini Apps API

---

## 📱 Usage

### For Development

1. Run the application locally
2. Open in browser: `http://localhost:8000/?user_id=demo_user`

### For Telegram Mini App

1. Create a bot via [@BotFather](https://t.me/botfather)
2. Configure Mini App in bot settings
3. Specify your application URL
4. Users will be able to open the app directly from Telegram

### Main Pages

- **`/`** — Main page with weekly calendar
- **`/calendar`** — Monthly calendar
- **`/reports`** — Reports and statistics
- **`/habits-list`** — Habits list (for synchronization)

---

## 📁 Project Structure

```
CloudHabits/
├── app/                    # Main application
│   ├── __init__.py
│   ├── main.py            # Entry point, FastAPI routes
│   ├── database.py        # Database models and queries
│   ├── services.py        # Business logic (streaks, statistics)
│   ├── telegram_auth.py  # Telegram authentication
│   ├── templates_helpers.py # Template helper functions
│   └── utils.py           # Utilities (calendar, formatting)
├── config/
│   └── env.example        # Environment variables example
├── scripts/
│   └── migrate_db.py      # Database migration script
├── templates/             # HTML templates
│   ├── index.html         # Main page (weekly calendar)
│   ├── calendar.html      # Monthly calendar
│   ├── reports.html       # Reports page
│   └── habits_list.html   # Habits list
├── requirements.txt       # Project dependencies
├── requirements-dev.txt   # Development dependencies
├── pyproject.toml         # Development tools configuration
├── gunicorn_config.py     # Gunicorn configuration
├── wsgi.py                # WSGI entry point
└── habits.db              # SQLite database (created automatically)
```

---

## 🔧 API Endpoints

### GET `/`
Main page with weekly habit calendar.

**Parameters:**
- `user_id` (query) — Telegram user ID

### GET `/calendar`
Monthly calendar with progress visualization.

**Parameters:**
- `user_id` (query) — Telegram user ID
- `year` (query, optional) — year
- `month` (query, optional) — month

### GET `/reports`
Page with reports and statistics.

**Parameters:**
- `user_id` (query) — Telegram user ID
- `period` (query, default: "7days") — period: "7days", "30days", "90days"

### POST `/habits`
Create new habit.

**Form parameters:**
- `name` — habit name
- `user_id` — user ID

### DELETE `/habits/{habit_id}`
Delete habit.

### POST `/completions`
Toggle habit completion status for a specific date.

**Form parameters:**
- `habit_id` — habit ID
- `date` — date in YYYY-MM-DD format
- `user_id` — user ID
- `context` — context ("week" or "month")

---

## 🎨 Implementation Features

- **Optimized queries** — using batch queries to retrieve habit completion data
- **HTMX integration** — dynamic interface updates without page reload
- **Color coding** — automatic assignment of unique colors for each habit
- **Streak calculation** — efficient algorithm for counting current and maximum completion streaks
- **Responsive design** — modern UI optimized for mobile devices

---

## 🔒 Security

- Authentication via Telegram Mini Apps API
- User data isolation at database level
- Validation of all input data
- SQL injection protection via SQLAlchemy ORM

---

## 📝 License

This project is distributed under the **Non-Commercial License**.

**Important:** Commercial use, sale, and monetization of this project are prohibited. The project is intended only for personal and educational use. See the [LICENSE](LICENSE) file for details.

---

## 🤝 Contributing

We welcome contributions to the project! Please create issues for bugs and feature requests, or submit pull requests with improvements.

---

## 📧 Contacts

If you have questions or suggestions, create an issue in the project repository.

---

<div align="center">

**Made with ❤️ for building useful habits**

⭐ If you liked the project, give it a star!

</div>

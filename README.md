## Educational AI Assistant - Учебный AI Ассистент

### Общая информация
Educational AI Assistant - это интеллектуальный учебный ассистент, который помогает в изучении программирования. Система использует современные технологии AI и RAG (Retrieval-Augmented Generation) для предоставления персонализированных ответов и проверки знаний.

### Что умеет ассистент:
**Персональное обучение**: Адаптируется под уровень пользователя (beginner, advanced, professional)

**Диалоговый режим**: Отвечает на вопросы по программированию с учетом контекста

**Проверка знаний**: Генерирует тесты и проверяет ответы через квиз-систему

**Рекомендации**: Предлагает следующие темы для изучения

**Мультиязычность**: Поддерживает изучение Python и JavaScript

## Быстрый старт
1. Скопируйте .env.example -> .env
2. Получение токена GigaChat
Перейдите в ![личный кабинет GigaChat](https://developers.sber.ru/studio/workspaces/my-space/get/gigachat-api)

Зарегистрируйтесь или войдите в аккаунт

Создайте новое приложение

Получите авторизационный токен (access key)
Скопируйте токен в файл .env в переменную GIGA_ACCESS_KEY

3. Запуск приложения
```bash
# Запуск всех сервисов
docker-compose up -d

# Просмотр логов
docker-compose logs -f backend

# Остановка всех сервисов
docker-compose down
```
### Мониторинг и документация
После запуска приложение доступно по следующим адресам:
![Swagger UI](http://localhost:8002)
![Метрики Prometheus](http://localhost:8002/prometheus)
![Дашборды Grafana](http://localhost:3000)
![ChromaDB UI](http://localhost:8001)

### API Endpoints
**Основные endpoints**:
Метод	Endpoint	Описание
POST	/api/v1/dialog	Основной диалог с ассистентом
POST	/api/v1/quiz	Генерация и проверка тестов
POST	/api/v1/history	Получение истории диалога по client_id

Примеры использования
```bash
curl -X POST "http://localhost:8002/api/v1/dialog" \
  -H "Content-Type: application/json" \
  -d '{
    "client_id": "6f707083-7458-4193-9435-36b539115049",
    "message": "Что такое декораторы в Python?",
    "study_topic": "python"
  }'
```
Генерация теста:
```bash
curl -X POST "http://localhost:8002/api/v1/quiz" \
  -H "Content-Type: application/json" \
  -d '{
    "client_id": "6f707083-7458-4193-9435-36b539115049", 
    "message": "",
    "study_topic": "python",
    "action": "generate_question"
  }'
```
### Настройки обучения
Поддерживаемые темы (study_topic):
**"python"** - Программирование на Python
**"javascript"** - JavaScript и веб-разработка

Уровни сложности (user_level):

**"beginner"** - Начальный уровень
**"advanced"** - Продвинутый уровень
**"professional"** - Профессиональный уровень


### Архитектура системы
Компоненты:
**Backend Service** (FastAPI) - Основное приложение
**ChromaDB** - Векторная база данных для RAG
**Apache Ignite** - Кэш для хранения истории диалогов
**GigaChat API** - AI модель для генерации ответов

Технологии:
**FastAPI** - ASGI веб-фреймворк
**Pydantic** - Валидация данных и типизация
**ChromaDB** - Векторные embeddings и поиск
**Docker** - Контейнеризация и оркестрация

### Troubleshooting
Распространенные проблемы:

**Ошибка аутентификации GigaChat**:
* Проверьте токен в .env файле
* Убедитесь, что токен активен в личном кабинете

**ChromaDB не запускается**:
```bash
docker-compose restart chromadb
```

**Проблемы с памятью**:

* Уменьшите VECTOR_DB_DOCUMENTS_NUMBER
* Увеличьте объем оперативной памяти

**Проверка здоровья**:

```bash
curl http://localhost:8002/api/v1/health
```

### Логи:
```bash
# Просмотр логов конкретного сервиса
docker-compose logs backend
docker-compose logs chromadb  
docker-compose logs ignite

# Просмотр всех логов в реальном времени
docker-compose logs -f
```
### Метрики и мониторинг
Система предоставляет метрики в формате Prometheus:

* Время ответа GigaChat API
* Количество активных сессий
* Статус здоровья компонентов

### Разработка
```text
app/
├── agents/           # AI агенты (диалог, квиз)
├── api/             # API endpoints и схемы
├── clients/         # Клиенты для внешних сервисов
├── databases/       # Работа с базами данных
├── services/        # Бизнес-логика (RAG, workflow)
├── settings.py        # Конфигурация приложения
└── utils/           # Вспомогательные утилиты
```

### Для запуска тестов
```bash
pip install pytest anyio pytest-asyncio
```


### Добавление новой темы обучения:
1. Добавьте тему в StudyTopic enum
2. Создайте папку с документами в ./sources/
3. Добавьте контекст в TOPIC_CONTEXT
4. Обновите системные промпты

# Рекомендация
Лучше запускать векторную базу и игнайт в докер контейнере, а само приложение локально, так как долго устанавливаются зависимости
Для этого нужно закомментировать сервис backend
и в .env заменить значения следующих ключей
```text
CHROMA_SERVER_HTTP_PORT=8001
CHROMA_SERVER_HOST=localhost
```

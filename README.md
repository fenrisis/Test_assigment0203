# Project Setup and Usage Guide

## 1. How to Run the Project Locally with Docker

### 1.1 Build the Project
```sh
docker-compose build
```

### 1.2 Start the Project
```sh
docker-compose up -d
```

### 1.3 Apply Migrations
```sh
docker-compose exec web poetry run alembic upgrade head
```

## 2. Generating Test Data
To create test data for the application, run:
```sh
docker-compose exec web poetry run python -m app.utils.create_test_data
```

## 3. Testing WebSocket
To test WebSocket functionality, execute:
```sh
docker-compose exec web poetry run python -m app.tests.test_websocket
```

## 4. API Documentation
Once the project is running, you can access the API documentation by visiting:
```
http://127.0.0.1:8000/docs
```

## 5. Endpoint Example

### **Retrieve Chat History**
#### **Request:**
```sh
curl -X 'GET' \
  'http://127.0.0.1:8000/api/history/1?limit=50&offset=0' \
  -H 'accept: application/json'
```

#### **Request URL:**
```
http://127.0.0.1:8000/api/history/1?limit=50&offset=0
```

#### **Response Example:**
```json
{
  "messages": [
    {
      "text": "Привет, Bob!",
      "id": 1,
      "chat_id": 1,
      "sender_id": 1,
      "receiver_id": 2,
      "timestamp": "2025-02-04T08:59:56.457108Z"
    },
    {
      "text": "Привет, Alice!",
      "id": 7,
      "chat_id": 1,
      "sender_id": 2,
      "receiver_id": 1,
      "timestamp": "2025-02-04T09:00:24.897580Z"
    },
    {
      "text": "Как дела?",
      "id": 9,
      "chat_id": 1,
      "sender_id": 1,
      "receiver_id": 2,
      "timestamp": "2025-02-04T09:00:25.935854Z"
    },
    {
      "text": "Все хорошо!",
      "id": 10,
      "chat_id": 1,
      "sender_id": 2,
      "receiver_id": 1,
      "timestamp": "2025-02-04T09:00:25.937320Z"
    }
  ]
}
```


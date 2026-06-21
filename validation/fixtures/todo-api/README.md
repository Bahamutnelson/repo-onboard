# todo-api

A small **REST API for managing todo lists**, built with Express.

## Endpoints

| Method | Path         | Description        |
|--------|--------------|--------------------|
| GET    | `/todos`     | List all todos     |
| GET    | `/todos/:id` | Get one todo       |
| POST   | `/todos`     | Create a todo      |
| PUT    | `/todos/:id` | Update a todo      |
| DELETE | `/todos/:id` | Delete a todo      |

## Run

```bash
npm install
npm start          # listens on http://localhost:3000
```

Todos are kept in memory, so they reset when the server restarts.

// Express REST API for managing todo lists.
// In-memory store; no persistence — this is a fixture, not production code.
const express = require("express");

const app = express();
app.use(express.json());

let nextId = 1;
const todos = [];

// GET /todos — list every todo
app.get("/todos", (req, res) => {
  res.json(todos);
});

// GET /todos/:id — fetch one todo
app.get("/todos/:id", (req, res) => {
  const todo = todos.find((t) => t.id === Number(req.params.id));
  if (!todo) return res.status(404).json({ error: "not found" });
  res.json(todo);
});

// POST /todos — create a todo
app.post("/todos", (req, res) => {
  const { title } = req.body || {};
  if (!title) return res.status(400).json({ error: "title is required" });
  const todo = { id: nextId++, title, done: false };
  todos.push(todo);
  res.status(201).json(todo);
});

// PUT /todos/:id — update a todo
app.put("/todos/:id", (req, res) => {
  const todo = todos.find((t) => t.id === Number(req.params.id));
  if (!todo) return res.status(404).json({ error: "not found" });
  const { title, done } = req.body || {};
  if (title !== undefined) todo.title = title;
  if (done !== undefined) todo.done = Boolean(done);
  res.json(todo);
});

// DELETE /todos/:id — remove a todo
app.delete("/todos/:id", (req, res) => {
  const idx = todos.findIndex((t) => t.id === Number(req.params.id));
  if (idx === -1) return res.status(404).json({ error: "not found" });
  const [removed] = todos.splice(idx, 1);
  res.json(removed);
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`todo-api listening on http://localhost:${PORT}`);
});

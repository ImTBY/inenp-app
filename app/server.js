const express = require('express');
const path = require('path');
const app = express();

app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

let todos = [];

app.get('/api/todos', (req, res) => {
  res.json(todos);
});

app.post('/api/todos', (req, res) => {
  const { text } = req.body;
  const todo = { id: Date.now(), text, done: false };
  todos.push(todo);
  res.status(201).json(todo);
});

app.put('/api/todos/:id', (req, res) => {
  const id = Number(req.params.id);
  todos = todos.map(t =>
    t.id === id ? { ...t, done: req.body.done } : t
  );
  res.sendStatus(204);
});

app.delete('/api/todos/:id', (req, res) => {
  const id = Number(req.params.id);
  todos = todos.filter(t => t.id !== id);
  res.sendStatus(204);
});

const port = process.env.PORT || 3000;
app.listen(port, () => {
  console.log(`Todo-App läuft auf http://localhost:${port}`);
});
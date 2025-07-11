const express = require('express');
const path = require('path');
const axios = require('axios');
const app = express();

app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

let todos = [];

// Configuration for app_two
const APP_TWO_URL = process.env.APP_TWO_URL || 'http://localhost:8000';

// Helper function to sync todos to app_two
async function syncToDatabase() {
  try {
    await axios.post(`${APP_TWO_URL}/todos/sync`, todos);
    console.log('Todos synced to database successfully');
  } catch (error) {
    console.error('Failed to sync todos to database:', error.message);
  }
}

// Helper function to load todos from app_two on startup
async function loadTodosFromDatabase() {
  try {
    const response = await axios.get(`${APP_TWO_URL}/todos`);
    todos = response.data;
    console.log(`Loaded ${todos.length} todos from database`);
  } catch (error) {
    console.error('Failed to load todos from database:', error.message);
    console.log('Starting with empty todo list');
  }
}

app.get('/api/todos', (req, res) => {
  res.json(todos);
});

app.post('/api/todos', async (req, res) => {
  const { text } = req.body;
  const todo = { id: Date.now(), text, done: false };
  todos.push(todo);
  
  // Sync to database
  await syncToDatabase();
  
  res.status(201).json(todo);
});

app.put('/api/todos/:id', async (req, res) => {
  const id = Number(req.params.id);
  todos = todos.map(t =>
    t.id === id ? { ...t, done: req.body.done } : t
  );
  
  // Sync to database
  await syncToDatabase();
  
  res.sendStatus(204);
});

app.delete('/api/todos/:id', async (req, res) => {
  const id = Number(req.params.id);
  todos = todos.filter(t => t.id !== id);
  
  // Sync to database
  await syncToDatabase();
  
  res.sendStatus(204);
});

const port = process.env.PORT || 3000;
app.listen(port, async () => {
  console.log(`Todo-App läuft auf http://localhost:${port}`);
  
  // Load existing todos from database on startup
  await loadTodosFromDatabase();
});
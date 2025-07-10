from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from typing import Dict, Any, List, Optional

app = FastAPI(title="Todo Persistence API", version="1.0.0")

class TodoModel(BaseModel):
    id: int
    text: str
    done: bool

class TodoCreate(BaseModel):
    id: int
    text: str
    done: bool = False

class TodoUpdate(BaseModel):
    done: bool

def get_db_connection():
    try:
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST", "localhost"),
            database=os.getenv("DB_NAME", "testdb"),
            user=os.getenv("DB_USER", "postgres"),
            password=os.getenv("DB_PASSWORD", "password"),
            port=os.getenv("DB_PORT", "5432")
        )
        return conn
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database connection failed: {str(e)}")

@app.on_event("startup")
async def startup_event():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create todos table if it doesn't exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS todos (
            id INTEGER PRIMARY KEY,
            text TEXT NOT NULL,
            done BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    cursor.close()
    conn.close()

# Get all todos
@app.get("/todos", response_model=List[TodoModel])
async def get_todos():
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        cursor.execute("SELECT id, text, done FROM todos ORDER BY created_at DESC")
        results = cursor.fetchall()
        return [TodoModel(**dict(row)) for row in results]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch todos: {str(e)}")
    finally:
        cursor.close()
        conn.close()

# Create or update a todo
@app.post("/todos", response_model=TodoModel)
async def create_todo(todo: TodoCreate):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        # Use INSERT ... ON CONFLICT to handle both create and update
        cursor.execute(
            """
            INSERT INTO todos (id, text, done, updated_at)
            VALUES (%s, %s, %s, CURRENT_TIMESTAMP)
            ON CONFLICT (id) DO UPDATE SET
                text = EXCLUDED.text,
                done = EXCLUDED.done,
                updated_at = CURRENT_TIMESTAMP
            RETURNING id, text, done
            """,
            (todo.id, todo.text, todo.done)
        )
        
        result = cursor.fetchone()
        conn.commit()
        
        return TodoModel(**dict(result))
        
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to save todo: {str(e)}")
    finally:
        cursor.close()
        conn.close()

# Update todo status
@app.put("/todos/{todo_id}", response_model=TodoModel)
async def update_todo(todo_id: int, todo_update: TodoUpdate):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        cursor.execute(
            """
            UPDATE todos SET done = %s, updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
            RETURNING id, text, done
            """,
            (todo_update.done, todo_id)
        )
        
        result = cursor.fetchone()
        if not result:
            raise HTTPException(status_code=404, detail="Todo not found")
        
        conn.commit()
        return TodoModel(**dict(result))
        
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update todo: {str(e)}")
    finally:
        cursor.close()
        conn.close()

# Delete a todo
@app.delete("/todos/{todo_id}")
async def delete_todo(todo_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("DELETE FROM todos WHERE id = %s", (todo_id,))
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Todo not found")
        
        conn.commit()
        return {"message": "Todo deleted successfully"}
        
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete todo: {str(e)}")
    finally:
        cursor.close()
        conn.close()

# Sync all todos (bulk operation)
@app.post("/todos/sync")
async def sync_todos(todos: List[TodoCreate]):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Clear existing todos and insert new ones
        cursor.execute("DELETE FROM todos")
        
        for todo in todos:
            cursor.execute(
                """
                INSERT INTO todos (id, text, done, updated_at)
                VALUES (%s, %s, %s, CURRENT_TIMESTAMP)
                """,
                (todo.id, todo.text, todo.done)
            )
        
        conn.commit()
        return {"message": f"Synced {len(todos)} todos successfully"}
        
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to sync todos: {str(e)}")
    finally:
        cursor.close()
        conn.close()

@app.get("/")
async def root():
    return {"message": "Todo Persistence API is running", "endpoints": ["/todos", "/todos/sync"]}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
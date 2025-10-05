from fastapi import FastAPI
from fastapi import HTTPException
from fastapi import status
from cc_simple_server.models import TaskCreate
from cc_simple_server.models import TaskRead
from cc_simple_server.database import init_db
from cc_simple_server.database import get_db_connection

# init
init_db()

app = FastAPI()

############################################
# Edit the code below this line
############################################

def row_to_task(row):
    """Convert a SQLite row to a TaskRead model"""
    return TaskRead(
        id=row["id"],
        title=row["title"],
        description=row["description"],
        completed=bool(row["completed"])
    )


@app.get("/")
async def read_root():
    """Welcome endpoint"""
    return {"message": "Welcome to the Cloud Computing!"}


@app.post("/tasks/", response_model=TaskRead, status_code=status.HTTP_200_OK)
async def create_task(task_data: TaskCreate):
    """Create a new task"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO tasks (title, description, completed) VALUES (?, ?, ?)",
        (task_data.title, task_data.description, int(task_data.completed)),
    )
    conn.commit()
    new_id = cursor.lastrowid
    cursor.execute("SELECT * FROM tasks WHERE id = ?", (new_id,))
    row = cursor.fetchone()
    conn.close()
    return row_to_task(row)


@app.get("/tasks/", response_model=list[TaskRead])
async def get_tasks():
    """Get all tasks"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks ORDER BY id ASC")
    rows = cursor.fetchall()
    conn.close()
    return [row_to_task(r) for r in rows]


@app.put("/tasks/{task_id}/", response_model=TaskRead)
async def update_task(task_id: int, task_data: TaskCreate):
    """Update a task by its ID"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
    existing = cursor.fetchone()
    if not existing:
        conn.close()
        raise HTTPException(status_code=404, detail="Task not found")

    cursor.execute(
        "UPDATE tasks SET title=?, description=?, completed=? WHERE id=?",
        (task_data.title, task_data.description, int(task_data.completed), task_id),
    )
    conn.commit()
    cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
    updated = cursor.fetchone()
    conn.close()
    return row_to_task(updated)


@app.delete("/tasks/{task_id}/")
async def delete_task(task_id: int):
    """Delete a task by its ID"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
    existing = cursor.fetchone()
    if not existing:
        conn.close()
        raise HTTPException(status_code=404, detail="Task not found")

    cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()
    return {"message": f"Task {task_id} deleted successfully"}
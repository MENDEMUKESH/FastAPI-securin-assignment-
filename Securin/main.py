from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
import sqlite3

app = FastAPI()

def get_db_connection():
    conn = sqlite3.connect("recipes.db")
    conn.row_factory = sqlite3.Row
    return conn

from fastapi import FastAPI
from fastapi.responses import JSONResponse

# first end point pagination

@app.get("/api/recipes")
def get_all_recipes(page: int = 1, limit: int = 10):
    offset = (page - 1) * limit

    conn = get_db_connection()
    cursor = conn.cursor()
    query = "SELECT * FROM recipes ORDER BY rating DESC LIMIT ? OFFSET ?"
    cursor.execute(query, (limit, offset))
    recipes = cursor.fetchall()
    conn.close()

    result = [dict(row) for row in recipes]
    return JSONResponse(content=result)


# second end point to search recepies


@app.get("/api/recipes/search")
def search_recipes(
    calories_op: str = Query(None), calories_val: int = Query(None),
    title: str = Query(None),
    cuisine: str = Query(None),
    total_time_op: str = Query(None), total_time_val: int = Query(None),
    rating_op: str = Query(None), rating_val: float = Query(None)
):
    conn = get_db_connection()
    cursor = conn.cursor()
    query = "SELECT * FROM recipes WHERE 1=1"
    params = []
    op_map = {"lt": "<", "gt": ">", "eq": "="}

    if calories_op in op_map and calories_val is not None:
        query += f" AND calories {op_map[calories_op]} ?"
        params.append(calories_val)

    if title:
        query += " AND LOWER(title) LIKE ?"
        params.append(f"%{title.lower()}%")

    if cuisine:
        query += " AND LOWER(cuisine) = ?"
        params.append(cuisine.lower())

    if total_time_op in op_map and total_time_val is not None:
        query += f" AND total_time {op_map[total_time_op]} ?"
        params.append(total_time_val)

    if rating_op in op_map and rating_val is not None:
        query += f" AND rating {op_map[rating_op]} ?"
        params.append(rating_val)

    cursor.execute(query, params)
    recipes = cursor.fetchall()
    conn.close()
    return JSONResponse([dict(row) for row in recipes])

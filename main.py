from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import sqlite3

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"],  # 限制允許來源
    allow_credentials=True,
    allow_methods=["POST", "GET"],  # 限制請求
    allow_headers=["*"]
)

def get_connection():
    return sqlite3.connect('user_database.db')

def fetch_tree_structure(code):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT u.code, u.name, u.registration_date, u.introducer_code
            FROM users u
            WHERE u.code = ?
        ''', (code,))
        main_node = cursor.fetchone()

        cursor.execute('''
            SELECT u.code, u.name, u.registration_date, u.introducer_code
            FROM Relationships r
            JOIN users u ON r.Left_Node_ID = u.code
            WHERE r.Main_Node_ID = ?
        ''', (code,))
        left_node = cursor.fetchall()

        cursor.execute('''
            SELECT u.code, u.name, u.registration_date, u.introducer_code
            FROM Relationships r
            JOIN users u ON r.Right_Node_ID = u.code
            WHERE r.Main_Node_ID = ?
        ''', (code,))
        right_node = cursor.fetchall()

        conn.close()

        return {
            "code": main_node[0],
            "name": main_node[1],
            "registration_date": main_node[2],
            "introducer_code": main_node[3],
            "l": [{
                "code": node[0],
                "name": node[1],
                "registration_date": node[2],
                "introducer_code": node[3]
            } for node in left_node],
            "r": [{
                "code": node[0],
                "name": node[1],
                "registration_date": node[2],
                "introducer_code": node[3]
            } for node in right_node]
        }
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))



def fetch_tree_structure_all():
    try:
        conn = sqlite3.connect('user_database.db')
        cursor = conn.cursor()

        cursor.execute('''
            SELECT u.code, u.name, u.registration_date, u.introducer_code
            FROM users u
        ''')
        nodes_info = cursor.fetchall()

        tree_structure = []

        for node_info in nodes_info:
            code = node_info[0]

            cursor.execute('''
                SELECT u.code, u.name, u.registration_date, u.introducer_code
                FROM users u
                INNER JOIN Relationships r ON u.code = r.Left_Node_ID
                WHERE r.Main_Node_ID = ?
            ''', (code,))
            left_tree = cursor.fetchall()

            cursor.execute('''
                SELECT u.code, u.name, u.registration_date, u.introducer_code
                FROM users u
                INNER JOIN Relationships r ON u.code = r.Right_Node_ID
                WHERE r.Main_Node_ID = ?
            ''', (code,))
            right_tree = cursor.fetchall()

            node_structure = {
                "code": node_info[0],
                "name": node_info[1],
                "registration_date": node_info[2],
                "introducer_code": node_info[3],
                "l": left_tree,
                "r": right_tree
            }

            tree_structure.append(node_structure)

        conn.close()

        return tree_structure

    except sqlite3.Error as e:
        # 資料庫查詢錯誤，回傳空值
        return None



@app.get("/")
async def index():
    return {"Hello": "World"}

@app.get("/api/policyholders/{code}/top") 
async def get_task_info(code: str):
    tree_structure = fetch_tree_structure(code)
    if not tree_structure["l"] and not tree_structure["r"]:
        raise HTTPException(status_code=404, detail="No data found for the specified code")
    return tree_structure


@app.get("/api/policyholders") 
async def get_policyholder_info():
    tree_structures = fetch_tree_structure_all()
    if not tree_structures:  # 沒有任何節點資訊的情況，回傳404
        raise HTTPException(status_code=404, detail="No data found for the specified code")
    
    nodes_info = []
    for tree_structure in tree_structures:
        node_info = {
            "code": tree_structure["code"],
            "name": tree_structure["name"],
            "registration_date": tree_structure["registration_date"],
            "introducer_code": tree_structure["introducer_code"],
            "l": tree_structure["l"],
            "r": tree_structure["r"]
        }
        nodes_info.append(node_info)

    return nodes_info


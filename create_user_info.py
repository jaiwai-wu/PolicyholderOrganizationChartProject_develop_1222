import sqlite3

class TreeDatabase:
    
    
    def __init__(self, db_name='user_database.db'):
        self.db_name = db_name


    def create_database(self):
        #建立資料庫
        
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        #用戶資料庫
        cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                            code char(60) PRIMARY KEY,
                            name char(15) NOT NULL,
                            registration_date DATE DEFAULT CURRENT_TIMESTAMP,
                            introducer_code char(60) -- Add introducer_code column
                        )''')

        #關係資料庫
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Relationships (
                Main_Node_ID char(60),
                Left_Node_ID char(60),
                Right_Node_ID char(60),
                FOREIGN KEY (Main_Node_ID) REFERENCES users(code),
                FOREIGN KEY (Left_Node_ID) REFERENCES users(code),
                FOREIGN KEY (Right_Node_ID) REFERENCES users(code)
            )
        ''')

        conn.commit()
        conn.close()


    def insert_user_info(self, user_names):
        #存入用戶資料
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        for index, user_name in enumerate(user_names):
            code = f"000000{int(index + 1)}"
            sql_insert = "INSERT INTO users (code, name, introducer_code) VALUES (?, ?, ?)"
            introducer_code = None if index == 0 else f"000000{index}"
            cursor.execute(sql_insert, (code, user_name, introducer_code))

        conn.commit()
        conn.close()


    def insert_relationships(self, main_node, child_nodes):
        #存入用戶關係資料
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        if len(child_nodes) >= 2:
            left_node, right_node = child_nodes[:2]
            sql_insert_relation = "INSERT INTO Relationships (Main_Node_ID, Left_Node_ID, Right_Node_ID) VALUES (?, ?, ?)"
            cursor.execute(sql_insert_relation, (main_node, left_node, right_node))

        conn.commit()
        conn.close()
        

    def build_tree_structure(self):
        #創建資料
        user_name_list = ["jerry", "json", "boo", "marry", "lisa", "jack", "rose", "sum", "roey", "mongo", "Django"]
        self.create_database()
        self.insert_user_info(user_name_list)

        self.insert_relationships("0000001", ["0000002", "0000003"])
        self.insert_relationships("0000002", ["0000004", "0000005"])
        self.insert_relationships("0000003", ["0000006", "0000007"])
        self.insert_relationships("0000004", ["0000008", "0000009"])
        self.insert_relationships("0000005", ["0000010", "0000011"])


if __name__ == "__main__":
    db = TreeDatabase()
    db.build_tree_structure()

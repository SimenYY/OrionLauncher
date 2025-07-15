import sqlite3
import json

from .types import UserInfo
from .Exceptions import *

def adapt_dict_to_json(data: dict) -> str:
    return json.dumps(data)
def adapt_list_to_json(data: list) -> str:
    return json.dumps(data)
def adapt_json_to_object(data: str) -> dict|list:
    return json.loads(data)

sqlite3.register_adapter(dict, adapt_dict_to_json)
sqlite3.register_adapter(list, adapt_list_to_json)
sqlite3.register_converter("JSON", adapt_json_to_object)

class Database:
    def __init__(self, db_path):
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()

    def create_tables(self):
        try:
            self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS UserData (
                id TEXT PRIMARY KEY,
                name TEXT,
                type TEXT,
                access_token TEXT,
                refresh_token TEXT,
                skins JSON,
                capes JSON
            )
            """)
            self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS ItemTable (
                key TEXT PRIMARY KEY,
                value TEXT
            )
            """)
            self.conn.commit()
        except sqlite3.Error as e:
            raise WrappedSystemException(e, f"Failed to create database tables: {e}")

    def user_add(self,
                 id: str,
                 name: str,
                 type: str,
                 access_token: str='',
                 refresh_token: str='',
                 skins: list=[],
                 capes: list=[],
                 ):
        try:
            self.cursor.execute("""
            INSERT INTO UserData (id, name, type, access_token, refresh_token, skins, capes)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (id, name, type, access_token, refresh_token, skins, capes))
            self.conn.commit()
        except sqlite3.Error as e:
            raise WrappedSystemException(e, f"Failed to add user {id}: {e}")

    def user_get(self, **kwargs) -> dict:
        """
        根据提供的参数查询用户数据

        Args:
            **kwargs: 查询条件，支持的字段包括：
                - id: 用户ID
                - name: 用户名
                - type: 账户类型
                - access_token: 访问令牌
                - refresh_token: 刷新令牌

        Returns:
            dict: 匹配的用户信息，如果未找到则返回空字典

        Example:
            # 根据ID查询用户
            user = db.user_get(id="12345")

            # 根据用户名查询
            user = db.user_get(name="Steve")

            # 根据多个条件查询
            user = db.user_get(name="Steve", type="Microsoft")
        """
        if not kwargs:
            return {}

        # 构建查询条件
        conditions = []
        values = []

        for key, value in kwargs.items():
            if key in ['id', 'name', 'type', 'access_token', 'refresh_token']:
                conditions.append(f"{key} = ?")
                values.append(value)

        if not conditions:
            return {}

        # 构建SQL查询
        query = f"SELECT * FROM UserData WHERE {' AND '.join(conditions)}"

        try:
            self.cursor.execute(query, values)
            result = self.cursor.fetchone()

            if result:
                # 将查询结果转换为字典
                columns = [description[0] for description in self.cursor.description]
                user_data = dict(zip(columns, result))
                return user_data
            else:
                return {}

        except sqlite3.Error as e:
            raise WrappedSystemException(e, f"Failed to query user data: {e}")

    def user_get_all(self) -> list:
        """
        获取所有用户数据

        Returns:
            list: 包含所有用户信息的列表，每个元素为一个用户字典
        """
        try:
            self.cursor.execute("SELECT * FROM UserData")
            results = self.cursor.fetchall()

            if results:
                columns = [description[0] for description in self.cursor.description]
                users = []
                for result in results:
                    user_data = dict(zip(columns, result))
                    users.append(user_data)
                return users
            else:
                return []

        except sqlite3.Error as e:
            raise WrappedSystemException(e, f"Failed to query all users: {e}")

    def user_exists(self, **kwargs) -> bool:
        """
        检查用户是否存在

        Args:
            **kwargs: 查询条件，支持的字段同 user_get()

        Returns:
            bool: 用户是否存在
        """
        user = self.user_get(**kwargs)
        return bool(user)

    def user_update(self, user_id: str, data: UserInfo) -> bool:
        """
        更新用户信息

        Args:
            user_id: 要更新的用户ID
            data: 包含要更新字段的用户信息

        Returns:
            bool: 更新是否成功
        """
        if not data:
            return False

        # 构建更新条件
        set_clauses = []
        values = []

        for key, value in data.items():
            if key in ['name', 'type', 'access_token', 'refresh_token', 'skins', 'capes']:
                set_clauses.append(f"{key} = ?")
                values.append(value)

        if not set_clauses:
            return False

        values.append(user_id)  # 添加WHERE条件的值

        try:
            query = f"UPDATE UserData SET {', '.join(set_clauses)} WHERE id = ?"
            self.cursor.execute(query, values)
            self.conn.commit()
            return self.cursor.rowcount > 0

        except sqlite3.Error as e:
            raise WrappedSystemException(e, f"Failed to update user {user_id}: {e}")

    def user_delete(self, user_id: str) -> bool:
        """
        删除用户

        Args:
            user_id: 要删除的用户ID

        Returns:
            bool: 删除是否成功
        """
        try:
            self.cursor.execute("DELETE FROM UserData WHERE id = ?", (user_id,))
            self.conn.commit()
            return self.cursor.rowcount > 0

        except sqlite3.Error as e:
            raise WrappedSystemException(e, f"Failed to delete user {user_id}: {e}")
        
    def item_set(self, key: str, value: str) -> bool:
        """
        设置键值对

        Args:
            key: 键
            value: 值

        Returns:
            bool: 设置是否成功
        """
        try:
            self.cursor.execute("INSERT OR REPLACE INTO ItemTable (key, value) VALUES (?, ?)", (key, value))
            self.conn.commit()
            return True

        except sqlite3.Error as e:
            raise WrappedSystemException(e, f"Failed to set item {key}: {e}")


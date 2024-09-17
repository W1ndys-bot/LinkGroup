# script/LinkGroup/main.py

import logging
import os
import sys
import asyncio

# 添加项目根目录到sys.path
sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

from app.config import *
from app.api import *
from app.switch import load_switch, save_switch

# 数据存储路径，实际开发时，请将LinkGroup替换为具体的数据存放路径
DATA_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "data",
    "LinkGroup",
)

DB_PATH = os.path.join(DATA_DIR, "LinkGroup.db")


# 初始化数据库，存储群号和监听群号
def init_db():
    # 确保数据目录存在
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(DB_PATH):
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """CREATE TABLE IF NOT EXISTS links (
                group_id TEXT UNIQUE,
                listen_group_id TEXT
            )"""
            )
            conn.commit()
            conn.close()
        logging.info(f"初始化LinkGroup数据库成功")


# 增加监听群号
def add_listen_group(group_id, listen_group_id):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO links (group_id, listen_group_id) VALUES (?, ?)""",
            (group_id, listen_group_id),
        )
        conn.commit()
        conn.close()


# 删除监听群号
def delete_listen_group(group_id):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""DELETE FROM links WHERE group_id = ?""", (group_id,))
        conn.commit()
        conn.close()


# 获取监听群号
def get_listen_group(group_id):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """SELECT listen_group_id FROM links WHERE group_id = ?""", (group_id,)
        )
        result = cursor.fetchall()
        conn.close()
        return result


# 群消息处理函数
async def handle_LinkGroup_group_message(websocket, msg):

    # 确保数据目录存在
    os.makedirs(DATA_DIR, exist_ok=True)
    init_db()
    try:
        user_id = str(msg.get("user_id"))
        group_id = str(msg.get("group_id"))
        raw_message = str(msg.get("raw_message"))
        role = str(msg.get("sender", {}).get("role"))
        message_id = str(msg.get("message_id"))

    except Exception as e:
        logging.error(f"处理LinkGroup群消息失败: {e}")
        return

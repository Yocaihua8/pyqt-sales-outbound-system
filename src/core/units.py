import logging
import os
from PyQt6.QtWidgets import QTableWidgetItem
from PyQt6.QtCore import Qt

# -------------------- 日志初始化 --------------------
def setup_logging(log_dir='logs', log_file='app.log'):
    """配置日志：同时输出到文件和控制台"""
    # 确保日志目录存在
    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, log_file)

    # 创建根日志记录器
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)  # 设置全局日志级别

    # 清除已有的处理器（避免重复）
    if logger.hasHandlers():
        logger.handlers.clear()

    # 文件处理器（写入文件）
    file_handler = logging.FileHandler(log_path, encoding='utf-8')
    file_handler.setLevel(logging.INFO)

    # 控制台处理器（输出到终端）
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    # 定义日志格式
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # 添加处理器
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    # logging.basicConfig(
    #     level=logging.INFO,
    #     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    #     handlers=[
    #         logging.FileHandler(log_path, encoding='utf-8'),
    #         logging.StreamHandler()
    #     ]
    # )
    # return logging.getLogger(__name__)

    return logger

# -------------------- 表格单元格辅助函数 --------------------
def get_cell_text(table, row, col):
    """安全获取单元格文本"""
    item = table.item(row, col)
    return item.text().strip() if item and item.text() else ""

def get_cell_int(table, row, col):
    """获取单元格整数值，失败返回0"""
    item = table.item(row, col)
    if item and item.text().strip():
        try:
            return int(item.text())
        except ValueError:
            return 0
    return 0

def get_cell_float(table, row, col):
    """获取单元格浮点数值，失败返回0.0"""
    item = table.item(row, col)
    if item and item.text().strip():
        try:
            return float(item.text())
        except ValueError:
            return 0.0
    return 0.0

def create_cell(text="", alignment=Qt.AlignmentFlag.AlignLeft, editable=True):
    """创建统一风格的单元格"""
    item = QTableWidgetItem(text)
    if not editable:
        item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
    item.setTextAlignment(alignment)
    return item
import os
import csv
import random
import base64
from botpy import logging

from typing import Optional

_log = logging.get_logger()

PICTURE_FOLDER = "./pictures"

def get_random_picture_path(group_name: str = "mygo", subfolder: str = "random_pictures") -> Optional[str]:
    folder_path = os.path.join(PICTURE_FOLDER, subfolder)
    csv_filename = f"{group_name}_list.csv"
    csv_path = os.path.join(folder_path, csv_filename)

    try:
        with open(csv_path, newline='', encoding='gbk') as csvfile:
            reader = list(csv.reader(csvfile))
            valid_files = [row[0].strip() for row in reader if row and row[0].strip()]
            if not valid_files:
                _log.warning(f"{csv_filename} 中没有图片文件名")
                return None

            chosen_file = random.choice(valid_files)
            image_path = os.path.join(folder_path, chosen_file)
            if os.path.exists(image_path):
                return image_path
            else:
                _log.warning(f"图片文件不存在：{image_path}")
                return None
    except Exception as e:
        _log.error(f"读取 {csv_filename} 失败: {e}")
        return None

def encode_image_base64(image_path: str) -> Optional[str]:
    try:
        with open(image_path, "rb") as f:
            encoded = base64.b64encode(f.read()).decode("utf-8")
            return encoded
    except Exception as e:
        _log.error(f"图片转 base64 失败: {e}")
        return None

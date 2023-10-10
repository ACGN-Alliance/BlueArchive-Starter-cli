from dataclasses import dataclass
from typing import Literal
from pathlib import Path
import json

"""
设置相关代码
"""


@dataclass
class Settings:
    username: str = ""
    guest: bool = False
    _link_account: bool = False  # 用于判断是否已经有link account弹窗出现
    ratio: str = "16:9"
    box_scan: bool = False
    scan_list: list = []
    main_line: bool = False
    recuit_num: int = 0
    if_screenshot: bool = False
    is_mumu: bool = False
    pool: int = 1
    speed: Literal["fast", "normal", "slow", "very slow"] = "normal"
    too_many_errors: int = 30
    _access_token: str = ""


setting_file = Path("./settings.json")
if setting_file.exists():
    setting = json.load(open(setting_file, "r", encoding="utf-8"))
else:
    setting = {}

try:
    settings = Settings(**setting)
except TypeError:
    print("WARNING: 配置文件格式错误(可能因为版本升级导致), 已重置配置文件")
    settings = Settings()

box_scan_preset = {
    "group-1": [("Ako", "亚子"), ("Himar", "阳葵/轮椅")],
    "group-2": [("Hibiki", "响"), ("Iori", "伊织/佐三枪"), "Iroha", "伊吕波/168"],
    "group-3": [("Aru", "阿露"), ("Haruna", "神秘狙/羽留奈")],
    "整活用": [("Saya", "纱绫/鼠鼠"), ("Izumi", "泉/八"), ("Sumire", "堇")]
}
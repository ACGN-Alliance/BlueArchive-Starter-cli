from dataclasses import dataclass, field
from typing import Literal, List
from pathlib import Path
from enum import Enum
import json
import os

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
    scan_list: list = field(default_factory=list)
    main_line: bool = False
    recuit_num: int = 0
    if_screenshot: bool = False
    is_mumu: bool = False
    pool: int = 1
    speed: Literal["fast", "normal", "slow", "very slow"] = "normal"
    too_many_errors: int = 30
    extra_delay: int = 0
    img_confidences: dict = field(default_factory=dict)


class OptionType(Enum):
    BOOL = "bool"
    NUM = "num"
    STR = "str"
    FUNC = "func"
    LITERAL_STR = "literal_str"


class Option:
    def __init__(
        self,
        name: str,
        type_: OptionType,
        setting_name: str,
        *args,
        func: callable = None,
        func_args: list = None,
    ) -> None:
        self.name = name
        self.type_ = type_
        self.setting_name = setting_name
        self.args = args
        self.func = func
        self.func_args = func_args

    def run(self):
        try:
            if self.type_ == OptionType.FUNC:
                self.func(*self.func_args)
            if self.type_ == OptionType.BOOL:
                setattr(
                    settings,
                    self.setting_name,
                    not getattr(settings, self.setting_name),
                )
            if self.type_ == OptionType.NUM:
                i = input("请输入新的值: ")
                if i.isdigit():
                    setattr(settings, self.setting_name, int(i))
                else:
                    print("输入不合法")
            if self.type_ == OptionType.STR:
                i = input("请输入新的值: ")
                setattr(settings, self.setting_name, i)
            if self.type_ == OptionType.LITERAL_STR:
                i = input("请输入新的值: ")
                if i in self.func_args:
                    setattr(settings, self.setting_name, i)
                else:
                    print("输入不合法")

            return True
        except Exception as e:
            print("设置失败: " + str(e))


class SettingsMenu:
    menu_list: List[Option] = []
    status_off: list = []

    def append(self, option: Option, show_status: bool = True) -> None:
        self.menu_list.append(option)
        if (not show_status) and option.setting_name:
            self.status_off.append(option.setting_name)

    def show(self):
        print("\n欢迎来到设置界面")
        for index, option in enumerate(self.menu_list):
            if (not option.setting_name) or (option.setting_name in self.status_off):
                print(f"{index + 1}. {option.name}")
            else:
                print(
                    f"{index + 1}. {option.name} 当前为 {getattr(settings, option.setting_name)}"
                )

        print(f"{len(self.menu_list) + 1}. 返回主菜单\n")

    def choose(self, index: int):
        return self.menu_list[index - 1].run()

    @property
    def length(self):
        return len(self.menu_list)


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

smenu = SettingsMenu()
smenu.append(Option("设置用户名", OptionType.STR, "username"))
smenu.append(Option("调整游客账户模式", OptionType.BOOL, "guest"))
smenu.append(Option("开/关box检测(BETA)", OptionType.BOOL, "box_scan"))
smenu.append(Option("开/关主线剧情收益(可多十连抽)", OptionType.BOOL, "main_line"))
smenu.append(Option("设置额外赠送抽数(单位: 十抽)", OptionType.NUM, "recuit_num"))
smenu.append(Option("开/关抽卡结果截图", OptionType.BOOL, "if_screenshot"))
smenu.append(Option("开/关mumu模拟器模式", OptionType.BOOL, "is_mumu"))
smenu.append(Option("设置需要抽取的卡池位置(*倒数*第几个)", OptionType.NUM, "pool"))
smenu.append(
    Option(
        "设置命令执行速度(fast, normal, slow, very slow)",
        OptionType.LITERAL_STR,
        "speed",
        func_args=["fast", "normal", "slow", "very slow"],
    )
)
smenu.append(Option("设置额外延迟(单位: 秒)", OptionType.NUM, "extra_delay"))
smenu.append(Option("设置识图错误中断数值(0为关闭)", OptionType.NUM, "too_many_errors"))


def img_confidence_set():
    if settings.img_confidences:
        print("当前置信度阈值:")
        for k, v in settings.img_confidences.items():
            print(f"{k} ==> {v}")
    else:
        print("当前置信度阈值均为0.91")

    print("\n")

    while True:
        arg = input(
            "输入格式: 图片名 阈值(其中阈值范围为0~1, 格式形如:main_interface 0.90), 输入exit退出, 输入reset重置为默认, 输入del 图片名删除\n"
        )
        if arg == "exit":
            return
        elif arg == "reset":
            settings.img_confidences = {}
            print("重置成功!")
            return
        elif arg.split(" ")[0] == "del":
            img_name = arg.split(" ")[1] + ".png"
            if img_name in settings.img_confidences:
                del settings.img_confidences[img_name]
                print("删除成功!")
            else:
                print("图片参数不存在")
        else:
            args = arg.split(" ")
            img_name = args[0] + ".png"
            confidence = float(args[1])

            if os.path.exists(f"./data/16_9/{img_name}"):
                settings.img_confidences[img_name] = confidence
                print("设置成功!")
            else:
                print("图片不存在")

        print("\n")


smenu.append(
    Option(
        "修改图片置信度阈值",
        OptionType.FUNC,
        "img_confidences",
        func=img_confidence_set,
        func_args=[],
    ),
    show_status=False,
)

box_scan_preset = {
    "group-1": [("Ako", "亚子"), ("Himar", "阳葵/轮椅")],
    "group-2": [("Hibiki", "响"), ("Iori", "伊织/佐三枪"), "Iroha", "伊吕波/168"],
    "group-3": [("Aru", "阿露"), ("Haruna", "神秘狙/羽留奈")],
    "整活用": [("Saya", "纱绫/鼠鼠"), ("Izumi", "泉/八"), ("Sumire", "堇")],
}

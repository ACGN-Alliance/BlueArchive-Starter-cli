import sys, os, time, json
from loguru import logger
from pathlib import Path
from typing import Optional

from utils import adb
from script import script

__version__ = "1.0.1"

device_now = ""
adb_con: Optional[adb.ADB] = None  # adb类变量
all_device_lst = {}
port = 0


def _if_adb_exists():
    # TODO 检测环境变量 + 子目录
    if os.path.exists("./platform-tools/adb.exe") or os.path.exists("./platform-tools/adb"):
        return True
    else:
        return False


def menu():
    print("\n" * 1)
    if device_now:
        print("当前设备: " + device_now + "端口: " + str(port) + "\n")
    else:
        print("当前未连接设备\n")

    print("1. 注意事项(必读)")
    print("2. 扫描设备")
    print("3. 截图适配(TODO)")
    print("4. 加载")
    print("5. 运行脚本")
    print("6. 退出")


def notice():
    notice = """
- 确保网络通畅, 中途尽量不要出现连接失败以及掉线的状况
- 请关闭手机休眠
- 游戏设置中的`Quality`调整为`Very high`
- 语言请使用`English`
- 游戏宽高比设置为`16:9`
- 如果加入了社团请先退出, 否则会导致操作失败
- 目前版本仅能抽取30抽, 40抽预计下个版本支持"""
    print(notice)
    input("按任意键以继续...")


def scan():
    if not _if_adb_exists():
        logger.error("未检测到adb可执行文件, 请将可执行文件放置于同目录下")

    while True:
        global adb_con, all_device_lst, device_now, port
        adb_con = adb.ADB(scan_mode=True)
        device_lst = adb_con.get_device_list()

        print("1. 返回主菜单")
        print("2. 重新扫描")
        for i, device in enumerate(device_lst):
            print(f"{i + 3}. {device}")
            # if "127.0.0.1" in device:  # 消除重复设备
            #     continue
            all_device_lst[i + 3] = device.split(" ")[0]

        if len(device_lst) == 0:
            print("\n未扫描到设备, 请尝试重新扫描")

        device_num = input("请选择设备: ")
        if device_num.isdigit():
            device_num = int(device_num)
        else:
            print("请输入数字")
            continue

        if device_num == 1:
            return
        elif device_num == 2:
            continue
        else:
            device_now = all_device_lst.get(device_num, "")
            if not device_now:
                print("请选择正确的设备")
                continue

            if "emulator" in device_now:
                port = int(device_now.split("-")[1]) + 1
            elif "127.0.0.1" in device_now:
                port = int(device_now.split(":")[1])
            else:
                port = 5555

            # TODO
            adb_con = adb.ADB(device_name=f"127.0.0.1:{port}")
            print(f"已选择设备: {device_now}")
            break


def screenshot():
    global adb_con


def load():
    while True:
        print("\n1.从文件加载(save.json)")
        print("2.从输入加载")
        print("3.返回主菜单")
        load_mode = int(input("请选择加载模式: "))
        if load_mode == 1:
            try:
                cot = json.load(open("save.json", "r", encoding="utf-8"))
            except FileNotFoundError:
                print("未找到save.json文件")
                continue
            return getattr(cot, "load_point", 0)
        elif load_mode == 2:
            point = input("请输入加载点(默认为0): ")
            if isinstance(point, int):
                return point
            else:
                print("加载点必须是数字, 详见文档")
                continue
        elif load_mode == 3:
            return 0
        else:
            print("请输入正确的加载模式")
            continue


def run(_load: int = 0):
    global adb_con
    path = Path("./data/16_9/")
    try:
        mapping = json.load(open(path.joinpath("mapping.json"), "r", encoding="utf-8"))
    except FileNotFoundError:
        logger.error("未找到资源文件, 请确认下载是否完整")
        return

    script(
        adb_con,
        path,
        mapping,
        load_point=_load
    )


def _verify_device():
    global adb_con
    if not adb_con:
        print("请先扫描并选择设备")
        return False
    else:
        return True


if __name__ == '__main__':
    print(f"欢迎使用BlueArchive-Starter-cli, 当前版本{__version__}, 作者: ACGN-Alliance, 交流群: 769521861")
    time.sleep(2)

    load_point = 0

    while True:
        menu()
        mode = input("请选择模式: ")
        if mode.isdigit():
            mode = int(mode)
        else:
            print("请输入数字")
            continue

        if mode == 1:
            notice()
        elif mode == 2:
            scan()
        elif mode == 3:
            if not _verify_device():
                continue
            print("该功能尚未开发, 敬请期待")
            screenshot()
        elif mode == 4:
            load_point = load()
        elif mode == 5:
            if not _verify_device():
                continue
            run(_load=load_point)
        elif mode == 6:
            print("感谢使用~")
            sys.exit(0)
        else:
            print("请选择正确的模式")
            continue

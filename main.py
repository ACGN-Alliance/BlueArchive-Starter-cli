import json
import os
import subprocess
import sys
import time
import signal
import traceback
from pathlib import Path
from typing import Optional

from loguru import logger

from script import script
from utils import adb

__version__ = "1.0.3"

device_now = ""
adb_con: Optional[adb.ADB] = None  # adb类变量
all_device_lst = {}
port = 0

# 异常处理装饰器
def exception_handle(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            traceback.print_exc()
            return None

    return wrapper

# ctrl+c退出时关闭adb server
def signal_handler(sig, frame):
    global adb_con
    if adb_con:
        adb_con.kill_server()

    sys.exit(-1)

signal.signal(signal.SIGINT, signal_handler)

def menu():
    global device_now, port
    print("\n" * 1)
    if device_now:
        print("当前设备: " + device_now + "端口: " + str(port) + "\n")
    else:
        print("当前未连接设备\n")

    print("1. 注意事项(必读)")
    print("2. 扫描设备")
    print("3. ADB工具箱")
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
- 目前版本仅能抽取30抽, 40抽预计下个版本支持
- 保持未绑定账号状态"""
    print(notice)
    input("按任意键以继续...")


def on_device_selected(is_physic=False):
    global adb_con, all_device_lst, device_now, port
    if "emulator" in device_now:
        port = int(device_now.split("-")[1]) + 1
    elif "127.0.0.1" in device_now or "localhost" in device_now:
        port = int(device_now.split(":")[1])
    else:
        is_physic = True
        port = 5555

    adb_con = adb.ADB(device_name=f"localhost:{port}", is_physic_device=is_physic)
    print(f"已选择设备: {device_now}")

@exception_handle
def scan():
    while True:
        global adb_con, all_device_lst, device_now, port
        is_physic = False
        adb_con = adb.ADB(scan_mode=True)
        device_lst = adb_con.get_device_list()

        print("0. 指定地址")
        print("1. 返回主菜单")
        print("2. 重新扫描")
        for i, device in enumerate(device_lst):
            print(f"{i + 3}. {device}")
            all_device_lst[i + 3] = device.split(" ")[0]

        if len(device_lst) == 0:
            print("\n未扫描到设备, 请尝试重新扫描, 或手动指定地址")

        device_num = input("请选择设备: ")
        if device_num.isdigit():
            device_num = int(device_num)
        else:
            print("请输入数字")
            continue

        if device_num == 0:
            if os.name == "nt":
                adb_path = "./platform-tools/adb.exe"
            else:
                adb_path = "./platform-tools/adb"
            rv = subprocess.run([adb_path, "connect", address := input("请输入设备地址: ")], stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)

            # 包含两种状态:1. already connected to 2. connected to
            if "connected to" in rv.stdout.decode("utf-8") or "connected to" in rv.stderr.decode("utf-8"):
                device_now = address
                on_device_selected(is_physic=is_physic)
                print("连接成功:", address)
                break
            else:
                print("连接失败:", rv.stdout.decode("utf-8"), rv.stderr.decode("utf-8"))
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

            on_device_selected(is_physic=is_physic)
            break

@exception_handle
def adb_test():
    global adb_con
    while True:
        mode = int(input("\n1.adb命令行工具(实验性功能)\n2.坐标测试与换算工具\n3.返回主菜单\n请选择需要的工具:"))
        if mode == 1:
            print("\n可以输入adb命令进行调试, 也可以输入exit退出(注: 使用getevent一类需要持续监听的命令只能用ctrl+c退出)")
            while True:
                cmd = input("ADB CMD> ")
                if cmd == "exit":
                    break
                elif cmd.startswith("adb "):
                    print("ADB OUTPUT> " + adb_con.command(cmd))
                else:
                    print("ADB OUTPUT> 请输入正确的ADB命令, 输入exit以退出")
        elif mode == 2:
            pos = input("请输入0-100的整数坐标(以空格分隔, 如50 50, exit退出):")

            while True:
                if pos == "exit":
                    break

                pos_args = pos.split()
                if pos_args[0].isdigit() and pos_args[1].isdigit():
                    real_x, real_y = adb_con._normalized_to_real_coordinates(int(pos_args[0]), int(pos_args[1]))
                    print("坐标转换结果: " + str(real_x) + " " + str(real_y))
                    adb_con.click(int(pos_args[0]), int(pos_args[1]))
                else:
                    print("请输入正确的坐标格式")

                pos = input("\n请输入0-100的整数坐标:")

        elif mode == 3:
            return
        else:
            print("请选择正确的工具")
            continue

@exception_handle
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
            return cot.get('load_point', 0)
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
            adb_test()
        elif mode == 4:
            load_point = load()
        elif mode == 5:
            if not _verify_device():
                continue
            run(_load=load_point)
        elif mode == 6:
            print("感谢使用~")
            signal_handler(0, 0)
            sys.exit(0)
        else:
            print("请选择正确的模式")
            continue

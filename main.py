import json
import os
import signal
import subprocess
import sys
import time
import traceback
from pathlib import Path
from typing import Optional

from loguru import logger

from script import script
from utils import adb
from utils.settings import settings, setting_file

__version__ = "1.0.6.3"

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
            print("发生异常, 请将以下信息反馈给开发者:")
            traceback.print_exc()
            return None
        except BaseException as e:
            print("发生异常, 请将以下信息反馈给开发者:")
            traceback.print_exc()
            return None

    return wrapper


# ctrl+c退出时关闭adb server
def signal_handler(sig, frame):
    global adb_con
    if adb_con:
        adb_con.kill_server()

    if settings:
        json.dump(settings.__dict__, open(setting_file, "w", encoding="utf-8"))

    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)


def menu():
    global port, device_now
    print("\n" * 1)
    if device_now:
        print("当前设备: " + device_now + " | 端口: " + str(port) + "\n")
    else:
        print("当前未连接设备\n")

    print("1. 注意事项(必读)")
    print("2. 扫描设备")
    print("3. ADB工具箱")
    print('4. 配置')
    print("5. 加载")
    print("6. 运行脚本")
    print("7. 退出")


def notice():
    notice = """
- 确保网络通畅, 中途尽量不要出现连接失败以及掉线的状况
- 请关闭手机休眠
- 游戏设置中的`Quality`调整为`Very high`
- 语言请使用`English`
- 游戏宽高比设置为`16:9`
- 如果加入了社团请先退出, 否则会导致操作失败
- 扫描并连接实体机时, 请留意手机上的rsa确认对话框并点击确认
- 用户名不能使用非法字符，中文因为adb的限制也不能使用
"""
    print(notice)
    input("按任意键以继续...")


def on_device_selected():
    global adb_con, all_device_lst, device_now, port

    pname = ""
    if "emulator" in device_now:
        port = int(device_now.split("-")[1]) + 1
    elif "127.0.0.1" in device_now or "localhost" in device_now:
        port = int(device_now.split(":")[1])
    else:
        pname = device_now
        port = 5555

    try:
        adb_con = adb.ADB(
            device_name=f"localhost:{port}",
            physic_device_name=pname,
            settings=settings, 
            is_mumu=settings.is_mumu
        )
        print(f"已选择设备: {device_now}")
        return True
    except IndexError:
        print("ERROR: 设备无效, 请重新选择")
        return False


@exception_handle
def scan():
    while True:
        global adb_con, all_device_lst, device_now, port
        adb_con = adb.ADB(scan_mode=True, settings=settings, delay=0.3)
        device_lst = adb_con.get_device_list()

        print("0. 指定地址")
        print("1. 返回主菜单")
        print("2. 重新扫描")
        for i, device in enumerate(device_lst):
            print(f"{i + 3}. {device}")
            all_device_lst[i + 3] = device.split(" ")[0]

        if len(device_lst) == 0:
            print("\n未扫描到设备, 请查看模拟器/手机是否已打开usb调试, 然后尝试重新扫描, 或手动指定地址")

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
                if on_device_selected():
                    print("连接成功:", address)
                    break
                else:
                    continue
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

            on_device_selected()
            break


@exception_handle
def adb_test():
    global adb_con
    while True:
        mode = int(input("\n1.adb命令行工具(实验性功能)\n2.坐标测试与换算工具\n3.返回主菜单\n请选择需要的工具:"))
        if mode == 1:
            print(
                "\n可以输入adb命令进行调试, 也可以输入exit退出(注: 使用getevent一类需要持续监听的命令只能用ctrl+c退出)")
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
def settings_menu():
    while True:
        print("\n欢迎来到设置界面")
        print(f"1. 设置用户名 当前为: {settings.username}")
        print(f"2. 调整游客账户模式 当前为: {settings.guest}")
        print(f"3. 设置高宽比(开发中) 当前为: {settings.ratio}")
        print(f"4. 开/关box检测(开发中) 当前为: {settings.box_scan}")
        print(f"5. 开/关主线剧情收益(可多十连抽) 当前为: {settings.main_line}")
        print(f"6. 设置额外赠送抽数(单位: 十抽) 当前为: {settings.recuit_num}")
        print(f"7. 开/关抽卡结果截图 当前为: {settings.if_screenshot}")
        print(f"8. 开/关mumu模拟器模式 当前为: {settings.is_mumu}")
        print(f"9. 设置需要抽取的卡池位置(*倒数*第几个) 当前为: {settings.pool}")
        print(f"10. 设置命令执行速度 当前为: {settings.speed}")
        print(f"11. 设置识图错误中断数值(0为关闭) 当前为: {settings.too_many_errors}")
        print("12. 返回主菜单\n")

        choice = int(input("请选择: "))
        if choice == 1:
            name = input("请输入用户名: ")
            if name.isalnum():
                settings.username = name
            else:
                print("用户名只能包含字母和数字!")
                continue
        elif choice == 2:
            if not settings.guest:
                ans = input("是否有提醒Link Account的弹窗? (y/n): ")
                if ans == "y":
                    settings._link_account = True
                elif ans == "n":
                    settings._link_account = False
                else:
                    print("请输入正确的选项")
                    continue

            settings.guest = not settings.guest
        elif choice == 3:
            print("该功能尚未开发完成, 请等待之后的版本")
            # settings.ratio = input("请输入高宽比(如16:9): ")
        elif choice == 4:
            print("该功能尚未开发完成, 请等待之后的版本")
            # settings.box_scan = not settings.box_scan
        elif choice == 5:
            settings.main_line = not settings.main_line
        elif choice == 6:
            num = input("请输入额外赠送的抽数(指当期活动送的而非新手奖励): ")
            if num.isdigit() and int(num) >= 0:
                settings.recuit_num = int(num)
            else:
                print("数值不合法")
                continue
        elif choice == 7:
            settings.if_screenshot = not settings.if_screenshot
        elif choice == 8:
            settings.is_mumu = not settings.is_mumu
        elif choice == 9:
            num = input("请输入需要抽取的卡池位置(倒数): ")
            if num.isdigit() and int(num) >= 1:
                settings.pool = int(num)
            else:
                print("数值不合法")
                continue
        elif choice == 10:
            speed = input("请输入命令执行速度(fast/normal/slow/very slow): ")
            if speed in ["fast", "normal", "slow", "very slow"]:
                settings.speed = speed
            else:
                print("请输入正确的速度")
                continue
        elif choice == 11:
            num = input("请输入识图错误中断数值: ")
            if num.isdigit():
                settings.too_many_errors = int(num)
            else:
                print("数值不合法")
                continue
        elif choice == 12:
            json.dump(settings.__dict__, open(setting_file, "w", encoding="utf-8"))
            return
        else:
            print("请选择正确的选项")
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
            point = input("请输入加载点: ")
            if point.isdigit():
                return int(point)
            else:
                print("加载点必须是数字, 详见文档")
                continue
        elif load_mode == 3:
            return 0
        else:
            print("请输入正确的加载模式")
            continue

@exception_handle
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
        settings,
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
            settings_menu()
        elif mode == 5:
            load_point = load()
        elif mode == 6:
            if not _verify_device():
                continue
            run(_load=load_point)
        elif mode == 7:
            print("感谢使用~")
            os.kill(signal.CTRL_C_EVENT, 0)  # 主动触发ctrl+c
        else:
            print("请选择正确的模式")
            continue

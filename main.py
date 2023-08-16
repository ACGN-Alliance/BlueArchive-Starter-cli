import sys, os, time
from loguru import logger

from utils import adb

__version__ = "0.0.1"

device_now = ""
adb_con = None  # adb类变量
all_device_lst = {}
port = 0

def _if_adb_exists():
    # TODO 检测环境变量 + 子目录
    if os.path.exists("adb.exe") or os.path.exists("adb"):
        return True
    else:
        return False

def menu():
    print("\n" * 3)
    if device_now:
        print("当前设备: " + device_now + "端口: " + str(port))
    else:
        print("当前未连接设备")

    print("1. 注意事项(必读)")
    print("2. 扫描设备(TODO)")
    print("3. 截图适配(TODO)")
    print("4. 加载")
    print("5. 运行脚本")
    print("6. 退出")

def notice():
    pass

def scan():
    if not _if_adb_exists():
        logger.error("未检测到adb可执行文件, 请将可执行文件放置于同目录下")

    while True:
        global adb_con, all_device_lst, device_now, port
        adb_con = adb.ADB()
        device_lst = adb_con.get_device_list()

        print("1. 返回主菜单")
        print("2. 重新扫描")
        for i, device in enumerate(device_lst):
            print(f"{i+3}. {device}")
            all_device_lst[i+3] = device.split(" ")[0]

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
                port = int(device_now.split("-")[1])
            else:
                port = 5555

            adb_con = adb.ADB(device_name=f"127.0.0.1:{port}")
            print(f"已选择设备: {device_now}")
            break

def screenshot():
    pass

def load():
    pass

def run():
    global adb_con
    adb_con: adb.ADB

    ...  # 脚本编写处

def _verify_device():
    global adb_con
    if not adb_con:
        print("请先扫描并选择设备")
        return False
    else:
        return True


if __name__ == '__main__':
    print(f"欢迎使用BlueArchive-Starter-cli, 当前版本{__version__}, 作者: ACGN-Alliance, 交流群: 769521861")
    # time.sleep(2)
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
                break
            screenshot()
        elif mode == 4:
            if not _verify_device():
                break
            load()
        elif mode == 5:
            if not _verify_device():
                break
            run()
        elif mode == 6:
            sys.exit(0)
        else:
            print("请选择正确的模式")
            continue

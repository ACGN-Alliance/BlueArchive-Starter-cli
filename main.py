import json
import os
import subprocess
import sys
import time
import traceback
from pathlib import Path
from typing import Optional
from zipfile import ZipFile

from loguru import logger

from utils.cmp_server import ImageComparatorServer

# for user
sys.path.append(os.path.abspath("ocr_dependencies"))
# for developer
sys.path.append(os.path.abspath(".ocr_venv/Lib/site-packages"))

from script import script
from utils import adb
from utils.settings import (settings,
                            setting_file,
                            box_scan_preset,
                            smenu
                            )

__version__ = "1.1.3.3"


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


class MainProgram:
    device_now = ""
    adb_con: Optional[adb.ADB] = None  # adb类变量
    all_device_lst = {}
    port = 0
    load_point = 0

    is_in_progress = False

    def __init__(self) -> None:
        pass

    def get_instance(self):
        return self

    def menu(self):
        print("\n" * 1)
        if self.device_now:
            print("当前设备: " + self.device_now + " | 端口: " + str(self.port) + "\n")
        else:
            print("当前未连接设备\n")

        print("1. 注意事项(必读)")
        print("2. 扫描设备")
        print("3. ADB工具箱")
        print('4. 配置')
        print("5. 加载")
        print("6. box检测清单")
        print("7. 运行脚本")
        print("8. 安装OCR依赖")
        print("9. 退出")

    def notice(self):
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

    def _on_device_selected(self):
        pname = ""
        if "emulator" in self.device_now:
            self.port = int(self.device_now.split("-")[1]) + 1
        elif "127.0.0.1" in self.device_now or "localhost" in self.device_now:
            self.port = int(self.device_now.split(":")[1])
        else:
            pname = self.device_now
            self.port = 5555

        try:
            self.adb_con = adb.ADB(
                device_name=f"localhost:{self.port}",
                physic_device_name=pname,
                settings=settings,
                is_mumu=settings.is_mumu
            )
            print(f"已选择设备: {self.device_now}")
            return True
        except IndexError:
            print("ERROR: 设备无效, 请重新选择")
            return False

    @exception_handle
    def scan(self):
        while True:
            temp_adb = adb.ADB(scan_mode=True, settings=settings, delay=0.3)
            self.device_lst = temp_adb.get_device_list()

            print("0. 指定地址")
            print("1. 返回主菜单")
            print("2. 重新扫描")
            for i, device in enumerate(self.device_lst):
                print(f"{i + 3}. {device}")
                self.all_device_lst[i + 3] = device.split(" ")[0]

            if len(self.device_lst) == 0:
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
                    self.device_now = address
                    if self._on_device_selected():
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
                self.device_now = self.all_device_lst.get(device_num, "")
                if not self.device_now:
                    print("请选择正确的设备")
                    continue

                self._on_device_selected()
                break

    def install_ocr_deps(self):
        try:
            from utils import ocr
            for box, text, confidence in ocr.ocr(r"tests/img.png"):
                box = str(box)
                print(f"box = {box:<80}, text = {text:<20}, confidence = {confidence:.2f}")
            print("OCR依赖已安装, 无需重复安装")
            del ocr
            return

        except Exception as e:
            dep = [f for f in os.listdir(os.getcwd()) if f.startswith("ocr_dependencies") and f.endswith(".zip")]
            print(f"{os.getcwd()=}, {dep=}")
            if len(dep) == 0:
                print(
                    "\033[91m未找到依赖包, 请先去对应的release中下载ocr_dependencies_win_3.10.zip并移动到程序目录下\033[0m")
                return
            dep = dep[0]
            print(f"正在安装依赖: {dep}...")
            # extract zip file to current dir,if dir or file exists,overwrite or merge
            with ZipFile(dep, "r") as zip_file:
                zip_file.extractall(os.getcwd())
            print("\033[91m安装完成,重启程序以生效\033[0m")
            os.remove(dep)

    @exception_handle
    def adb_test(self):
        while True:
            mode = int(input(
                "\n1.adb命令行工具(实验性功能)\n2.坐标测试与换算工具\n3.截图&坐标记录工具\n4.图像对比工具\n5.返回主菜单\n请选择需要的工具:"
                ))
            if mode == 1:
                print(
                    "\n可以输入adb命令进行调试, 也可以输入exit退出(注: 使用getevent一类需要持续监听的命令只能用ctrl+c退出)")
                while True:
                    cmd = input("ADB CMD> ")
                    if cmd == "exit":
                        break
                    elif cmd.startswith("adb "):
                        print("ADB OUTPUT> " + self.adb_con.command(cmd))
                    else:
                        print("ADB OUTPUT> 请输入正确的ADB命令, 输入exit以退出")
            elif mode == 2:
                pos = input("请输入0-100的整数坐标(以空格分隔, 如50 50, exit退出):")

                while True:
                    if pos == "exit":
                        break

                    pos_args = pos.split()
                    if pos_args[0].isdigit() and pos_args[1].isdigit():
                        real_x, real_y = self.adb_con._normalized_to_real_coordinates(int(pos_args[0]), int(pos_args[1]))
                        print("坐标转换结果: " + str(real_x) + " " + str(real_y))
                        self.adb_con.click(int(pos_args[0]), int(pos_args[1]))
                    else:
                        print("请输入正确的坐标格式")

                    pos = input("\n请输入0-100的整数坐标:")
            elif mode == 3:
                if not Path("temp").exists():
                    Path("temp").mkdir()
                if not Path("temp/mapping.json").exists():
                    Path("temp/mapping.json").touch()

                (x1, x2, y1, y2) = (0, 0, 0, 0)
                while True:
                    pos = input("请输入整数坐标(以空格分隔, 如1280 720, exit退出):")
                    if pos == "exit":
                        break
                    pos_args = pos.split()
                    if pos_args[0].isdigit() and pos_args[1].isdigit():
                        x1, y1 = self.adb_con._real_to_normalized_coordinates(int(pos_args[0]), int(pos_args[1]))

                    pos_1 = input("请输入整数坐标(以空格分隔, 如1280 720, exit退出):")
                    if pos_1 == "exit":
                        break
                    pos_args_1 = pos_1.split()
                    if pos_args_1[0].isdigit() and pos_args_1[1].isdigit():
                        x2, y2 = self.adb_con._real_to_normalized_coordinates(int(pos_args_1[0]), int(pos_args_1[1]))

                    self.adb_con.screenshot_region(x1, y1, x2, y2, "temp/adb_test.png")
                    Path("temp/mapping.json").write_text(json.dumps({"adb_test.png": (x1, y1, x2, y2)}))
            elif mode == 4:
                mapping = json.load(open("temp/mapping.json", "r", encoding="utf-8"))
                self.adb_con.compare_img(
                    *mapping["adb_test.png"],
                    img = Path("./temp/adb_test.png"),
                    debug=True
                )
            elif mode == 5:
                return
            else:
                print("请选择正确的工具")
                continue

    @exception_handle
    def settings_menu(self):
        while True:
            smenu.show()
            choice = int(input("请选择: "))
            if choice == smenu.length + 1:
                json.dump(settings.__dict__, open(setting_file, "w", encoding="utf-8"))
                return
            elif choice >= 1 and choice <= smenu.length:
                smenu.choose(choice)
            else:
                print("请选择正确的选项")
                continue

    def load(self):
        while True:
            print(f"\n当前加载点: {self.load_point}\n")
            print("1.从输入加载")
            print("2.返回主菜单")
            load_mode = int(input("请选择加载模式: "))
            if load_mode == 1:
                point = input("请输入加载点: ")
                if point.isdigit():
                    if int(point) < 18:
                        self.load_point = int(point)
                    else:
                        print("加载点必须小于18")
                        continue
                else:
                    print("加载点必须是数字")
                    continue
            elif load_mode == 2:
                return
            else:
                print("请输入正确的加载模式")
                continue

    def box_scan_settings(self):
        while True:
            print("\n1.查看box检测队列")
            print("2.添加人物")
            print("3.删除人物")
            print("4.清空队列")
            print("5.选取预设队列")
            print("6.返回主菜单")

            choice = int(input("请选择: "))
            if choice == 1:
                print(settings.scan_list)
            elif choice == 2:
                name = input("请输入人物名: ")
                if name in settings.scan_list:
                    print("该人物已存在")
                    continue
                settings.scan_list.append(name)
            elif choice == 3:
                name = input("请输入人物名: ")
                if name not in settings.scan_list:
                    print("该人物不存在")
                    continue
                settings.scan_list.remove(name)
            elif choice == 4:
                settings.scan_list = []
            elif choice == 5:
                for k, v in box_scan_preset.items():
                    print(f"{k} ==> {v}")
                choice = input("请选择: ")
                if box_scan_preset.get(choice, None):
                    for chara in box_scan_preset[choice]:
                        settings.scan_list.append(chara[0])
                else:
                    print("请输入正确的预设名")
            elif choice == 6:
                return
            else:
                print("请输入正确的选项")
                continue

    @exception_handle
    def run(self):
        path = Path("./data/16_9/")
        try:
            mapping = json.load(open(path.joinpath("mapping.json"), "r", encoding="utf-8"))
        except FileNotFoundError:
            logger.error("未找到资源文件, 请确认下载是否完整")
            return

        while True:
            self.is_in_progress = True
            res = script(
                self.adb_con,
                path,
                mapping,
                settings,
                load_point=self.load_point
            )
            if res:
                self.is_in_progress = False
                break
            else:
                self.load_point = 0
                continue

    def _verify_device(self):
        if not self.adb_con:
            print("请先扫描并选择设备")

        return bool(self.adb_con)

    def register_ocr_path(self):
        # for user
        sys.path.append(os.path.abspath("ocr_dependencies"))
        # for developer
        sys.path.append(os.path.abspath(".ocr_venv/Lib/site-packages"))

    def __del__(self):
        try:
            if self.adb_con:
                self.adb_con.kill_server()
            ImageComparatorServer.get_global_instance().stop()  # stop server
        except Exception as e:
            print(e)


def register_ocr_path():
    # for user
    sys.path.append(os.path.abspath("ocr_dependencies"))
    # for developer
    sys.path.append(os.path.abspath(".ocr_venv/Lib/site-packages"))


if __name__ == '__main__':
    register_ocr_path()
    print(f"欢迎使用BlueArchive-Starter-cli, 当前版本{__version__}, 作者: ACGN-Alliance, 交流群: 769521861")
    time.sleep(1)
    ImageComparatorServer.get_global_instance()  # start Server
    program = MainProgram()

    while True:
        program.menu()
        mode = input("请选择模式: ")
        if mode.isdigit():
            mode = int(mode)
        else:
            print("请输入数字")
            continue

        if mode == 1:
            program.notice()
        elif mode == 2:
            program.scan()
        elif mode == 3:
            if not program._verify_device():
                continue
            program.adb_test()
        elif mode == 4:
            program.settings_menu()
        elif mode == 5:
            program.load()
        elif mode == 6:
            program.box_scan_settings()
        elif mode == 7:
            if not program._verify_device():
                continue
            program.run()
        elif mode == 8:
            program.install_ocr_deps()
        elif mode == 9:
            # os.kill(signal.CTRL_C_EVENT, 0)  # 主动触发ctrl+c
            break
        else:
            print("请选择正确的模式")
            continue
    del program
    sys.exit(0)

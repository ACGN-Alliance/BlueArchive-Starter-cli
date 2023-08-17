import sys, os, time, json
from loguru import logger
from pathlib import Path
from typing import Optional

from utils import adb

__version__ = "0.0.1"

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
        adb_con = adb.ADB(scan_mode=True)
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
    global adb_con

def load():
    pass

def run():
    def skip_story():
        adb_con.click(95, 5)
        adb_con.click(95, 15)
        adb_con.click(63, 71)

    global adb_con
    name = input("请输入你想要的昵称(禁止非法字符): ")

    path = Path("./data/16_9/")
    mapping = json.load(open(path.joinpath("mapping.json"), "r", encoding="utf-8"))

    while not adb_con.compare_img(
        *mapping["main_momotalk.png"], img=path.joinpath("main_momotalk.png")
    ):
        adb_con.back()

    logger.info("已回到主菜单，开始销号")
    adb_con.click(95, 4)
    adb_con.click(60, 40)
    adb_con.click(70, 50)
    adb_con.click(55, 45)
    adb_con.input_text("BlueArchive")
    adb_con.click(58, 67)
    adb_con.click(58, 67)
    adb_con.multi_click(55, 70, 5)

    logger.success("1. 创建账号")
    while not adb_con.compare_img(
            *mapping["start_menu_icon.png"], img=path.joinpath("start_menu_icon.png")
    ):
        adb_con.sleep(1)
    logger.info("已进入开始界面")
    adb_con.multi_click(50, 70, 4)
    while not adb_con.compare_img(
            *mapping["start_name.png"], img=path.joinpath("start_name.png")
    ):
        adb_con.click(50, 70)
    logger.info("输入名字")
    adb_con.click(50, 50)

    adb_con.input_text(name)
    adb_con.multi_click(50, 70, 40)

    logger.success("2. 初始剧情")
    while not adb_con.compare_img(
            *mapping["story_menu.png"], img=path.joinpath("story_menu.png")
    ):
        adb_con.click(50, 50)
    skip_story()
    logger.success("3. 战斗1")
    logger.info("跳过介绍")
    adb_con.multi_click(50, 70, 25)
    while not adb_con.compare_img(
        *mapping["battle_finish.png"], img=path.joinpath("battle_finish.png")
    ):
        logger.info("尝试使用技能")
        for _ in range(2):
            adb_con.click(80, 88)
            adb_con.click(80, 35)
            adb_con.click(70, 88)
            adb_con.click(43, 52)
    logger.info("战斗结束")
    adb_con.click(90, 90)
    logger.success("4. 两段剧情")
    for _ in range(2):
        while not adb_con.compare_img(
                *mapping["story_menu.png"], img=path.joinpath("story_menu.png")
        ):
            adb_con.click(50, 50)
        skip_story()
    logger.success("5. 战斗2")
    adb_con.multi_click(50, 50, 15)
    for i in range(4):
        while not adb_con.compare_img(
                *mapping["story_menu.png"], img=path.joinpath("story_menu.png")
        ):
            adb_con.multi_click(50, 50, 3)
        logger.info(f"第 {i + 1} 段剧情")
        skip_story()
    logger.success("使用技能")
    adb_con.multi_click(50, 50, 5)
    adb_con.click(70, 88)
    adb_con.click(80, 20)
    while not adb_con.compare_img(
            *mapping["battle_finish.png"], img=path.joinpath("battle_finish.png")
    ):
        adb_con.sleep(1)
    adb_con.click(90, 90)
    logger.success("5. 两段剧情")
    while not adb_con.compare_img(
            *mapping["story_menu.png"], img=path.joinpath("story_menu.png")
    ):
        adb_con.click(50, 50)
    for _ in range(4):
        skip_story()
    logger.success("6. OP 动画")
    adb_con.multi_click(60, 70, 10)

    logger.success("1. 开局抽卡")
    while not adb_con.compare_img(
            *mapping["main_recurit.png"], img=path.joinpath("main_recurit.png"), confidence=0.6
    ):
        adb_con.multi_click(50, 50, 3)
    adb_con.click(70, 90)
    adb_con.sleep(10)
    adb_con.click(76, 72)
    adb_con.click(60, 70)
    adb_con.multi_click(50, 75, 10)
    while not adb_con.compare_img(
            *mapping["recurit_confirm.png"], img=path.joinpath("recurit_confirm.png")
    ):
        adb_con.multi_click(92, 7, 5)
    adb_con.screenshot("1.png")
    adb_con.click(50, 90)
    adb_con.sleep(10)
    logger.success("2. 开始作战")
    adb_con.multi_click(88, 35, 4)
    adb_con.multi_click(75, 75, 3)
    adb_con.multi_click(40, 65, 10)
    logger.success("3. 开始编队")
    adb_con.multi_click(95, 25, 5)
    adb_con.sleep(3)
    adb_con.multi_click(25, 50, 10)
    logger.success("4. 开始道中作战")
    adb_con.multi_click(90, 80, 2)
    for _ in range(2):
        adb_con.multi_click(90, 90, 2)
        adb_con.sleep(5)
    adb_con.multi_click(50, 63, 5)
    adb_con.sleep(10)
    logger.success("5. 开启auto")
    adb_con.click(95, 95)
    while not adb_con.compare_img(
            *mapping["battle_finish.png"], img=path.joinpath("battle_finish.png")
    ):
        adb_con.sleep(1)
    logger.success("6. 完成作战")
    adb_con.click(90, 90)
    adb_con.sleep(5)
    adb_con.click(50, 90)
    adb_con.sleep(5)
    adb_con.multi_click(90, 90, 5)
    logger.success("7. 开始BOSS作战")
    adb_con.multi_click(60, 55, 5)
    while not adb_con.compare_img(
            *mapping["battle_finish.png"], img=path.joinpath("battle_finish.png")
    ):
        adb_con.sleep(1)
    logger.success("8. 完成作战")
    adb_con.multi_click(90, 90, 5)
    adb_con.multi_click(85, 90, 10)
    logger.success("9. 返回大厅")
    adb_con.multi_click(40, 90, 20)
    while not adb_con.compare_img(
            *mapping["main_momotalk.png"], img=path.joinpath("main_momotalk.png")
    ):
        adb_con.multi_click(40, 90, 5)
    logger.success("10. MomoTalk & 收取邮件")
    while not adb_con.compare_img(
            *mapping["no_mail.png"], img=path.joinpath("no_mail.png"), confidence=0.5
    ):
        for _ in range(2):
            adb_con.click(12.18, 18.66)
            adb_con.click(11.56, 41.11)
            adb_con.click(88, 5)
            adb_con.click(88, 5)
            adb_con.click(82.5, 94.44)
    logger.success("11. 开始抽卡")
    while not adb_con.compare_img(
            *mapping["main_momotalk.png"], img=path.joinpath("main_momotalk.png")
    ):
        for _ in range(3):
            adb_con.back()
    logger.info("进入抽卡")
    adb_con.multi_click(70, 90, 3)
    while not adb_con.compare_img(
            *mapping["recurit_page.png"], img=path.joinpath("recurit_page.png")
    ):
        logger.info("翻页")
        adb_con.click(3, 55)
    logger.debug("切换卡池")
    adb_con.multi_click(3, 55, 2)
    logger.info("开始抽卡")
    adb_con.click(76, 72)
    adb_con.click(60, 70)
    adb_con.sleep(5)
    for i in range(2):
        adb_con.multi_click(50, 75, 5)
        while not adb_con.compare_img(
                *mapping["recurit_confirm.png"], img=path.joinpath("recurit_confirm.png")
        ):
            adb_con.multi_click(92, 7, 3)
        adb_con.screenshot(f"{i + 2}.png")
        adb_con.click(50, 90)
        adb_con.sleep(3)
        adb_con.click(60, 90)
        adb_con.click(60, 65)
    logger.info("回到主菜单")
    while not adb_con.compare_img(
            *mapping["main_momotalk.png"], img=path.joinpath("main_momotalk.png")
    ):
        for _ in range(3):
            adb_con.back()

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

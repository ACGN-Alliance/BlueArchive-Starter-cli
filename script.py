import pathlib
from typing import Any, Tuple
from loguru import logger
import json

from utils import adb

def checkpoint(
        position: int,
        load_point: int,
        *args,
        alias: str = ""
) -> bool:
    """
    检查点

    :param position: 当前位置
    :param load_point: 检查点位置
    :param alias: 检查点别名
    :return: Tuple[bool, bool]: 是否需要跳过
    """
    if position != load_point:
        return True

    with open("save.json", "w", encoding="utf-8") as f:
        json.dump({"load_point": position}, f)

    logger.info(f"到达检查点 {position}.{alias}")
    return False

def script(
        adb_con: adb.ADB,
        path: pathlib.Path,
        mapping: Any,
        *args,
        load_point: int = 0
):
    """
    执行脚本
    adb_con: adb连接对象
    path: 图片加载地址
    mapping: 图片映射表
    load_point: 起始位置
    """
    def skip_story():
        adb_con.click(95, 5)
        adb_con.click(95, 15)
        adb_con.click(63, 71)

    if load_point >= 14:
        logger.error("加载点超出范围, 自动结束脚本")

    name = input("请输入你想要的昵称(禁止非法字符): ")

    if not checkpoint(0, load_point, alias="重置账号"):
        while not adb_con.compare_img(
                *mapping["main_momotalk.png"], img=path.joinpath("main_momotalk.png")
        ):
            adb_con.back()

        logger.info("已回到主菜单，开始销号")
        adb_con.click(95, 4)  # 菜单
        adb_con.click(60, 40)  # 账号
        adb_con.click(99, 4)  # 弹出网页关闭
        adb_con.click(70, 60)  # 重置账号
        adb_con.click(55, 45)
        adb_con.input_text("BlueArchive")
        adb_con.click(58, 67)
        adb_con.click(58, 67)
        adb_con.multi_click(55, 70, 5)
        load_point+=1

    if not checkpoint(1, load_point, alias="创建新账号"):
        # logger.success("1. 创建账号")
        while not adb_con.compare_img(
                *mapping["start_menu_icon.png"], img=path.joinpath("start_menu_icon.png")
        ):
            adb_con.sleep(1)
        logger.info("已进入开始界面")
        adb_con.click(99, 4)  # 弹出网页关闭
        adb_con.multi_click(50, 70, 4)
        while not adb_con.compare_img(
                *mapping["start_name.png"], img=path.joinpath("start_name.png")
        ):
            adb_con.click(50, 70)
        logger.info("输入名字")
        adb_con.click(50, 50)

        adb_con.input_text(name)
        adb_con.multi_click(50, 70, 40)
        load_point += 1

    if not checkpoint(2, load_point, alias="初始剧情"):
        # logger.success("2. 初始剧情")
        while not adb_con.compare_img(
                *mapping["story_menu.png"], img=path.joinpath("story_menu.png")
        ):
            adb_con.click(50, 50)
        skip_story()
        load_point += 1

    if not checkpoint(3, load_point, alias="战斗-1"):
        # logger.success("3. 战斗1")
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
        load_point += 1

    if not checkpoint(4, load_point, alias="剧情"):
        # logger.success("4. 两段剧情")
        for _ in range(2):
            while not adb_con.compare_img(
                    *mapping["story_menu.png"], img=path.joinpath("story_menu.png")
            ):
                adb_con.click(50, 50)
            skip_story()
        load_point += 1

    if not checkpoint(5, load_point, alias="战斗-2"):
        # logger.success("5. 战斗2")
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
        load_point += 1

    if not checkpoint(6, load_point, alias="剧情"):
        # logger.success("5. 两段剧情")
        while not adb_con.compare_img(
                *mapping["story_menu.png"], img=path.joinpath("story_menu.png")
        ):
            adb_con.click(50, 50)
        for _ in range(4):
            skip_story()
        logger.success("OP 动画")
        adb_con.multi_click(60, 70, 10)
        load_point += 1

    if not checkpoint(7, load_point, alias="教学抽卡"):
        # logger.success("1. 开局抽卡")
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
        load_point += 1

    if not checkpoint(8, load_point, alias="开始教学作战"):
        # logger.success("2. 开始作战")
        adb_con.multi_click(88, 35, 4)
        adb_con.multi_click(75, 75, 3)
        adb_con.multi_click(40, 65, 10)
        logger.success("开始编队")
        adb_con.multi_click(95, 25, 5)
        adb_con.sleep(3)
        adb_con.multi_click(25, 50, 10)
        load_point += 1

    if not checkpoint(9, load_point, alias="进入第一步作战"):
        # logger.success("道中作战")
        adb_con.multi_click(90, 80, 2)
        for _ in range(2):
            adb_con.multi_click(90, 90, 2)
            adb_con.sleep(5)
        adb_con.multi_click(50, 63, 5)
        adb_con.sleep(10)
        logger.success("开启auto")
        adb_con.click(95, 95)
        while not adb_con.compare_img(
                *mapping["battle_finish.png"], img=path.joinpath("battle_finish.png")
        ):
            adb_con.sleep(1)

        logger.success("完成作战")
        adb_con.click(90, 90)
        adb_con.sleep(5)
        adb_con.click(50, 90)
        adb_con.sleep(5)
        adb_con.multi_click(90, 90, 5)
        load_point += 1

    if not checkpoint(10, load_point, alias="开始BOSS作战"):
        # logger.success("开始BOSS作战")
        adb_con.multi_click(60, 55, 5)
        while not adb_con.compare_img(
                *mapping["battle_finish.png"], img=path.joinpath("battle_finish.png")
        ):
            adb_con.sleep(1)
        logger.success("完成作战")
        adb_con.multi_click(90, 90, 5)
        adb_con.multi_click(85, 90, 10)
        load_point += 1

    if not checkpoint(11, load_point, alias="返回大厅"):
        # logger.success("9. 返回大厅")
        adb_con.multi_click(40, 90, 20)
        while not adb_con.compare_img(
                *mapping["main_momotalk.png"], img=path.joinpath("main_momotalk.png")
        ):
            adb_con.multi_click(40, 90, 5)
        load_point += 1

    if not checkpoint(12, load_point, alias="MomoTalk & 收取邮件"):
        # logger.success("10. MomoTalk & 收取邮件")
        while not adb_con.compare_img(
                *mapping["no_mail.png"], img=path.joinpath("no_mail.png"), confidence=0.5
        ):
            for _ in range(2):
                adb_con.click(12.18, 18.66)
                adb_con.click(11.56, 41.11)
                adb_con.click(88, 5)
                adb_con.click(88, 5)
                adb_con.click(82.5, 94.44)
        adb_con.sleep(1)
        adb_con.back()
        load_point += 1

    if not checkpoint(13, load_point, alias="绑定账号"):
        adb_con.multi_click(50, 50, 10)
        adb_con.click(95, 4)  # 菜单
        adb_con.multi_click(50, 50, 5)
        adb_con.click(60, 40)  # 账号
        adb_con.click(99, 4)   # 弹出网页关闭
        adb_con.multi_click(50, 50, 10)
        while not adb_con.compare_img(
                *mapping["main_momotalk.png"], img=path.joinpath("main_momotalk.png")
        ):
            adb_con.back() # 返回主界面
        load_point += 1

    if not checkpoint(14, load_point, alias="开始自定义抽卡"):
        # logger.success("开始抽卡")
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
            logger.info("翻页，常驻池")
            adb_con.click(3, 55)  # 常驻池
        # logger.debug("切换卡池")
        # adb_con.multi_click(3, 55, 2)
        logger.info("开始抽卡")
        adb_con.click(76, 72)
        adb_con.click(60, 70)
        adb_con.sleep(5)
        for i in range(3):  # 40抽
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
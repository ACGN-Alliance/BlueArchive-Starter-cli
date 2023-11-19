from pathlib import Path
from typing import Any

from loguru import logger

from utils import adb
from utils.box_scan import Scan
from utils.settings import Settings


def checkpoint_new(
    current_position: int,
    load_point: int,
    settings: Settings,
    is_start_from_zero: bool = True,
    alias: str = "",
):
    """
    检查点

    :param current_position: 当前位置
    :param load_point: 检查点位置
    :param is_start_from_zero: 是否从0开始
    :param settings: 设置
    :param alias: 检查点别名
    :return: bool, : 是否进入流程
    """
    if_run = True

    if current_position == 13 and not settings.guest:
        if_run = False
    elif current_position == 14 and not settings.main_line:
        if_run = False
    elif current_position in [16, 17] and not settings.box_scan:
        if_run = False

    if is_start_from_zero:
        pass
    else:
        if load_point > current_position:
            if_run = False

    if if_run:
        logger.info(f"到达检查点 {current_position}.{alias}")
    else:
        logger.info(f"跳过检查点 {current_position}.{alias}")

    return if_run


def script(
    adb_con: adb.ADB,
    path: Path,
    mapping: Any,
    settings: Settings,
    *args,
    load_point: int = 0,
):
    """
    执行脚本

    adb_con: adb连接对象
    path: 图片加载地址
    mapping: 图片映射表
    settings: 设置
    load_point: 起始位置
    """

    def skip_story():
        adb_con.click(95, 5)
        adb_con.click(95, 15)
        adb_con.click(63, 71)

    if load_point == 0:
        is_start_from_zero = True
    else:
        is_start_from_zero = False
    if load_point >= 18:
        logger.error("加载点超出范围, 自动结束脚本")
        return True

    adb_con.clear_compare_fail_count()

    name = settings.username
    if not name:
        name = input("未设置昵称, 请输入你想要的昵称(禁止非法字符): ")

    if checkpoint_new(
        0,
        load_point,
        alias="重置账号",
        is_start_from_zero=is_start_from_zero,
        settings=settings,
    ):
        while not adb_con.compare_img(
            *mapping["main_interface.png"], img=path.joinpath("main_interface.png")
        ):
            adb_con.back()

        logger.info("已回到主菜单，开始销号")
        adb_con.click(95, 4)  # 菜单
        adb_con.sleep(2)
        adb_con.click(60, 40)  # 账号
        if settings.guest:
            time_count = 0
            while not adb_con.compare_img(
                *mapping["lk_tip.png"], img=path.joinpath("lk_tip.png")
            ):
                time_count += 1

                if time_count > 3:
                    break

            adb_con.click(99, 4)  # 弹出网页关闭
            adb_con.sleep(1)
            adb_con.click(70, 60)  # 重置账号
        else:
            adb_con.click(70, 50)
        adb_con.click(55, 45)
        adb_con.input_text("BlueArchive")
        adb_con.click(58, 67)
        adb_con.sleep(2)
        adb_con.multi_click(58, 67, 3)

    if checkpoint_new(
        1,
        load_point,
        alias="创建新账号",
        is_start_from_zero=is_start_from_zero,
        settings=settings,
    ):
        # logger.success("1. 创建账号")
        while not adb_con.compare_img(
            *mapping["start_menu_icon.png"], img=path.joinpath("start_menu_icon.png")
        ):
            pass
        adb_con.sleep(2)
        logger.info("已进入开始界面")
        adb_con.multi_click(99, 4, 3)  # 弹出网页关闭
        adb_con.multi_click(50, 70, 4)
        while not adb_con.compare_img(
            *mapping["start_name.png"], img=path.joinpath("start_name.png")
        ):
            adb_con.click(50, 70)
        logger.info("输入名字")
        adb_con.sleep(1)
        adb_con.click(50, 50)
        adb_con.input_text(name)
        adb_con.multi_click(50, 70, 5)
        adb_con.sleep(20)
        adb_con.click(50, 50)
        adb_con.sleep(22)
        # adb_con.multi_click(50, 70, 40)

    if checkpoint_new(
        2,
        load_point,
        alias="初始剧情",
        is_start_from_zero=is_start_from_zero,
        settings=settings,
    ):
        # logger.success("2. 初始剧情")
        while not adb_con.compare_img(
            *mapping["story_menu.png"], img=path.joinpath("story_menu.png")
        ):
            adb_con.click(50, 70)
            adb_con.sleep(3)
        skip_story()

    if checkpoint_new(
        3,
        load_point,
        alias="战斗-1",
        is_start_from_zero=is_start_from_zero,
        settings=settings,
    ):
        # logger.success("3. 战斗1")
        adb_con.sleep(5)
        adb_con.multi_click(50, 70, 10)

        while not adb_con.compare_img(
            *mapping["student_1.png"], img=path.joinpath("student_1.png")
        ):
            adb_con.multi_click(50, 70, 3)

        adb_con.click(80, 88)
        adb_con.click(80, 35)

        while not adb_con.compare_img(
            *mapping["battle_finish.png"], img=path.joinpath("battle_finish.png")
        ):
            logger.info("尝试使用技能~")
            adb_con.multi_click(50, 50, 2)
            adb_con.click(70, 88)
            adb_con.click(43, 52)
            adb_con.sleep(1)
            adb_con.click(80, 88)
            adb_con.click(80, 35)

        logger.success("战斗结束")
        adb_con.click(90, 90)

    if checkpoint_new(
        4,
        load_point,
        alias="剧情",
        is_start_from_zero=is_start_from_zero,
        settings=settings,
    ):
        # logger.success("4. 两段剧情")
        adb_con.sleep(1)
        for _ in range(2):
            while not adb_con.compare_img(
                *mapping["story_menu.png"], img=path.joinpath("story_menu.png")
            ):
                adb_con.click(50, 50)
            skip_story()

    if checkpoint_new(
        5,
        load_point,
        alias="战斗-2",
        is_start_from_zero=is_start_from_zero,
        settings=settings,
    ):
        # logger.success("5. 战斗2")
        adb_con.sleep(10)
        adb_con.multi_click(50, 50, 7)
        for i in range(4):
            while not adb_con.compare_img(
                *mapping["story_menu.png"], img=path.joinpath("story_menu.png")
            ):
                adb_con.click(50, 50)
            logger.info(f"第 {i + 1} 段剧情")
            skip_story()
        # logger.success("使用技能")
        adb_con.multi_click(50, 50, 5)
        while not adb_con.compare_img(
            *mapping["student_2.png"], img=path.joinpath("student_2.png")
        ):
            adb_con.click(50, 50)

        adb_con.click(70, 88)
        adb_con.click(80, 20)
        while not adb_con.compare_img(
            *mapping["battle_finish.png"], img=path.joinpath("battle_finish.png")
        ):
            adb_con.click(70, 88)
            adb_con.click(80, 20)

        adb_con.click(90, 90)

    if checkpoint_new(
        6,
        load_point,
        alias="剧情",
        is_start_from_zero=is_start_from_zero,
        settings=settings,
    ):
        # logger.success("5. 两段剧情")
        while not adb_con.compare_img(
            *mapping["story_menu.png"], img=path.joinpath("story_menu.png")
        ):
            adb_con.click(50, 50)
        for _ in range(4):
            skip_story()
        adb_con.sleep(2)
        adb_con.click(60, 70)

    if checkpoint_new(
        7,
        load_point,
        alias="教学抽卡",
        is_start_from_zero=is_start_from_zero,
        settings=settings,
    ):
        # logger.success("1. 开局抽卡")
        while not adb_con.compare_img(
            *mapping["main_recurit.png"], img=path.joinpath("main_recurit.png")
        ):
            adb_con.multi_click(50, 5, 3)
            # adb_con.back()
        adb_con.click(70, 90)
        adb_con.sleep(4)  # todo 优化
        adb_con.click(76, 72)
        adb_con.sleep(1)
        adb_con.click(60, 70)
        adb_con.sleep(3)
        adb_con.multi_click(50, 75, 5)
        while not adb_con.compare_img(
            *mapping["recurit_confirm.png"], img=path.joinpath("recurit_confirm.png")
        ):
            adb_con.multi_click(92, 7, 3)
        if settings.if_screenshot:
            adb_con.screenshot("1.png")
        adb_con.click(50, 90)

    if checkpoint_new(
        8,
        load_point,
        alias="开始教学作战",
        is_start_from_zero=is_start_from_zero,
        settings=settings,
    ):
        # logger.success("2. 开始作战")
        while not adb_con.compare_img(
            *mapping["level1.png"], img=path.joinpath("level1.png"), confidence=0.93
        ):
            adb_con.click(50, 90)
        adb_con.multi_click(88, 35, 3)
        adb_con.multi_click(75, 75, 3)
        adb_con.multi_click(40, 65, 5)
        logger.info("开始编队")
        adb_con.multi_click(95, 25, 5)
        adb_con.sleep(1)
        adb_con.multi_click(25, 50, 8)

    if checkpoint_new(
        9,
        load_point,
        alias="进入第一步作战",
        is_start_from_zero=is_start_from_zero,
        settings=settings,
    ):
        # logger.success("道中作战")
        adb_con.multi_click(90, 85, 3)

        while not adb_con.compare_img(
            *mapping["begin_mission.png"], img=path.joinpath("begin_mission.png")
        ):
            adb_con.click(90, 85)
        adb_con.click(92, 90)
        adb_con.sleep(3)
        adb_con.multi_click(50, 63, 5)
        while not adb_con.compare_img(
            *mapping["auto.png"], img=path.joinpath("auto.png"), confidence=0.95
        ):
            adb_con.sleep(1)
        logger.info("开启auto")  # todo 需要优化
        adb_con.click(95, 93)
        while not adb_con.compare_img(
            *mapping["battle_finish.png"], img=path.joinpath("battle_finish.png")
        ):
            # adb_con.click(50, 63)
            adb_con.sleep(0.5)
        logger.success("完成作战")
        adb_con.click(90, 90)
        adb_con.sleep(5)
        adb_con.click(50, 90)
        adb_con.sleep(3)

        while not adb_con.compare_img(
            *mapping["end_phase.png"], img=path.joinpath("end_phase.png")
        ):
            adb_con.multi_click(50, 90, 2)

        adb_con.click(94, 94)

    if checkpoint_new(
        10,
        load_point,
        alias="开始BOSS作战",
        is_start_from_zero=is_start_from_zero,
        settings=settings,
    ):
        # logger.success("开始BOSS作战")
        adb_con.sleep(3)
        adb_con.multi_click(60, 55, 5)
        while not adb_con.compare_img(
            *mapping["battle_finish.png"], img=path.joinpath("battle_finish.png")
        ):
            adb_con.click(65, 55)
            adb_con.sleep(3)
        logger.success("完成作战")
        adb_con.click(90, 90)
        adb_con.sleep(4)
        adb_con.click(85, 90)

    if checkpoint_new(
        11,
        load_point,
        alias="返回大厅",
        is_start_from_zero=is_start_from_zero,
        settings=settings,
    ):
        # logger.success("9. 返回大厅")
        while not adb_con.compare_img(
            *mapping["go_to_lobby.png"],
            img=path.joinpath("go_to_lobby.png"),
        ):
            adb_con.click(90, 90)
            adb_con.click(85, 90)

        adb_con.sleep(2)

        adb_con.multi_click(40, 90, 18)
        while not adb_con.compare_img(
            *mapping["momotalk.png"],
            img=path.joinpath("momotalk.png"),
        ):
            adb_con.back()

    if checkpoint_new(
        12,
        load_point,
        alias="MomoTalk & 收取邮件",
        is_start_from_zero=is_start_from_zero,
        settings=settings,
    ):
        # logger.success("10. MomoTalk & 收取邮件")
        adb_con.click(12.18, 18.66)
        adb_con.sleep(2)
        adb_con.multi_click(11.56, 41.11, 12)

        while not adb_con.compare_img(
            *mapping["main_interface.png"], img=path.joinpath("main_interface.png")
        ):
            adb_con.back()
        adb_con.sleep(3)
        adb_con.click(89, 5)
        adb_con.sleep(2)
        adb_con.multi_click(87, 92, 5)
        adb_con.sleep(2)
        adb_con.back()

    if checkpoint_new(
        13,
        load_point,
        alias="绑定账号",
        is_start_from_zero=is_start_from_zero,
        settings=settings,
    ):
        while not adb_con.compare_img(
            *mapping["main_interface_dark.png"],
            img=path.joinpath("main_interface_dark.png"),
        ):
            adb_con.back()  # 返回主界面

        adb_con.sleep(2)
        adb_con.multi_click(50, 50, 2)
        adb_con.click(95, 4)  # 菜单
        # adb_con.multi_click(50, 50, 5)
        adb_con.sleep(2)
        adb_con.click(60, 40)  # 账号
        adb_con.sleep(3)
        adb_con.click(99, 4)  # 弹出网页关闭
        adb_con.multi_click(50, 50, 7)
        adb_con.back()
        while not adb_con.compare_img(
            *mapping["main_interface.png"], img=path.joinpath("main_interface.png")
        ):
            adb_con.back()

    if checkpoint_new(
        14,
        load_point,
        alias="开始获取主线青辉石",
        is_start_from_zero=is_start_from_zero,
        settings=settings,
    ):
        while not adb_con.compare_img(
            *mapping["main_interface.png"], img=path.joinpath("main_interface.png")
        ):
            adb_con.back()
        # ==============40抽起始==============
        adb_con.click(92, 82)
        adb_con.sleep(2)
        adb_con.click(95, 5)
        adb_con.multi_click(5, 50, 10)  # 跳过演示
        # adb_con.click(48, 70)

        adb_con.click(85, 35)  # 进入剧情
        adb_con.multi_click(5, 50, 11)  # 跳过演示
        adb_con.click(30, 50)  # 进入主线
        adb_con.sleep(2)
        adb_con.click(90, 45)  # 第一章
        adb_con.sleep(2)

        def chapter(
            ctype: str, *args, is_first_bat: bool = False, story_after_bat: bool = True
        ):
            adb_con.sleep(1.5)
            adb_con.click(85, 48)
            adb_con.click(50, 70)
            while not adb_con.compare_img(
                *mapping["story_menu.png"], img=path.joinpath("story_menu.png")
            ):
                adb_con.click(50, 50)
            for _ in range(2):
                skip_story()

            if ctype == "battle":
                adb_con.multi_click(95, 95, 3)
                if is_first_bat:
                    adb_con.sleep(8)
                    adb_con.click(95, 95)

                while not adb_con.compare_img(
                    *mapping["battle_finish.png"],
                    img=path.joinpath("battle_finish.png"),
                ):
                    adb_con.sleep(1)
                adb_con.click(90, 95)

                if story_after_bat:
                    while not adb_con.compare_img(
                        *mapping["story_menu.png"], img=path.joinpath("story_menu.png")
                    ):
                        adb_con.sleep(1)
                    for _ in range(2):
                        skip_story()
                else:
                    logger.info("此处确保稳定性停顿时间较长, 请耐心等待")
                    adb_con.sleep(24)

            adb_con.sleep(4)
            adb_con.multi_click(50, 90, 2)

        chapter("normal")  # 第一话
        chapter("battle", is_first_bat=True)  # 第二话
        chapter("battle")  # 第三话
        chapter("normal")  # 第四话
        chapter("normal")  # 第五话
        chapter("battle", story_after_bat=False)  # 第六话
        chapter("normal")  # 第七话
        chapter("normal")  # 第八话

        while not adb_con.compare_img(
            *mapping["main_interface.png"], img=path.joinpath("main_interface.png")
        ):
            adb_con.back()

        adb_con.click(6, 32)  # 进入任务
        while not adb_con.compare_img(
            *mapping["story_menu.png"], img=path.joinpath("story_menu.png")
        ):
            adb_con.click(50, 50)
        skip_story()

        adb_con.sleep(5)
        adb_con.click(90, 95)
        adb_con.multi_click(50, 90, 5)
        adb_con.sleep(3)  # 等待可能得弹框
        while not adb_con.compare_img(
            *mapping["main_interface.png"], img=path.joinpath("main_interface.png")
        ):
            adb_con.back()
            adb_con.sleep(3)  # 等待可能得弹框

    if checkpoint_new(
        15,
        load_point,
        alias="开始抽卡",
        is_start_from_zero=is_start_from_zero,
        settings=settings,
    ):
        while not adb_con.compare_img(
            *mapping["main_interface.png"], img=path.joinpath("main_interface.png")
        ):
            adb_con.back()

        adb_con.click(70, 90)
        adb_con.sleep(6)
        for _ in range(settings.pool):
            adb_con.click(3, 55)
            adb_con.sleep(2)
        logger.info("开始抽卡")
        adb_con.click(76, 72)
        adb_con.click(60, 70)
        adb_con.sleep(2)

        recuit_times = settings.recuit_num + 2 + (1 if settings.main_line else 0)
        for i in range(recuit_times):
            adb_con.sleep(2)
            adb_con.multi_click(50, 75, 3)
            while not adb_con.compare_img(
                *mapping["recurit_confirm.png"],
                img=path.joinpath("recurit_confirm.png"),
            ):
                adb_con.sleep(1)
                adb_con.multi_click(92, 7, 2)
            adb_con.sleep(2)

            if settings.if_screenshot:
                adb_con.screenshot(f"{i + 2}.png")

            adb_con.click(50, 90)  # 确认
            adb_con.sleep(3)

            while adb_con.compare_img(
                *mapping["recruit_again.png"],
                img=path.joinpath("recruit_again.png"),
            ):
                adb_con.click(60, 87)  # 跳过动画&确认

            if i == recuit_times - 1:
                break
            adb_con.sleep(2)
            adb_con.click(60, 65)
        logger.info("回到主菜单")
        adb_con.back()
        adb_con.back()
        while not adb_con.compare_img(
            *mapping["main_interface.png"], img=path.joinpath("main_interface.png")
        ):
            adb_con.back()

    if checkpoint_new(
        16,
        load_point,
        alias="学生清单教学",
        is_start_from_zero=is_start_from_zero,
        settings=settings,
    ):
        if not settings.scan_list:
            logger.error("box检测队列为空")
            return True

        while not adb_con.compare_img(
            *mapping["main_interface.png"], img=path.joinpath("main_interface.png")
        ):
            adb_con.back()
        adb_con.click(25, 92)
        adb_con.sleep(2)
        adb_con.multi_click(50, 50, 3)
        adb_con.sleep(1)
        adb_con.click(10, 40)
        adb_con.multi_click(50, 50, 10)
        adb_con.sleep(2)
        adb_con.click(70, 20)
        adb_con.multi_click(50, 50, 7)
        adb_con.sleep(1)
        adb_con.click(5, 5)
        adb_con.sleep(2)

        adb_con.multi_click(50, 50, 3)
        adb_con.sleep(1)
        adb_con.click(10, 40)
        adb_con.multi_click(50, 50, 9)
        adb_con.sleep(1)
        adb_con.click(5, 5)
        adb_con.sleep(2)

        adb_con.multi_click(50, 50, 3)
        adb_con.sleep(1)
        adb_con.click(10, 40)
        adb_con.multi_click(50, 50, 4)
        adb_con.sleep(1)
        adb_con.click(58, 50)
        adb_con.multi_click(50, 50, 5)
        adb_con.sleep(1)
        adb_con.click(90, 50)
        adb_con.multi_click(95, 95, 10)
        adb_con.click(5, 5)

    if checkpoint_new(
        17,
        load_point,
        alias="box检查",
        is_start_from_zero=is_start_from_zero,
        settings=settings,
    ):
        adb_con.sleep(2)
        bscan = Scan(adb_con=adb_con, offline=True)

        if bscan.students_in(settings.scan_list):
            logger.success("学生已刷齐~")
            return True
        else:
            logger.error("学生未刷齐~重启执行脚本")
            return False

    logger.success("脚本执行完毕")
    return True

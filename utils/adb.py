import os
import subprocess
import sys
import time
import traceback
from pathlib import Path

from PIL import Image
from loguru import logger

from .image_compare import compare_images_binary_old
from .cmp_server import ImageComparatorServer
from .settings import Settings


class ScreenShotCompareError(BaseException):
    pass


class ADB:
    """
    使用ADB (Android Debug Bridge) 与 Android 设备进行接口交互的类。
    属性:
        device_name (str): 设备的名称。
        delay (int): 执行ADB命令后的延迟时间，单位为秒，默认为1秒。
        adb_path (str): adb.exe可执行文件的路径。
    """

    compare_fail_count: int = 1

    def __init__(
        self,
        adb_path: str = "",
        device_name: str = "",
        delay: int | float = 1,
        scan_mode: bool = False,
        physic_device_name: str = "",
        is_mumu: bool = False,
        settings: Settings = None,
    ):
        """
        初始化针对特定Android设备的ADB接口。
        参数:
            adb_path (str): adb 的路径
            device_name (str): 设备的名称。
            delay (int, optional): 执行ADB命令后的延迟时间，单位为秒。默认为1秒。
        """
        self.device_name = device_name
        self.setting = settings

        if settings.speed == "fast":
            self.delay = 0.8
        elif settings.speed == "normal":
            self.delay = 1
        elif settings.speed == "slow":
            self.delay = 1.8
        elif settings.speed == "very slow":
            self.delay = 3
        else:
            self.delay = delay

        self.delay += settings.extra_delay

        sys.path.append(os.path.abspath("platform-tools"))
        self.adb_path = adb_path or os.environ["BAS$PLATFORM_TOOLS"] + '//adb'

        if not physic_device_name:
            subprocess.run(
                [self.adb_path, "connect", device_name],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
        else:
            self.device_name = physic_device_name

        if not scan_mode:
            if is_mumu:
                self.screen_height, self.screen_width = self._get_screen_resolution()
            else:
                self.screen_width, self.screen_height = self._get_screen_resolution()

    def _run_command(self, cmd: list[str]) -> str:
        """执行一个ADB命令。"""
        try:
            result = subprocess.run(
                [self.adb_path, "-s", self.device_name] + cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            return result.stdout.decode("utf-8")
        finally:
            if self.setting.speed == "fast":
                extra_delay = -0.2
            elif self.setting.speed == "normal":
                extra_delay = 0
            elif self.setting.speed == "slow":
                extra_delay = 0.6
            elif self.setting.speed == "very slow":
                extra_delay = 2

            time.sleep(self.delay + extra_delay)

    def command(self, cmd: str) -> str:
        args = cmd.removeprefix("adb ").split()
        return self._run_command(args)

    def _get_screen_resolution(self) -> tuple[int, int]:
        """获取设备的屏幕分辨率."""
        result = self._run_command(["shell", "wm", "size"])
        output = result.strip().split()[-1]
        width, height = output.split("x")
        return int(width), int(height)

    def _normalized_to_real_coordinates(self, x: float, y: float) -> tuple[int, int]:
        """将0-100的浮点数坐标转换为实际的屏幕坐标."""
        real_x = int(self.screen_width * x / 100)
        real_y = int(self.screen_height * y / 100)
        return real_x, real_y

    def _real_to_normalized_coordinates(self, x: int, y: int) -> tuple[float, float]:
        """将实际的屏幕坐标转换为0-100的浮点数坐标."""
        normalized_x = (x / self.screen_width) * 100
        normalized_y = (y / self.screen_height) * 100
        return normalized_x, normalized_y

    def click(self, x: float, y: float) -> str:
        """
        在给定的坐标上模拟设备屏幕上的点击操作。
        参数:
            x (float): 点击的x坐标(0-100表示)。
            y (float): 点击的y坐标(0-100表示)。
        """
        real_x, real_y = self._normalized_to_real_coordinates(x, y)
        return self._run_command(["shell", "input", "tap", str(real_x), str(real_y)])

    def multi_click(self, x: float, y: float, count: int = 2) -> None:
        """
        在给定的坐标上模拟设备屏幕上的多次点击操作。
        参数:
            x (float): 点击的x坐标(0-100表示)。
            y (float): 点击的y坐标(0-100表示)。
            count (int, optional): 点击的次数。默认为2次。
        """
        if self.setting.speed == "slow":
            count += 1
        elif self.setting.speed == "very slow":
            count += 2

        for _ in range(count):
            self.click(x, y)

    def input_text(self, text: str) -> str:
        """在设备上输入文字."""
        return self._run_command(["shell", "input", "text", text])

    def sleep(self, time_: int | float = 0) -> None:
        """暂停指定的持续时间。"""
        if not time_:
            time_ = self.delay

        if self.setting.speed == "slow":
            time.sleep(time_ * 1.15)
        elif self.setting.speed == "very slow":
            time.sleep(time_ * 1.3)
        elif self.setting.speed == "fast":
            time.sleep(time_ * 0.95)
        elif self.setting.speed == "normal":
            time.sleep(time_)

        return None

    def back(self) -> str:
        """模拟设备上的返回按钮操作。"""
        return self._run_command(["shell", "input", "keyevent", "KEYCODE_BACK"])

    def screenshot(self, save_path: str) -> None:
        """在设备上截屏并将其保存到主机机器的给定路径。"""
        tmp_path = "/sdcard/screenshot.png"
        self._run_command(["shell", "screencap", tmp_path])
        self._run_command(["pull", tmp_path, save_path])
        self._run_command(["shell", "rm", tmp_path])

    def get_device_list(self) -> list:
        """
        获取设备列表
        :return: tuple(序列号, 状态, 连接)
        """
        devices = []
        out = self._run_command(["devices", "-l"])
        for line in out.splitlines():
            # line = line.encode('utf-8')
            if line.find("product") != -1:
                devices.append(line)

        return devices

    def kill_server(self) -> None:
        """停止adb服务"""
        self._run_command(["kill-server"])

    def vertical_swipe(self, x: float, y1: float, y2: float) -> str:
        """
        模拟设备屏幕上的垂直滑动操作。
        参数:
            x (float): 滑动的x坐标(0-100表示)。
            y1 (float): 滑动的起始y坐标(0-100表示)。
            y2 (float): 滑动的结束y坐标(0-100表示)。
        """
        real_x, real_y1 = self._normalized_to_real_coordinates(x, y1)
        _, real_y2 = self._normalized_to_real_coordinates(x, y2)
        return self._run_command(
            [
                "shell",
                "input",
                "swipe",
                str(real_x),
                str(real_y1),
                str(real_x),
                str(real_y2),
            ]
        )

    def _fail_handle(self) -> bool:
        self.compare_fail_count += 1
        if self.compare_fail_count >= self.setting.too_many_errors + 1:
            self.compare_fail_count = 0
            raise ScreenShotCompareError("图片对比失败次数过多, 已退出脚本")

        return False

    def screenshot_region(
        self,
        x1: float,
        y1: float,
        x2: float,
        y2: float,
        save_path: str = "",
    ) -> Image.Image:
        """
        截取并保存设备上的一个特定区域的屏幕截图。
        参数:
            x1, y1, x2, y2 (float): 要截取的屏幕区域的坐标(0-100表示)。
            save_path (str): 保存截图的路径。
        """
        full_screenshot_path = "temp_full_screenshot.png"
        self.screenshot(full_screenshot_path)

        # i = Path(".").iterdir()
        # logger.debug(list(i))

        with Image.open(full_screenshot_path) as img:
            real_x1, real_y1 = self._normalized_to_real_coordinates(x1, y1)
            real_x2, real_y2 = self._normalized_to_real_coordinates(x2, y2)
            region = img.crop((real_x1, real_y1, real_x2, real_y2))

        if save_path:
            region.save(save_path)

        # logger.debug("已保存")
        return region

    def compare_img(
        self,
        x1: float,
        y1: float,
        x2: float,
        y2: float,
        img: str | Path,
        thresh=-1,  # -1: 自动计算阈值
        confidence: float = 0.91,
        debug: bool = False,
    ) -> bool:
        """
        比较截图区域与指定图片的相似度。

        参数:
            x1, y1, x2, y2 (float): 要截取的屏幕区域的坐标(0-100表示)。
            img (Union[str, Path, BytesIO]): 比较的图片路径或字节流。
            confidence (float): 图像相似度的阈值。默认值为0.9。

        返回:
            bool: 如果两张图片的相似度超过给定的confidence，则返回True，否则返回False。
        """
        img_name = str(img).split("\\")[-1].split(".")[0]
        if self.setting.img_confidences.get("all"):
            confidence = self.setting.img_confidences["all"]
            
        if self.setting.img_confidences.get(img_name):
            confidence = self.setting.img_confidences[img_name]

        try:
            # 截图并从区域获取Image对象
            im: Image.Image = self.screenshot_region(x1, y1, x2, y2)
            im_s = Image.open(img)
            dst = im.copy()
            src = im_s.copy()

            # 确保两个图像的尺寸一致
            # if im.size[0] / im.size[1] != im_s.size[0] / im_s.size[1]:
            #     logger.warning(
            #         "图片尺寸不一致!如果此提示一直出现(>=25条)请向开发者反馈。"
            #     )

            im_s = im_s.resize(im.size)

            # 转换为RGB以确保图像格式一致
            im = im.convert("RGB")
            im_s = im_s.convert("RGB")

            # 计算两个图像的差异
            now_confidence, diff, thresh = compare_images_binary_old(
                im_s, im, thresh=thresh
            )
            instance = ImageComparatorServer.get_global_instance()
            instance.send_all(
                src,
                dst,
                diff,
                f"{now_confidence:.2f}",
                str(thresh),
                "True" if now_confidence > confidence else "False",
            )

            if debug:
                logger.debug(f'图片 "{img.name}" 与当前图像相似度为 {now_confidence:.2f}')
                return

            if now_confidence > confidence:
                info = f'图片 "{img.name}" 与当前图像相似度为 {now_confidence:.2f}(>={confidence}), 匹配>>>成功<<<'
                self.compare_fail_count = 0  # 重置失败次数
                logger.success(info)
            else:
                info = f'图片 "{img.name}" 与当前图像相似度为 {now_confidence:.2f}(<{confidence}), 匹配>>>失败<<<\n已累计: {self.compare_fail_count} 次'
                if self.setting.too_many_errors != 0:
                    self._fail_handle()
                logger.debug(info)

            return now_confidence > confidence
        except Exception as e:
            logger.error(f"图片对比失败 {type(e)} {e}")
            traceback.print_exception(type(e), e, e.__traceback__)
            return False

    def clear_compare_fail_count(self):
        self.compare_fail_count = 0

import base64
import os.path
import time
from pathlib import Path
from typing import List

from PIL import Image
from loguru import logger

from .adb import ADB

class Scan:
    access_token = ""

    def __init__(self, adb_con: ADB, offline: bool = True):
        self.adb = adb_con
        self.offline = offline

        if not os.path.exists("temp"):
            os.mkdir("temp")

    def pic2name(self, stu_name_img: Image.Image) -> List[str]:
        """
        从学生名称图片中获取学生名称
        """
        from utils.ocr import ocr
        student_list = []
        stu_name_img.save("temp/stu_name.png")
        for box, text, confidence in ocr("temp/stu_name.png"):
            if confidence >= 0.7 and "lv" not in text.lower():
                student_list.append(text)

        print("stu_list: " + str(student_list))
        return student_list

    def scan(self) -> List[str]:
        # 读取学生清单
        page = 0
        name_list = []
        is_finish = False
        times = 0

        self.adb.vertical_swipe(50, 50, 40)
        while True:
            page = page + 1
            self.adb.screenshot(f"temp/{page}.png")
            sc_img = Image.open(Path(f"temp/{page}.png"))

            pos_1 = self.adb._normalized_to_real_coordinates(4, 25)
            pos_2 = self.adb._normalized_to_real_coordinates(99, 97)
            pos = (pos_1[0], pos_1[1], pos_2[0], pos_2[1])
            stu_lst = self.pic2name(
                sc_img.crop(pos)
            )
            for stu in stu_lst:
                if "Owned" in stu:
                    is_finish = True
                    break
                else:
                    name_list.append(stu)

            if not is_finish:
                times = times + 1
                self.adb.vertical_swipe(50, 66.7, 15.1)
                if times >= 4:
                    break
            else:
                break

        return name_list

    def students_in(self, stu: list | str) -> bool:
        if isinstance(stu, str):
            stu = [stu]

        student_list = self.scan()
        logger.info(f"学生清单: {student_list}")
        if stu in student_list:
            return True
        else:
            return False

import os.path
from pathlib import Path
from typing import List, Tuple
import base64, requests, time
from loguru import logger

from adb import ADB
from PIL import Image, ImageChops

page_position = {
    "1": [0, 0, 1080, 1920],
    "2": [0, 1920, 1080, 1920]
}


class Scan:
    token = ""
    url = "https://aip.baidubce.com/rest/2.0/ocr/v1/general_basic?access_token=" + token

    def __init__(self, adb_con: ADB):
        self.adb = adb_con

    def get_page_students(
            self,
            page_screenshot: Image.Image
            ) -> List[Image.Image]:
        """
        从单页学生清单截图中获取学生名称
        """
        img_lst = []

        for k, v in page_position.items():
            img_lst.append(page_screenshot.crop(tuple(v)))

        return img_lst

    def set_token(self, token: str) -> None:
        self.token = token

    def have_token(self) -> bool:
        return self.token != ""

    def pic2name(self, stu_name_img: Image.Image) -> str:
        """
        从学生名称图片中获取学生名称
        """
        bs64 = base64.b64encode(stu_name_img.tobytes())
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        data = {
            'image': bs64,
            'language_type': 'ENG',
            'detect_direction': True,
            'paragraph': False,
            'probability': True
        }
        response = requests.post(self.url, headers=headers, data=data)
        if response.status_code != 200:
            logger.debug(response.status_code)
            logger.error("百度OCR接口调用失败")
            return ""
        else:
            result = response.json()

        logger.debug(str(getattr(result, "log_id")))
        words = getattr(result, "words_result")
        logger.info(str(words))

        time.sleep(0.5)

        return words[0]

    def scan(self) -> List[Image.Image]:
        # 请确保执行前已退回至主界面
        # 1.进入学生清单

        # 2.读取学生清单
        page = 0
        name_list = []
        while True:
            page = page + 1
            self.adb.screenshot(f"temp/{page}.png")
            sc_img = Image.open(Path(f"temp/{page}.png"))
            os.remove(Path(f"temp/{page}.png"))

            stu_lst = self.get_page_students(sc_img)
            for stu_img in stu_lst:
                name_list.append(stu_img)

            # for stu_img in stu_lst:
            #     name_list.append(self.pic2name(stu_img))

            # 判定是否需要滑动翻页
            if ...:
                # TODO 滑页
                self.adb.vertical_swipe(0.5, 0.8, 0.5)
            else:
                break

        return name_list
    
    def students_in(self, stu: list | str) -> bool:
        local_file_list: list = []  # 本地文件列表
        local_temp_list: list = []  # 临时列表，用于用户需要且本地的已存在学生
        not_local_list: list = []  # 本地没有的需要ocr的学生清单
        matched_group: list = []  # 已匹配到的学生列表
        is_all_local: bool = False

        if isinstance(stu, str):
            stu = [stu]

        if not os.path.exists("data/names"):
            os.mkdir("data/names")
        else:
            for file in os.listdir("data/names"):
                local_file_list.append(file.split(".")[0])
            if stu in local_file_list:
                local_temp_list = stu
                is_all_local = True
            else:
                not_local_list = stu.copy()
                for item in local_file_list:
                    if item in stu:
                        local_temp_list.append(item)
                        not_local_list.remove(item)

        name_imgs = self.scan()
        for local_name in local_temp_list:
            temp_img = Image.open(f"data/names/{local_name}.png")
            for name_img in name_imgs:
                if self.adb.compare_img(name_img, temp_img, confidence=0.8):
                    name_imgs.remove(name_img)
                    local_temp_list.remove(local_name)
                    matched_group.append(local_name)
                    break
        
        if len(local_temp_list) == 0 and is_all_local:
            return True
        elif len(local_temp_list) != 0:
            return False
        else:
            name_list = []
            for img in name_imgs:
                for local in local_temp_list:
                    temp_img = Image.open(f"data/names/{local}.png")
                    if self.adb.compare_img(img, temp_img, confidence=0.8):
                        name_imgs.remove(img)

            for img in name_imgs:
                res = self.pic2name(img)
                img.save(f"data/names/{res}.png")
                if res:
                    name_list.append(res)
                else:
                    continue
            
            if not_local_list in name_list:
                return True
            else:
                return False
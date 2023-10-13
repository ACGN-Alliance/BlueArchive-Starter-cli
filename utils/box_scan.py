import os.path
from pathlib import Path
from typing import List, Tuple
import base64, requests, time
from loguru import logger
from PIL import Image, ImageChops

from .adb import ADB

page_position = {
    "1": [3.125, 56, 18.75, 62],
    "2": [18.75, 56, 34.375, 62],
    "3": [34.375, 56, 50, 62],
    "4": [50, 56, 65.625, 62],
    "5": [65.625, 56, 81.25, 62],
    "6": [81.25, 56, 96.875, 62],
}


class Scan:
    access_token = ""

    def __init__(self, adb_con: ADB):
        self.adb = adb_con

        if not os.path.exists("temp"):
            os.mkdir("temp")

    def get_page_students(
            self,
            page_screenshot: Image.Image
            ) -> List[Image.Image]:
        """
        从单页学生清单截图中获取学生名称
        """
        img_lst = []

        for k, v in page_position.items():
            real_x1, real_y1 = self.adb._normalized_to_real_coordinates(v[0], v[1])
            real_x2, real_y2 = self.adb._normalized_to_real_coordinates(v[2], v[3])
            img_lst.append(page_screenshot.crop((real_x1, real_y1, real_x2, real_y2)))

        for i, img in enumerate(img_lst):
            img.save(f"temp/1-{i}.png")

        return img_lst

    def set_token(self, APIkey: str, secretKey: str) -> bool:
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        response = requests.post(
            f"https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id={APIkey}&client_secret={secretKey}&",
            headers=headers
        )

        if response.status_code != 200:
            print("无法获取百度云token, 错误信息: " + str(response.status_code))
            return False
        res_data = response.json()
        if res_data.get("error"):
            print("无法获取百度云token, 错误信息: " + res_data.get("error_description"))
            return False
        
        self.access_token = res_data.get("access_token")
        return True

    def have_token(self) -> bool:
        return self.access_token != ""
    
    def directly_set_token(self, token: str) -> None:
        self.access_token = token

    def pic2name(self, stu_name_img: Image.Image) -> List[str]:
        """
        从学生名称图片中获取学生名称
        """
        url = "https://aip.baidubce.com/rest/2.0/ocr/v1/general_basic?access_token=" + self.access_token
        stu_name_img.save("temp/stu_name.png")
        with open("temp/stu_name.png", "rb") as f:
            bs64 = base64.b64encode(f.read())
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        data = {
            'image': bs64,
            'language_type': 'ENG',
            'detect_direction': "false",
            'paragraph': "false",
            'probability': "true"
        }
        response = requests.post(url, headers=headers, data=data)
        if response.status_code != 200:
            logger.error("百度OCR接口调用失败, 错误信息: " + str(response.status_code) + " " + response.text)
            return ""
        else:
            result = response.json()
        if result.get("error_code"):
            logger.error("百度OCR接口调用失败, 错误信息: " + result.get("error_msg"))
            return ""
        
        student_list = []
        for res in result["words_result"]:
            if res["probability"]["average"] >= 0.98:
                student_list.append(res["words"])

        for stu in student_list:
            if "L.1" in stu or "Lv." in stu:
                student_list.remove(stu)

        time.sleep(0.5)

        return student_list

    def scan(self) -> List[Image.Image]:
        # 读取学生清单
        page = 0
        name_list = []
        is_finish = False

        self.adb.vertical_swipe(50, 50, 40)
        while True:
            page = page + 1
            self.adb.screenshot(f"temp/{page}.png")
            sc_img = Image.open(Path(f"temp/{page}.png"))
            # os.remove(Path(f"temp/{page}.png"))

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
                self.adb.vertical_swipe(50, 66.7, 11.1)
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
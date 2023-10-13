import os

from utils import ocr

if __name__ == '__main__':
    # 工作目录切换到项目根目录
    os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    print(ocr.ocr(r"data\16_9\recurit_confirm.png"))

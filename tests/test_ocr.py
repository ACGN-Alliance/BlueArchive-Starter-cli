import os
import sys
import time


def main():
    from utils import ocr
    print("file: ", r"tests/ocr_test.png")

    begin = time.time()
    for box, text, confidence in ocr.ocr(r"tests/img.png"):
        box = str(box)
        print(f"box = {box:<80}, text = {text:<20}, confidence = {confidence:.2f}")
    print("time: ", time.time() - begin)
    print("-" * 150)
    # for img in os.listdir(r"data\16_9"):
    #     if not img.endswith(".png"):
    #         continue
    #     img_path = os.path.join(r"data\16_9", img)
    #     print("file: ", img_path)
    #     data = ocr.ocr(img_path)
    #     if data is None:
    #         print("nothing found")
    #     else:
    #         begin = time.time()
    #         for box, text, confidence in data:
    #             box = str(box)
    #             print(
    #                 f"box = {box:<80}, text = {text:<20}, confidence = {confidence:.2f}"
    #             )
    #         print("time: ", time.time() - begin)
    #     print("-" * 150)


if __name__ == "__main__":
    # 工作目录切换到项目根目录
    os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    # for user
    sys.path.append(os.path.abspath("ocr_dependencies"))
    # for developer
    sys.path.append(os.path.abspath(".ocr_venv/Lib/site-packages"))
    main()

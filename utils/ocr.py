from functools import wraps

READY = False
INFO = """
    \033[91m安装OCR依赖后才能使用OCR功能,
    1.如果是在开发环境下,请先运行:create_ocr_venv.bat 或 create_ocr_venv.sh
    2.如果是正式环境,请下载 'ocr_dependencies_win_3.10.zip' 到当前目录,然后运行主菜单的8号选项执行安装\033[0m
    """
try:
    print("正在加载OCR引擎,请稍等...")
    from rapidocr_onnxruntime import RapidOCR

    engine = RapidOCR()
    READY = True
except Exception as e:
    print(e)


# decorator
def engine_ready(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not READY:
            raise RuntimeError("OCR engine is not ready!\n\n" + INFO)
        return func(*args, **kwargs)

    return wrapper


@engine_ready
def ocr(img: str | bytes) -> list[list[list[list[float]], str, float]]:
    """
    ref ==> https://rapidai.github.io/RapidOCRDocs/docs/install_usage/rapidocr/usage/
    :param img:图片路径或者图片二进制数据
    :return:返回3个元素的元组列表,每个元组包含3个元素:
        1.字符所在的最小矩形的位置(绝对坐标): [左上, 右上, 右下, 左下]
        2.识别出的文字
        3.置信度
        [
            [
                [[202.0, 12.0], [245.0, 12.0], [245.0, 34.0], [202.0, 34.0]],
                '120',
                0.74925297498703
            ],
            [
                [[129.0, 49.0], [304.0, 49.0], [304.0, 90.0], [129.0, 90.0]],
                'Recruit 1',
                0.896042674779892
            ],
            ...
        ]
    """
    r, _ = engine(img)
    return r

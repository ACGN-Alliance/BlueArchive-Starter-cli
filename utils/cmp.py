import enum
import os.path
import subprocess
import sys
import warnings
from typing import Any, Tuple

from PIL.Image import Image

sys.path.append(os.path.abspath("../.ocr_venv/Lib/site-packages"))
from utils.evaluate_images import evaluate_image, EvaluateMetric, evaluate_thresh, evaluate_thresh_runtime

try:
    import cv2
    import numpy
except ImportError:
    pass

__all__ = ['CompareMetrics', 'compare_images']

from pathlib import Path

from PIL import ImageChops, Image

IMAGE_MAGICK_LINK = 'https://imagemagick.org/archive/binaries/ImageMagick-7.1.1-20-portable-Q16-x86.zip'
BASE_DIR = './'

proxy = {
    "http": "127.0.0.1:7890",
    "https": "127.0.0.1:7890"
}


class CompareMetrics(enum.Enum):
    """
    AE（Absolute Error）：返回绝对误差，即不同像素之间的绝对差值之和。
    MAE（Mean Absolute Error）：返回绝对误差的平均值。
    MSE（Mean Squared Error）：返回均方误差，即误差的平方和的均值。
    PSNR（Peak Signal-to-Noise Ratio）：返回峰值信噪比，用于衡量图像质量。
    RMSE（Root Mean Squared Error）：返回均方根误差，即均方误差的平方根。
    NCC（Normalized Cross-Correlation）：返回标准化的互相关系数，用于比较两个图像之间的相似度。
    SSIM（Structural Similarity Index）：返回结构相似性指数，用于测量两个图像之间的结构相似性。
    """
    AE = 'ae'
    MAE = 'mae'
    MSE = 'mse'
    PSNR = 'psnr'
    RMSE = 'rmse'
    NCC = 'ncc'
    SSIM = 'ssim'


def download_compare_binary(use_proxy: bool = False):
    import requests
    import threading
    import time

    progress = 0
    file_length = 0
    stop = False

    def print_progress():
        nonlocal progress, file_length, stop
        while progress < file_length:
            print(f'Downloading binaries: {100 * progress / file_length :.2f}%')
            time.sleep(1)
            if stop:
                break

    head = requests.head(IMAGE_MAGICK_LINK)
    if head.status_code != 200:
        raise Exception('Cannot download compare.exe')
    file_length = int(head.headers['Content-Length'])

    progress_bar = threading.Thread(target=print_progress)
    progress_bar.start()

    os.makedirs(BASE_DIR + "binaries", exist_ok=True)
    with open(BASE_DIR + r'binaries/ImageMagick.zip', 'wb') as f:
        with requests.get(IMAGE_MAGICK_LINK, stream=True, proxies=proxy if use_proxy else {}) as r:
            for chunk in r.iter_content(chunk_size=8192):
                progress += len(chunk)
                f.write(chunk)

    stop = True
    progress_bar.join()
    print('Download complete')


def get_compare_binary():
    if os.path.exists(BASE_DIR + 'binaries/compare.exe'):
        return BASE_DIR + 'binaries/compare.exe'
    else:  # download
        if not os.path.exists(BASE_DIR + r'binaries/ImageMagick.zip'):
            download_compare_binary()

        import zipfile
        try:
            with zipfile.ZipFile(BASE_DIR + r"binaries/ImageMagick.zip", 'r') as zip_ref:
                # only extract compare.exe
                zip_ref.extract('compare.exe', BASE_DIR + 'binaries')
        except zipfile.BadZipFile:
            # delete zip file
            os.remove(BASE_DIR + r"binaries/ImageMagick.zip")
            return get_compare_binary()  # re-get

        # delete zip file
        os.remove(BASE_DIR + r"binaries/ImageMagick.zip")
        return BASE_DIR + 'binaries/compare.exe'


def compare_images(dst_path: str, src_path: str, metric: CompareMetrics = CompareMetrics.SSIM) -> float:
    warnings.warn(f"dont use this function, it has not been fully tested!:compare_images", DeprecationWarning)
    compare_binary = get_compare_binary()
    cmds = [
        compare_binary,
        '-metric',
        metric.value,
        dst_path,
        src_path,
        'null:'
    ]
    result = subprocess.run(cmds, capture_output=True, text=True, check=False).stderr
    return float(result)


def get_thresh(path: str | Path):
    if str(path).endswith(".png"):
        fn = os.path.basename(path)
        fn = fn[:-4]
        for _file in os.listdir(os.path.dirname(path)):
            if fn + '.thresh' in _file:
                file = _file
                break
        else:
            return -1, path

        s = file.split('.')
        if len(s) > 2:
            if s[-2].startswith("thresh"):
                try:
                    return int(s[-2][6:]), os.path.join(os.path.dirname(path), file)
                except ValueError:
                    pass


def compare_images_binary_cv2(
        srcIm: Image.Image,
        dstIm: str | Path,
        # evaluated: bool = False,
        thresh=127
) -> float:
    dstIm = cv2.imread(dstIm)
    srcIm = numpy.asarray(srcIm)
    srcIm = cv2.cvtColor(srcIm, cv2.COLOR_RGB2BGR)
    # resize
    dstIm = cv2.resize(dstIm, (srcIm.shape[1], srcIm.shape[0]))
    print(srcIm.shape, dstIm.shape, thresh)

    # 生成灰度图
    srcIm = cv2.cvtColor(srcIm, cv2.COLOR_BGR2GRAY)

    # 二值化
    srcIm = cv2.threshold(srcIm, thresh, 255, cv2.THRESH_BINARY)[1]

    dstIm = dstIm[:, :, 2]

    # 计算差异
    diff = cv2.absdiff(srcIm, dstIm)
    total_pixels = diff.shape[0] * diff.shape[1]
    diff_pixels = cv2.countNonZero(diff)
    return (total_pixels - diff_pixels) / total_pixels


def compare_images_binary_pil(
        srcIm: Image.Image,
        dstIm: str | Path,
        # evaluated: bool = False,
        thresh=127
) -> float:
    dstIm = Image.open(dstIm)
    # resize
    dstIm = dstIm.resize((srcIm.size[0], srcIm.size[1]))

    # 生成灰度图
    srcIm = srcIm.convert('L')

    # 二值化
    srcIm = srcIm.point(lambda x: 0 if x < thresh else 255, '1')

    # 计算差异
    diff = ImageChops.difference(srcIm, dstIm)
    total_pixels = diff.size[0] * diff.size[1]
    zero_pixels = 0
    for x in range(diff.size[0]):
        for y in range(diff.size[1]):
            if diff.getpixel((x, y)) == 0:
                zero_pixels += 1
    return (zero_pixels) / total_pixels


def compare_images_binary(
        dstIm: str | Path,
        srcIm: Image.Image,
) -> float:
    import loguru
    dstIm = str(dstIm)
    # find evaluated image
    t, p = get_thresh(dstIm)
    if t == -1:
        loguru.logger.warning(
            "WARNING: compare_images_binary: dstIm is not evaluated image, it will be evaluated automatically.")
        # evaluate image
        if "cv2" in sys.modules and "numpy" in sys.modules:
            t, c, p = evaluate_image(dstIm, metric=EvaluateMetric.CV2, target=0.15, error=0.05)
        else:
            t, c, p = evaluate_image(dstIm, metric=EvaluateMetric.PIL, target=0.15, error=0.05)
        loguru.logger.debug(
            f"compare_images_binary: evaluating image: {dstIm}, thresh: {t}, criterion: {c:.2f}, evaluated image: {p}")

    if "cv2" in sys.modules and "numpy" in sys.modules and False:
        loguru.logger.debug("compare_images_binary: using cv2")
        return compare_images_binary_cv2(srcIm, p, thresh=t)  # faster
    else:
        loguru.logger.debug("compare_images_binary: using PIL")
        return compare_images_binary_pil(srcIm, p, thresh=t)  # standard


def compare_images_binary_cv2_old(
        srcIm: Image,
        dstIm: Image,
        thresh=127
) -> tuple[Any, Any, int]:
    """
    :param srcIm: 本地图片
    :param dstIm: 游戏截图
    :return:
    """

    srcIm = cv2.cvtColor(numpy.asarray(srcIm), cv2.COLOR_RGB2BGR)
    dstIm = cv2.cvtColor(numpy.asarray(dstIm), cv2.COLOR_RGB2BGR)

    # 生成灰度图
    srcIm = cv2.cvtColor(srcIm, cv2.COLOR_BGR2GRAY)
    dstIm = cv2.cvtColor(dstIm, cv2.COLOR_BGR2GRAY)

    # 二值化
    srcIm1 = cv2.threshold(srcIm, thresh, 255, cv2.THRESH_BINARY)[1]

    total_pixels = srcIm1.shape[0] * srcIm1.shape[1]
    if cv2.countNonZero(srcIm1) / total_pixels < 0.1:  #
        thresh = evaluate_thresh_runtime(srcIm1, target=0.12, error=0.02, metric=EvaluateMetric.CV2)[0]
        srcIm = cv2.threshold(srcIm, thresh, 255, cv2.THRESH_BINARY)[1]
    else:
        srcIm = srcIm1

    dstIm = cv2.threshold(dstIm, thresh, 255, cv2.THRESH_BINARY)[1]

    # 计算差异
    diff = cv2.absdiff(srcIm, dstIm)
    diff_pixels = cv2.countNonZero(diff)
    return (total_pixels - diff_pixels) / total_pixels, diff,thresh


def compare_images_binary_pil_old(
        srcIm: Image,
        dstIm: Image,
        thresh=127
) -> tuple[float | Any, Image, int]:
    """
    :param srcIm: 本地图片
    :param dstIm: 游戏截图
    :return:
    """
    # 生成灰度图
    srcIm = srcIm.convert('L')
    dstIm = dstIm.convert('L')

    # 二值化
    srcIm1 = srcIm.point(lambda x: 0 if x < thresh else 255, '1')

    black_pixels = 0
    for x in range(srcIm1.size[0]):
        for y in range(srcIm1.size[1]):
            if srcIm1.getpixel((x, y)) != 0:
                black_pixels += 1
    if black_pixels / (srcIm1.size[0] * srcIm1.size[1]) < 0.1:  #
        thresh = evaluate_thresh_runtime(srcIm1, target=0.12, error=0.02, metric=EvaluateMetric.PIL)[0]
        srcIm = srcIm.point(lambda x: 0 if x < thresh else 255, '1')
    else:
        srcIm = srcIm1

    dstIm = dstIm.point(lambda x: 0 if x < thresh else 255, '1')

    # 计算差异
    diff = ImageChops.difference(srcIm, dstIm)
    total_pixels = diff.size[0] * diff.size[1]
    zero_pixels = 0
    for x in range(diff.size[0]):
        for y in range(diff.size[1]):
            if diff.getpixel((x, y)) == 0:
                zero_pixels += 1
    return (zero_pixels) / total_pixels, diff,thresh


def compare_images_binary_old(
        srcIm: Image,
        dstIm: Image,
        thresh=127
) -> tuple[Any, Any, int] | tuple[float | Any, Any, int]:
    """
    :param srcIm: 本地图片
    :param dstIm: 游戏截图
    :return:
    """
    if "cv2" in sys.modules and ("np" in sys.modules or "numpy" in sys.modules):
        return compare_images_binary_cv2_old(srcIm, dstIm, thresh)  # faster
    else:
        return compare_images_binary_pil_old(srcIm, dstIm, thresh)  # standard


if __name__ == '__main__':
    print(compare_images_binary(
        dstIm=r"../data/16_9/no_mail.png",
        srcIm=Image.open(r"../data/16_9/no_mail.png")
    ))

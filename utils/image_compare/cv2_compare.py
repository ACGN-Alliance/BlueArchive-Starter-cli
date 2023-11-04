import warnings
from pathlib import Path
from typing import Any

import cv2
import numpy
from PIL import Image
from cv2 import Mat
from numpy import ndarray, dtype, generic

from utils.evaluate_images import EvaluateMetric, evaluate_thresh_runtime


def compare_images_binary_cv2_old(
        srcIm: Mat | ndarray[Any, dtype[generic]] | ndarray,
        dstIm: Mat | ndarray[Any, dtype[generic]] | ndarray,
        thresh=-1
) -> tuple[Any, Any, int]:
    """
    :param srcIm: 本地图片
    :param dstIm: 游戏截图
    :param thresh: -1 to auto evaluate
    :return:
    """
    warnings.warn(f"compare_images_binary_cv2_old is deprecated", DeprecationWarning)
    srcIm = cv2.cvtColor(srcIm, cv2.COLOR_RGB2BGR)
    dstIm = cv2.cvtColor(dstIm, cv2.COLOR_RGB2BGR)

    # 生成灰度图
    srcIm = cv2.cvtColor(srcIm, cv2.COLOR_BGR2GRAY)
    dstIm = cv2.cvtColor(dstIm, cv2.COLOR_BGR2GRAY)

    # 二值化
    srcIm1 = cv2.threshold(srcIm, thresh, 255, cv2.THRESH_BINARY)[1]

    total_pixels = srcIm1.shape[0] * srcIm1.shape[1]
    if thresh == -1:
        criterion = cv2.countNonZero(srcIm1) / total_pixels
        if criterion < 0.1 or criterion > 0.9:  #
            thresh = evaluate_thresh_runtime(srcIm, target=0.5, error=0.4, metric=EvaluateMetric.CV2)[0]
            srcIm = cv2.threshold(srcIm, thresh, 255, cv2.THRESH_BINARY)[1]
        else:
            srcIm = srcIm1
    else:
        srcIm = srcIm1

    dstIm = cv2.threshold(dstIm, thresh, 255, cv2.THRESH_BINARY)[1]

    # 计算差异
    diff = cv2.absdiff(srcIm, dstIm)
    diff_pixels = cv2.countNonZero(diff)
    return (total_pixels - diff_pixels) / total_pixels, diff, thresh


def compare_images_binary_cv2(
        srcIm: Image.Image,
        dstIm: str | Path,
        # evaluated: bool = False,
        thresh=127
) -> float:
    warnings.warn("compare_images_binary_cv2 is deprecated", DeprecationWarning)
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

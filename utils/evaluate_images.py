import enum
import os

try:
    import cv2
    import numpy
except ImportError:
    pass

from PIL import Image


class EvaluateMetric(enum.Enum):
    CV2 = 'cv2'
    PIL = 'pil'


def calc_criterion_cv2(img, thresh=127):
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    img = cv2.threshold(img, thresh, 255, cv2.THRESH_BINARY)[1]

    total_pixels = img.shape[0] * img.shape[1]
    black_pixels = cv2.countNonZero(img)
    return (total_pixels - black_pixels) / total_pixels, img


def calc_criterion_pil(img: Image.Image, thresh=127):
    img = img.convert('L')
    img = img.point(lambda x: 0 if x < thresh else 255, '1')

    total_pixels = img.size[0] * img.size[1]
    zero_pixels = 0
    for x in range(img.size[0]):
        for y in range(img.size[1]):
            if img.getpixel((x, y)) == 0:
                zero_pixels += 1
    return (zero_pixels) / total_pixels, img


def evaluate_thresh(img_path, target=0.175, error=0.025, metric=EvaluateMetric.CV2) \
        -> tuple[int, float, Image] | tuple[int, int, None]:
    """
    get the binary threshold of image,use binary search to find the best threshold
    :param img_path: file path of image
    :param target: target percentage of criterion in total pixel
    :param error: acceptable error
    :param metric: use cv2 or PIL to calculate criterion
    :return: tuple of binary threshold, percentage of criterion in total pixel, evaluated image
    """
    img = Image.open(img_path)
    img.convert('RGB')
    if metric == EvaluateMetric.CV2:
        img = cv2.cvtColor(numpy.asarray(img), cv2.COLOR_RGB2BGR)
    elif metric == EvaluateMetric.PIL:
        ...
    else:
        raise ValueError(f"Unsupported metric: {metric}")

    L = 0
    R = 255
    history = {}
    while L < R:
        thresh = (L + R) // 2

        if metric == EvaluateMetric.CV2:
            criterion, _img = calc_criterion_cv2(img, thresh)
        elif metric == EvaluateMetric.PIL:
            criterion, _img = calc_criterion_pil(img, thresh)
        else:
            raise ValueError(f"Unsupported metric: {metric}")

        if thresh in history:
            e = thresh, history[thresh]
            for _thresh, value in history.items():
                if abs(value[0] - criterion) < abs(e[1][0] - criterion):
                    e = _thresh, value
            return e[0], e[1][0], e[1][1]
        if criterion < target - error:
            L = thresh
        elif criterion > target + error:
            R = thresh + 1
        else:
            return thresh, criterion, _img
        history[thresh] = criterion, _img
    return -1, -1, None

def evaluate_thresh_runtime(img, target=0.175, error=0.025, metric=EvaluateMetric.CV2) \
        -> tuple[int, float, Image] | tuple[int, int, None]:

    L = 0
    R = 255
    history = {}
    while L < R:
        thresh = (L + R) // 2

        if metric == EvaluateMetric.CV2:
            criterion, _img = calc_criterion_cv2(img, thresh)
        elif metric == EvaluateMetric.PIL:
            criterion, _img = calc_criterion_pil(img, thresh)
        else:
            raise ValueError(f"Unsupported metric: {metric}")

        if thresh in history:
            e = thresh, history[thresh]
            for _thresh, value in history.items():
                if abs(value[0] - criterion) < abs(e[1][0] - criterion):
                    e = _thresh, value
            return e[0], e[1][0], e[1][1]
        if criterion < target - error:
            L = thresh
        elif criterion > target + error:
            R = thresh + 1
        else:
            return thresh, criterion, _img
        history[thresh] = criterion, _img
    return -1, -1, None


def evaluate_image(path, target=0.175, error=0.025, metric=EvaluateMetric.CV2) -> tuple[int, float, str]:
    """
    evaluate single image from disk and create evaluated image
    :param path:
    :param target:
    :param error:
    :param metric:
    :return: binary threshold, percentage of criterion in total pixel, evaluated image path
    """
    thresh, criterion, _img = evaluate_thresh(path, target, error, metric)
    path = path.replace(".png", f".thresh{thresh}.png")
    if metric == EvaluateMetric.CV2:
        cv2.imwrite(path, _img)
    elif metric == EvaluateMetric.PIL:
        _img.save(path)
    else:
        raise ValueError(f"Unsupported metric: {metric}")
    return thresh, criterion, path


def show_img(img, title=""):
    cv2.imshow(title, img)
    cv2.waitKey()
    cv2.destroyAllWindows()


def clean_evaluated_images(top_path="../data"):
    """
    clean all evaluated images in top_path recursively,end with ".thresh*.png"
    :param top_path: top level path to scan
    :return: None
    """
    for root, dirs, files in os.walk(top_path, topdown=False):
        for file in files:
            if file.endswith(".png"):
                s = file.split('.')
                if len(s) > 2:
                    if s[-2].startswith("thresh"):
                        p = os.path.join(root, file)
                        print("CLEANING", f"{p:<50}", " ==> ", end="")
                        os.remove(p)
                        print("DONE")


def evaluate_images(top_path="../data", metric=EvaluateMetric.CV2) -> float:
    """
    evaluate all images in top_path recursively, and return the advisable default confidence for image comparison
    :param metric:
    :param top_path: top level path to scan
    :return: advisable default confidence
    """
    clean_evaluated_images()
    cs = []
    for root, dirs, files in os.walk(top_path, topdown=False):
        for file in files:
            if file.endswith(".png"):
                p = os.path.join(root, file)
                print("EVALUATING", f"{p:<50}", " ==> ", end="")
                thresh, criterion, _ = evaluate_image(p, metric=metric)
                cs.append(criterion / 2)
                print(f"\t{thresh=:<10},{criterion=:.2f}")
    default = round(1 - sorted(cs)[len(cs) // 2], 2)
    print(f"\n>>> Advisable default confidence: {default} <<<")
    return default


if __name__ == '__main__':
    import sys
    sys.path.append(os.path.abspath("../.ocr_venv/Lib/site-packages"))
    import cv2
    import numpy
    evaluate_images()

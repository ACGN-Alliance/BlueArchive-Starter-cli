import os

import cv2


def calc_criterion(img, thresh=127):
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    img = cv2.threshold(img, thresh, 255, cv2.THRESH_BINARY)[1]

    total_pixels = img.shape[0] * img.shape[1]
    black_pixels = cv2.countNonZero(img)
    return (total_pixels - black_pixels) / total_pixels, img


def evaluate_thresh(img_path, target=0.175, error=0.025):
    img = cv2.imread(img_path)
    # img = cv2.cvtColor(np.asarray(img), cv2.COLOR_RGB2BGR)
    L = 0
    R = 255
    history = {}
    while L < R:
        thresh = (L + R) // 2
        criterion, _img = calc_criterion(img, thresh)
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


def evaluate_image(path):
    thresh, criterion, _img = evaluate_thresh(path)
    cv2.imwrite(path.replace(".png", f".thresh{thresh}.png"), _img)
    return thresh, criterion


def show_img(img, title=""):
    cv2.imshow(title, img)
    cv2.waitKey()
    cv2.destroyAllWindows()


def clean_evaluated_images():
    for root, dirs, files in os.walk("data", topdown=False):
        for file in files:
            if file.endswith(".png"):
                s = file.split('.')
                if len(s) > 2:
                    if s[-2].startswith("thresh"):
                        p = os.path.join(root, file)
                        print("CLEANING", f"{p:<50}", " ==> ", end="")
                        os.remove(p)
                        print("DONE")


def evaluate_images():
    clean_evaluated_images()
    cs = []
    for root, dirs, files in os.walk("data", topdown=False):
        for file in files:
            if file.endswith(".png"):
                p = os.path.join(root, file)
                print("EVALUATING", f"{p:<50}", " ==> ", end="")
                thresh, criterion = evaluate_image(p)
                cs.append(criterion / 2)
                print(f"\t{thresh=:<10},{criterion=:.2f}")
    print(f"\n>>> Advisable default confidence: {1 - sum(cs) / len(cs):.2f} <<<")


clean_evaluated_images()

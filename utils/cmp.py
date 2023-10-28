import enum
import os.path
import subprocess
import warnings

__all__ = ['CompareMetrics', 'compare_images']

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
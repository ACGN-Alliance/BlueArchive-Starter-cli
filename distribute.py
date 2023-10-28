import os
import shutil
import subprocess
import sys
from zipfile import ZipFile, ZIP_DEFLATED

from tqdm import tqdm

site_packages = ".ocr_venv/Lib/site-packages"
test_ocr_code = """import sys
import os
site_packages = ".ocr_venv/Lib/site-packages"
sys.path.append(os.path.abspath(site_packages))
flag = False
def test_ocr():
    try:
        from rapidocr_onnxruntime import RapidOCR
        engine = RapidOCR()

        for box, text, confidence in engine(r"tests/img.png")[0]:
            box = str(box)
            print(f"box = {box:<80}, text = {text:<20}, confidence = {confidence:.2f}")
        flag = True
    except Exception as e:
        print(e)
if __name__ == '__main__':
    test_ocr()
"""


def test_ocr():
    namespace = {}
    exec(test_ocr_code, namespace)
    return namespace["flag"]


def test_ocr_internal():
    try:
        from rapidocr_onnxruntime import RapidOCR
        engine = RapidOCR()

        for box, text, confidence in engine(r"tests/img.png")[0]:
            box = str(box)
            print(f"box = {box:<80}, text = {text:<20}, confidence = {confidence:.2f}")
        return True
    except Exception as e:
        print(e)
        return False


def create_ocr_env():
    run = subprocess.run('tasklist|findstr "clash"', shell=True, capture_output=True)
    if len(run.stdout) > 0:
        for _ in range(3):
            print(
                "\033[91m### clash is running, please ensure that <TURN MODE> is <TURNED OFF> for a successful installation of additional requirements ###\033[0m"
            )
        input("press enter to continue")
    run = subprocess.run("python --version", shell=True, capture_output=True, text=True)
    py_ver = run.stdout.lower().replace("python ", "").strip()
    assert py_ver.startswith("3.10"), f"global python version must be 3.10, but got {py_ver}"
    # run bat file
    result = subprocess.run("create_ocr_env.bat", shell=True, cwd=os.getcwd())
    assert result.returncode == 0, f"create_ocr_env.bat failed: {result.stderr.decode('utf-8')}"


def pack_dependencies(zip_name="ocr_dependencies_win_3.10.zip"):
    # pack zip file
    with ZipFile(zip_name, "w", compression=ZIP_DEFLATED, compresslevel=9) as zip_file:
        # pack all files in dir "site-packages" to "/ocr_dependencies/"
        print("scanning files...")
        file_list = []
        for root, dirs, files in os.walk(site_packages, topdown=False):
            for file in files:
                if '__pycache__' in root: continue
                file_list.append((
                    p := os.path.join(root, file),
                    "ocr_dependencies" + p.replace(site_packages, "")
                ))
        for p, arcname in tqdm(file_list, desc="pack dependencies", unit="file"):
            zip_file.write(p, arcname=arcname)

        file_list.clear()
        PIL = os.path.join(site_packages, "PIL")
        # pack PIL in dir "site-packages" to "/PIL/"
        for root, dirs, files in os.walk(PIL, topdown=False):
            for file in files:
                if '__pycache__' in root: continue
                file_list.append((
                    p := os.path.join(root, file),
                    p.replace(site_packages, "")
                ))
        for p, arcname in tqdm(file_list, desc="pack PIL", unit="file"):
            zip_file.write(p, arcname=arcname)

        for _, _, files in os.walk('tests'):
            for file in files:
                zip_file.write(os.path.join('tests', file), arcname='tests/' + file)


def build_ocr_dependencies():
    # build ocr_dependencies
    if not test_ocr_internal():
        if not test_ocr():
            print("test ocr failed, try to create ocr env")
            create_ocr_env()
    if not test_ocr_internal():
        if not test_ocr():
            print("test ocr failed, please check your environment")
            exit(1)
    print("test ocr success, try to pack dependencies")
    pack_dependencies()
    print("pack dependencies success")
    shutil.move("ocr_dependencies_win_3.10.zip", "build/ocr_dependencies_win_3.10.zip")


def read_version():
    with open("pack.bat", "r", encoding="utf-8") as f:
        lines = f.readlines()
    version = [line for line in lines if "file-version" in line][0]
    return version.split('"')[1]


def build_main():
    # build main
    print("build main")
    result = subprocess.run("pack.bat", shell=True)
    assert result.returncode == 0, f"pack.bat failed: {result.stderr.decode('utf-8')}"
    print("build success")

    # move all dll file in dir "platform-tools" to dir "build/main.dist/platform-tools"
    print("move all dll file in dir 'platform-tools' to dir 'build/main.dist/platform-tools'")
    for root, dirs, files in os.walk("platform-tools"):
        for file in files:
            if file.endswith(".dll"):
                os.replace(os.path.join(root, file), os.path.join("build/main.dist/platform-tools", file))
                print(f"\tmoved {file}")

    print("upx files in dir 'build/main.dist'")
    # upx files in dir "build/main.dist"
    subprocess.run("upx -9 build/main.dist/* --force", shell=True)
    # pack main
    print("pack main")
    file_list = []
    print("scanning files...")
    for root, dirs, files in os.walk("build/main.dist", topdown=False):
        for file in files:
            if '__pycache__' in root: continue
            file_list.append((
                p := os.path.join(root, file),
                p.replace("build/main.dist", "")
            ))
    ver = read_version()
    with ZipFile(f"build/bas_{ver}.zip", "w", compression=ZIP_DEFLATED, compresslevel=9) as zip_file:
        for p, arcname in tqdm(file_list, desc="pack main", unit="file"):
            zip_file.write(p, arcname=arcname)
    print("pack success")


def build_all():
    try:
        build_main()
        build_ocr_dependencies()
        print("build all success")
        # open dir "build"
        os.startfile("build")
        exit(0)
    except Exception as e:
        print(e)
        print("build all failed")
        exit(1)


if __name__ == '__main__':
    sys.path.append(os.path.abspath(site_packages))
    build_all()

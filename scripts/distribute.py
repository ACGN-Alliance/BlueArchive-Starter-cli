import argparse
import os
import re
import shutil
import subprocess
import sys
import zipfile
from io import BytesIO
from zipfile import ZipFile, ZIP_DEFLATED

import urllib3
from tqdm import tqdm

script = """
python -m nuitka ^
    --standalone ^
    --lto=no ^
    --assume-yes-for-downloads ^
    --output-dir=build ^
    --company-name="ACGN-Alliance" ^
    --product-name="BlueArchive-Starter" ^
    --windows-icon-from-ico=bas.ico ^
    --disable-plugin=multiprocessing ^
    --file-version="$FILE_VERSION$" ^
    --product-version="$FILE_VERSION$" ^
    --windows-file-description="BlueArchive Account tool" ^
    --include-data-dir=platform-tools=platform-tools ^
    --include-data-dir=data/16_9=data/16_9 ^
    --nofollow-import-to=tqdm,mypy-extensions,tomli,packaging,platformdirs,click,pathspec,typing-extensions,black,urllib3 ^
    --copyright="Copyright ACGN-Alliance. All right reserved." ^
    --remove-output ^
    main.py ^
"""


class Distributor:
    __site_packages = ".ocr_venv/Lib/site-packages"
    __test_ocr_code = """
import sys
import os
site_packages = ".ocr_venv/Lib/site-packages"
sys.path.append(os.path.abspath(site_packages))
def test_ocr():
    try:
        from rapidocr_onnxruntime import RapidOCR
        engine = RapidOCR()

        for box, text, confidence in engine(r"tests/img.png")[0]:
            box = str(box)
            print(f"box = {box:<80}, text = {text:<20}, confidence = {confidence:.2f}")
        print(True)
    except Exception as e:
        print(False)
if __name__ == '__main__':
    test_ocr()
    """

    @classmethod
    def test_ocr(cls):
        with open("_test_ocr.py", "w") as f:
            f.write(cls.__test_ocr_code)
        result = subprocess.run("pdm run _test_ocr.py".split(" "), shell=True, capture_output=True)
        os.remove("_test_ocr.py")
        return eval(result.stdout.splitlines()[-1].decode("utf-8"))

    @classmethod
    def __test_ocr_internal(cls):
        try:
            from rapidocr_onnxruntime import RapidOCR

            engine = RapidOCR()

            for box, text, confidence in engine(r"tests/img.png")[0]:
                box = str(box)
                print(
                    f"box = {box:<80}, text = {text:<20}, confidence = {confidence:.2f}"
                )
            return True
        except Exception as e:
            print(e)
            return False

    @classmethod
    def __create_ocr_env(cls):
        run = subprocess.run(
            'tasklist|findstr "clash"', shell=True, capture_output=True
        )
        if len(run.stdout) > 0:
            for _ in range(3):
                print(
                    "\033[91m### clash is running, please ensure that <TURN MODE> is <TURNED OFF> for a successful installation of additional requirements ###\033[0m"
                )
            input("press enter to continue")
        run = subprocess.run(
            "python --version", shell=True, capture_output=True, text=True
        )
        py_ver = run.stdout.lower().replace("python ", "").strip()
        assert py_ver.startswith(
            "3.10"
        ), f"global python version must be 3.10, but got {py_ver}"
        # run bat file
        result = subprocess.run("pdm run .\\scripts\\create_ocr_env.bat".split(' '), shell=True, cwd=os.getcwd())
        assert (
                result.returncode == 0
        ), f"create_ocr_env.bat failed: {result.stderr.decode('utf-8')}"

    @classmethod
    def __pack_dependencies(cls, zip_name="ocr_dependencies_win_3.10.zip"):
        # pack zip file
        with ZipFile(
                zip_name, "w", compression=ZIP_DEFLATED, compresslevel=9
        ) as zip_file:
            # pack all files in dir "site-packages" to "/ocr_dependencies/"
            print("scanning files...")
            file_list = []
            for root, dirs, files in os.walk(cls.__site_packages, topdown=False):
                for file in files:
                    if "__pycache__" in root:
                        continue
                    file_list.append(
                        (
                            p := os.path.join(root, file),
                            "ocr_dependencies" + p.replace(cls.__site_packages, ""),
                        )
                    )
            for p, arcname in tqdm(file_list, desc="pack dependencies", unit="file"):
                zip_file.write(p, arcname=arcname)

            file_list.clear()
            PIL = os.path.join(cls.__site_packages, "PIL")
            # pack PIL in dir "site-packages" to "/PIL/"
            for root, dirs, files in os.walk(PIL, topdown=False):
                for file in files:
                    if "__pycache__" in root:
                        continue
                    file_list.append(
                        (
                            p := os.path.join(root, file),
                            p.replace(cls.__site_packages, ""),
                        )
                    )
            for p, arcname in tqdm(file_list, desc="pack PIL", unit="file"):
                zip_file.write(p, arcname=arcname)

            for _, _, files in os.walk("tests"):
                for file in files:
                    if file.endswith(".pyc"):
                        continue
                    zip_file.write(os.path.join("tests", file), arcname="tests/" + file)

    @classmethod
    def register_dependencies_path(cls):
        if cls.__site_packages not in sys.path[-1]:
            sys.path.append(os.path.abspath(cls.__site_packages))

    @classmethod
    def build_ocr_dependencies(cls):
        """
        only build ocr_dependencies to FILE "build/release/ocr_dependencies_win_3.10.zip"
        :return:
        """
        cls.register_dependencies_path()
        os.makedirs("build", exist_ok=True)
        os.makedirs("build/release", exist_ok=True)
        # build ocr_dependencies
        if not cls.__test_ocr_internal():
            if not cls.test_ocr():
                print("test ocr failed, try to create ocr env")
                cls.__create_ocr_env()
        if not cls.__test_ocr_internal():
            if not cls.test_ocr():
                print("test ocr failed, please check your environment")
                exit(1)
        print("test ocr success, try to pack dependencies")
        cls.__pack_dependencies()
        print("pack dependencies success")
        shutil.move(
            "ocr_dependencies_win_3.10.zip", "build/release/ocr_dependencies_win_3.10.zip"
        )

    @staticmethod
    def get_build_script(version):
        _script = script.replace("$FILE_VERSION$", version)
        return _script

    @staticmethod
    def get_version(raw_version):
        # 提取版本号 x.x.x.x
        version = re.findall(r"\d+\.\d+\.\d+\.\d+", raw_version)[0]
        return version

    @classmethod
    def get_upx(cls):
        try:
            subprocess.run("upx -h", shell=True, stdout=subprocess.PIPE)
            return "upx"
        except FileNotFoundError:
            if os.path.exists("build\\upx"):
                # delete old upx
                shutil.rmtree("build\\upx")
            # get upx ==> build\upx\upx.exe
            url = "https://github.com/upx/upx/releases/download/v4.2.1/upx-4.2.1-win64.zip"
            file = BytesIO(b"")
            r = urllib3.request("GET", url)
            file.write(r.data)
            file.seek(0)

            with zipfile.ZipFile(file) as f:
                # upx-4.2.1-win64\upx.exe
                f.extractall("build\\upx")
            _upx = "build\\upx\\upx-4.2.1-win64\\upx.exe"
            file.close()
            return _upx

    @classmethod
    def build_main(cls, version):
        """
        only build main program to FILE "build/bas_{ver}.zip"
        :return:
        """
        version = cls.get_version(version)  # 提取版本号 x.x.x.x

        cls.register_dependencies_path()
        # build main
        print("build main")
        # dump build script
        with open("_pack.bat", "w", encoding="utf-8") as f:
            f.write(cls.get_build_script(version))

        result = subprocess.run("pdm run _pack.bat".split(" "), shell=True)

        assert (
                result.returncode == 0
        ), f"pack.bat failed: {result.stderr.decode('utf-8')}"
        print("build success")
        # delete build script
        os.remove("_pack.bat")

        # move all dll file in dir "platform-tools" to dir "build/main.dist/platform-tools"
        print(
            "move all dll file in dir 'platform-tools' to dir 'build/main.dist/platform-tools'"
        )
        for root, dirs, files in os.walk("platform-tools"):
            for file in files:
                if file.endswith(".dll"):
                    shutil.copyfile(
                        os.path.join(root, file),
                        os.path.join("build/main.dist/platform-tools", file),
                    )
                    print(f"\tmoved {file}")

        print("upx files in dir 'build/main.dist'")
        # upx files in dir "build/main.dist"
        subprocess.run(f"{Distributor.get_upx()} -9 build/main.dist/* --force", shell=True)
        # pack main
        print("pack main")
        file_list = []
        print("scanning files...")
        for root, dirs, files in os.walk("build/main.dist", topdown=False):
            for file in files:
                if "__pycache__" in root:
                    continue
                file_list.append(
                    (p := os.path.join(root, file), p.replace("build/main.dist", ""))
                )
        with ZipFile(
                f"build/release/bas_{version}.zip", "w", compression=ZIP_DEFLATED, compresslevel=9
        ) as zip_file:
            for p, arcname in tqdm(file_list, desc="pack main", unit="file"):
                zip_file.write(p, arcname=arcname)
        print("pack success")

    @classmethod
    def reformat_code(cls):
        subprocess.run("pdm run black main.py", shell=True)
        subprocess.run("pdm run black script.py", shell=True)
        subprocess.run("pdm run black utils", shell=True)

    @classmethod
    def build_all(cls, version):
        """
        build main and ocr_dependencies to DIR "build"
        :return:
        """
        cls.register_dependencies_path()
        print("reformat code")
        cls.reformat_code()
        try:
            cls.build_main(version=version)
            cls.build_ocr_dependencies()
            print("build all success")
            # open dir "build"
            os.startfile("build")
            exit(0)
        except Exception as e:
            print(e)
            print("build all failed")
            exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-v',
        '--version',
        type=str,
        help='version of this release',
    )
    parser.add_argument(
        '--build_main',
        action='store_true',
        help='build main program',
    )
    parser.add_argument(
        '--build_ocr',
        action='store_true',
        help='build ocr dependencies',
    )
    args = parser.parse_args()

    os.makedirs("build", exist_ok=True)
    os.makedirs("build/release", exist_ok=True)
    Distributor.register_dependencies_path()
    if args.build_main:
        Distributor.build_main(version=args.version)
    if args.build_ocr:
        Distributor.build_ocr_dependencies()
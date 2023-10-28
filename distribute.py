import os
import shutil
import subprocess
import sys
from zipfile import ZipFile, ZIP_DEFLATED

from tqdm import tqdm


class Distributor:
    __site_packages = ".ocr_venv/Lib/site-packages"
    __test_ocr_code = """import sys
    import os
    cls.site_packages = ".ocr_venv/Lib/site-packages"
    sys.path.append(os.path.abspath(cls.site_packages))
    flag = False
    def cls.test_ocr():
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
        cls.test_ocr()
    """

    @classmethod
    def __test_ocr(cls):
        namespace = {}
        exec(cls.__test_ocr_code, namespace)
        return namespace["flag"]

    @classmethod
    def __test_ocr_internal(cls):
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

    @classmethod
    def __create_ocr_env(cls):
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

    @classmethod
    def __pack_dependencies(cls, zip_name="ocr_dependencies_win_3.10.zip"):
        # pack zip file
        with ZipFile(zip_name, "w", compression=ZIP_DEFLATED, compresslevel=9) as zip_file:
            # pack all files in dir "site-packages" to "/ocr_dependencies/"
            print("scanning files...")
            file_list = []
            for root, dirs, files in os.walk(cls.__site_packages, topdown=False):
                for file in files:
                    if '__pycache__' in root: continue
                    file_list.append((
                        p := os.path.join(root, file),
                        "ocr_dependencies" + p.replace(cls.__site_packages, "")
                    ))
            for p, arcname in tqdm(file_list, desc="pack dependencies", unit="file"):
                zip_file.write(p, arcname=arcname)

            file_list.clear()
            PIL = os.path.join(cls.__site_packages, "PIL")
            # pack PIL in dir "site-packages" to "/PIL/"
            for root, dirs, files in os.walk(PIL, topdown=False):
                for file in files:
                    if '__pycache__' in root: continue
                    file_list.append((
                        p := os.path.join(root, file),
                        p.replace(cls.__site_packages, "")
                    ))
            for p, arcname in tqdm(file_list, desc="pack PIL", unit="file"):
                zip_file.write(p, arcname=arcname)

            for _, _, files in os.walk('tests'):
                for file in files:
                    zip_file.write(os.path.join('tests', file), arcname='tests/' + file)

    @classmethod
    def __register_dependencies_path(cls):
        if cls.__site_packages not in sys.path[-1]:
            sys.path.append(os.path.abspath(cls.__site_packages))

    @classmethod
    def build_ocr_dependencies(cls):
        """
        only build ocr_dependencies to FILE "build/ocr_dependencies_win_3.10.zip"
        :return:
        """
        cls.__register_dependencies_path()
        os.makedirs("build", exist_ok=True)
        # build ocr_dependencies
        if not cls.__test_ocr_internal():
            if not cls.__test_ocr():
                print("test ocr failed, try to create ocr env")
                cls.__create_ocr_env()
        if not cls.__test_ocr_internal():
            if not cls.__test_ocr():
                print("test ocr failed, please check your environment")
                exit(1)
        print("test ocr success, try to pack dependencies")
        cls.__pack_dependencies()
        print("pack dependencies success")
        shutil.move("ocr_dependencies_win_3.10.zip", "build/ocr_dependencies_win_3.10.zip")

    @classmethod
    def read_version(cls):
        with open("pack.bat", "r", encoding="utf-8") as f:
            lines = f.readlines()
        version = [line for line in lines if "file-version" in line][0]
        return version.split('"')[1]

    @classmethod
    def build_main(cls):
        """
        only build main program to FILE "build/bas_{ver}.zip"
        :return:
        """
        cls.__register_dependencies_path()
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
        ver = cls.read_version()
        with ZipFile(f"build/bas_{ver}.zip", "w", compression=ZIP_DEFLATED, compresslevel=9) as zip_file:
            for p, arcname in tqdm(file_list, desc="pack main", unit="file"):
                zip_file.write(p, arcname=arcname)
        print("pack success")

    @classmethod
    def build_all(cls):
        """
        build main and ocr_dependencies to DIR "build"
        :return:
        """
        cls.__register_dependencies_path()
        try:
            cls.build_main()
            cls.build_ocr_dependencies()
            print("build all success")
            # open dir "build"
            os.startfile("build")
            exit(0)
        except Exception as e:
            print(e)
            print("build all failed")
            exit(1)


if __name__ == '__main__':
    Distributor.build_all()

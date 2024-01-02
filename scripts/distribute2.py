import argparse
import pathlib
import shutil
from pathlib import Path
from distribute import Distributor

from tqdm import tqdm

python_url = "https://www.python.org/ftp/python/3.10.8/python-3.10.8-embed-amd64.zip"
venv_path = Path('./.venv')
bootstrap = """
import os
import sys
import pathlib

# DIR -
#     | - .env
#     | - .ocr_env (optional)
#     | - .python
#     | - bas
#         | - data
#         | - utils
#         | - main.py
#         | - script.py
#     | - platform-tools
#     | - bootstrap.py
#     | - run.bat

env = pathlib.Path(".") / ".env"
ocr_env = pathlib.Path(".") / ".ocr_env"
python = pathlib.Path(".") / ".python"
bas = pathlib.Path(".") / "bas"
platform_tools = pathlib.Path(".") / "platform-tools"

# Register to sys.path only in Runtime
sys.path.append(str(pathlib.Path(".").absolute()))
sys.path.append(str(bas.absolute()))
sys.path.append(str(platform_tools.absolute()))
sys.path.append(str(python.absolute()))
sys.path.append(str(env.absolute()))
if ocr_env.exists():
    sys.path.append(str(ocr_env.absolute()))

from bas.main import main
print("Running BAS... ,with args:",sys.argv)
if len(sys.argv) == 1:
    os.chdir(bas) # normal mode
main(sys.argv)
"""
run_script = """
@echo off
".\\.python\\python.exe" bootstrap.py
"""


def main(version):
    # clean dir
    target = Path("build/embed")
    python_cache = Path("build/python_embed.zip")

    if target.exists():
        shutil.rmtree(target)
    else:
        target.mkdir(parents=True)

    # get python embed
    import urllib3
    import zipfile
    import io

    if not python_cache.exists():
        print("downloading python embed...")
        r = urllib3.request(method="GET", url=python_url)
        z = zipfile.ZipFile(io.BytesIO(r.data))
        with open(python_cache, "wb") as f:
            f.write(r.data)
    else:
        z = zipfile.ZipFile(python_cache)

    print("extracting python embed...")
    python_target = target / ".python"
    z.extractall(python_target)

    print("copy libs")
    libs = venv_path / "Lib" / "site-packages"
    lib_target = target / ".env"
    shutil.copytree(libs, lib_target)

    print("copy bas")
    bas_target = target / "bas"
    dirs = [
        "data",
        "utils",
    ]
    files = [
        "main.py",
        "script.py",
    ]
    for d in dirs:
        shutil.copytree(d, bas_target / d)
    for f in files:
        shutil.copy(f, bas_target / f)

    print("download platform-tools")
    Distributor.get_platform_tools()

    print("copy platform-tools")
    platform_tools_target = target / "platform-tools"
    shutil.copytree(Path("platform-tools").absolute(), platform_tools_target)

    print("write bootstrap.py")
    bootstrap_target = target / "bootstrap.py"
    with open(bootstrap_target, "w") as f:
        f.write(bootstrap)

    print("write run.bat")
    run_target = target / "run.bat"
    with open(run_target, "w") as f:
        f.write(run_script)

    print("packing")
    file_list = []
    for i in pathlib.Path(target).glob("**/*"):
        if i.is_file():
            file_list.append(i)

    (target.parent / "release").mkdir(exist_ok=True)
    f = target.parent / f"release/bas_{version}.zip"
    with zipfile.ZipFile(f, "w", compresslevel=9, compression=zipfile.ZIP_LZMA) as z:
        for i in tqdm(file_list):
            z.write(i, arcname=i.relative_to(target))
    print("clean")
    shutil.rmtree(target)

    print("done")


if __name__ == '__main__':
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
    if args.build_main:
        main(args.version)
        print("*** build main done ***")
    if args.build_ocr:
        Distributor.build_ocr_dependencies()
        print("*** build ocr done ***")
    print("*** all done ***")

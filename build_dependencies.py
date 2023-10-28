"""
coloredlogs          15.0.1
flatbuffers          23.5.26
humanfriendly        10.0
mpmath               1.3.0
numpy                1.26.0
onnxruntime          1.16.1
opencv-python        4.8.1.78
packaging            23.2
Pillow               10.0.1
pip                  23.2.1
protobuf             4.24.4
pyclipper            1.3.0.post5
pyreadline3          3.4.1
PyYAML               6.0.1
rapidocr-onnxruntime 1.3.7
setuptools           68.2.2
shapely              2.0.2
six                  1.16.0
sympy                1.12
wheel                0.41.2
"""
import os
import subprocess

cmd = "nuitka --module --include-module=coloredlogs,flatbuffers,humanfriendly,mpmath,numpy,onnxruntime" \
      ",cv2,packaging,PIL,protobuf,pyclipper,pyreadline3,PyYAML,rapidocr-onnxruntime,setuptools" \
      ",shapely,six,sympy,wheel onnxruntime"

# 切换到.ocr_venv/Lib/site-packages目录
os.chdir(os.path.join(os.getcwd(), ".ocr_venv/Lib/site-packages"))
subprocess.run(cmd, shell=True)

@echo off

chdir
@REM 创建"ocr_venv" venv
echo "create '.ocr_venv' venv"
python -m venv .ocr_venv

@REM 激活"ocr_venv" venv
echo "activate '.ocr_venv' venv"
call .ocr_venv\Scripts\activate.bat

@REM 更新pip
echo "update pip..."
python.exe -m pip install --upgrade pip -i https://mirrors.aliyun.com/pypi/simple

@REM 安装rapidocr_onnxruntime
echo "pip install rapidocr_onnxruntime..."
pip install rapidocr_onnxruntime -i https://mirrors.aliyun.com/pypi/simple

echo "create '.ocr_venv' venv success!"
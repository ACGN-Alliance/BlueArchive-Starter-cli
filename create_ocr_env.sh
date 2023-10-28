#!/bin/bash

# 创建"ocr_venv" venv
echo "create '.ocr_venv' venv"
python -m venv .ocr_venv

# 激活"ocr_venv" venv
echo "activate '.ocr_venv' venv"
source .ocr_venv/Scripts/activate

# 安装rapidocr_onnxruntime
echo "pip install rapidocr_onnxruntime..."
pip install rapidocr_onnxruntime

echo "create '.ocr_venv' venv success!"
read -p "Press Enter to continue..."

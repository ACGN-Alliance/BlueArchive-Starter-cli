# For Linux
python -m nuitka --mingw64 --standalone \
    --assume-yes-for-downloads \
    --follow-import-to=utils \
    --lto=no \
    --disable-plugin=multiprocessing\
    --output-dir=build \
    --company-name="ACGN-Alliance" \
    --product-name="BlueArchive-Starter" \
    --file-version="1.0.6" \
    --product-version="1.0.6" \
    --file-description="BlueArchive Account tool" \
    --include-data-dir=platform-tools=platform-tools\
    --include-data-dir=data/16_9=data/16_9 \
    --copyright="Copyright ©ACGN-Alliance. All right reserved." \
    --remove-output \
    --onefile \
    main.py

#    --disable-console \
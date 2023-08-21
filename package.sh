# For Linux
python -m nuitka --mingw64 --standalone \
    --assume-yes-for-downloads \
    --follow-import-to=utils \
    --lto=no \
    --disable-plugin=multiprocessing\
    --output-dir=build \
    --company-name="ACGN-Alliance" \
    --product-name="BlueArchive-Starter" \
    --file-version="1.0.0" \
    --product-version="1.0.0" \
    --file-description="BlueArchive Account tool" \
    --remove-output \
    --onefile \
    main.py

#    --disable-console \
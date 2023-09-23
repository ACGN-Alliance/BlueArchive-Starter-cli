nuitka ^
    --standalone ^
    --lto=no ^
    --output-dir=build ^
    --company-name="ACGN-Alliance" ^
    --product-name="BlueArchive-Starter" ^
    --windows-icon-from-ico=bas.ico ^
    --disable-plugin=multiprocessing ^
    --file-version="1.0.5.1" ^
    --product-version="1.0.5.1" ^
    --windows-file-description="BlueArchive Account tool" ^
    --include-data-dir=platform-tools=platform-tools ^
    --include-data-dir=data/16_9=data/16_9 ^
    --copyright="Copyright ©ACGN-Alliance. All right reserved." ^
    --remove-output ^
    main.py ^
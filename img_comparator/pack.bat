nuitka ^
    --standalone ^
    --lto=no ^
    --output-dir=build ^
    --company-name="ACGN-Alliance" ^
    --product-name="BlueArchive-Starter-ImageComparator" ^
    --windows-icon-from-ico=../bas.ico ^
    --disable-plugin=multiprocessing ^
    --file-version="0.0.1" ^
    --product-version="0.0.1" ^
    --windows-file-description="BlueArchive Account tool" ^
    --copyright="Copyright @ACGN-Alliance. All right reserved." ^
    --remove-output ^
    --plugin-enable=pyqt5 ^
    --msvc=latest ^
    --clang ^
    --windows-disable-console ^
    Entry.py
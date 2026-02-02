@echo off
echo ========================================================
echo  KHOI DONG CHROME CHO TOOL SPAM
echo ========================================================
echo.
echo Luu y: Ban nen tat het cac cua so Chrome dang mo truoc khi chay file nay de tranh xung dot.
echo.
echo Dang khoi dong Chrome...
echo.

:: Tao thu muc profile rieng de khong anh huong chrome chinh
if not exist "chrome_profile" mkdir "chrome_profile"

:: Start chrome with debugging port 9222 and local profile
start "" "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir="%~dp0chrome_profile"

echo DONE! Chrome da duoc mo.
echo Bay gio ban hay quay lai cua so cmd va chay lenh: py main.py
echo.
pause

@echo off
setlocal enabledelayedexpansion

REM --- 1. Find first matching file ---
for %%F in (*.png *.jpg *.jpeg *.svg) do (
    set "FILE=%%F"
    goto found
)

echo Brak plikow PNG/JPG/JPEG/SVG w tym folderze.
exit /b 1

:found
echo Znaleziono plik: %FILE%

REM --- 2. Temp Base64 file ---
set "TMP=%TEMP%\tmp_b64.txt"

REM --- 3. Encode to Base64 ---
certutil -encode "%FILE%" "%TMP%" >nul

REM --- 4. Remove certutil headers ---
set "BASE64="
for /f "usebackq skip=1 delims=" %%A in ("%TMP%") do (
    if "%%A"=="-----END CERTIFICATE-----" goto done
    set "BASE64=!BASE64!%%A"
)

:done

REM --- 5. Detect MIME ---
set "MIME=image/jpeg"
echo "%FILE%" | findstr /i ".png" >nul && set "MIME=image/png"
echo "%FILE%" | findstr /i ".gif" >nul && set "MIME=image/gif"
echo "%FILE%" | findstr /i ".webp" >nul && set "MIME=image/webp"
echo "%FILE%" | findstr /i ".svg" >nul && set "MIME=image/svg+xml"

REM --- 6. Build HTML IMG tag ---
set "HTML=<img src="data:%MIME%;base64,!BASE64!" alt="image" />"

REM --- 7. Copy to clipboard safely ---
set "OUT=%TEMP%\tmp_html.txt"
echo !HTML! > "%OUT%"
type "%OUT%" | clip

REM --- 8. Output confirmation ---
echo.
echo Skopiowano do schowka:
echo.
type "%OUT%"

del "%TMP%" >nul 2>&1
del "%OUT%" >nul 2>&1
endlocal

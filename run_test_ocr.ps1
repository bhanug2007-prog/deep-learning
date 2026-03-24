# UTF-8 + EasyOCR download progress (avoids cp1252 Unicode errors on Windows)
chcp 65001 | Out-Null
$env:PYTHONUTF8 = "1"
Set-Location $PSScriptRoot
python test_ocr.py

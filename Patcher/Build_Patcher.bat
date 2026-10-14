@echo off
setlocal
cd /d "%~dp0"
title Ambidextro Vita Patcher - Build
python "src\build_patch_data.py" || goto error
python -m PyInstaller --clean --noconfirm --distpath "dist" --workpath "build" "src\AmbidextroVitaPatcher.spec" || goto error
python "src\package_release.py" || goto error
echo.
echo Build concluido. Veja Patcher\release-v1.0
exit /b 0
:error
echo ERRO - veja o log acima.
exit /b 1

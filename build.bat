@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ===================================================
echo 清风工具箱 v3 打包脚本
echo ===================================================
echo.

echo 开始执行PyInstaller编译...
echo.
pyinstaller main.spec --noconfirm
if %errorlevel% neq 0 (
    echo.
    echo ❌ 编译失败，错误代码: %errorlevel%
    echo 程序退出!
    exit /b %errorlevel%
)
echo.
echo ✅ PyInstaller编译成功!
echo.

if not exist "dist\" (
    echo ❌ 错误: dist文件夹不存在!
    exit /b 1
)

echo 开始打包dist文件夹...
echo.
set zip_filename=FengAmongUsTool.zip
if exist "%zip_filename%" (
    echo 删除已存在的压缩包文件...
    del /f /q "%zip_filename%"
)
powershell -Command "& {Add-Type -AssemblyName System.IO.Compression.FileSystem; [System.IO.Compression.ZipFile]::CreateFromDirectory('dist', '%zip_filename%')}"
:: 检查打包是否成功
if %errorlevel% neq 0 (
    echo ❌ 创建压缩包失败!
    exit /b %errorlevel%
)
echo.
echo ✅ 压缩包创建成功: %zip_filename%

echo.
echo ===================================================
echo ✅ 所有操作完成!
echo ===================================================

exit /b 0
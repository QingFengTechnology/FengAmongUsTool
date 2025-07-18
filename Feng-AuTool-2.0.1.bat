chcp 65001 > nul
@echo off
set "Version=2.0.1"
title QingFeng AmongUs工具箱
echo.
echo ======================================================
echo.
echo QingFeng AmongUs工具箱
echo.
echo 版本：%Version%
echo.
echo ======================================================
echo.
timeout /t 2 /NoBreak > nul
goto initialization

:initialization
cls
echo.
echo ======================================================
echo.
echo QingFeng AmongUs工具箱
echo.
echo 正在初始化脚本……
echo.
echo ======================================================
echo.
timeout /t 1 /NoBreak > nul
goto system_version_check

:system_version_check
cls
echo.
echo ======================================================
echo.
echo QingFeng AmongUs工具箱
echo.
echo 系统版本检查……
echo.
echo ======================================================
echo.
timeout /t 1 /NoBreak > nul
ver | find "10." > nul && goto dependency_check
cls
echo.
echo ======================================================
echo.
echo QingFeng AmongUs工具箱
echo.
echo 你的Windows版本已过时，请升级你的Windows。
echo.
echo ======================================================
echo.
set "InitializationErrorMessage=需要Windows 10/11才能运行此脚本。"
timeout /t 2 /NoBreak > nul
goto initialization_failed

:dependency_check
cls
echo.
echo ======================================================
echo.
echo QingFeng AmongUs工具箱
echo.
echo 依赖项检查……
echo.
echo ======================================================
echo.
timeout /t 1 /NoBreak > nul
where curl > nul 2>&1 || (
  cls 
  echo.
  echo ======================================================
  echo.
  echo QingFeng AmongUs工具箱
  echo.
  echo 你的电脑缺失了必备组件,请自行安装。
  echo.
  echo ======================================================
  echo.
  set "InitializationErrorMessage=缺失组件curl，需要此组件才能运行工具箱的完整功能。"
  timeout /t 2 /NoBreak > nul
  goto initialization_failed
)

:main_menu
cls
echo.
echo ======================================================
echo.
echo 工具箱主菜单
echo.
echo 1. 安装清风服
echo.
echo 2. 修复旧版AmongUs黑屏问题
echo.
echo 3. 关于此工具箱
echo.
echo 4. 退出
echo.
echo ======================================================
echo.
timeout /t 1 /NoBreak > nul
choice /c 1234 /n /m "请输入你的选择：[1,2,3,4]"
if "%ERRORLEVEL%"=="0" goto main_menu
if "%ERRORLEVEL%"=="1" goto install_server_wait
if "%ERRORLEVEL%"=="2" goto fix_old_amongus_wait
if "%ERRORLEVEL%"=="3" goto about
if "%ERRORLEVEL%"=="4" goto exit_tool

:install_server_wait
cls
echo.
echo ======================================================
echo.
echo 安装清风服
echo.
echo 请稍候……
echo.
echo ======================================================
echo.
timeout /t 2 /NoBreak > nul
goto install_server_confirm

:install_server_confirm
cls
echo.
echo ======================================================
echo.
echo 安装清风服
echo.
echo 此操作将*删除*原先你安装的所有私服。
echo.
echo 请自行备份相关文件。
echo.
echo ======================================================
echo.
timeout /t 1 /NoBreak > nul
choice /n /m "你确定要继续此操作吗?输入y确认,n取消并返回主菜单。"
if "%ERRORLEVEL%"=="0" goto install_server_confirm
if "%ERRORLEVEL%"=="1" goto install_server_delete
if "%ERRORLEVEL%"=="2" goto main_menu

:install_server_delete
cls
echo.
echo ======================================================
echo.
echo 安装清风服
echo.
echo 正在删除旧服务器配置文件……
echo.
echo ======================================================
echo.
timeout /t 2 /NoBreak > nul
del /f "%APPDATA%\..\LocalLow\Innersloth\Among Us\regionInfo.json" > nul 2>&1
goto install_server_download

:install_server_download
cls
echo.
echo ======================================================
echo.
echo 安装清风服
echo.
echo 正在下载清风服配置文件…
echo.
echo ======================================================
echo.
timeout /t 2 /NoBreak > nul
curl --ssl-no-revoke "https://api.xtreme.net.cn/Server/regionInfo.json" -o "%APPDATA%\..\LocalLow\Innersloth\Among Us\regionInfo.json"
if %ERRORLEVEL% neq 0 (
  cls
  echo.
  echo ======================================================
  echo.
  echo 你无法安装服务器配置文件。
  echo.
  echo 下载文件出现时异常，下载失败。
  echo.
  echo ======================================================
  echo.
  timeout /t 1 /NoBreak > nul
  echo 按任意键返回主菜单。
  echo.
  pause > nul
  goto main_menu
)
timeout /t 1 /NoBreak > nul
goto install_server_done

:install_server_done
cls
echo.
echo ======================================================
echo.
echo 服务器配置文件安装完成。
echo.
echo 要立即打开AmongUs吗?
echo.
echo 此操作通过Steam进行,因而有些情况下AmongUs启动可能不是那么及时。
echo.
echo ======================================================
echo.
choice /n /m "输入y确认并返回主菜单,输入n直接返回主菜单。"
if "%ERRORLEVEL%"=="0" goto install_server_done
if "%ERRORLEVEL%"=="1" goto install_server_run_amongus
if "%ERRORLEVEL%"=="2" goto main_menu

:install_server_run_amongus
cls
echo.
echo ======================================================
echo.
echo 安装清风服
echo.
echo 正在打开AmongUs……
echo.
echo ======================================================
echo.
timeout /t 1 /NoBreak > nul
start steam://rungameid/945360
goto main_menu

:about
cls
echo.
echo ======================================================
echo.
echo 关于QingFeng AmongUs工具箱
echo.
echo 版本: %Version%
echo.
echo 开发者: QingFeng (https://github.com/QingFeng-awa)
echo.
echo 工具箱仍在持续维护中,因此可能有功能还尚未开发,或存在bug。
echo.
echo 如果你遇到了bug或是想提议一个新功能,请联系QingFeng。
echo.
echo ======================================================
echo.
timeout /t 1 /NoBreak > nul
echo 按任意键返回主菜单。
echo.
pause > nul
goto main_menu

:fix_old_amongus_wait
cls
echo.
echo ======================================================
echo.
echo 修复旧版AmongUs黑屏问题
echo.
echo 请稍候……
echo.
echo ======================================================
echo.
timeout /t 2 /NoBreak > nul
goto fix_old_amongus_confirm

:fix_old_amongus_confirm
cls
echo.
echo ======================================================
echo.
echo 修复旧版AmongUs黑屏问题
echo.
echo 此操作通过替换或删除文件来修复旧版AmongUs黑屏问题。
echo.
echo ======================================================
echo.
timeout /t 1 /NoBreak > nul
choice /n /m "请自行备份相关文件,输入y继续执行,输入n返回主菜单。"
if "%ERRORLEVEL%"=="0" goto fix_old_amongus_confirm
if "%ERRORLEVEL%"=="1" goto fix_old_amongus_choose
if "%ERRORLEVEL%"=="2" goto main_menu

:fix_old_amongus_choose
cls
echo.
echo ======================================================
echo.
echo 选择修复方式
echo.
echo 1. 直接删除 (AmongUs会自动生成默认配置文件,但这会导致包括语言选项的自定义配置全部丢失。)
echo.
echo 2. 下载文件替换 (需要网络连接,且下载文件只是帮你设定了语言为简体中文,其余设置均为默认。)
echo.
echo ======================================================
echo.
timeout /t 1 /NoBreak > nul
choice /c 12 /n /m "请选择修复方式：[1,2]"
if "%ERRORLEVEL%"=="0" goto fix_old_amongus_choose
if "%ERRORLEVEL%"=="1" goto fix_old_amongus_delete
if "%ERRORLEVEL%"=="2" goto fix_old_amongus_download

:fix_old_amongus_delete
cls
echo.
echo ======================================================
echo.
echo 修复旧版AmongUs黑屏问题
echo.
echo 正在删除配置文件……
echo.
echo ======================================================
echo.
timeout /t 2 /NoBreak > nul
del /f "%APPDATA%\..\LocalLow\Innersloth\Among Us\settings.amogus" > nul 2>&1
goto fix_old_amongus_done

:fix_old_amongus_download
cls
echo.
echo ======================================================
echo.
echo 修复旧版AmongUs黑屏问题
echo.
echo 正在下载配置文件……
echo.
echo ======================================================
echo.
timeout /t 2 /NoBreak > nul
curl --ssl-no-revoke "https://api.xtreme.net.cn/Server/settings.amogus" -o "%APPDATA%\..\LocalLow\Innersloth\Among Us\settings.amogus"
if %ERRORLEVEL% neq 0 (
  cls
  echo.
  echo ======================================================
  echo.
  echo 你无法下载配置文件。
  echo.
  echo 下载文件出现时异常，下载失败。
  echo.
  echo ======================================================
  echo.
  timeout /t 1 /NoBreak > nul
  echo 按任意键返回主菜单。
  echo.
  pause > nul
  goto main_menu
)
goto fix_old_amongus_done

:fix_old_amongus_done
cls
echo.
echo ======================================================
echo.
echo 修复完成。
echo.
echo 按任意键返回主菜单。
echo.
echo ======================================================
echo.
timeout /t 1 /NoBreak > nul
pause > nul
goto main_menu

:initialization_failed
cls
echo.
echo ======================================================
echo.
echo 工具箱初始化失败
echo.
echo 脚本版本: %Version%
echo.
echo 错误原因：%InitializationErrorMessage%
echo.
echo 如果你无法理解这是什么，请将此段错误截图发送给(天云群)群成员以寻求帮助。
echo.
echo ======================================================
echo.
echo 脚本初始化失败，按任意键退出。
echo.
pause > nul
exit /b 1

:exit_tool
exit /b 0
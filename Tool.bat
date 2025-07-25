chcp 65001 > nul
@echo off
set "Version=2.1.0"
title 清风 Among Us 工具箱
echo.
echo ======================================================
echo.
echo 清风 Among Us 工具箱
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
echo 清风 Among Us 工具箱
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
echo 清风 Among Us 工具箱
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
echo 清风 Among Us 工具箱
echo.
echo 你的 Windows 版本已过时，请更新你的 Windows。
echo.
echo ======================================================
echo.
set "InitializationErrorMessage=需要 Windows 10/11 才能运行此脚本。"
timeout /t 2 /NoBreak > nul
goto initialization_failed

:dependency_check
cls
echo.
echo ======================================================
echo.
echo 清风 Among Us 工具箱
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
  echo 清风 Among Us 工具箱
  echo.
  echo 你的电脑缺失了必备组件，请自行安装。
  echo.
  echo ======================================================
  echo.
  set "InitializationErrorMessage=缺失组件 cURL，需要此组件才能运行工具箱的完整功能。"
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
echo 2. 修复旧版 Among Us 黑屏问题
echo.
echo 3. 关于此工具箱
echo.
echo 4. 退出
echo.
echo ======================================================
echo.
timeout /t 1 /NoBreak > nul
choice /c 1234 /n /m "请输入你的选择：[1，2，3，4]"
if "%ERRORLEVEL%"=="0" goto main_menu
if "%ERRORLEVEL%"=="1" goto install_server_wait
if "%ERRORLEVEL%"=="2" goto fix_old_amongus_wait
if "%ERRORLEVEL%"=="3" goto about
if "%ERRORLEVEL%"=="4" goto exit_tool
goto main_menu

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
timeout /t 1 /NoBreak > nul
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
choice /n /m "你确定要继续此操作吗？输入 Y 确认，输入 N 取消并返回主菜单。"
if "%ERRORLEVEL%"=="0" goto install_server_confirm
if "%ERRORLEVEL%"=="1" goto install_server_delete
if "%ERRORLEVEL%"=="2" goto main_menu
goto install_server_confirm

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
goto install_server_region_choose

:install_server_region_choose
cls
echo.
echo ======================================================
echo.
echo 安装清风服
echo.
echo 选择下载源
echo.
echo 1. Github
echo.
echo 2. 清风 API (中国大陆可用区)
echo.
echo ======================================================
echo.
timeout /t 1 /NoBreak > nul
choice /c 12 /n /m "请输入你的选择[1，2]："
if "%ERRORLEVEL%"=="0" goto install_server_region_choose
if "%ERRORLEVEL%"=="1" (
  set "ServerDownloadURL=https://raw.githubusercontent.com/QingFengTechnology/FengAmongUsTool/refs/heads/Next/regionInfo.json"
  goto install_server_download
)
if "%ERRORLEVEL%"=="2" (
  set "ServerDownloadURL=https://feng-public.cn-nb1.rains3.com/regionInfo.json"
  goto install_server_download
)
goto install_server_region_choose

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
curl --ssl-no-revoke "%ServerDownloadURL%" -o "%APPDATA%\..\LocalLow\Innersloth\Among Us\regionInfo.json"
if %ERRORLEVEL% neq 0 (
  echo.
  echo 下载文件出现时异常，下载失败。
  echo.
  echo 如果脚本无问题，那么你应该能看到错误信息，请使用电脑软件截图并发送至天云群以请求帮助。
  timeout /t 1 /NoBreak > nul
  echo.
  echo 按任意键返回主菜单。
  pause > nul
  goto main_menu
)
timeout /t 1 /NoBreak > nul
goto install_server_set_read_only_confirm

:install_server_set_read_only_confirm
cls
echo.
echo ======================================================
echo.
echo 安装清风服
echo.
echo 要为配置文件设置只读吗？
echo.
echo 这将阻止 Among Us 修改配置文件，避免安装失效问题。
echo.
echo 但极少数模组可能在设置只读后出现无法启动的问题。
echo.
echo ======================================================
echo.
timeout /t 1 /NoBreak > nul
choice /n /m "输入 Y 设定只读，输入 N 跳过。"
if "%ERRORLEVEL%"=="0" goto install_server_set_read_only_confirm
if "%ERRORLEVEL%"=="1" goto install_server_set_read_only
if "%ERRORLEVEL%"=="2" goto install_server_done
goto install_server_set_read_only_confirm

:install_server_set_read_only
cls
echo.
echo ======================================================
echo.
echo 安装清风服
echo.
echo 正在设置配置文件只读……
echo.
echo ======================================================
echo.
timeout /t 1 /NoBreak > nul
attrib +r "%APPDATA%\..\LocalLow\Innersloth\Among Us\regionInfo.json" > nul 2>&1
goto install_server_done

:install_server_done
cls
echo.
echo ======================================================
echo.
echo 服务器安装完成。
echo.
echo 要立即打开 Among Us 吗?
echo.
echo 此操作通过 Steam 进行，因而有些情况下 Among Us 启动可能不是那么及时。
echo.
echo ======================================================
echo.
choice /n /m "输入 Y 确认并返回主菜单，输入 N 直接返回主菜单。"
if "%ERRORLEVEL%"=="0" goto install_server_done
if "%ERRORLEVEL%"=="1" goto install_server_run_amongus
if "%ERRORLEVEL%"=="2" goto main_menu
goto install_server_done

:install_server_run_amongus
cls
echo.
echo ======================================================
echo.
echo 安装清风服
echo.
echo 正在打开 Among Us……
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
echo 关于清风 Among Us 工具箱
echo.
echo 版本: %Version%
echo.
echo 开发者: QingFeng (https://github.com/QingFeng-awa)
echo.
echo 仓库链接：https://github.com/QingFengTechnology/FengAmongUsTool
echo.
echo 如果你遇到了 Bug 或是想提议一个新功能，请在此工具箱 GitHub 仓库提出 issue。
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
echo 修复旧版 Among Us 黑屏问题
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
echo 修复旧版 Among Us 黑屏问题
echo.
echo 此操作通过删除文件来解决旧版 Among Us 黑屏问题。
echo.
echo 此操作可能会导致极个别模组储存的存档丢失，请自行备份文件。
echo.
echo ======================================================
echo.
timeout /t 1 /NoBreak > nul
choice /n /m "你确定要继续吗？输入 Y 继续执行，输入 N 返回主菜单。"
if "%ERRORLEVEL%"=="0" goto fix_old_amongus_confirm
if "%ERRORLEVEL%"=="1" goto fix_old_amongus_delete
if "%ERRORLEVEL%"=="2" goto main_menu
goto fix_old_amongus_confirm

:fix_old_amongus_delete
cls
echo.
echo ======================================================
echo.
echo 修复旧版 Among Us 黑屏问题
echo.
echo 正在删除配置文件……
echo.
echo ======================================================
echo.
timeout /t 1 /NoBreak > nul
del /f "%APPDATA%\..\LocalLow\Innersloth\Among Us\settings.amogus" > nul 2>&1
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
echo 如果你无法理解这是什么，请使用电脑截图错误信息并发送给天云群以寻求帮助。
echo.
echo ======================================================
echo.
echo 脚本初始化失败，按任意键退出。
echo.
pause > nul
exit /b 1

:exit_tool
exit /b 0

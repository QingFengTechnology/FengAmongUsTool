import os
import sys
import signal
import platform

from time import sleep
from rich.console import Console

from module.about import showAboutPage
from function.updateCheck import checkUpdate
from module.changeSetting import fixAmongUsSetting
from module.changeSetting import updateAmongUsSetting
from module.installServer import installServerRegion
from function.main import defaultHeader, generalMainMenu, selectBestSource

if __name__ == '__main__':
    os.system('title 清风 Among Us 工具箱')

    def signalHandler(sig, frame):
        """处理程序退出"""
        sys.exit(0)
    signal.signal(signal.SIGINT, signalHandler)

    console = Console()

    defaultHeader()
    if platform.system() != "Windows":
        console.print("此项目[red1]不支持[/red1]当前系统，请在 Windows 系统上运行。")
        console.input("按下 [plum1]Enter[/plum1] 退出[white]...[/white]")
        sys.exit(1)
    if platform.version().find("10") != 0:
        console.print("当前系统版本[red1]不满足[/red1]所需的要求，请升级你的 Windows 版本。")
        console.print("此项目不支持[red1]Windows 7 及以下版本[/red1]。")
        console.input("按下 [plum1]Enter[/plum1] 退出[white]...[/white]")
        sys.exit(1)
    console.log(f"Windows 版本[green1]有效[/green1], 当前版本：[cornflower_blue]{platform.version()}[/cornflower_blue]")
    selectBestSource()
    update_result = checkUpdate()
    if update_result:
        import function.variable
        function.variable.UpdateAvailable = True
        function.variable.UpdateInfo = update_result

    while True:
        import function.variable
        currentSource = function.variable.BestDownloadSource
        currentSourceName = currentSource['name'] if currentSource else "无"
        mainMenuText = f"""
-  安装清风服

    1.1 正常安装服务器 (检查是否重复，在原文件上新增服务器)

    1.2 强制安装服务器 (不检查是否重复，直接删除原文件)

-  调整 Among Us 配置版本

    2.1 使用老版本配置 (修复旧版游戏)

    2.2 使用新版本配置

3. 启动 Steam Among Us

4. 重新自动选择源服务器 (当前源：{currentSourceName})

5. 关于工具箱

6. 退出
"""
        generalMainMenu(mainMenuText, "主菜单")
        commandNumber = console.input("请输入要执行的命令编号：").strip()
        if commandNumber == "1" or commandNumber == "1.1":
            installServerRegion(merge=True)
        elif commandNumber == "1.2":
            installServerRegion(merge=False)
        elif commandNumber == "2" or commandNumber == "2.1":
            fixAmongUsSetting()
        elif commandNumber == "2.2":
            updateAmongUsSetting()
        elif commandNumber == "3":
            try:
                os.startfile("steam://rungameid/945360")
                console.print("[green1]已尝试通过 Steam 启动 Among Us。[/green1]")
                sleep(1)
            except Exception as e:
                console.print(f"[red1]通过 Steam 启动 Among Us 时出错：{e}[/red1]")
        elif commandNumber == "4":
            selectBestSource()
            sleep(2)
        elif commandNumber == "5":
            showAboutPage()
        elif commandNumber == "6":
            sys.exit(0)
        else:
            console.print("[red1]输入的命令编号无效，请重新输入。[/red1]")
            sleep(1)
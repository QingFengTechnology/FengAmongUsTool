import platform
import os
from time import sleep
import signal
import sys
from rich.console import Console

from installServer import run as installServer
from fixAmongUs import run as fixAmongUs
from about import run as aboutPage
from function.main import defaultHeader, generalMainMenu

os.system('title 清风 Among Us 工具箱')

# 没看懂 sig frame 干啥的，但不加就不工作
def signalHandler(sig, frame):
  """修正 Ctrl + C 退出报错问题"""
  sys.exit(0)
signal.signal(signal.SIGINT, signalHandler)

console = Console()

defaultHeader()
sleep(2)
with console.status("系统环境检查...") as status:
  sleep(1)
  status.update("检查系统版本...")
  sleep(1)
  if platform.version().find("10") != 0:
    status.stop()
    console.print("当前系统版本[bold red]不满足[/bold red]所需的要求，请升级你的 Windows 版本。")
    console.print("此项目不支持 [bold red]Windows 7 及以下版本[/bold red]。")
    console.input("按 Enter 退出...")
    sys.exit(1)
  console.log(f"Windows 版本有效, 当前版本：{platform.version()}")
  status.update("请稍后...")
  sleep(2)

mainMenuText = """
1. 安装清风服

-  调整 Among Us 配置版本
   
   2.1 使用老版本配置 (修复旧版游戏)

   2.2 使用新版本配置 (仍在开发)

3. 关于工具箱

4. 退出
"""
while True:
  generalMainMenu(mainMenuText, "主菜单")
  sleep(1)
  commandNumber = console.input("请输入要执行的命令编号：").strip()
  if commandNumber == "1":
    installServer()
  elif commandNumber == "2.1":
    fixAmongUs()
  elif commandNumber == "2.2":
    console.print("[bold yellow]功能仍在开发，暂不可用。[/bold yellow]")
  elif commandNumber == "3":
    aboutPage()
  elif commandNumber == "4":
    sys.exit(0)
  else:
    console.print("[bold red]输入的命令编号无效，请重新输入。[/bold red]")
    sleep(1)
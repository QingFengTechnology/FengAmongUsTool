import os
import sys
import signal
import platform

from time import sleep
from rich.console import Console

from about import run as aboutPage
from fixAmongUs import run as fixAmongUs
from fixAmongUs import run2 as updateAmongUs
from function.updateCheck import checkUpdate
from installServer import run as installServer
from function.main import defaultHeader, generalMainMenu

os.system('title 清风 Among Us 工具箱')

# 没看懂 sig frame 干啥的，但不加就不工作
def signalHandler(sig, frame):
  """修正 Ctrl + C 退出报错问题"""
  sys.exit(0)
signal.signal(signal.SIGINT, signalHandler)

console = Console()

defaultHeader()
if platform.version().find("10") != 0:
  console.print("当前系统版本[red1]不满足[/red1]所需的要求，请升级你的 Windows 版本。")
  console.print("此项目不支持[red1]Windows 7 及以下版本[/red1]。")
  console.input("按下 [plum1]Enter[/plum1] 退出[white]...[/white]")
  sys.exit(1)
console.log(f"Windows 版本[green1]有效[/green1], 当前版本：[cornflower_blue]{platform.version()}[/cornflower_blue]")
update_result = checkUpdate()
if update_result:
  import function.variable
  function.variable.UpdateAvailable = True
  function.variable.UpdateInfo = update_result
sleep(2)

mainMenuText = """
-  安装清风服

   1.1 正常安装服务器 (检查是否重复，在原文件上新增服务器)

   1.2 强制安装服务器 (不检查是否重复，直接删除原文件)

-  调整 Among Us 配置版本
   
   2.1 使用老版本配置 (修复旧版游戏)

   2.2 使用新版本配置

3. 关于工具箱

4. 退出
"""
while True:
  generalMainMenu(mainMenuText, "主菜单")
  commandNumber = console.input("请输入要执行的命令编号：").strip()
  if commandNumber == "1" or commandNumber == "1.1":
    installServer(merge=True)
  elif commandNumber == "1.2":
    installServer(merge=False)
  elif commandNumber == "2" or commandNumber == "2.1":
    fixAmongUs()
  elif commandNumber == "2.2":
    updateAmongUs()
  elif commandNumber == "3":
    aboutPage()
  elif commandNumber == "4":
    sys.exit(0)
  else:
    console.print("[red1]输入的命令编号无效，请重新输入。[/red1]")
    sleep(1)
from rich.box import DOUBLE_EDGE
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

# 这个地方不用绝对路径会报错循环引用然后死掉，第一次遇到还挺意外
from function.variable import Version, ToolTitle
from function.updateCheck import updateNotification

console = Console()

def cls():
  """仿制批处理的 cls 清屏操作"""
  print("\033c", end="")

def defaultHeader(title=ToolTitle,version=Version):
  """打印默认工具箱标题"""
  cls()
  console.print(Panel(Text(title, style="bold", justify="left"), subtitle=version, box=DOUBLE_EDGE))
  # alpha 版本检查
  if Version.find("alpha") != -1:
    br()
    console.print(Panel(Text("\n当前版本为[orange1]开发版本[/orange1]，可能存在较多问题。\n", style="bold", justify="center"),title="警告"))
  # 显示更新提示（如果有）
  import function.variable
  if function.variable.UpdateAvailable and function.variable.UpdateInfo:
    br()
    updateNotification(function.variable.UpdateInfo)


def br():
  """(名称)HTML 风格的换行"""
  console.print("\n")

def generalMainMenu(pageText, title):
    """打印通用主菜单"""
    defaultHeader()
    br()
    console.print(Panel(Text(pageText, style="bold"), title=Text(title, style="bold")))
    br()
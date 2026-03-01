import ctypes
from rich.text import Text
from rich.panel import Panel
from rich.box import DOUBLE_EDGE
from rich.console import Console

from function.updateCheck import updateNotification
from function.variable import Version, VersionType, ToolTitle

console = Console()

def cls():
  """仿制批处理的 cls 清屏操作"""
  print("\033c", end="")

def defaultHeader(title=ToolTitle, version=Version, isMainMenu=False):
    """打印默认工具箱标题"""
    cls()
    console.print(Panel(Text(title, style="bold", justify="left"), subtitle=version, box=DOUBLE_EDGE))
    # alpha 版本检查
    if VersionType == "alpha" or VersionType == "beta":
        br()
        console.print(Panel(Text("\n当前版本为开发版本，可能存在较多问题。\n", justify="center"), title="警告", style="yellow1"))
    # 显示更新提示（如果有）
    import function.variable
    if function.variable.UpdateAvailable and function.variable.UpdateInfo:
        br()
        updateNotification(function.variable.UpdateInfo)
    
    # （仅 isMainMenu = True 显示）检查窗口是否最大化
    if isMainMenu:
        hwnd = ctypes.windll.user32.FindWindowW(None, "清风 Among Us 工具箱")
        if hwnd:
            class RECT(ctypes.Structure):
                _fields_ = [("left", ctypes.c_long), ("top", ctypes.c_long), ("right", ctypes.c_long), ("bottom", ctypes.c_long)]
            rect = RECT()
            ctypes.windll.user32.GetWindowRect(hwnd, ctypes.byref(rect))
        windowWidth = rect.right - rect.left
        screenWidth = ctypes.windll.user32.GetSystemMetrics(0)
        if windowWidth <= screenWidth:
            br()
            console.print(Panel(Text("\n当前窗口似乎并未最大化显示，这可能会影响显示效果。\n", justify="center"), title="警告", style="yellow1"))

def br():
  """(名称)HTML 风格的换行"""
  console.print("\n")

def generalMainMenu(pageText, title):
    """打印通用主菜单"""
    defaultHeader(isMainMenu=bool(title=="主菜单"))
    br()
    console.print(Panel(Text(pageText, style="bold"), title=Text(title, style="bold")))
    br()
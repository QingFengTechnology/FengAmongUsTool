import ctypes
import requests

from time import time
from rich.text import Text
from rich.panel import Panel
from rich.box import DOUBLE_EDGE
from rich.console import Console

from function.updateCheck import updateNotification
from function.variable import Version, VersionType, ToolTitle, DownloadSources

console = Console()

def testLatency(base_url, timeout=3):
    """测试下载源延迟"""
    try:
        start_time = time()
        response = requests.head(base_url, timeout=timeout, allow_redirects=True)
        end_time = time()
        if response.status_code < 500:
            latency = (end_time - start_time) * 1000
            return latency
        else:
            return float('inf')
    except:
        return float('inf')

def selectBestSource():
    """选择延迟最低的下载源"""
    import function.variable
    results = []
    for source in DownloadSources:
        console.log(f"测试[cornflower_blue]{source['name']}[/cornflower_blue]延迟[white]...[/white]")
        latency = testLatency(source['base_url'])
        if latency == float('inf'):
            console.log(f"[orange1]未能连接[/orange1]到[cornflower_blue]{source['name']}[/cornflower_blue]。")
        else:
            console.log(f"[green1]成功连接[/green1]到[cornflower_blue]{source['name']}[/cornflower_blue]延迟: [cornflower_blue]{latency:.2f}ms[/cornflower_blue]")
        results.append((source, latency))
    
    available_sources = [(s, l) for s, l in results if l != float('inf')]
    
    if not available_sources:
        console.log("[red1]所有下载源均无法连接[/red1]。")
        function.variable.BestDownloadSource = None
        return False
    
    best_source = min(available_sources, key=lambda x: x[1])[0]
    console.log(f"已选择[cornflower_blue]{best_source['name']}[/cornflower_blue]为下载源。")
    function.variable.BestDownloadSource = best_source

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
    
    # 仅在主菜单显示
    if isMainMenu:
        # 窗口最大化检测
        hwnd = ctypes.windll.kernel32.GetConsoleWindow()
        if hwnd:
            class RECT(ctypes.Structure):
                _fields_ = [("left", ctypes.c_long), ("top", ctypes.c_long), ("right", ctypes.c_long), ("bottom", ctypes.c_long)]
            rect = RECT()
            ctypes.windll.user32.GetWindowRect(hwnd, ctypes.byref(rect))
            windowWidth = rect.right - rect.left
            screenWidth = ctypes.windll.user32.GetSystemMetrics(0)
            if windowWidth < screenWidth:
                br()
                console.print(Panel(Text("\n当前窗口似乎并未最大化显示，这可能会影响显示效果。\n", justify="center"), title="警告", style="yellow1"))
        
        # 下载源无效警告
        if not function.variable.BestDownloadSource:
            br()
            console.print(Panel(Text("\n无法连接到可用的源服务器，这将导致工具箱绝大部分功能不可用。\n", justify="center"), title="未连接至可用源服务器", style="red1"))

def br():
  """(名称)HTML 风格的换行"""
  console.print("\n")

def generalMainMenu(pageText, title):
    """打印通用主菜单"""
    defaultHeader(isMainMenu=bool(title=="主菜单"))
    br()
    console.print(Panel(Text(pageText, style="bold"), title=Text(title, style="bold")))
    br()
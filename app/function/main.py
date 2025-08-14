from rich.console import Console
from rich.panel import Panel
from rich.text import Text
import os
import stat
import random
import requests
from time import time

# 这个地方不用绝对路径会报错循环引用然后死掉，第一次遇到还挺意外
from function.about import Version

console = Console()

def cls():
  """仿制批处理的 cls 清屏操作"""
  print("\033c", end="")

def defaultHeader(title="\n清风工具箱\n",version=Version):
  """打印默认工具箱标题"""
  cls()
  console.print(Panel(Text(title, style="bold", justify="center"), subtitle=version))
  # alpha 版本检查
  if Version.find("alpha") != -1:
    br()
    console.print(Panel(Text("\n当前版本为开发版本，可能存在较多问题。\n", style="bold", justify="center"),title="警告"))

def br():
  """(名称)HTML 风格的换行"""
  console.print("\n")

def generalMainMenu(pageText, title):
    """打印通用主菜单"""
    defaultHeader()
    br()
    console.print(Panel(Text(pageText, style="bold"), title=Text(title, style="bold")))
    br()

def setFileWritable(regionFilePath):
    """设置私服文件为可写状态"""
    if os.path.exists(regionFilePath):
        try:
            os.chmod(regionFilePath, stat.S_IWRITE)
            console.log(f"已移除私服文件只读属性。")
            return True
        except Exception as e:
            console.log(f"[bold red]未能成功移除私服文件只读属性: {str(e)}[/bold red]")
    return False

def getGameFilePath(fileName):
    """获取游戏文件的完整路径"""
    appdataPath = os.environ['APPDATA']
    targetDir = os.path.join(os.path.dirname(appdataPath), 'LocalLow', 'Innersloth', 'Among Us')
    return os.path.join(targetDir, fileName)

def selectBestServer(ServerSources):
    """选择延迟最低的下载源"""
    results = []

    random.shuffle(ServerSources)
    
    for server in ServerSources:
        console.log(f"测试 {server['name']}...")
        latency = testServerLatency(server['url'])
        if latency == float('inf'):
            console.log(f"[bold yellow]{server['name']} 不可用[/bold yellow]")
        else:
            console.log(f"[bold green]{server['name']} 延迟: {latency:.2f}ms[/bold green]")
        results.append((server, latency))
    
    available_servers = [(s, l) for s, l in results if l != float('inf')]
    
    if not available_servers:
        console.log("[bold red]所有下载源均无法连接[/bold red]")
        return None
    
    best_server, best_latency = min(available_servers, key=lambda x: x[1])
    console.log(f"[bold blue]已选择最快下载源: {best_server['name']} (延迟: {best_latency:.2f}ms)[/bold blue]")
    return best_server['url']

def testServerLatency(url, timeout=5):
    """测试下载源延迟"""
    try:
        start_time = time()
        response = requests.head(url, timeout=timeout, allow_redirects=True)
        if response.status_code == 200:
            end_time = time()
            latency = (end_time - start_time) * 1000
            return latency
        else:
            return float('inf')
    except:
        return float('inf')
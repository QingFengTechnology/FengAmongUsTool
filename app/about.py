from time import sleep

from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from function.main import printHeader, br
from function.about import Version

console = Console()

def aboutPage(pageText):
    """打印关于页面"""
    printHeader()
    br()
    console.print(Panel(Text(pageText, style="bold"), title=Text("关于工具箱", style="bold")))
    br()

pageText = f"""

版本：{Version}

许可：GPL-3.0

反馈：https://github.com/QingFengTechnology/FengAmongUsTool/issues

源码：https://github.com/QingFengTechnology/FengAmongUsTool

作者：https://github.com/QingFeng-awa

赞助：https://docs.qingfengawa.top/Donate.html

"""

def run():
  aboutPage(pageText)
  sleep(1)
  console.input("按 Enter 返回主菜单...")
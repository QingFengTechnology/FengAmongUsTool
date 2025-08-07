from time import sleep
from rich.console import Console

from function.main import generalMainMenu
from function.about import Version

console = Console()

pageText = f"""

版本：{Version}

许可：GPL-3.0

反馈：https://github.com/QingFengTechnology/FengAmongUsTool/issues

源码：https://github.com/QingFengTechnology/FengAmongUsTool

作者：https://github.com/QingFeng-awa

赞助：https://docs.qingfengawa.top/Donate.html

"""

def run():
  generalMainMenu(pageText, "关于工具箱")
  sleep(1)
  console.input("按 Enter 返回主菜单...")
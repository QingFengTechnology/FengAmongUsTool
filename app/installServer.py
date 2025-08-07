from time import sleep
import requests
import os
import shutil
import stat

from rich.console import Console
from rich.syntax import Syntax
from rich.panel import Panel
from rich.text import Text

from function.main import defaultHeader, br, generalMainMenu

console = Console()

MenuTitle = "清风服安装器"
MenuMainText = """
请选择下载源：
    
1. 清风 API (中国大陆可用区)
    
2. Github
"""

def getRegionInfoPath():
    """获取私服文件的完整路径"""
    appdata_path = os.environ['APPDATA']
    target_dir = os.path.join(os.path.dirname(appdata_path), 'LocalLow', 'Innersloth', 'Among Us')
    return os.path.join(target_dir, 'regionInfo.json')

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

def run():
    """工具箱主要模块：安装清风服"""
    regionInfoPath = getRegionInfoPath()
    regionInfoBakPath = regionInfoPath + '.bak'
    success = False
    while True:
        generalMainMenu(MenuMainText, MenuTitle)
        sleep(1)
        downloadServerRegion = input("请输入要选择的下载源编号：").strip()
        if downloadServerRegion == "1":
            DownloadServerURL = "https://feng-public.cn-nb1.rains3.com/regionInfo.json"
            break
        elif downloadServerRegion == "2":
            DownloadServerURL = "https://raw.githubusercontent.com/QingFengTechnology/FengAmongUsTool/refs/heads/v2/regionInfo.json"
            break
        else:
            console.print("[bold red]输入的下载源编号无效，请重新输入。[/bold red]")
            sleep(1)
    
    try:
        defaultHeader()
        br()
        with console.status("准备下载清风服文件...") as status:
            sleep(1)
            status.update("备份已有文件...")
            sleep(1)
            try:
                if os.path.exists(regionInfoPath):
                    setFileWritable(regionInfoPath)
                    if os.path.exists(regionInfoBakPath):
                        setFileWritable(regionInfoBakPath)
                    shutil.copy2(regionInfoPath, regionInfoBakPath)
                    console.log(f"原始私服文件已备份至 {regionInfoBakPath}")
                else:
                    console.log("未找到原始私服文件，跳过备份")
            except Exception as e:
                console.log(f"[bold red]备份原始私服文件失败[/bold red]: {str(e)}")
            status.update("删除原有文件...")
            sleep(1)
            try:
                if os.path.exists(regionInfoPath):
                    setFileWritable(regionInfoPath)
                    os.remove(regionInfoPath)
                    console.log("原始私服文件已删除")
                else:
                    console.log("原始私服文件不存在，跳过删除")
            except Exception as e:
                console.log(f"[bold red]删除原始文件失败[/bold red]: {str(e)}")
                try:
                    status.update("强制删除原始文件...")
                    os.chmod(regionInfoPath, stat.S_IWRITE | stat.S_IREAD)
                    os.remove(regionInfoPath)
                    console.log("原始私服文件强制删除成功")
                except:
                    console.log("[bold red]强制删除失败。[/bold red]")
            status.update("下载文件...")
            sleep(1)
            try:
                response = requests.get(DownloadServerURL)
                response.raise_for_status()
                ServerFileResponse = response.content
                console.log(f"文件下载成功，大小: {len(ServerFileResponse)}B")
            except Exception as e:
                console.log(f"[bold red]文件下载失败[/bold red]: {str(e)}")
                if os.path.exists(regionInfoBakPath):
                    try:
                        if os.path.exists(regionInfoPath):
                            setFileWritable(regionInfoPath)
                        shutil.copy2(regionInfoBakPath, regionInfoPath)
                        setFileWritable(regionInfoPath)
                        console.log("已从备份恢复原始文件")
                    except Exception as restoreError:
                        console.log(f"[bold red]恢复备份失败:[/bold red] {str(restoreError)}")
                raise
            status.update("校验文件...")
            sleep(1)
            try:
                if "清风服".encode('utf-8') not in ServerFileResponse:
                    raise ValueError("下载的私服文件缺少必备字符，疑似下载文件不正确")
                console.log("文件校验成功")
            except Exception as e:
                console.log(f"[bold red]文件校验失败[/bold red]: {str(e)}")
                if os.path.exists(regionInfoBakPath):
                    try:
                        if os.path.exists(regionInfoPath):
                            setFileWritable(regionInfoPath)
                        shutil.copy2(regionInfoBakPath, regionInfoPath)
                        setFileWritable(regionInfoPath)
                        console.log("已从备份恢复原始文件")
                    except Exception as restoreError:
                        console.log(f"[bold red]恢复备份失败[/bold red]: {str(restoreError)}")
                console.print("[bold red]发生了错误[/bold red]。")
                console.print("下载的文件存在问题，已回滚更改。")
                console.print("下方为工具箱获取到的 JSON 文件内容:")
                try:
                    content = ServerFileResponse.decode('utf-8', errors='replace')
                    console.print(Syntax(content, "json", theme="github-dark", line_numbers=False))
                except:
                    console.print(f"无法解码内容: {ServerFileResponse[:100].hex()}")
                raise
            status.update("导入文件...")
            sleep(1)
            try:
                os.makedirs(os.path.dirname(regionInfoPath), exist_ok=True)
                if os.path.exists(regionInfoPath):
                    setFileWritable(regionInfoPath)
                with open(regionInfoPath, 'wb') as f:
                    f.write(ServerFileResponse)
                console.log(f"文件保存成功")
                if os.path.exists(regionInfoBakPath):
                    try:
                        setFileWritable(regionInfoBakPath)
                        os.remove(regionInfoBakPath)
                    except Exception as e:
                        console.log(f"[bold yellow]清理备份文件失败[/bold yellow]: {str(e)}")
                success = True
                
            except Exception as e:
                console.log(f"[bold red]导入失败[/bold red]: {str(e)}")
                if os.path.exists(regionInfoBakPath):
                    try:
                        if os.path.exists(regionInfoPath):
                            setFileWritable(regionInfoPath) 
                        shutil.copy2(regionInfoBakPath, regionInfoPath)
                        setFileWritable(regionInfoPath)
                        console.log("已从备份恢复原始文件")
                    except Exception as restoreError:
                        console.log(f"[bold red]恢复备份失败[/bold red]: {str(restoreError)}")
                raise
            status.update("请稍后……")
            sleep(3)
    
    except Exception as e:
        console.log(f"[bold red]安装过程中发生错误[/bold red]: {str(e)}")
        success = False
        console.print("\n如果你确认这是工具箱问题，请截图相关信息并通过 GitHub Issue 报告问题。\n")
        console.input("按 Enter 继续...")
    if success:
        finalMessage = "\n服务器安装完成。\n"
        generalMainMenu(finalMessage, MenuTitle)
    else:
        finalMessage = "\n服务器安装失败，请查看日志以了解详情。\n"
        console.print(Panel(Text(finalMessage, style="bold red"), title=Text(MenuTitle, style="bold")))
    
    console.input("按 Enter 返回主菜单...")
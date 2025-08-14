from time import sleep, time
import os
import shutil
import stat
import random
import requests
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.syntax import Syntax

from function.main import generalMainMenu, defaultHeader, br

console = Console()

MenuTitle = "修复旧版 Among Us"
MenuMainText = """
此操作将重新下载 Among Us 配置文件来实现修复效果。

这可能会导致极少数模组出现存档丢失问题。
"""

# 下载源列表
SettingsSources = [
    {
        "name": "清风 API (全球可用区)",
        "url": "https://cn.api.qingfengawa.top/old.settings.amongus"
    },
    {
        "name": "Github",
        "url": "https://raw.githubusercontent.com/QingFengTechnology/FengAmongUsTool/refs/heads/v3/asset/old.settings.amongus"
    }
]

def getSettingsFilePath():
    """获取游戏设置文件的完整路径"""
    appdata_path = os.environ['APPDATA']
    target_dir = os.path.join(os.path.dirname(appdata_path), 'LocalLow', 'Innersloth', 'Among Us')
    return os.path.join(target_dir, 'settings.amogus')


def setFileWritable(filePath):
    """设置文件为可写状态"""
    if os.path.exists(filePath):
        try:
            os.chmod(filePath, stat.S_IWRITE)
            console.log(f"已移除文件只读属性。")
            return True
        except Exception as e:
            console.log(f"[bold red]未能成功移除文件只读属性: {str(e)}[/bold red]")
    return False

def testSettingsLatency(url, timeout=5):
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

def selectBestSettingsSource():
    """选择延迟最低的下载源"""
    results = []

    random.shuffle(SettingsSources)
    
    for source in SettingsSources:
        console.log(f"测试 {source['name']}...")
        latency = testSettingsLatency(source['url'])
        if latency == float('inf'):
            console.log(f"[bold yellow]{source['name']} 不可用[/bold yellow]")
        else:
            console.log(f"[bold green]{source['name']} 延迟: {latency:.2f}ms[/bold green]")
        results.append((source, latency))
    
    available_sources = [(s, l) for s, l in results if l != float('inf')]
    
    if not available_sources:
        console.log("[bold red]所有下载源均无法连接[/bold red]")
        return None
    
    best_source, best_latency = min(available_sources, key=lambda x: x[1])
    console.log(f"[bold blue]已选择最快下载源: {best_source['name']} (延迟: {best_latency:.2f}ms)[/bold blue]")
    return best_source['url']

def run():
    """工具箱主模块：修复旧版 Among Us"""
    settingsFilePath = getSettingsFilePath()
    settingsFileBakPath = settingsFilePath + '.bak'
    success = False

    while True:
        generalMainMenu(MenuMainText, MenuTitle)
        sleep(1)
        downloadFileConfirm = console.input("你确定要继续吗? (Y / N)").strip()
        if downloadFileConfirm.upper() == "Y":
            break
        elif downloadFileConfirm.upper() == "N":
            generalMainMenu("\n操作已取消，即将返回主菜单...\n", MenuTitle)
            sleep(3)
            return
        else:
            console.print("[bold red]输入无效，请重新输入。[/bold red]")
            sleep(1)

    try:
        defaultHeader("修复旧版游戏")
        br()
        with console.status("准备下载设置文件...") as status:
            sleep(1)
            status.update("检测下载源延迟...")
            sleep(1)
            DownloadSettingsURL = selectBestSettingsSource()
            if not DownloadSettingsURL:
                status.stop()
                console.print("[bold red]未能连接至可用下载服务器。[/bold red]")
                console.input("按 Enter 返回主菜单...")
                return
            status.update("备份已有文件...")
            sleep(1)
            try:
                if os.path.exists(settingsFilePath):
                    setFileWritable(settingsFilePath)
                    if os.path.exists(settingsFileBakPath):
                        setFileWritable(settingsFileBakPath)
                    shutil.copy2(settingsFilePath, settingsFileBakPath)
                    console.log(f"[bold green]原始设置文件已备份至 {settingsFileBakPath}[/bold green]")
                else:
                    console.log("未找到原始设置文件，跳过备份")
            except Exception as e:
                console.log(f"[bold red]备份原始设置文件失败[/bold red]: {str(e)}")
            status.update("删除原有文件...")
            sleep(1)
            try:
                if os.path.exists(settingsFilePath):
                    setFileWritable(settingsFilePath)
                    os.remove(settingsFilePath)
                    console.log("[bold green]原始设置文件已删除[/bold green]")
                else:
                    console.log("原始设置文件不存在，跳过删除")
            except Exception as e:
                console.log(f"[bold red]删除原始文件失败[/bold red]: {str(e)}")
                try:
                    status.update("强制删除原始文件...")
                    os.chmod(settingsFilePath, stat.S_IWRITE | stat.S_IREAD)
                    os.remove(settingsFilePath)
                    console.log("[bold green]原始设置文件强制删除成功[/bold green]")
                except:
                    console.log("[bold red]强制删除失败[/bold red]")
            status.update("下载文件...")
            sleep(1)
            try:
                response = requests.get(DownloadSettingsURL)
                response.raise_for_status()
                SettingsFileResponse = response.content
                console.log(f"[bold green]文件下载成功，大小: {len(SettingsFileResponse)}B[/bold green]")
            except Exception as e:
                console.log(f"[bold red]文件下载失败[/bold red]: {str(e)}")
                if os.path.exists(settingsFileBakPath):
                    try:
                        if os.path.exists(settingsFilePath):
                            setFileWritable(settingsFilePath)
                        shutil.copy2(settingsFileBakPath, settingsFilePath)
                        setFileWritable(settingsFilePath)
                        console.log("[bold green]已从备份恢复原始文件[/bold green]")
                    except Exception as restoreError:
                        console.log(f"[bold red]恢复备份失败:[/bold red] {str(restoreError)}")
                raise
            status.update("校验文件...")
            sleep(1)
            try:
                if "currentLanguage".encode('utf-8') not in SettingsFileResponse:
                    raise ValueError("下载的设置文件缺少必备字符，疑似下载文件不正确。")
                console.log("[bold green]文件校验成功[/bold green]")
            except Exception as e:
                console.log(f"[bold red]文件校验失败[/bold red]: {str(e)}")
                if os.path.exists(settingsFileBakPath):
                    try:
                        if os.path.exists(settingsFilePath):
                            setFileWritable(settingsFilePath)
                        shutil.copy2(settingsFileBakPath, settingsFilePath)
                        setFileWritable(settingsFilePath)
                        console.log("已从备份恢复原始文件")
                    except Exception as restoreError:
                        console.log(f"[bold red]恢复备份失败[/bold red]: {str(restoreError)}")
                console.print("[bold red]发生了错误[/bold red]。")
                console.print("[bold red]下载的文件存在问题，已回滚更改。[/bold red]")
                console.print("下方为工具箱获取到的文件内容:")
                try:
                    content = SettingsFileResponse.decode('utf-8', errors='replace')
                    console.print(Syntax(content, "text", theme="github-dark", line_numbers=False))
                except:
                    console.print(f"[bold red]解码内容失败: {SettingsFileResponse[:100].hex()}[/bold red]")
                raise
            status.update("导入文件...")
            sleep(1)
            try:
                os.makedirs(os.path.dirname(settingsFilePath), exist_ok=True)
                if os.path.exists(settingsFilePath):
                    setFileWritable(settingsFilePath)
                with open(settingsFilePath, 'wb') as f:
                    f.write(SettingsFileResponse)
                console.log(f"[bold green]文件导入成功[/bold green]")
                if os.path.exists(settingsFileBakPath):
                    try:
                        setFileWritable(settingsFileBakPath)
                        os.remove(settingsFileBakPath)
                    except Exception as e:
                        console.log(f"[bold yellow]清理备份文件失败[/bold yellow]: {str(e)}")
                success = True
                
            except Exception as e:
                console.log(f"[bold red]导入失败[/bold red]: {str(e)}")
                if os.path.exists(settingsFileBakPath):
                    try:
                        if os.path.exists(settingsFilePath):
                            setFileWritable(settingsFilePath) 
                        shutil.copy2(settingsFileBakPath, settingsFilePath)
                        setFileWritable(settingsFilePath)
                        console.log("[bold green]已从备份恢复原始文件[/bold green]")
                    except Exception as restoreError:
                        console.log(f"[bold red]恢复备份失败[/bold red]: {str(restoreError)}")
                raise
            status.update("请稍后……")
            sleep(3)

    except Exception as e:
        console.log(f"[bold red]修复过程中发生错误[/bold red]: {str(e)}")
        success = False
        console.print("\n如果你确认这是工具箱问题，请截图相关信息并通过 GitHub Issue 报告问题。\n")
        console.input("按 Enter 返回主菜单...")
        return

    if success:
        finalMessage = "\n修复完成。\n"
        generalMainMenu(finalMessage, MenuTitle)
    else:
        # 应当删除，但保不齐会有什么问题，我不想动
        # 要删就应该顺便清理下整体错误处理的代码
        finalMessage = "\n修复失败，请查看日志以了解详情。\n"
        console.print(Panel(Text(finalMessage, style="bold red"), title=Text(MenuTitle, style="bold")))
    
    console.input("按 Enter 返回主菜单...")
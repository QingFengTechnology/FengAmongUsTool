import os
import stat
import shutil
import requests

from rich.text import Text
from rich.panel import Panel
from time import sleep
from rich.syntax import Syntax
from rich.console import Console

from function.main import generalMainMenu, defaultHeader, br
from function.variable import DownloadSources, BestDownloadSource

console = Console()

CONFIG_TYPES = {
    "old": {
        "title": "修复旧版 Among Us",
        "menu_text": """
此操作将重新下载 Among Us 配置文件来实现修复效果。

这可能会导致极少数模组出现存档丢失问题。
""",
        "filename": "old.settings.amogus",
        "header": "修复旧版游戏",
        "success_message": "修复完成。"
    },
    "new": {
        "title": "更换新版配置", 
        "menu_text": """
此操作将重新下载 Among Us 配置文件来实现修复效果。

这可能会导致极少数模组出现存档丢失问题。
""",
        "filename": "new.settings.amogus",
        "header": "更换新版配置",
        "success_message": "更换配置完成。"
    }
}

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
            console.log(f"[green1]成功移除[/green1]文件只读属性。")
            return True
        except Exception as e:
            console.log(f"[red1]未能移除[/red1]文件只读属性: {str(e)}")
    return False

def getBestSourceUrl(filename):
    """获取最佳下载源的完整URL"""
    import function.variable
    if function.variable.BestDownloadSource:
        return function.variable.BestDownloadSource['base_url'] + filename
    return DownloadSources[0]['base_url'] + filename

def download_and_install_config(config_type):
    """通用的下载和安装配置函数"""
    config = CONFIG_TYPES[config_type]
    settingsFilePath = getSettingsFilePath()
    settingsFileBakPath = settingsFilePath + '.bak'
    success = False

    while True:
        generalMainMenu(config["menu_text"], config["title"])
        downloadFileConfirm = console.input("你确定要继续吗？( [green1]Y[/green1] [white]/[/white] [red1]N[/red1] )").strip()
        if downloadFileConfirm.upper() == "Y":
            break
        elif downloadFileConfirm.upper() == "N":
            generalMainMenu("\n操作已取消，即将返回主菜单...\n", config["title"])
            return
        else:
            console.print("[red1]输入无效[/red1]，请重新输入。")
            sleep(1)

    try:
        defaultHeader()
        br()
        with console.status("准备下载设置文件...") as status:
            DownloadSettingsURL = getBestSourceUrl(config["filename"])
            status.update("备份已有文件...")
            try:
                if os.path.exists(settingsFilePath):
                    setFileWritable(settingsFilePath)
                    if os.path.exists(settingsFileBakPath):
                        setFileWritable(settingsFileBakPath)
                    shutil.copy2(settingsFilePath, settingsFileBakPath)
                    console.log(f"[green1]成功备份[/green1]原始设置文件。")
                else:
                    console.log("[orange1]未找到[/orange1]原始设置文件，跳过备份。")
            except Exception as e:
                console.log(f"[red1]未能备份[/red1]原始设置文件: {str(e)}")
            status.update("删除原有文件...")
            try:
                if os.path.exists(settingsFilePath):
                    setFileWritable(settingsFilePath)
                    os.remove(settingsFilePath)
                    console.log("[green1]成功删除[/green1]原始设置文件。")
                else:
                    console.log("原始设置文件[orange1]不存在[/orange1]，跳过删除。")
            except Exception as e:
                console.log(f"[orange1]未能删除[/orange1]原始文件: {str(e)}")
                try:
                    status.update("强制删除原始文件...")
                    os.chmod(settingsFilePath, stat.S_IWRITE | stat.S_IREAD)
                    os.remove(settingsFilePath)
                    console.log("[green1]成功强制删除[/green1]原始设置文件。")
                except:
                    console.log("[orange1]未能强制删除[/orange1]原始设置文件，将直接尝试下载并覆盖。")
            status.update("下载文件...")
            try:
                response = requests.get(DownloadSettingsURL)
                response.raise_for_status()
                SettingsFileResponse = response.content
                console.log(f"[green1]成功下载[/green1]设置文件，大小: [cornflower_blue]{len(SettingsFileResponse)}B[/cornflower_blue]。")
            except Exception as e:
                console.log(f"[red1]未能下载[/red1]文件下载: {str(e)}")
                if os.path.exists(settingsFileBakPath):
                    try:
                        if os.path.exists(settingsFilePath):
                            setFileWritable(settingsFilePath)
                        shutil.copy2(settingsFileBakPath, settingsFilePath)
                        setFileWritable(settingsFilePath)
                        console.log("[green1]已从备份恢复[/green1]原始文件。")
                    except Exception as restoreError:
                        console.log(f"[red1]未能从备份恢复[/red1]原始文件: {str(restoreError)}")
                raise
            status.update("校验文件...")
            try:
                if "currentLanguage".encode('utf-8') not in SettingsFileResponse:
                    raise ValueError("下载的设置文件缺少必备字符，疑似下载文件不正确。")
                console.log("[green1]成功校验[/green1]文件正确性。")
            except Exception as e:
                console.log(f"[red1]未能校验[/red1]文件: {str(e)}")
                if os.path.exists(settingsFileBakPath):
                    try:
                        if os.path.exists(settingsFilePath):
                            setFileWritable(settingsFilePath)
                        shutil.copy2(settingsFileBakPath, settingsFilePath)
                        setFileWritable(settingsFilePath)
                        console.log("[green1]已从备份恢复[/green1]原始文件。")
                    except Exception as restoreError:
                        console.log(f"[red1]未能从备份恢复[/red1]原始文件: {str(restoreError)}")
                console.print("下方为工具箱获取到的文件内容:")
                try:
                    content = SettingsFileResponse.decode('utf-8', errors='replace')
                    console.print(Syntax(content, "text", theme="github-dark", line_numbers=False))
                except:
                    console.print(f"[red1]未能解码内容[/red1]: {SettingsFileResponse[:100].hex()}")
                raise
            status.update("导入文件...")
            try:
                os.makedirs(os.path.dirname(settingsFilePath), exist_ok=True)
                if os.path.exists(settingsFilePath):
                    setFileWritable(settingsFilePath)
                with open(settingsFilePath, 'wb') as f:
                    f.write(SettingsFileResponse)
                console.log(f"[green1]成功导入[/green1]文件。")
                if os.path.exists(settingsFileBakPath):
                    try:
                        setFileWritable(settingsFileBakPath)
                        os.remove(settingsFileBakPath)
                    except Exception as e:
                        console.log(f"[orange1]未能清理[/orange1]备份文件: {str(e)}")
                success = True
                
            except Exception as e:
                console.log(f"[red1]未能导入[/red1]文件: {str(e)}")
                if os.path.exists(settingsFileBakPath):
                    try:
                        if os.path.exists(settingsFilePath):
                            setFileWritable(settingsFilePath) 
                        shutil.copy2(settingsFileBakPath, settingsFilePath)
                        setFileWritable(settingsFilePath)
                        console.log("[green1]成功从备份恢复[/green1]原始文件。")
                    except Exception as restoreError:
                        console.log(f"[red1]未能从备份恢复[/red1]原始文件: {str(restoreError)}")
                raise
            status.update("请稍后...")

    except Exception as e:
        console.log(f"[red1]{config['header']}过程中发生意外错误[/red1]: {str(e)}")
        success = False
        console.print("\n如果你确认这是工具箱问题，请截图相关信息并通过 GitHub Issue 报告问题。\n")
        console.input("按 [plum1]Enter[/plum1] 返回主菜单...")
        return

    if success:
        finalMessage = f"\n{config['success_message']}\n"
        generalMainMenu(finalMessage, config["title"])
    else:
        finalMessage = f"\n[red1]{config['header']}失败[/red1]，请查看日志以了解详情。\n"
        console.print(Panel(Text(finalMessage, style="red1"), title=Text(config["title"], style="bold")))
    
    console.input("按 [plum1]Enter[/plum1] 返回主菜单。")

def fixAmongUsSetting():
    """工具箱主模块：修复旧版 Among Us"""
    download_and_install_config("old")

def updateAmongUsSetting():
    """工具箱主模块：配置新版 Among Us"""
    download_and_install_config("new")
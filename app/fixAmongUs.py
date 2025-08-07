from time import sleep
import os
import shutil
import stat
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from function.main import generalMainMenu, defaultHeader, br

console = Console()

MenuTitle = "修复旧版 Among Us"
MenuMainText = """
此操作将移除 Among Us 配置文件来实现修复效果。

这可能会导致极少数模组出现存档丢失问题。
"""

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

def run():
    """工具箱主模块：修复旧版 Among Us"""
    settingsFilePath = getSettingsFilePath()
    settingsFileBakPath = settingsFilePath + '.bak'
    success = False

    while True:
        generalMainMenu(MenuMainText, MenuTitle)
        sleep(1)
        deleteFileConfirm = console.input("你确定要继续吗? (Y / N)").strip()
        if deleteFileConfirm.upper() == "Y":
            break
        elif deleteFileConfirm.upper() == "N":
            generalMainMenu("\n操作已取消，即将返回主菜单...\n", MenuTitle)
            sleep(3)
            return
        else:
            console.print("[bold red]输入无效，请重新输入。[/bold red]")
            sleep(1)

    try:
        defaultHeader("修复旧版游戏")
        br()
        with console.status("准备修复游戏...") as status:
            sleep(1)
            status.update("备份已有文件...")
            sleep(1)
            try:
                if os.path.exists(settingsFilePath):
                    setFileWritable(settingsFilePath)
                    if os.path.exists(settingsFileBakPath):
                        setFileWritable(settingsFileBakPath)
                    shutil.copy2(settingsFilePath, settingsFileBakPath)
                    console.log(f"设置文件已备份至 {settingsFileBakPath}")
                else:
                    console.log("未找到设置文件，跳过备份")
            except Exception as e:
                console.log(f"[bold red]备份设置文件失败[/bold red]: {str(e)}")

            status.update("删除设置文件...")
            sleep(1)
            try:
                if os.path.exists(settingsFilePath):
                    setFileWritable(settingsFilePath)
                    os.remove(settingsFilePath)
                    console.log("设置文件已删除，修复成功")
                    success = True
                else:
                    console.log("设置文件不存在，无需删除")
                    success = True
            except Exception as e:
                console.log(f"[bold red]删除设置文件失败[/bold red]: {str(e)}")
                try:
                    status.update("强制删除设置文件...")
                    os.chmod(settingsFilePath, stat.S_IWRITE | stat.S_IREAD)
                    os.remove(settingsFilePath)
                    console.log("设置文件强制删除成功")
                    success = True
                except Exception as force_delete_error:
                    console.log(f"[bold red]强制删除失败: {str(force_delete_error)}[/bold red]")
                    success = False

            status.update("请稍后……")
            sleep(3)

    except Exception as e:
        console.log(f"[bold red]修复过程中发生错误[/bold red]: {str(e)}")
        success = False
        console.print("\n如果你确认这是工具箱问题，请截图相关信息并通过 GitHub Issue 报告问题。\n")
        console.input("按 Enter 返回主菜单...")

    if success:
        finalMessage = "\n修复完成。\n"
        if os.path.exists(settingsFileBakPath):
            try:
                setFileWritable(settingsFileBakPath)
                os.remove(settingsFileBakPath)
                console.log("已清理备份文件")
            except Exception as e:
                console.log(f"[bold yellow]清理备份文件失败[/bold yellow]: {str(e)}")
    else:
        finalMessage = "\n修复失败，请查看日志以了解详情。\n"
        if os.path.exists(settingsFileBakPath):
            try:
                if os.path.exists(settingsFilePath):
                    setFileWritable(settingsFilePath)
                shutil.copy2(settingsFileBakPath, settingsFilePath)
                setFileWritable(settingsFilePath)
                console.log("已从备份恢复设置文件")
            except Exception as restoreError:
                console.log(f"[bold red]恢复备份失败:[/bold red] {str(restoreError)}")

    if success:
        generalMainMenu(finalMessage, MenuTitle)
    else:
        console.print(Panel(Text(finalMessage, style="bold red"), title=Text(MenuTitle, style="bold")))
    sleep(1)
    console.input("按 Enter 返回主菜单...")
from datetime import datetime

import requests
from function.variable import VersionType, versionDate
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

console = Console()

def checkUpdate():
    """检查工具箱更新，返回更新信息（如果有）"""
    import function.variable
    
    if not function.variable.BestDownloadSource:
        console.log("[orange1]未检测到可用的源服务器[/orange1]，跳过更新检查。")
        return None
    
    source = function.variable.BestDownloadSource
    
    try:
        console.log(f"尝试从[cornflower_blue]{source['name']}[/cornflower_blue]检查更新...")
        response = requests.get(source['base_url'] + 'version.json', timeout=3)
        response.raise_for_status()
        remote_version_data = response.json()
    
        version_hierarchy = ["alpha", "beta", "preview", "release"]
        current_type_index = version_hierarchy.index(VersionType)
        
        for i in range(current_type_index, len(version_hierarchy)):
            version_type = version_hierarchy[i]
            
            if version_type in remote_version_data and remote_version_data[version_type]["enable"]:
                remote_version_info = remote_version_data[version_type]
                
                remote_date = datetime.fromisoformat(remote_version_info["versionDate"].replace('Z', '+00:00')).date()
                if remote_date > versionDate:
                    console.log(f"[green1]发现新版本[/green1]更新可用！")
                    return remote_version_info
                else:
                    console.log(f"当前版本已是[green1]最新[/green1]。")
                    return None
            
            if version_type == "release":
                console.log(f"[orange1]尚无可用[/orange1]的 Release 版本，[yellow1]你的工具箱是官方版本吗？[/yellow1]")
                return None
        
        console.log(f"[orange1]未找到[/orange1]适用的版本类型，[yellow1]你的工具箱是官方版本吗？[/yellow1]")
        return None
        
    except requests.exceptions.RequestException as e:
        console.log(f"[orange1]无法连接[/orange1]到[cornflower_blue]{source['name']}[/cornflower_blue]: {e}")
        return None
    except Exception as e:
        console.log(f"从[cornflower_blue]{source['name']}[/cornflower_blue]检查更新时[orange1]出错[/orange1]: {e}")
        return None

def updateNotification(version_info):
    """显示更新通知"""
    console.print(Panel(
        Text(
            f"\n发现新版本：{version_info['version']} ({version_info['versionDate']})\n"
            f"请访问此链接下载最新版本：\n{version_info['releaseLink']}\n",
            justify="center"
        ),
        title="新版本可用",
        style="green1"
    ))
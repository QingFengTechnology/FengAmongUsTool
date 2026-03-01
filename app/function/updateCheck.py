import requests

from rich.text import Text
from rich.panel import Panel
from datetime import datetime
from rich.console import Console

from function.variable import VersionType, versionDate, DownloadSources

console = Console()

def checkUpdate():
    """检查工具箱更新，返回更新信息（如果有）"""
    # 按顺序尝试各个更新源
    for source in DownloadSources:
        try:
            console.log(f"尝试从[cornflower_blue]{source['name']}[/cornflower_blue]检查更新...")
            # 从远程获取版本信息
            response = requests.get(source['base_url'] + 'version.json', timeout=3)
            response.raise_for_status()
            remote_version_data = response.json()
        
            # 定义版本类型检查顺序
            version_hierarchy = ["alpha", "beta", "preview", "release"]
            
            # 获取当前版本类型在层级中的位置
            current_type_index = version_hierarchy.index(VersionType)
            
            # 按优先级顺序检查更新
            for i in range(current_type_index, len(version_hierarchy)):
                version_type = version_hierarchy[i]
                
                # 检查该版本类型是否启用
                if version_type in remote_version_data and remote_version_data[version_type]["enable"]:
                    remote_version_info = remote_version_data[version_type]
                    
                    # 比较日期
                    remote_date = datetime.fromisoformat(remote_version_info["versionDate"].replace('Z', '+00:00')).date()
                    if remote_date > versionDate:
                        # 发现新版本，返回更新信息
                        console.log(f"[green1]发现新版本[/green1]更新可用！")
                        return remote_version_info
                    else:
                        # 当前类型版本已是最新，停止检查
                        console.log(f"当前版本已是[green1]最新[/green1]。")
                        return None
                
                # 如果是release类型且未启用，停止检查
                if version_type == "release":
                    console.log(f"[orange1]尚无可用[/orange1]的 Release 版本，[yellow1]你的工具箱是官方版本吗？[/yellow1]")
                    return None
            
            console.log(f"[orange1]未找到[/orange1]适用的版本类型，[yellow1]你的工具箱是官方版本吗？[/yellow1]")
            return None
            
        except requests.exceptions.RequestException as e:
            console.log(f"[orange1]无法连接[/orange1]到[cornflower_blue]{source['name']}[/cornflower_blue]，尝试下一个源: {e}")
            continue  # 继续尝试下一个源
        except Exception as e:
            console.log(f"从[cornflower_blue]{source['name']}[/cornflower_blue]检查更新时[orange1]出错[/orange1]: {e}")
            continue  # 继续尝试下一个源
    
    # 所有源都尝试失败
    console.log("所有更新源[red1]均无法连接[/red1]，[orange1]跳过[/orange1]更新检查。")
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
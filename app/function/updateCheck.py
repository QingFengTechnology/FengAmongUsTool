import requests
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from function.variable import VersionType, versionDate

console = Console()

def checkUpdate():
    """检查工具箱更新，返回更新信息（如果有）"""
    try:
        # 从远程获取版本信息
        response = requests.get("https://api.qingfengawa.top/FengAmongUsTool-Asset/version.json", timeout=10)
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
                local_date = datetime.fromisoformat(versionDate.replace('Z', '+00:00'))
                remote_date = datetime.fromisoformat(remote_version_info["versionDate"].replace('Z', '+00:00'))
                
                if remote_date > local_date:
                    # 发现新版本，返回更新信息
                    return remote_version_info
                else:
                    # 当前类型版本已是最新，停止检查
                    return None
            
            # 如果是release类型且未启用，停止检查
            if version_type == "release":
                return None
        
        return None
        
    except requests.exceptions.RequestException as e:
        console.log(f"无法连接到更新服务器，跳过更新检查: {e}")
        return None
    except Exception as e:
        console.log(f"更新检查出错: {e}")
        return None

def updateNotification(version_info):
    """显示更新通知"""
    console.print(Panel(
        Text(
            f"\n发现新版本：{version_info['version']} ({version_info['versionDate']})\n"
            f"请访问以下链接下载最新版本：\n{version_info['releaseLink']}\n",
            style="bold",
            justify="center"
        ),
        title="新版本可用",
        style="green"
    ))
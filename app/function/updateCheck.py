import requests
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from function.variable import VersionType, versionDate

console = Console()

# 更新源列表
UpdateSources = [
    {
        "name": "清风 API (中华人民共和国可用区)",
        "url": "https://api.qingfengawa.top/FengAmongUsTool-Asset/version.json"
    },
    {
        "name": "Xget",
        "url": "https://xget.xi-xu.me/gh/QingFengTechnology/FengAmongUsTool-Asset/raw/refs/heads/main/version.json"
    },
    {
        "name": "Github",
        "url": "https://github.com/QingFengTechnology/FengAmongUsTool-Asset/raw/refs/heads/main/version.json"
    }
]

def checkUpdate():
    """检查工具箱更新，返回更新信息（如果有）"""
    # 按顺序尝试各个更新源
    for source in UpdateSources:
        try:
            console.log(f"尝试从 {source['name']} 检查更新...")
            # 从远程获取版本信息
            response = requests.get(source['url'], timeout=10)
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
                        console.log(f"从 {source['name']} 成功获取更新信息")
                        return remote_version_info
                    else:
                        # 当前类型版本已是最新，停止检查
                        console.log(f"从 {source['name']} 检查到当前版本已是最新")
                        return None
                
                # 如果是release类型且未启用，停止检查
                if version_type == "release":
                    console.log(f"从 {source['name']} 检查到release版本未启用")
                    return None
            
            console.log(f"从 {source['name']} 未找到适用的版本类型")
            return None
            
        except requests.exceptions.RequestException as e:
            console.log(f"无法连接到 {source['name']}，尝试下一个源: {e}")
            continue  # 继续尝试下一个源
        except Exception as e:
            console.log(f"从 {source['name']} 检查更新时出错: {e}")
            continue  # 继续尝试下一个源
    
    # 所有源都尝试失败
    console.log("所有更新源均无法连接，跳过更新检查")
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
from time import time
import requests
import os
import shutil
import stat
import random
import json

from rich.console import Console
from rich.syntax import Syntax
from rich.panel import Panel
from rich.text import Text

from function.main import defaultHeader, br, generalMainMenu
from function.variable import REGIONVALIDATIONKEY

console = Console()

MenuTitle = "清风服安装器"

# 下载源列表
ServerSources = [
    {
        "name": "清风 API",
        "url": "https://api.qingfengawa.top/FengAmongUsTool-Asset/regionInfo.json"
    },
    {
        "name": "GhProxy (CloudFlare)",
        "url": "https://gh-proxy.org/https://github.com/QingFengTechnology/FengAmongUsTool-Asset/raw/refs/heads/main/regionInfo.json"
    },
    {
        "name": "GhProxy (HongKong)",
        "url": "https://hk.gh-proxy.org/https://github.com/QingFengTechnology/FengAmongUsTool-Asset/raw/refs/heads/main/regionInfo.json"
    },
    {
        "name": "Github",
        "url": "https://github.com/QingFengTechnology/FengAmongUsTool-Asset/raw/refs/heads/main/regionInfo.json"
    }
]

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
            console.log(f"[green1]成功移除[/green1]私服文件只读属性。")
            return True
        except Exception as e:
            console.log(f"[red]未能成功移除[/red]私服文件只读属性: {str(e)}")
    return False

def testServerLatency(url, timeout=5):
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

def selectBestServer():
    """选择延迟最低的下载源"""
    results = []

    random.shuffle(ServerSources)
    
    for server in ServerSources:
        console.log(f"测试下载源[cornflower_blue]{server['name']}[/cornflower_blue][white]...[/white]")
        latency = testServerLatency(server['url'])
        if latency == float('inf'):
            console.log(f"[orange1]无法连接[/orange1]至下载源[cornflower_blue]{server['name']}[/cornflower_blue]。")
        else:
            console.log(f"[green1]成功连接[/green1]至下载源[cornflower_blue]{server['name']}[/cornflower_blue]，延迟: [cornflower_blue]{latency:.2f}ms[/cornflower_blue]")
        results.append((server, latency))
    
    available_servers = [(s, l) for s, l in results if l != float('inf')]
    
    if not available_servers:
        console.log("安装时[red1]发生意外错误[/red1]，所有下载源均[red1]无法连接[/red1]。")
        return None
    
    best_server, best_latency = min(available_servers, key=lambda x: x[1])
    console.log(f"已选择最快下载源：[cornflower_blue]{best_server['name']}[/cornflower_blue]。")
    return best_server['url']

def run(merge=True):
    """工具箱主要模块：安装清风服
    Args:
        merge: 是否为合并模式。
    """
    regionInfoPath = getRegionInfoPath()
    regionInfoBakPath = regionInfoPath + '.bak'
    success = False
    added_servers_count = 0
    duplicate_servers_count = 0
    try:
        defaultHeader()
        br()
        with console.status("准备下载清风服文件...") as status:
            status.update("检测下载源延迟...")
            DownloadServerURL = selectBestServer()
            if not DownloadServerURL:
                status.stop()
                console.print("[red1]未能连接[/red1]至可用下载服务器。")
                console.input("按 [plum1]Enter[/plum1] 返回主菜单...")
                return
            status.update("备份已有文件...")
            try:
                if os.path.exists(regionInfoPath):
                    setFileWritable(regionInfoPath)
                    if os.path.exists(regionInfoBakPath):
                        setFileWritable(regionInfoBakPath)
                    shutil.copy2(regionInfoPath, regionInfoBakPath)
                    console.log(f"原始私服文件[green1]已备份[/green1]至[cornflower_blue]{regionInfoBakPath}[/cornflower_blue]。")
                else:
                    console.log("[orange1]未找到[/orange1]原始私服文件，跳过备份。")
            except Exception as e:
                console.log(f"[orange1]未能备份[/orange1]原始私服文件: {str(e)}")
            
            if not merge:
                status.update("删除原有文件...")
                try:
                    if os.path.exists(regionInfoPath):
                        setFileWritable(regionInfoPath)
                        os.remove(regionInfoPath)
                        console.log("[green1]已删除[/green1]原始私服文件。")
                    else:
                        console.log("原始私服文件[orange1]不存在[/orange1]，跳过删除。")
                except Exception as e:
                    console.log(f"[orange1]未能删除[/orange1]原始私服文件: {str(e)}")
                    try:
                        status.update("强制删除原始文件...")
                        os.chmod(regionInfoPath, stat.S_IWRITE | stat.S_IREAD)
                        os.remove(regionInfoPath)
                        console.log("[green1]成功强制删除[/green1]原始私服文件。")
                    except:
                        console.log("安装时[red1]发生意外错误[/red1]，[red1]未能强制删除[/red1]原始私服文件。")
            
            status.update("下载文件...")
            try:
                response = requests.get(DownloadServerURL)
                response.raise_for_status()
                ServerFileResponse = response.content
                console.log(f"[green1]文件下载成功[/green1]，大小：[cornflower_blue]{len(ServerFileResponse)}B[/cornflower_blue]。")
            except Exception as e:
                console.log(f"[red1]文件下载失败[/red1]: {str(e)}")
                if os.path.exists(regionInfoBakPath):
                    try:
                        if os.path.exists(regionInfoPath):
                            setFileWritable(regionInfoPath)
                        shutil.copy2(regionInfoBakPath, regionInfoPath)
                        setFileWritable(regionInfoPath)
                        console.log("[green1]成功从备份中恢复[/green1]原始文件。")
                    except Exception as restoreError:
                        console.log(f"[red1]恢复备份失败:[/red1] {str(restoreError)}")
                raise
            status.update("校验文件...")
            try:
                if REGIONVALIDATIONKEY.encode('utf-8') not in ServerFileResponse:
                    raise ValueError("下载的私服文件缺少必备字符，疑似下载文件不正确。")
                
                if merge:
                    remote_region_data = json.loads(ServerFileResponse)
                console.log("文件[green1]校验成功[/green1]。")
            except Exception as e:
                console.log(f"文件[red1]校验失败[/red1]: {str(e)}")
                if os.path.exists(regionInfoBakPath):
                    try:
                        if os.path.exists(regionInfoPath):
                            setFileWritable(regionInfoPath)
                        shutil.copy2(regionInfoBakPath, regionInfoPath)
                        setFileWritable(regionInfoPath)
                        console.log("[green1]成功从备份中恢复[/green1]原始文件。")
                    except Exception as restoreError:
                        console.log(f"[red1]恢复备份失败[/red1]: {str(restoreError)}")
                console.print("[red1]发生意外错误[/red1]，下载的文件存在问题，已回滚更改。")
                console.print("下方为工具箱获取到的文件内容:")
                try:
                    content = ServerFileResponse.decode('utf-8', errors='replace')
                    console.print(Syntax(content, theme="github-dark", line_numbers=False))
                except:
                    console.print(f"[red1]解码内容失败[/red1]: {ServerFileResponse[:100].hex()}")
                raise
            status.update("合并配置文件...")
            if merge:
                try:
                    if os.path.exists(regionInfoPath):
                        with open(regionInfoPath, 'r', encoding='utf-8') as f:
                            local_region_data = json.load(f)
                    else:
                        local_region_data = {
                            "CurrentRegionIdx": 0,
                            "Regions": []
                        }
                    
                    added_servers_count = 0
                    duplicate_servers_count = 0
                    
                    for region in remote_region_data["Regions"]:
                        new_ip = ""
                        if region.get("Servers"):
                            new_ip = region["Servers"][0].get("Ip", "") if region["Servers"] else ""
                        
                        duplicate_found = False
                        for existing_region in local_region_data["Regions"]:
                            existing_ip = ""
                            if existing_region.get("Servers"):
                                existing_ip = existing_region["Servers"][0].get("Ip", "") if existing_region["Servers"] else ""
                            
                            if new_ip == existing_ip:
                                duplicate_found = True
                                server_name = region['Name']
                                import re
                                server_name = re.sub(r'<color=#([0-9A-F]{6})>([^<]+)</color>', r'\2', server_name)
                                console.log(f"检测到重复服务器{server_name}，跳过安装。")
                                break
                        
                        if not duplicate_found:
                            local_region_data["Regions"].append(region)
                            added_servers_count += 1
                        else:
                            duplicate_servers_count += 1
                    
                    if added_servers_count > 0:
                        local_region_data["CurrentRegionIdx"] = len(local_region_data["Regions"]) - 1
                    
                    console.log(f"[green1]成功合并[/green1]服务器配置，新增 {added_servers_count} 个服务器。")
                except Exception as e:
                    console.log(f"[red1]合并配置失败[/red1]: {str(e)}")
                    if os.path.exists(regionInfoBakPath):
                        try:
                            if os.path.exists(regionInfoPath):
                                setFileWritable(regionInfoPath)
                            shutil.copy2(regionInfoBakPath, regionInfoPath)
                            setFileWritable(regionInfoPath)
                            console.log("[green1]成功从备份中恢复[/green1]原始文件。")
                        except Exception as restoreError:
                            console.log(f"[red1]恢复备份失败[/red1]: {str(restoreError)}")
                    raise
            else:
                console.log("[green1]跳过合并[/green1]，直接使用下载的配置文件。")
            
            status.update("导入文件...")
            try:
                os.makedirs(os.path.dirname(regionInfoPath), exist_ok=True)
                if os.path.exists(regionInfoPath):
                    setFileWritable(regionInfoPath)
                
                if merge:
                    with open(regionInfoPath, 'w', encoding='utf-8') as f:
                        json.dump(local_region_data, f, ensure_ascii=False, indent=2)
                else:
                    with open(regionInfoPath, 'wb') as f:
                        f.write(ServerFileResponse)
                console.log(f"文件[green1]导入成功[/green1]。")
                if os.path.exists(regionInfoBakPath):
                    try:
                        setFileWritable(regionInfoBakPath)
                        os.remove(regionInfoBakPath)
                    except Exception as e:
                        console.log(f"[orange1]未能清理[/orange1]备份文件: {str(e)}")
                success = True    
            except Exception as e:
                console.log(f"[red1]导入文件失败[/red1]: {str(e)}")
                if os.path.exists(regionInfoBakPath):
                    try:
                        if os.path.exists(regionInfoPath):
                            setFileWritable(regionInfoPath) 
                        shutil.copy2(regionInfoBakPath, regionInfoPath)
                        setFileWritable(regionInfoPath)
                        console.log("[green1]成功从备份恢复[/green1]原始文件。")
                    except Exception as restoreError:
                        console.log(f"[red1]恢复备份失败[/red1]: {str(restoreError)}")
                raise
            status.update("设置只读...")
            try:
                os.chmod(regionInfoPath, stat.S_IREAD)
                console.log("[green1]成功设置[/green1]私服文件为只读属性。")
            except Exception as e:
                console.log(f"[red1]设置只读属性失败: {str(e)}[/red1]")
            status.update("请稍后...")
    
    except Exception as e:
        console.log(f"[red1]发生意外错误[/red1]，安装失败: {str(e)}")
        success = False
        console.print("\n如果你确认这是工具箱问题，请截图相关信息并通过 GitHub Issue 报告问题。\n")
        console.input("按 [plum1]Enter[/plum1] 返回主菜单。")
        return
    if success:
        if merge:
            if added_servers_count == 0 and duplicate_servers_count > 0:
                finalMessage = f"\n已取消安装服务器，所有服务器均为重复项。\n若仍需要安装清风服，请选择强制安装。\n"
            else:
                finalMessage = f"\n服务器安装完成。\n"
                if duplicate_servers_count > 0:
                    finalMessage += f"已跳过安装 {duplicate_servers_count} 个服务器，如果你仍需要安装，请选择强制安装。\n"
        else:
            finalMessage = "\n服务器安装完成。\n"
        generalMainMenu(finalMessage, MenuTitle)
    else:
        finalMessage = "\n服务器安装失败，请查看日志以了解详情。\n"
        console.print(Panel(Text(finalMessage, style="red1"), title=Text(MenuTitle, style="bold")))
    
    console.input("按 [plum1]Enter[/plum1] 返回主菜单。")

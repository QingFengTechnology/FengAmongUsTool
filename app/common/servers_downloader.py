# coding: utf-8
"""
servers.json 下载器模块
支持从多个源并发下载，设置超时并优先使用最先完成的源
"""

import asyncio
import aiohttp
import json
import os
from typing import Optional, Dict, Any


class ServersDownloader:
    """Servers.json 下载器"""
    
    # 默认的下载源
    DEFAULT_SOURCES = [
        "https://github.com/YvonneOfficial/FengAmongUsTool-Asset/raw/main/servers.json",
        "https://gh-proxy.org/https://github.com/YvonneOfficial/FengAmongUsTool-Asset/raw/main/servers.json"
    ]
    
    # 默认超时时间（秒）
    DEFAULT_TIMEOUT = 5
    
    def __init__(self, sources: list = None, timeout: int = None):
        """
        初始化下载器
        
        Args:
            sources: 下载源列表，默认使用 DEFAULT_SOURCES
            timeout: 超时时间（秒），默认使用 DEFAULT_TIMEOUT
        """
        self.sources = sources or self.DEFAULT_SOURCES
        self.timeout = timeout or self.DEFAULT_TIMEOUT
    
    async def download_from_source(self, session: aiohttp.ClientSession, url: str) -> tuple:
        """
        从单个源下载 servers.json
        
        Args:
            session: aiohttp 会话
            url: 下载地址
            
        Returns:
            tuple: (是否成功, 数据或异常信息, 源URL)
        """
        try:
            async with session.get(url, timeout=self.timeout) as response:
                if response.status == 200:
                    content = await response.text()
                    # 验证 JSON 格式
                    data = json.loads(content)
                    return True, data, url
                else:
                    return False, f"HTTP {response.status}", url
        except asyncio.TimeoutError:
            return False, "Timeout", url
        except Exception as e:
            return False, str(e), url
    
    async def download_servers_json(self) -> Optional[Dict[Any, Any]]:
        """
        从多个源并发下载 servers.json，返回第一个成功的响应
        
        Returns:
            dict: 解析后的 JSON 数据，如果所有源都失败则返回 None
        """
        async with aiohttp.ClientSession() as session:
            # 创建所有下载任务
            tasks = [
                asyncio.create_task(self.download_from_source(session, source)) 
                for source in self.sources
            ]
            
            # 等待第一个任务完成
            done, pending = await asyncio.wait(
                tasks, 
                return_when=asyncio.FIRST_COMPLETED
            )
            
            # 处理已完成的任务
            for task in done:
                success, data, source_url = await task
                if success:
                    # 取消所有未完成的任务
                    for pending_task in pending:
                        pending_task.cancel()
                    return data
            
            # 如果第一个完成的任务失败，等待其他任务看是否有成功的
            if pending:
                done, pending = await asyncio.wait(
                    pending, 
                    return_when=asyncio.FIRST_COMPLETED
                )
                
                for task in done:
                    success, data, source_url = await task
                    if success:
                        # 取消所有未完成的任务
                        for pending_task in pending:
                            pending_task.cancel()
                        return data
            
            # 所有源都失败
            return None
    
    def save_to_local(self, data: Dict[Any, Any], file_path: str) -> bool:
        """
        将下载的数据保存到本地文件
        
        Args:
            data: 要保存的数据
            file_path: 保存路径
            
        Returns:
            bool: 是否保存成功
        """
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # 保存文件
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"保存文件时出错: {e}")
            return False


# 用于同步调用的便捷函数
def download_servers_json_sync(sources: list = None, timeout: int = None) -> Optional[Dict[Any, Any]]:
    """
    同步方式下载 servers.json
    
    Args:
        sources: 下载源列表
        timeout: 超时时间（秒）
        
    Returns:
        dict: 解析后的 JSON 数据，如果所有源都失败则返回 None
    """
    downloader = ServersDownloader(sources, timeout)
    try:
        # 在 Windows 上需要设置事件循环策略
        import sys
        if sys.platform.startswith("win"):
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        
        return asyncio.run(downloader.download_servers_json())
    except Exception as e:
        print(f"下载 servers.json 时出错: {e}")
        return None


# 获取临时缓存目录
def get_temp_cache_dir() -> str:
    """
    获取临时缓存目录路径
    
    Returns:
        str: 临时缓存目录路径
    """
    import tempfile
    import os
    cache_dir = os.path.join(tempfile.gettempdir(), "FengAmongUsTool")
    os.makedirs(cache_dir, exist_ok=True)
    return cache_dir


# 获取缓存的 servers.json 文件路径
def get_cached_servers_json_path() -> str:
    """
    获取缓存的 servers.json 文件路径
    
    Returns:
        str: 缓存文件路径
    """
    import os
    return os.path.join(get_temp_cache_dir(), "servers.json")
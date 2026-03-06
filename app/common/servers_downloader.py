# coding: utf-8
"""
servers.json 下载器模块
通过并发ping测速选择最优线路下载
"""

import asyncio
import aiohttp
import json
import logging
import os
import time
from typing import Optional, Dict, Any, Tuple

logger = logging.getLogger(__name__)


class ServersDownloader:
    """Servers.json 下载器"""

    # 默认的下载源
    DEFAULT_SOURCES = [
        "https://github.com/BreezeCrew/FengAmongUsTool-Asset/raw/main/servers.json",
        "https://gh-proxy.org/https://github.com/BreezeCrew/FengAmongUsTool-Asset/raw/main/servers.json",
        "https://api.qingfengawa.top/FengAmongUsTool-Asset/servers.json"
    ]

    # ping 超时时间（秒）
    PING_TIMEOUT = 6

    # 下载超时时间（秒）
    DOWNLOAD_TIMEOUT = 10

    def __init__(self, sources: list = None, ping_timeout: int = None, download_timeout: int = None):
        """
        初始化下载器

        Args:
            sources: 下载源列表，默认使用 DEFAULT_SOURCES
            ping_timeout: ping超时时间（秒），默认使用 PING_TIMEOUT
            download_timeout: 下载超时时间（秒），默认使用 DOWNLOAD_TIMEOUT
        """
        self.sources = sources or self.DEFAULT_SOURCES
        self.ping_timeout = ping_timeout or self.PING_TIMEOUT
        self.download_timeout = download_timeout or self.DOWNLOAD_TIMEOUT

    async def ping_source(self, session: aiohttp.ClientSession, url: str) -> Tuple[str, Optional[float]]:
        """
        ping单个源，获取响应时间

        Args:
            session: aiohttp 会话
            url: 下载地址

        Returns:
            tuple: (url, 响应时间秒数，失败则返回 None)
        """
        try:
            start_time = time.time()
            # 使用 HEAD 请求进行测速，只响应头不下载内容
            async with session.head(url, timeout=self.ping_timeout, allow_redirects=True) as response:
                if response.status == 200 or 300 <= response.status < 400:
                    elapsed = time.time() - start_time
                    logger.debug(f"Ping {url} 成功，耗时: {elapsed:.3f}s")
                    return url, elapsed
                else:
                    logger.debug(f"Ping {url} 失败，状态码: {response.status}")
                    return url, None
        except asyncio.TimeoutError:
            logger.debug(f"Ping {url} 超时 (>{self.ping_timeout}s)")
            return url, None
        except Exception as e:
            logger.debug(f"Ping {url} 出错: {e}")
            return url, None

    async def select_best_source(self) -> Optional[str]:
        """
        并发ping所有源，选择响应最快的源

        Returns:
            str: 最快的源 URL，如果所有源都失败则返回 None
        """
        async with aiohttp.ClientSession() as session:
            # 创建所有ping任务
            tasks = [
                asyncio.create_task(self.ping_source(session, source))
                for source in self.sources
            ]

            # 等待所有ping任务完成
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # 收集有效的结果
            valid_results = []
            for result in results:
                if isinstance(result, tuple) and len(result) == 2:
                    url, elapsed = result
                    if elapsed is not None:
                        valid_results.append((url, elapsed))

            if not valid_results:
                logger.warning("所有源 ping 测试失败")
                return None

            # 选择响应时间最短的源
            best_url, best_time = min(valid_results, key=lambda x: x[1])
            logger.info(f"选择最优线路: {best_url} (耗时: {best_time:.3f}s)")
            return best_url

    async def download_from_source(self, url: str) -> Optional[Dict[Any, Any]]:
        """
        从指定源下载 servers.json

        Args:
            url: 下载地址

        Returns:
            dict: 解析后的 JSON 数据，如果失败则返回 None
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=self.download_timeout) as response:
                    if response.status == 200:
                        content = await response.text()
                        # 验证 JSON 格式
                        data = json.loads(content)
                        return data
                    else:
                        logger.warning(f"从 {url} 下载失败，状态码: {response.status}")
                        return None
        except asyncio.TimeoutError:
            logger.error(f"从 {url} 下载超时 (>{self.download_timeout}s)")
            return None
        except Exception as e:
            logger.error(f"从 {url} 下载出错: {e}")
            return None

    async def download_servers_json(self) -> Optional[Dict[Any, Any]]:
        """
        通过并发ping测速选择最优线路下载 servers.json

        Returns:
            dict: 解析后的 JSON 数据，如果所有源都失败则返回 None
        """
        logger.info(f"开始测速，共 {len(self.sources)} 个源")

        # 测速选择最优线路
        best_source = await self.select_best_source()

        if not best_source:
            logger.error("无可用源，下载失败")
            return None

        # 从最优线路下载
        logger.info(f"开始从最优线路下载: {best_source}")
        data = await self.download_from_source(best_source)

        if data:
            logger.info("下载成功")
        else:
            logger.error(f"从 {best_source} 下载失败")

        return data

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
            logger.error(f"保存文件时出错: {e}")
            return False


# 用于同步调用的便捷函数
def download_servers_json_sync(
    sources: list = None,
    ping_timeout: int = None,
    download_timeout: int = None
) -> Optional[Dict[Any, Any]]:
    """
    同步方式下载 servers.json

    Args:
        sources: 下载源列表
        ping_timeout: ping超时时间（秒）
        download_timeout: 下载超时时间（秒）

    Returns:
        dict: 解析后的 JSON 数据，如果所有源都失败则返回 None
    """
    downloader = ServersDownloader(sources, ping_timeout, download_timeout)
    try:
        # 在 Windows 上需要设置事件循环策略
        import sys
        if sys.platform.startswith("win"):
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

        return asyncio.run(downloader.download_servers_json())
    except Exception as e:
        logger.error(f"下载 servers.json 时出错: {e}")
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
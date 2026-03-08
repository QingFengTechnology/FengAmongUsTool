# coding: utf-8
"""
更新检查模块
使用 /releases?per_page=100，过滤 v4+ 及以后的 tag，取 created_at 最大值与本地 VERSION_DATE 比对。
"""

import asyncio
import logging
from datetime import datetime
from typing import Literal, Optional, Tuple, Union

import aiohttp
from .setting import REPO_URL as _REPO_URL

logger = logging.getLogger(__name__)

# 从 REPO_URL 推导出 API 路径，避免硬编码仓库名
# 例如 https://github.com/BreezeCrew/FengAmongUsTool → repos/BreezeCrew/FengAmongUsTool
_REPO_PATH = _REPO_URL.removeprefix("https://github.com/")
_API_SUFFIX = f"repos/{_REPO_PATH}/releases?per_page=100"

# 诡异GHProxy源无法成功加速Github API，所以此处不添加GHProxy源
_SOURCES = [
    f"https://api.github.com/{_API_SUFFIX}",
    f"https://gh.llkk.cc/https://api.github.com/{_API_SUFFIX}",
    f"https://tvv.tw/https://api.github.com/{_API_SUFFIX}",
]

_PING_TIMEOUT = 6
_REQUEST_TIMEOUT = 10


async def _ping(session: aiohttp.ClientSession, url: str) -> Tuple[str, Optional[float]]:
    """测速，返回 (url, 响应秒数) 或 (url, None)。HEAD 失败时回退 GET。"""
    import time
    try:
        start = time.monotonic()
        async with session.head(url, timeout=_PING_TIMEOUT, allow_redirects=True) as resp:
            if resp.status < 400:
                elapsed = time.monotonic() - start
                logger.debug("Ping %s 成功（HEAD），耗时: %.3fs", url, elapsed)
                return url, elapsed
            if resp.status not in (403, 405, 501):
                logger.debug("Ping %s 失败（HEAD），状态码: %d", url, resp.status)
                return url, None
        # HEAD 返回 403/405，部分代理不支持 HEAD，改用 GET 重试
        start = time.monotonic()
        async with session.get(url, timeout=_PING_TIMEOUT, allow_redirects=True) as resp:
            elapsed = time.monotonic() - start
            if resp.status < 400:
                logger.debug("Ping %s 成功（GET 回退），耗时: %.3fs", url, elapsed)
                return url, elapsed
            logger.debug("Ping %s 失败（GET 回退），状态码: %d", url, resp.status)
            return url, None
    except asyncio.TimeoutError:
        logger.debug("Ping %s 超时 (>%ds)", url, _PING_TIMEOUT)
        return url, None
    except Exception as e:
        logger.debug("Ping %s 出错: %s", url, e)
        return url, None


# 版本号 major 不低于此数值的 tag 才参与比较（排除 v1~v3）
_MIN_MAJOR = 4


def _is_valid_tag(tag_name: str) -> bool:
    """tag 格式为 vN.* 且 N >= _MIN_MAJOR 时返回 True"""
    if not tag_name.startswith("v"):
        return False
    try:
        major = int(tag_name[1:].split(".")[0])
        return major >= _MIN_MAJOR
    except (ValueError, IndexError):
        return False


async def _fetch_latest_release() -> Union[dict, Literal[False]]:
    """并发测速后从最快源拉取 releases 列表，过滤并返回 created_at 最大的 release"""
    async with aiohttp.ClientSession(headers={"Accept": "application/vnd.github+json"}) as session:
        # 并发 ping
        ping_results = await asyncio.gather(*[_ping(session, u) for u in _SOURCES])
        valid = [(u, t) for u, t in ping_results if t is not None]
        # 按响应时间排序；ping 全失败时按原始顺序兜底
        ordered_urls = [u for u, _ in sorted(valid, key=lambda x: x[1])] if valid else list(_SOURCES)
        if not valid:
            logger.warning("更新检查：所有源 ping 失败，将逐一尝试所有源")
        else:
            logger.info("更新检查：共 %d/%d 个源可用，按速度依次尝试", len(valid), len(_SOURCES))

        releases = None
        for url in ordered_urls:
            try:
                async with session.get(url, timeout=_REQUEST_TIMEOUT) as resp:
                    if resp.status != 200:
                        logger.warning("更新检查：HTTP %d from %s，尝试下一源", resp.status, url)
                        continue
                    data = await resp.json()
                    if not isinstance(data, list):
                        logger.warning("更新检查：%s 响应非列表（可能触发速率限制）: %s，尝试下一源", url, data)
                        continue
                    releases = data
                    logger.info("更新检查：成功从 %s 获取数据", url)
                    break
            except Exception as e:
                logger.warning("更新检查：请求 %s 失败: %s，尝试下一源", url, e)
                continue

        if releases is None:
            logger.warning("更新检查：所有源均失败")
            return False

    # 过滤掉草稿及 v1~v3
    candidates = [
        r for r in releases
        if not r.get("draft", False) and _is_valid_tag(r.get("tag_name", ""))
    ]
    if not candidates:
        logger.warning("更新检查：未找到符合条件的 release")
        return False

    latest = max(candidates, key=lambda r: r.get("created_at", ""))
    logger.debug("更新检查：最新符合版本 %s (%s)", latest.get("tag_name"), latest.get("created_at"))
    return latest


async def check_update() -> Union[dict, None, Literal[False]]:
    """
    检查是否有新版本。

    Returns:
        有新版时返回 release dict（包含 tag_name / created_at / html_url）；
        无新版返回 None；
        网络/HTTP 出错返回 False。
    """
    from .setting import VERSION_DATE

    release = await _fetch_latest_release()
    if release is False:
        return False

    remote_date = release.get("created_at", "")
    if not remote_date:
        logger.warning("更新检查：release 缺少 created_at 字段")
        return False

    # 使用解析后的 datetime 比较，避免依赖 ISO 字符串字典序
    try:
        local_dt = datetime.fromisoformat(VERSION_DATE.replace("Z", "+00:00"))
        remote_dt = datetime.fromisoformat(remote_date.replace("Z", "+00:00"))
    except ValueError:
        logger.warning(
            "更新检查：版本日期解析失败，回退到字符串比较（本地 %s，远程 %s）",
            VERSION_DATE, remote_date, exc_info=True,
        )
        if remote_date > VERSION_DATE:
            logger.info("发现新版本：%s (%s)", release.get("tag_name"), remote_date)
            return release
        logger.info("已是最新版本（本地 %s，远程 %s）", VERSION_DATE, remote_date)
        return None

    if remote_dt > local_dt:
        logger.info("发现新版本：%s (%s)", release.get("tag_name"), remote_date)
        return release

    logger.info("已是最新版本（本地 %s，远程 %s）", VERSION_DATE, remote_date)
    return None

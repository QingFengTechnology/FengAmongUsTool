# coding: utf-8
"""
更新检查模块
使用 /releases?per_page=100，过滤 v4+ 及以后的 tag，取 created_at 最大值与本地 VERSION_DATE 比对。
"""

import asyncio
import logging
from typing import Optional, Tuple

import aiohttp

logger = logging.getLogger(__name__)

# 三个Github API源
# 诡异GHProxy源无法成功加速Github API，所以此处不添加GHProxy源
_SOURCES = [
    "https://api.github.com/repos/BreezeCrew/FengAmongUsTool/releases?per_page=100",
    "https://gh.llkk.cc/https://api.github.com/repos/BreezeCrew/FengAmongUsTool/releases?per_page=100",
    "https://tvv.tw/https://api.github.com/repos/BreezeCrew/FengAmongUsTool/releases?per_page=100"
]

_PING_TIMEOUT = 6
_REQUEST_TIMEOUT = 10


async def _ping(session: aiohttp.ClientSession, url: str) -> Tuple[str, Optional[float]]:
    """HEAD 测速，返回 (url, 响应秒数) 或 (url, None)"""
    import time
    try:
        start = time.monotonic()
        async with session.head(url, timeout=_PING_TIMEOUT, allow_redirects=True) as resp:
            if resp.status < 400:
                elapsed = time.monotonic() - start
                logger.debug("Ping %s 成功，耗时: %.3fs", url, elapsed)
                return url, elapsed
            logger.debug("Ping %s 失败，状态码: %d", url, resp.status)
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


async def _fetch_latest_release() -> Optional[dict]:
    """并发测速后从最快源拉取 releases 列表，过滤并返回 created_at 最大的 release"""
    async with aiohttp.ClientSession(headers={"Accept": "application/vnd.github+json"}) as session:
        # 并发 ping
        ping_results = await asyncio.gather(*[_ping(session, u) for u in _SOURCES])
        valid = [(u, t) for u, t in ping_results if t is not None]
        if not valid:
            logger.warning("更新检查：所有源 ping 失败")
            return None

        best_url, best_time = min(valid, key=lambda x: x[1])
        logger.info("更新检查：共 %d/%d 个源可用，选用 %s (耗时: %.3fs)", len(valid), len(_SOURCES), best_url, best_time)

        try:
            async with session.get(best_url, timeout=_REQUEST_TIMEOUT) as resp:
                if resp.status != 200:
                    logger.warning("更新检查：HTTP %d from %s", resp.status, best_url)
                    return None
                releases = await resp.json()
        except Exception as e:
            logger.warning("更新检查：请求失败 %s", e)
            return None

    # 过滤掉草稿及 v1~v3
    candidates = [
        r for r in releases
        if not r.get("draft", False) and _is_valid_tag(r.get("tag_name", ""))
    ]
    if not candidates:
        logger.warning("更新检查：未找到符合条件的 release")
        return None

    latest = max(candidates, key=lambda r: r.get("created_at", ""))
    logger.debug("更新检查：最新符合版本 %s (%s)", latest.get("tag_name"), latest.get("created_at"))
    return latest


async def check_update() -> Optional[dict]:
    """
    检查是否有新版本。

    Returns:
        有新版时返回 release dict（包含 tag_name / created_at / html_url）；
        无新版或出错返回 None。
    """
    from .setting import VERSION_DATE

    release = await _fetch_latest_release()
    if not release:
        return None

    remote_date = release.get("created_at", "")
    if not remote_date:
        return None

    # ISO 8601 字符串字典序 == 时间顺序
    if remote_date > VERSION_DATE:
        logger.info("发现新版本：%s (%s)", release.get("tag_name"), remote_date)
        return release

    logger.info("已是最新版本（本地 %s，远程 %s）", VERSION_DATE, remote_date)
    return None

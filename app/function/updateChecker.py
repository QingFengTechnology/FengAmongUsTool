# coding:utf-8
"""
版本更新检查功能
"""

import logging
import threading
from datetime import datetime, timezone
from typing import Any, Dict, Optional, Tuple

import requests
from PySide6.QtCore import QTimer, QUrl
from PySide6.QtGui import QDesktopServices
from qfluentwidgets import MessageBox

from .variableConfig import PROJECT_CONFIG


LOGGER = logging.getLogger("FengAmongUsTool")

VERSION_SOURCES: Tuple[Tuple[str, str], ...] = (
    (
        "GitHub",
        "https://raw.githubusercontent.com/QingFengTechnology/FengAmongUsTool-Asset/main/version.json",
    ),
    (
        "镜像源",
        "https://gh-proxy.com/https://raw.githubusercontent.com/QingFengTechnology/FengAmongUsTool-Asset/main/version.json",
    ),
)

FETCH_TIMEOUT = 10
WAIT_TIMEOUT = 30
LATEST_RELEASE_URL = "https://github.com/QingFengTechnology/FengAmongUsTool/releases/latest"


def startUpdateCheck(parentWindow) -> None:
    """入口：启动后台线程进行版本检查"""
    if not parentWindow:
        LOGGER.debug("无法执行更新检查：缺少父窗口引用")
        return

    localDate = PROJECT_CONFIG.get("versionDate")
    if not localDate:
        LOGGER.debug("本地版本日期缺失，跳过更新检查")
        return

    worker = threading.Thread(
        target=_runUpdateCheck,
        name="UpdateCheckWorker",
        args=(parentWindow, PROJECT_CONFIG.get("versionType", "release"), localDate),
        daemon=True,
    )
    worker.start()


def _parse_version_date(value: Any) -> Optional[datetime]:
    """解析版本日期，统一转换为 UTC"""
    if isinstance(value, datetime):
        return value.astimezone(timezone.utc) if value.tzinfo else value.replace(tzinfo=timezone.utc)

    if not value:
        return None

    normalized = str(value).strip()
    if normalized.endswith("Z"):
        normalized = normalized[:-1] + "+00:00"

    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError:
        fallback_format = PROJECT_CONFIG.get("versionDateFormat")
        if not fallback_format:
            return None
        try:
            parsed = datetime.strptime(normalized, fallback_format)
        except ValueError:
            return None

    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _runUpdateCheck(parentWindow, channel: str, localDate: Any) -> None:
    """后台线程主体：拉取远程版本信息并比较"""
    LOGGER.debug("启动版本检查线程，通道=%s，本地日期=%s", channel, localDate)
    resultLock = threading.Lock()
    finishEvent = threading.Event()
    fetchResult: Dict[str, Any] = {"data": None, "source": None}

    def fetchFromSource(sourceName: str, url: str) -> None:
        if finishEvent.is_set():
            return

        LOGGER.debug("正在从%s获取版本信息...", sourceName)
        try:
            response = requests.get(url, timeout=FETCH_TIMEOUT)
            response.raise_for_status()
            remoteData = response.json()
        except Exception as exc:
            LOGGER.warning("从%s获取版本信息失败: %s", sourceName, exc)
            return

        if finishEvent.is_set():
            LOGGER.debug("%s 的版本信息已过期，忽略", sourceName)
            return

        with resultLock:
            if finishEvent.is_set():
                LOGGER.debug("%s 的版本信息已过期，忽略", sourceName)
                return

            fetchResult["data"] = remoteData
            fetchResult["source"] = sourceName
            finishEvent.set()
            LOGGER.info("版本信息已从%s获取成功", sourceName)

    threads = []
    for sourceName, url in VERSION_SOURCES:
        thread = threading.Thread(target=fetchFromSource, args=(sourceName, url), daemon=True)
        threads.append(thread)
        thread.start()

    finishEvent.wait(timeout=WAIT_TIMEOUT)

    for thread in threads:
        thread.join(timeout=1)

    remoteData = fetchResult.get("data")
    if not remoteData:
        LOGGER.warning("未能从任何源获取到版本信息，更新检查终止")
        return

    local_date_obj = _parse_version_date(localDate)
    if local_date_obj is None:
        LOGGER.warning("本地版本日期解析失败：%s，将视为最早时间", localDate)
        local_date_obj = datetime.min.replace(tzinfo=timezone.utc)

    channel_priority = ["alpha", "beta", "preview", "release"]
    local_channel = str(channel).lower()
    try:
        start_index = channel_priority.index(local_channel)
    except ValueError:
        LOGGER.warning("未知的本地通道 %s，按默认顺序检测", channel)
        start_index = 0

    selected_channel: Optional[str] = None
    selected_data: Optional[Dict[str, Any]] = None
    selected_remote_date: Optional[datetime] = None

    for channel_name in channel_priority[start_index:]:
        channel_data: Optional[Dict[str, Any]] = remoteData.get(channel_name)
        if not isinstance(channel_data, dict):
            LOGGER.debug("远程版本信息中缺少通道 %s，跳过", channel_name)
            continue

        if not channel_data.get("enable", False):
            LOGGER.debug("通道 %s 已被禁用，跳过", channel_name)
            continue

        remote_date_str = channel_data.get("versionDate")
        if not remote_date_str:
            LOGGER.warning("通道 %s 的版本信息缺少 versionDate 字段，跳过", channel_name)
            continue

        remote_date_obj = _parse_version_date(remote_date_str)
        if remote_date_obj is None:
            LOGGER.warning("通道 %s 的版本日期解析失败：%s，跳过", channel_name, remote_date_str)
            continue

        if remote_date_obj <= local_date_obj:
            LOGGER.debug(
                "通道 %s 版本已是最新 (local=%s, remote=%s)",
                channel_name,
                local_date_obj.isoformat(),
                remote_date_obj.isoformat(),
            )
            continue

        selected_channel = channel_name
        selected_data = channel_data
        selected_remote_date = remote_date_obj
        break

    if not selected_data or not selected_channel or not selected_remote_date:
        LOGGER.debug("未检测到比本地更新的版本，更新检查结束")
        return

    remote_version = selected_data.get("version") or "未知版本"
    LOGGER.info(
        "检测到通道 %s 有新版本: localDate=%s, remoteDate=%s, version=%s",
        selected_channel,
        local_date_obj.isoformat(),
        selected_remote_date.isoformat(),
        remote_version,
    )

    def notifyUser() -> None:
        message = (
            f"检测到新版本 {remote_version}！\n"
            "是否前往发布页面？"
        )
        dialog = MessageBox("发现新版本可用！", message, parentWindow)
        dialog.yesButton.setText("是")
        dialog.cancelButton.setText("否")
        if dialog.exec():
            QDesktopServices.openUrl(QUrl(LATEST_RELEASE_URL))

    QTimer.singleShot(0, notifyUser)

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


logger = logging.getLogger("FengAmongUsTool")

versionSources: Tuple[Tuple[str, str], ...] = (
    (
        "GitHub",
        "https://raw.githubusercontent.com/QingFengTechnology/FengAmongUsTool-Asset/main/version.json",
    ),
    (
        "镜像源",
        "https://gh-proxy.com/https://raw.githubusercontent.com/QingFengTechnology/FengAmongUsTool-Asset/main/version.json",
    ),
)

fetchTimeout = 10
waitTimeout = 30
latestReleaseUrl = "https://github.com/QingFengTechnology/FengAmongUsTool/releases/latest"


def startUpdateCheck(parentWindow) -> None:
    """入口：启动后台线程进行版本检查"""
    if not parentWindow:
        logger.debug("跳过更新检查：缺少父窗口引用。")
        return

    localDate = PROJECT_CONFIG.get("versionDate")
    if not localDate:
        logger.debug("跳过更新检查：本地版本日期缺失。")
        return

    worker = threading.Thread(
        target=_runUpdateCheck,
        name="UpdateCheckWorker",
        args=(parentWindow, PROJECT_CONFIG.get("versionType", "release"), localDate),
        daemon=True,
    )
    worker.start()


def _parseVersionDate(value: Any) -> Optional[datetime]:
    """解析版本日期并统一转换为 UTC"""
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
        fallbackFormat = PROJECT_CONFIG.get("versionDateFormat")
        if not fallbackFormat:
            return None
        try:
            parsed = datetime.strptime(normalized, fallbackFormat)
        except ValueError:
            return None

    return parsed.astimezone(timezone.utc) if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)


def _runUpdateCheck(parentWindow, channel: str, localDate: Any) -> None:
    """后台线程主体：拉取远程版本信息并比较"""
    logger.debug(f"启动版本检查线程，通道={channel}，本地日期={localDate}")
    resultLock = threading.Lock()
    finishEvent = threading.Event()
    fetchResult: Dict[str, Any] = {"data": None, "source": None}

    def fetchFromSource(sourceName: str, url: str) -> None:
        if finishEvent.is_set():
            return

        logger.debug(f"正在从 {sourceName} 获取版本信息…")
        try:
            response = requests.get(url, timeout=fetchTimeout)
            response.raise_for_status()
            remoteData = response.json()
        except Exception as exc:
            logger.warning(f"从 {sourceName} 获取版本信息失败：{exc}")
            return

        if finishEvent.is_set():
            logger.debug(f"{sourceName} 的版本信息已过期，忽略。")
            return

        with resultLock:
            if finishEvent.is_set():
                logger.debug(f"{sourceName} 的版本信息已过期，忽略。")
                return

            fetchResult["data"] = remoteData
            fetchResult["source"] = sourceName
            finishEvent.set()
            logger.info(f"已从 {sourceName} 获取版本信息。")

    threads = []
    for sourceName, url in versionSources:
        thread = threading.Thread(target=fetchFromSource, args=(sourceName, url), daemon=True)
        threads.append(thread)
        thread.start()

    finishEvent.wait(timeout=waitTimeout)

    for thread in threads:
        thread.join(timeout=1)

    remoteData = fetchResult.get("data")
    if not remoteData:
        logger.warning("未能获取任何版本信息，更新检查终止。")
        return

    localDateObj = _parseVersionDate(localDate)
    if localDateObj is None:
        logger.warning(f"无法解析本地版本日期：{localDate}，将视为最早时间。")
        localDateObj = datetime.min.replace(tzinfo=timezone.utc)

    channelPriority = ["alpha", "beta", "preview", "release"]
    localChannel = str(channel).lower()
    try:
        startIndex = channelPriority.index(localChannel)
    except ValueError:
        logger.warning(f"未知的本地通道 {channel}，按默认顺序检测。")
        startIndex = 0

    selectedChannel: Optional[str] = None
    selectedData: Optional[Dict[str, Any]] = None
    selectedRemoteDate: Optional[datetime] = None

    for channelName in channelPriority[startIndex:]:
        channelData: Optional[Dict[str, Any]] = remoteData.get(channelName)
        if not isinstance(channelData, dict):
            logger.debug(f"远程元数据缺少通道 {channelName}，跳过。")
            continue

        if not channelData.get("enable", False):
            logger.debug(f"通道 {channelName} 已被禁用，跳过。")
            continue

        remoteDateStr = channelData.get("versionDate")
        if not remoteDateStr:
            logger.warning(f"通道 {channelName} 缺少 versionDate 字段，跳过。")
            continue

        remoteDateObj = _parseVersionDate(remoteDateStr)
        if remoteDateObj is None:
            logger.warning(f"通道 {channelName} 的版本日期解析失败：{remoteDateStr}，跳过。")
            continue

        if remoteDateObj <= localDateObj:
            logger.debug(
                f"通道 {channelName} 已是最新版本（本地={localDateObj.isoformat()}，远程={remoteDateObj.isoformat()}）。"
            )
            continue

        selectedChannel = channelName
        selectedData = channelData
        selectedRemoteDate = remoteDateObj
        break

    if not selectedData or not selectedChannel or not selectedRemoteDate:
        logger.debug("未检测到更新版本，更新检查结束。")
        return

    remoteVersion = selectedData.get("version") or "未知版本"
    logger.info(
        f"检测到通道 {selectedChannel} 有新版本：本地={localDateObj.isoformat()}，"
        f"远程={selectedRemoteDate.isoformat()}，版本={remoteVersion}"
    )

    def notifyUser() -> None:
        message = (
            f"检测到新版本 {remoteVersion}。\n"
            "是否前往最新发布页面？"
        )
        dialog = MessageBox("发现新版本可用", message, parentWindow)
        dialog.yesButton.setText("是")
        dialog.cancelButton.setText("否")
        if dialog.exec():
            QDesktopServices.openUrl(QUrl(latestReleaseUrl))

    QTimer.singleShot(0, notifyUser)

# coding:utf-8
"""
变量定义文件
"""

from datetime import datetime

# 窗口配置
WINDOW_CONFIG = {
    "width": 1000,
    "height": 700,
    "title": "清风工具箱"
}

# 主题配置
THEME_CONFIG = {
    "theme": "AUTO"  # AUTO, LIGHT, DARK
}

# 日志配置
LOG_CONFIG = {
    "timestamp_format": "%H:%M:%S"
}

# 版本日期格式
VERSION_DATE_FORMAT = "%Y-%m-%dT%H:%M"

# 版本发布日期
VERSION_RELEASE_DATE = datetime(2025, 10, 31, 23, 22)

# 更新检查配置
UPDATE_CHECK_FETCH_TIMEOUT = 10
UPDATE_CHECK_WAIT_TIMEOUT = 30
UPDATE_CHECK_LATEST_RELEASE_URL = "https://github.com/QingFengTechnology/FengAmongUsTool/releases/latest"

# 项目信息配置
PROJECT_CONFIG = {
    "name": "清风工具箱",
    "version": "4.0.0-alpha.1",
    "versionType": "alpha",
    "versionDateFormat": VERSION_DATE_FORMAT,
    "versionDate": VERSION_RELEASE_DATE.strftime(VERSION_DATE_FORMAT),
    "author": "QingFeng",
    "year": "2025",
    "github_url": "https://github.com/QingFengTechnology/FengAmongUsTool",
    "issues_url": "https://github.com/QingFengTechnology/FengAmongUsTool/issues",
    "help_url": "https://github.com/QingFengTechnology/FengAmongUsTool"
}
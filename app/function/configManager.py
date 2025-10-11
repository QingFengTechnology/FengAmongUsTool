# coding:utf-8
"""
配置管理器 - 基于QFluentWidgets的配置系统
"""
import os
import json
from enum import Enum
from pathlib import Path

from PySide6.QtCore import QLocale
from qfluentwidgets import (qconfig, QConfig, ConfigItem, OptionsConfigItem, 
                           BoolValidator, OptionsValidator, Theme, ConfigSerializer, setTheme)


class Language(Enum):
    """语言枚举"""
    CHINESE_SIMPLIFIED = QLocale(QLocale.Chinese, QLocale.China)
    CHINESE_TRADITIONAL = QLocale(QLocale.Chinese, QLocale.HongKong)
    ENGLISH = QLocale(QLocale.English)
    AUTO = QLocale()


class LanguageSerializer(ConfigSerializer):
    """语言序列化器"""
    def serialize(self, language):
        return language.value.name() if language != Language.AUTO else "Auto"

    def deserialize(self, value: str):
        return Language(QLocale(value)) if value != "Auto" else Language.AUTO


class ThemeSerializer(ConfigSerializer):
    """主题序列化器"""
    def serialize(self, theme):
        if theme == Theme.LIGHT:
            return "Light"
        elif theme == Theme.DARK:
            return "Dark"
        else:
            return "Auto"

    def deserialize(self, value: str):
        if value == "Light":
            return Theme.LIGHT
        elif value == "Dark":
            return Theme.DARK
        else:
            return Theme.AUTO


class Config(QConfig):
    """应用程序配置"""
    
    # 主题配置
    themeMode = OptionsConfigItem(
        "Personalization", "Theme", Theme.AUTO, 
        OptionsValidator([Theme.LIGHT, Theme.DARK, Theme.AUTO]), 
        ThemeSerializer()
    )
    
    # 界面缩放
    dpiScale = OptionsConfigItem(
        "Personalization", "DpiScale", "Auto", 
        OptionsValidator(["100%", "125%", "150%", "175%", "200%", "Auto"]),
        restart=True
    )
    
    # 语言设置
    language = OptionsConfigItem(
        "Personalization", "Language", Language.AUTO, 
        OptionsValidator(Language), LanguageSerializer()
    )
    
    # 启动时检查更新
    checkUpdateAtStartUp = ConfigItem("Update", "CheckUpdateAtStartUp", True, BoolValidator())
    
    # 窗口配置
    windowWidth = ConfigItem("Window", "Width", 1000)
    windowHeight = ConfigItem("Window", "Height", 700)


# 配置文件路径 - 使用项目目录下的config文件夹
project_root = Path(__file__).parent.parent.parent
CONFIG_DIR = project_root / "config"
CONFIG_FILE = CONFIG_DIR / "config.json"

# 确保配置目录存在
CONFIG_DIR.mkdir(parents=True, exist_ok=True)

# 创建配置实例
cfg = Config()


def load_config():
    """加载配置"""
    try:
        if CONFIG_FILE.exists():
            qconfig.load(str(CONFIG_FILE.absolute()), cfg)
        else:
            # 如果配置文件不存在，保存默认配置
            save_config()
    except Exception as e:
        print(f"加载配置失败: {e}")
        # 使用默认配置
        save_config()


def save_config():
    """保存配置"""
    try:
        cfg.save()
    except Exception as e:
        print(f"保存配置失败: {e}")


def get_theme_text(theme):
    """获取主题对应的文本"""
    if theme == Theme.LIGHT:
        return "浅色"
    elif theme == Theme.DARK:
        return "深色"
    else:
        return "跟随系统"


def get_theme_from_text(theme_text):
    """从文本获取主题"""
    if theme_text == "浅色":
        return Theme.LIGHT
    elif theme_text == "深色":
        return Theme.DARK
    else:
        return Theme.AUTO


def get_zoom_text(zoom_value):
    """获取缩放对应的文本"""
    zoom_map = {
        "100%": "100%",
        "125%": "125%", 
        "150%": "150%",
        "175%": "175%",
        "200%": "200%",
        "Auto": "跟随系统"
    }
    return zoom_map.get(zoom_value, "跟随系统")


def get_zoom_from_text(zoom_text):
    """从文本获取缩放值"""
    zoom_map = {
        "100%": "100%",
        "125%": "125%", 
        "150%": "150%",
        "175%": "175%",
        "200%": "200%",
        "跟随系统": "Auto"
    }
    return zoom_map.get(zoom_text, "Auto")
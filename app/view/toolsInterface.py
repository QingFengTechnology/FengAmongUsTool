# coding:utf-8
"""工具箱页面 UI"""
import json
import logging
import os
import shutil
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QWidget, QVBoxLayout
from qfluentwidgets import (
    ScrollArea, SubtitleLabel, SettingCardGroup, SettingCard,
    FluentIcon, ComboBox, PrimaryPushButton, setFont,
    InfoBar, InfoBarPosition, MessageBox
)

logger = logging.getLogger("FengAmongUsTool")

OLD_HOST_OPTIONS = {
    "normalHostOptions": "B1UAAAEPAAABAAEAAIA/AACAPwAAwD8AAHBBAQECAQAAAAMBDwAAAHgAAAABAAEBAAAEBQAAAAMAAAAKCAIAAAACAAAPBQQAAAADAAA8CgADAAAAAgAAHg8=",
    "normalSearchOptions": "B1UAAAEKAAABAHcAAIA/AACAPwAAwD8AAHBBAQECAQAAAAMBDwAAAHgAAAABAAEBAAAEBQAAAAMAAAAKCAIAAAACAAAPBQQAAAADAAA8CgADAAAAAgAAHg8=",
    "hideNSeekHostOptions": "Bz8AAAIPAAEAAAAAAIA/AACAPwAAwD8BAQIBAQAAAAAASEMzM7M+AACAPgEBAABIQpqZmT8BAP////8AAMBAAABAQA==",
    "hideNSeekSearchOptions": "Bz8AAAIPAAEAAAAAAIA/AACAPwAAwD8BAQIBAQAAAAAASEMzM7M+AACAPgEBAABIQpqZmT8BAP////8AAMBAAABAQA=="
}

NEW_HOST_OPTIONS = {
    "normalHostOptions": "CoQAAAEAZBQYAAAAAgAAoD8AAKA/AADgPwAAtEECAQMCAAAAAwEPAAAAtAAAAAAPAQABAQAJBQAAAAMAAAAKHgIAAAACAAAPBQQAAAADAAA8CgADAAAAAgAAHg8IAAAAAgAACgEJAAAAAgAADx4KAAAAAwAADx4BDAAAAAEAAAMSAAAAAQAADw==",
    "normalSearchOptions": "CoQAAAEAAAoAAAEAdwAAgD8AAIA/AADAPwAAcEEBAQIBAAAAAwEPAAAAeAAAAAEAAQEAAAAJBQAAAAMAAAAKCAIAAAACAAAPBQQAAAADAAA8CgADAAAAAgAAHg8IAAAAAgAACgEJAAAAAgAADx4KAAAAAwAADx4BDAAAAAEAAAMSAAAAAQAADw==",
    "hideNSeekHostOptions": "CkIAAAIAAA8AAQAAAAAAgD8AAIA/AADAPwEBAgEBAAAAAABIQzMzsz4AAIA+AQEAAEhCmpmZPwEA/////wAAwEAAAEBAAA==",
    "hideNSeekSearchOptions": "CkIAAAIAAA8AAQAAAAAAgD8AAIA/AADAPwEBAgEBAAAAAABIQzMzsz4AAIA+AQEAAEhCmpmZPwEA/////wAAwEAAAEBAAA=="
}


class SwitchConfigCard(SettingCard):
    """用于切换新旧配置的设置卡片"""

    def __init__(self, parent=None):
        super().__init__(FluentIcon.SYNC, '切换新旧配置', '切换 Among Us 的配置以适配新旧版本', parent)

        self.modeComboBox = ComboBox(self)
        self.modeComboBox.addItems(['切换旧版配置', '切换新版配置'])
        self.modeComboBox.setCurrentIndex(0)

        self.switchButton = PrimaryPushButton('切换', self)

        # 将控件放置在卡片右侧
        self.hBoxLayout.addWidget(self.modeComboBox, 0, Qt.AlignRight)
        self.hBoxLayout.addSpacing(12)
        self.hBoxLayout.addWidget(self.switchButton, 0, Qt.AlignRight)
        self.hBoxLayout.addSpacing(16)


class ToolsInterface(ScrollArea):
    """工具箱界面（仅 UI 到功能实现）"""

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.scrollWidget = QWidget()
        self.vBoxLayout = QVBoxLayout(self.scrollWidget)

        self.titleLabel = SubtitleLabel('工具集合')
        self.settingGroup = SettingCardGroup('配置工具', self.scrollWidget)
        setFont(self.settingGroup.titleLabel, 14, QFont.Weight.DemiBold)

        self.switchCard = SwitchConfigCard(self.settingGroup)
        self.settingGroup.addSettingCard(self.switchCard)

        self.initWidget()
        self.switchCard.switchButton.clicked.connect(self._onSwitchButtonClicked)

    def initWidget(self):
        """初始化界面"""
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setWidget(self.scrollWidget)
        self.setWidgetResizable(True)
        self.setObjectName('toolsInterface')

        self.vBoxLayout.setSpacing(20)
        self.vBoxLayout.setContentsMargins(36, 36, 36, 36)
        self.vBoxLayout.addWidget(self.titleLabel)
        self.vBoxLayout.addWidget(self.settingGroup)
        self.vBoxLayout.addStretch(1)

        self.scrollWidget.setStyleSheet('QWidget{background:transparent}')
        self.setStyleSheet('ToolsInterface{background:transparent}')

    # -------------------------- 内部工具方法 --------------------------
    def _showInfoBar(self, level: str, title: str, content: str, duration: int = 2500):
        """显示 InfoBar"""
        level_map = {
            'success': InfoBar.success,
            'info': InfoBar.info,
            'warning': InfoBar.warning,
            'error': InfoBar.error
        }
        func = level_map.get(level, InfoBar.info)
        func(
            title,
            content,
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=duration,
            parent=self
        )

    def _getSettingsPath(self) -> Path | None:
        appdata = os.getenv('APPDATA')
        if not appdata:
            return None
        return Path(appdata).parent / 'LocalLow' / 'Innersloth' / 'Among Us' / 'settings.amogus'

    def _loadSettings(self, path: Path) -> dict | None:
        try:
            with path.open('r', encoding='utf-8') as fp:
                return json.load(fp)
        except FileNotFoundError:
            self._showInfoBar('error', '错误', '未找到 settings.amogus 文件')
        except json.JSONDecodeError as e:
            logger.error('解析 settings.amogus 失败: %s', e)
            self._showInfoBar('error', '错误', '配置文件格式不正确，无法解析')
        except Exception as e:
            logger.exception('读取 settings.amogus 时发生异常')
            self._showInfoBar('error', '错误', f'读取配置失败: {e}')
        return None

    def _saveSettings(self, path: Path, data: dict) -> bool:
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open('w', encoding='utf-8') as fp:
                json.dump(data, fp, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            logger.exception('保存 settings.amogus 时发生异常')
            self._showInfoBar('error', '错误', f'保存配置失败: {e}')
            return False

    def _backupSettings(self, source: Path) -> bool:
        backup_path = source.parent / 'settings.amogus.bak'
        try:
            shutil.copy2(source, backup_path)
            logger.info('已创建配置备份: %s', backup_path)
            return True
        except FileNotFoundError:
            self._showInfoBar('error', '错误', '无法找到原始配置文件进行备份')
        except Exception as e:
            logger.exception('备份 settings.amogus 失败')
            self._showInfoBar('error', '错误', f'备份配置失败: {e}')
        return False

    def _applyOldConfig(self, data: dict) -> None:
        input_section = data.setdefault('input', {})
        input_section.pop('inputData', None)

        multiplayer = data.setdefault('multiplayer', {})
        multiplayer.update(OLD_HOST_OPTIONS)
        for extra in ('filterDictionary', 'classicFilterSet', 'hnsFilterSet'):
            multiplayer.pop(extra, None)

    def _applyNewConfig(self, data: dict) -> None:
        input_section = data.setdefault('input', {})
        input_section['inputData'] = {'initialization': 'initialized'}

        multiplayer = data.setdefault('multiplayer', {})
        multiplayer.update(NEW_HOST_OPTIONS)
        multiplayer['filterDictionary'] = multiplayer.get('filterDictionary', {})
        multiplayer['classicFilterSet'] = {'GameMode': 1, 'Filters': []}
        multiplayer['hnsFilterSet'] = {'GameMode': 2, 'Filters': []}

    # -------------------------- 交互逻辑 --------------------------
    def _onSwitchButtonClicked(self):
        option = self.switchCard.modeComboBox.currentText()

        parent_window = self.window() if self.window() else self
        dialog = MessageBox('风险提示', '该操作将修改 Among Us 配置文件，可能存在风险。是否继续？', parent_window)
        dialog.yesButton.setText('是')
        dialog.cancelButton.setText('否')

        if not dialog.exec():
            return

        settings_path = self._getSettingsPath()
        if not settings_path:
            self._showInfoBar('error', '错误', '未找到 APPDATA 环境变量，无法定位配置文件')
            return

        config = self._loadSettings(settings_path)
        if config is None:
            return

        if not self._backupSettings(settings_path):
            return

        if option == '切换旧版配置':
            self._applyOldConfig(config)
            target = '旧版'
        else:
            self._applyNewConfig(config)
            target = '新版'

        if self._saveSettings(settings_path, config):
            self._showInfoBar('success', '完成', f'已成功切换至{target}配置')

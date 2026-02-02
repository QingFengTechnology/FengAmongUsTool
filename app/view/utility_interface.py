# coding: utf-8
import json
import os
import shutil
import logging
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QLabel, QVBoxLayout, QWidget
from qfluentwidgets import (
    ScrollArea,
    setFont,
    SettingCard,
    ComboBox,
    PrimaryPushButton,
    InfoBar,
    InfoBarPosition,
    MessageBox,
    FluentIcon as FIF,
)
from ..common.style_sheet import StyleSheet

logger = logging.getLogger(__name__)


# 旧版配置的多player配置
OLD_MULTIPLAYER_VALUES = {
    "normalHostOptions": "B1UAAAEPAAABAAEAAIA/AACAPwAAwD8AAHBBAQECAQAAAAMBDwAAAHgAAAABAAEBAAAEBQAAAAMAAAAKCAIAAAACAAAPBQQAAAADAAA8CgADAAAAAgAAHg8=",
    "normalSearchOptions": "B1UAAAEKAAABAHcAAIA/AACAPwAAwD8AAHBBAQECAQAAAAMBDwAAAHgAAAABAAEBAAAEBQAAAAMAAAAKCAIAAAACAAAPBQQAAAADAAA8CgADAAAAAgAAHg8=",
    "hideNSeekHostOptions": "Bz8AAAIPAAEAAAAAAIA/AACAPwAAwD8BAQIBAQAAAAAASEMzM7M+AACAPgEBAABIQpqZmT8BAP////8AAMBAAABAQA==",
    "hideNSeekSearchOptions": "Bz8AAAIPAAEAAAAAAIA/AACAPwAAwD8BAQIBAQAAAAAASEMzM7M+AACAPgEBAABIQpqZmT8BAP////8AAMBAAABAQA==",
}

# 新版配置的multiplayer配置
NEW_MULTIPLAYER_VALUES = {
    "normalHostOptions": "CoQAAAEAZBQYAAAAAgAAoD8AAKA/AADgPwAAtEECAQMCAAAAAwEPAAAAtAAAAAAPAQABAQAJBQAAAAMAAAAKHgIAAAACAAAPBQQAAAADAAA8CgADAAAAAgAAHg8IAAAAAgAACgEJAAAAAgAADx4KAAAAAwAADx4BDAAAAAEAAAMSAAAAAQAADw==",
    "normalSearchOptions": "CoQAAAEAAAoAAAEAdwAAgD8AAIA/AADAPwAAcEEBAQIBAAAAAwEPAAAAeAAAAAEAAQEAAAAJBQAAAAMAAAAKCAIAAAACAAAPBQQAAAADAAA8CgADAAAAAgAAHg8IAAAAAgAACgEJAAAAAgAADx4KAAAAAwAADx4BDAAAAAEAAAMSAAAAAQAADw==",
    "hideNSeekHostOptions": "CkIAAAIAAA8AAQAAAAAAgD8AAIA/AADAPwEBAgEBAAAAAABIQzMzsz4AAIA+AQEAAEhCmpmZPwEA/////wAAwEAAAEBAAA==",
    "hideNSeekSearchOptions": "CkIAAAIAAA8AAQAAAAAAgD8AAIA/AADAPwEBAgEBAAAAAABIQzMzsz4AAIA+AQEAAEhCmpmZPwEA/////wAAwEAAAEBAAA==",
}

# 新版配置额外需要添加的字段
NEW_MULTIPLAYER_EXTRA = {
    "filterDictionary": {},
    "classicFilterSet": {
        "GameMode": 1,
        "Filters": []
    },
    "hnsFilterSet": {
        "GameMode": 2,
        "Filters": []
    }
}

# 新版配置input额外需要添加的字段
NEW_INPUT_EXTRA = {
    "inputData": {
        "initialization": "initialized"
    }
}


class SwitchConfigCard(SettingCard):
    """用于切换 Among Us 新旧配置的设置卡片"""

    def __init__(self, parent=None):
        super().__init__(FIF.SYNC, '切换新旧配置', '切换 Among Us 配置以适配不同版本', parent)

        self.modeComboBox = ComboBox(self)
        self.modeComboBox.addItems(['切换旧版配置', '切换新版配置'])
        self.modeComboBox.setCurrentIndex(0)

        self.switchButton = PrimaryPushButton('切换', self)

        self.hBoxLayout.addWidget(self.modeComboBox, 0, Qt.AlignmentFlag.AlignRight)
        self.hBoxLayout.addSpacing(12)
        self.hBoxLayout.addWidget(self.switchButton, 0, Qt.AlignmentFlag.AlignRight)
        self.hBoxLayout.addSpacing(16)

    def getIsNewVersion(self) -> bool:
        """获取当前是否选择切换新版配置"""
        return self.modeComboBox.currentIndex() == 1


class UtilityInterface(ScrollArea):
    """ Utility interface """

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.scrollWidget = QWidget()
        self.vBoxLayout = QVBoxLayout(self.scrollWidget)

        # 添加页面标题
        self.titleLabel = QLabel('实用功能', self)

        # 切换配置卡片
        self.switchCard = SwitchConfigCard(self)

        self.__initWidget()
        self.switchCard.switchButton.clicked.connect(self._onSwitchButtonClicked)

    def __initWidget(self):
        self.setObjectName('utilityInterface')
        self.scrollWidget.setObjectName('scrollWidget')
        StyleSheet.UTILITY_INTERFACE.apply(self)

        # 设置标题样式，与私服安装页面保持一致
        setFont(self.titleLabel, 23, QFont.Weight.DemiBold)
        self.titleLabel.setObjectName('settingLabel')
        # 移动标题到正确位置
        self.titleLabel.move(30, 50)

        self.setViewportMargins(0, 100, 0, 20)
        self.setWidget(self.scrollWidget)
        self.setWidgetResizable(True)

        # 添加卡片到布局
        self.vBoxLayout.addWidget(self.switchCard)

        self.vBoxLayout.setSpacing(30)
        self.vBoxLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.vBoxLayout.setContentsMargins(36, 10, 36, 0)

    def _showInfoBar(self, level: str, title: str, content: str, duration: int = 2500):
        """根据级别显示信息条"""
        if level == 'success':
            InfoBar.success(title, content, orient=Qt.Orientation.Horizontal, isClosable=True,
                          position=InfoBarPosition.TOP_RIGHT, duration=duration, parent=self)
        elif level == 'info':
            InfoBar.info(title, content, orient=Qt.Orientation.Horizontal, isClosable=True,
                       position=InfoBarPosition.TOP_RIGHT, duration=duration, parent=self)
        elif level == 'warning':
            InfoBar.warning(title, content, orient=Qt.Orientation.Horizontal, isClosable=True,
                          position=InfoBarPosition.TOP_RIGHT, duration=duration, parent=self)
        elif level == 'error':
            InfoBar.error(title, content, orient=Qt.Orientation.Horizontal, isClosable=True,
                         position=InfoBarPosition.TOP_RIGHT, duration=duration, parent=self)

    def _onSwitchButtonClicked(self):
        """处理切换配置的按钮点击事件"""
        is_new_version = self.switchCard.getIsNewVersion()
        target = '新版' if is_new_version else '旧版'

        parent_window = self.window() or self
        dialog = MessageBox('风险提示', f'该操作将修改 Among Us 配置文件，可能存在风险。是否切换到{target}配置？', parent_window)
        dialog.yesButton.setText('是')
        dialog.cancelButton.setText('否')

        if not dialog.exec():
            return

        # 获取配置文件路径
        import platform
        if platform.system() == "Windows":
            settings_path = os.path.expandvars(r'%APPDATA%\..\LocalLow\Innersloth\Among Us\settings.amogus')
        else:
            logger.error("不支持的操作系统")
            self._showInfoBar('error', '错误', '不支持的操作系统')
            return

        # 检查文件是否存在
        if not os.path.exists(settings_path):
            logger.error(f"配置文件不存在: {settings_path}")
            self._showInfoBar('error', '错误', '配置文件不存在')
            return

        try:
            # 读取配置文件
            with open(settings_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
        except FileNotFoundError:
            self._showInfoBar('error', '错误', '未找到 settings.amogus 文件')
            return
        except json.JSONDecodeError as exc:
            logger.error(f'解析 settings.amogus 失败: {exc}')
            self._showInfoBar('error', '错误', '配置文件格式不正确，无法解析')
            return
        except Exception:
            logger.exception('读取 settings.amogus 时发生异常')
            self._showInfoBar('error', '错误', '读取配置失败，请查看日志了解详情')
            return

        try:
            # 备份配置文件
            backup_path = settings_path + '.backup'
            shutil.copy2(settings_path, backup_path)
            logger.info(f"已备份配置文件到: {backup_path}")
        except FileNotFoundError:
            self._showInfoBar('error', '错误', '无法找到原始配置文件进行备份')
            return
        except Exception:
            logger.exception('备份 settings.amogus 失败')
            self._showInfoBar('error', '错误', '备份配置失败，请查看日志了解详情')
            return

        # 修改配置
        if is_new_version:
            self._switchToNewVersion(config_data)
            success_message = '已成功切换为新版配置'
        else:
            self._switchToOldVersion(config_data)
            success_message = '已成功切换为旧版配置'

        try:
            # 保存配置
            with open(settings_path, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, ensure_ascii=False, indent=4)
            logger.info(f"配置切换成功: {target}")
        except Exception:
            logger.exception('保存 settings.amogus 时发生异常')
            self._showInfoBar('error', '错误', '保存配置失败，请查看日志了解详情')
            return

        self._showInfoBar('success', '完成', success_message)

    def _switchToNewVersion(self, config_data: dict):
        """ 切换到新版配置 """
        # 修改 multiplayer 中的值
        if 'multiplayer' not in config_data:
            config_data['multiplayer'] = {}
        multiplayer = config_data['multiplayer']
        for key, value in NEW_MULTIPLAYER_VALUES.items():
            multiplayer[key] = value
        # 添加新版额外字段
        multiplayer.update(NEW_MULTIPLAYER_EXTRA)

        # 添加 input 中的 inputData
        if 'input' not in config_data:
            config_data['input'] = {}
        config_data['input'].update(NEW_INPUT_EXTRA)

    def _switchToOldVersion(self, config_data: dict):
        """ 切换到旧版配置 """
        # 修改 multiplayer 中的值
        if 'multiplayer' not in config_data:
            config_data['multiplayer'] = {}
        multiplayer = config_data['multiplayer']
        for key, value in OLD_MULTIPLAYER_VALUES.items():
            multiplayer[key] = value
        # 移除新版额外字段
        for key in NEW_MULTIPLAYER_EXTRA:
            multiplayer.pop(key, None)

        # 移除 input 中的 inputData
        if 'input' in config_data:
            config_data['input'].pop('inputData', None)
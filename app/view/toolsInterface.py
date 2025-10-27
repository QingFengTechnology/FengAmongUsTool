# coding:utf-8
"""工具集合界面"""
import logging
from json import JSONDecodeError

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QWidget, QVBoxLayout
from qfluentwidgets import (
    ScrollArea, SubtitleLabel, SettingCardGroup, SettingCard,
    FluentIcon, ComboBox, PrimaryPushButton, setFont,
    InfoBar, InfoBarPosition, MessageBox
)

from ..module.configSwitcher import (
    applyNewConfig,
    applyOldConfig,
    backupSettings,
    getSettingsPath,
    loadSettings,
    saveSettings,
)

logger = logging.getLogger("FengAmongUsTool")


class SwitchConfigCard(SettingCard):
    """用于切换 Among Us 新旧配置的设置卡片"""

    def __init__(self, parent=None):
        super().__init__(FluentIcon.SYNC, '切换新旧配置', '切换 Among Us 配置以适配不同版本', parent)

        self.modeComboBox = ComboBox(self)
        self.modeComboBox.addItems(['切换旧版配置', '切换新版配置'])
        self.modeComboBox.setCurrentIndex(0)

        self.switchButton = PrimaryPushButton('切换', self)

        self.hBoxLayout.addWidget(self.modeComboBox, 0, Qt.AlignRight)
        self.hBoxLayout.addSpacing(12)
        self.hBoxLayout.addWidget(self.switchButton, 0, Qt.AlignRight)
        self.hBoxLayout.addSpacing(16)


class ToolsInterface(ScrollArea):
    """工具集合界面"""

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.scrollWidget = QWidget()
        self.vBoxLayout = QVBoxLayout(self.scrollWidget)

        self.titleLabel = SubtitleLabel('工具集合')
        self.settingGroup = SettingCardGroup('配置工具', self.scrollWidget)
        setFont(self.settingGroup.titleLabel, 14, QFont.Weight.DemiBold)

        self.switchCard = SwitchConfigCard(self.settingGroup)
        self.settingGroup.addSettingCard(self.switchCard)

        self._init_widget()
        self.switchCard.switchButton.clicked.connect(self._on_switch_button_clicked)

    def _init_widget(self):
        """初始化界面布局和样式"""
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

    def _show_info_bar(self, level: str, title: str, content: str, duration: int = 2500):
        """根据级别显示信息条"""
        level_map = {
            'success': InfoBar.success,
            'info': InfoBar.info,
            'warning': InfoBar.warning,
            'error': InfoBar.error
        }
        func = level_map.get(level, InfoBar.info)
        func(title, content, orient=Qt.Horizontal, isClosable=True,
             position=InfoBarPosition.TOP, duration=duration, parent=self)

    def _on_switch_button_clicked(self):
        """处理切换配置的按钮点击事件"""
        option = self.switchCard.modeComboBox.currentText()

        parent_window = self.window() or self
        dialog = MessageBox('风险提示', '该操作将修改 Among Us 配置文件，可能存在风险。是否继续？', parent_window)
        dialog.yesButton.setText('是')
        dialog.cancelButton.setText('否')

        if not dialog.exec():
            return

        settings_path = getSettingsPath()
        if not settings_path:
            self._show_info_bar('error', '错误', '未找到 APPDATA 环境变量，无法定位配置文件')
            return

        try:
            config = loadSettings(settings_path)
        except FileNotFoundError:
            self._show_info_bar('error', '错误', '未找到 settings.amogus 文件')
            return
        except JSONDecodeError as exc:
            logger.error('解析 settings.amogus 失败: %s', exc)
            self._show_info_bar('error', '错误', '配置文件格式不正确，无法解析')
            return
        except Exception as exc:
            logger.exception('读取 settings.amogus 时发生异常')
            self._show_info_bar('error', '错误', '读取配置失败，请查看日志了解详情')
            return

        try:
            backupSettings(settings_path)
        except FileNotFoundError:
            self._show_info_bar('error', '错误', '无法找到原始配置文件进行备份')
            return
        except Exception as exc:
            logger.exception('备份 settings.amogus 失败')
            self._show_info_bar('error', '错误', '备份配置失败，请查看日志了解详情')
            return

        if option == '切换旧版配置':
            applyOldConfig(config)
            target = '旧版'
        else:
            applyNewConfig(config)
            target = '新版'

        try:
            saveSettings(settings_path, config)
        except Exception as exc:
            logger.exception('保存 settings.amogus 时发生异常')
            self._show_info_bar('error', '错误', '保存配置失败，请查看日志了解详情')
            return

        self._show_info_bar('success', '完成', f'已成功切换至{target}配置')

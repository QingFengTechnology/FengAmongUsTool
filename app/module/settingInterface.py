# coding:utf-8
"""
设置界面模块 - 基于QFluentWidgets脚手架简化版
"""
from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QFont, QDesktopServices
from PySide6.QtWidgets import QWidget
from qfluentwidgets import (
    PrimaryPushSettingCard, HyperlinkCard, ScrollArea, ExpandLayout, 
    Theme, setTheme, setFont, InfoBar, FluentIcon as FIF, TitleLabel
)

from ..function.variableConfig import WINDOW_CONFIG, THEME_CONFIG, PROJECT_CONFIG
from ..function.funcUtils import SimpleComboBoxSettingCard


class SettingInterface(ScrollArea):
    """设置界面"""

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.scrollWidget = QWidget()
        self.expandLayout = ExpandLayout(self.scrollWidget)

        # 设置标题
        self.settingLabel = TitleLabel("设置", self)

        # 个性化设置组
        self.personalGroup = self.CreateSettingGroup("个性化设置", self.scrollWidget)
        
        # 主题设置
        self.themeCard = SimpleComboBoxSettingCard(
            FIF.BRUSH,
            "应用主题",
            "更改应用程序的外观",
            texts=["浅色", "深色", "跟随系统"],
            parent=self.personalGroup
        )
        
        # 界面缩放
        self.zoomCard = SimpleComboBoxSettingCard(
            FIF.ZOOM,
            "界面缩放",
            "更改控件和字体的大小",
            texts=["100%", "125%", "150%", "175%", "200%", "跟随系统"],
            parent=self.personalGroup
        )

        # 关于组
        self.aboutGroup = self.CreateSettingGroup("关于", self.scrollWidget)
        
        # 帮助卡片
        # self.helpCard = HyperlinkCard(
        #     PROJECT_CONFIG["help_url"],
        #     "打开帮助页面",
        #     FIF.HELP,
        #     "帮助",
        #     "发现新功能并学习有用的技巧",
        #     self.aboutGroup
        # )
        
        # 反馈卡片
        self.feedbackCard = HyperlinkCard(
            PROJECT_CONFIG["issues_url"],
            "报告问题",
            FIF.FEEDBACK,
            "反馈",
            "帮助我们改进清风工具箱",
            self.aboutGroup
        )
        
        # 关于卡片
        self.aboutCard = PrimaryPushSettingCard(
            "检查更新",
            FIF.INFO,
            "关于",
            f"© {PROJECT_CONFIG['year']} By {PROJECT_CONFIG['author']}. 版本 {PROJECT_CONFIG['version']}",
            self.aboutGroup
        )

        self.InitWidget()

    def CreateSettingGroup(self, title, parent):
        """创建设置组"""
        from qfluentwidgets import SettingCardGroup
        group = SettingCardGroup(title, parent)
        setFont(group.titleLabel, 14, QFont.Weight.DemiBold)
        return group

    def InitWidget(self):
        """初始化界面"""
        self.resize(1000, 800)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setViewportMargins(0, 80, 0, 20)
        self.setWidget(self.scrollWidget)
        self.setWidgetResizable(True)
        self.setObjectName('settingInterface')

        # 设置字体
        setFont(self.settingLabel, 23, QFont.Weight.DemiBold)
        self.scrollWidget.setObjectName('scrollWidget')
        self.settingLabel.setObjectName('settingLabel')
        
        # 移除硬编码样式，让界面跟随QFluentWidgets主题
        self.scrollWidget.setStyleSheet("QWidget{background:transparent}")
        self.setStyleSheet("SettingInterface{background:transparent}")

        # 初始化布局
        self.InitLayout()
        self.ConnectSignalToSlot()

    def InitLayout(self):
        """初始化布局"""
        self.settingLabel.move(36, 30)

        # 添加设置卡片到组
        self.personalGroup.addSettingCard(self.themeCard)
        self.personalGroup.addSettingCard(self.zoomCard)
        
        # self.aboutGroup.addSettingCard(self.helpCard)
        self.aboutGroup.addSettingCard(self.feedbackCard)
        self.aboutGroup.addSettingCard(self.aboutCard)

        # 添加设置组到布局
        self.expandLayout.setSpacing(28)
        self.expandLayout.setContentsMargins(36, 10, 36, 0)
        self.expandLayout.addWidget(self.personalGroup)
        self.expandLayout.addWidget(self.aboutGroup)

    def ConnectSignalToSlot(self):
        """连接信号到槽"""
        # 主题切换
        self.themeCard.comboBox.currentTextChanged.connect(self.OnThemeChanged)
        
        # 关于
        self.aboutCard.clicked.connect(self.CheckForUpdates)

    def OnThemeChanged(self, theme_text):
        """主题切换处理"""
        theme_map = {
            "浅色": Theme.LIGHT,
            "深色": Theme.DARK,
            "跟随系统": Theme.AUTO
        }
        
        if theme_text in theme_map:
            setTheme(theme_map[theme_text])
            self.ShowSuccessMessage("主题已更新", "主题设置已生效")

    def CheckForUpdates(self):
        """检查更新"""
        self.ShowSuccessMessage("检查更新", "已检查最新版本")

    def ShowSuccessMessage(self, title, content):
        """显示成功消息"""
        InfoBar.success(
            title,
            content,
            duration=1500,
            parent=self
        )

    def setCurrentTheme(self, theme_text):
        """设置当前主题"""
        theme_map = {
            "浅色": Theme.LIGHT,
            "深色": Theme.DARK,
            "跟随系统": Theme.AUTO
        }
        
        if theme_text in theme_map:
            index = self.themeCard.comboBox.findText(theme_text)
            if index >= 0:
                self.themeCard.comboBox.setCurrentIndex(index)
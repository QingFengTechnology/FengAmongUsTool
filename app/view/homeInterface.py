# coding:utf-8
"""
首页界面
"""
from asyncio.windows_events import NULL
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout
from qfluentwidgets import ScrollArea, FluentIcon, qconfig, isDarkTheme

from ..function.variableConfig import PROJECT_CONFIG
from .components.BannerWidget import BannerWidget
from .components.ElevatedCardView import ElevatedCardView


class HomeInterface(ScrollArea):
    """首页界面"""

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.view = QWidget(self)
        self.vBoxLayout = QVBoxLayout(self.view)

        self.setObjectName('HomeInterface')
        self.view.setObjectName('view')
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setWidget(self.view)
        self.setWidgetResizable(True)

        self.banner = BannerWidget(self.view)
        self.functionCardView = ElevatedCardView("", self.view)

        self.initWidget()

    def initWidget(self):
        """初始化组件"""
        self.vBoxLayout.setSpacing(0)
        self.vBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.vBoxLayout.addWidget(self.banner, 6)
        self.vBoxLayout.addSpacing(10)
        self.vBoxLayout.addWidget(self.functionCardView, 4)
        
        # 添加功能卡片
        self.initFunctionCards()

        # 应用初始样式
        self.updateStyleSheet()
        
        # 监听主题变化
        qconfig.themeChanged.connect(self.onThemeChanged)

    def onThemeChanged(self, theme):
        """主题变化处理"""
        self.updateStyleSheet()

    def updateStyleSheet(self):
        """根据当前主题更新样式表"""
        # 检查当前是否为深色模式
        if isDarkTheme():
            # 深色模式样式
            self.setStyleSheet("""
                HomeInterface {
                    background-color: rgba(28, 28, 28, 0.8);
                }
                #view {
                    background-color: transparent;
                }
                BannerWidget {
                    background-color: transparent;
                    border: none;
                }
                ElevatedCardView {
                    background-color: transparent;
                    border: none;
                }
                BannerWidget > QLabel#titleLabel {
                    font: 28px 'Microsoft YaHei';
                    font-weight: 600;
                    color: white;
                    background: transparent;
                    margin-left: 18px;
                }
                BannerWidget > QLabel#subtitleLabel {
                    font: 12px 'Microsoft YaHei';
                    color: rgba(255, 255, 255, 0.8);
                    background: transparent;
                    margin-left: 24px;
                }
                QLabel#viewTitleLabel {
                    font: 18px 'Microsoft YaHei';
                    font-weight: 600;
                    color: white;
                    background: transparent;
                    margin-bottom: 12px;
                }
            """)
        else:
            # 浅色模式样式
            self.setStyleSheet("""
                HomeInterface {
                    background-color: rgba(249, 249, 249, 0.8);
                }
                #view {
                    background-color: transparent;
                }
                BannerWidget {
                    background-color: transparent;
                    border: none;
                }
                ElevatedCardView {
                    background-color: transparent;
                    border: none;
                }
                BannerWidget > QLabel#titleLabel {
                    font: 28px 'Microsoft YaHei';
                    font-weight: 600;
                    color: white;
                    background: transparent;
                    margin-left: 18px;
                }
                BannerWidget > QLabel#subtitleLabel {
                    font: 12px 'Microsoft YaHei';
                    color: rgba(255, 255, 255, 0.8);
                    background: transparent;
                    margin-left: 24px;
                }
                QLabel#viewTitleLabel {
                    font: 18px 'Microsoft YaHei';
                    font-weight: 600;
                    color: black;
                    background: transparent;
                    margin-bottom: 12px;
                }
            """)

    def initFunctionCards(self):
        """初始化功能卡片"""
        # 只添加实际需要的功能卡片
        cards = [
            (FluentIcon.SETTING, "设置", "程序设置和配置管理", "settingInterface"),
            (FluentIcon.GAME, "私服管理", "私人服务器管理功能", "privateServerInterface"),
            (FluentIcon.APPLICATION, "工具集", "各种实用工具集合", "toolsInterface"),
            (FluentIcon.INFO, "关于", "程序信息和版本信息", "aboutInterface")
        ]

        for icon, title, content, routeKey in cards:
            self.functionCardView.addElevatedCard(
                icon, title, content, routeKey, self.onCardClicked
            )

    def onCardClicked(self, routeKey):
        """卡片点击事件"""
        print(f"点击了卡片: {routeKey}")
        # 这里可以添加导航逻辑
        if hasattr(self.parent(), 'switchToInterface'):
            self.parent().switchToInterface(routeKey)
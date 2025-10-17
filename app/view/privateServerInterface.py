# coding:utf-8
"""
私服安装界面模块
"""
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QFrame
from qfluentwidgets import (
    SubtitleLabel, BodyLabel, CheckBox, PrimaryPushButton,
    SimpleCardWidget, VBoxLayout, FluentIcon, InfoBarPosition, ScrollArea, InfoBar
)

from ..function.serverManager import ServerLoader, installPrivateServer
from ..function.logManager import logInfo


class PrivateServerInterface(ScrollArea):
    """私服安装界面类"""
    
    # 定义信号用于在主线程中显示消息
    showMessageSignal = Signal(str, str, object)
    
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.serverConfig = {}
        self.serverCheckboxes = {}
        
        self.scrollWidget = QWidget()
        self.vBoxLayout = QVBoxLayout(self.scrollWidget)
        
        # 连接信号
        self.showMessageSignal.connect(self._showMessage)
        
        self.initWidget()
        
        # 创建服务器加载器
        self.serverLoader = ServerLoader(self)
        self.serverLoader.serversLoaded.connect(self.onServersLoaded)
        self.serverLoader.loadFailed.connect(self.onLoadFailed)
        
        # 开始加载服务器列表
        self.loadServers()
        
    def initWidget(self):
        """初始化界面"""
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setWidget(self.scrollWidget)
        self.setWidgetResizable(True)
        self.setObjectName('privateServerInterface')
        
        # 设置布局边距，与其他界面保持一致
        self.vBoxLayout.setSpacing(20)
        self.vBoxLayout.setContentsMargins(36, 36, 36, 36)
        
        # 标题
        titleLabel = SubtitleLabel('私服安装')
        self.vBoxLayout.addWidget(titleLabel)
        
        # 分隔线
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        self.vBoxLayout.addWidget(separator)
        
        # 服务器选择区域
        self.serverCard = SimpleCardWidget()
        self.serverLayout = VBoxLayout(self.serverCard)
        
        self.serverTitle = BodyLabel('选择服务器:')
        self.serverLayout.addWidget(self.serverTitle)
        
        # 添加加载提示
        self.loadingLabel = BodyLabel('正在加载服务器列表...')
        self.serverLayout.addWidget(self.loadingLabel)
        
        self.vBoxLayout.addWidget(self.serverCard)
        
        # 按钮区域
        buttonCard = SimpleCardWidget()
        buttonLayout = QHBoxLayout(buttonCard)
        
        self.installButton = PrimaryPushButton('安装私服')
        self.installButton.clicked.connect(self.installPrivateServer)
        buttonLayout.addWidget(self.installButton)
        
        self.vBoxLayout.addWidget(buttonCard)
        self.vBoxLayout.addStretch(1)
        
        # 设置样式，与其他界面保持一致
        self.scrollWidget.setStyleSheet("QWidget{background:transparent}")
        self.setStyleSheet("PrivateServerInterface{background:transparent}")
    
    def loadServers(self):
        """加载服务器列表"""
        self.serverLoader.loadServers()
    
    def onServersLoaded(self, server_config):
        """服务器列表加载完成"""
        logInfo("服务器列表加载成功")
        self.serverConfig = server_config
        self.updateServerCheckboxes()
        
    def onLoadFailed(self, error_msg):
        """服务器列表加载失败"""
        logInfo(f"服务器列表加载失败: {error_msg}")
        # 移除加载提示
        self.loadingLabel.setParent(None)
        self.loadingLabel.deleteLater()
        
        # 显示错误信息
        errorLabel = BodyLabel(f'加载失败: {error_msg}')
        errorLabel.setStyleSheet("color: red;")
        self.serverLayout.addWidget(errorLabel)
        
        # 使用默认配置
        self.serverConfig = {
            "server1": {"name": "清风", "filename": "QingFeng.json", "enabled": False},
            "server2": {"name": "帆船", "filename": "FanChuan.json", "enabled": False}
        }
        self.updateServerCheckboxes()
    
    def updateServerCheckboxes(self):
        """更新服务器复选框"""
        # 移除加载提示
        if self.loadingLabel:
            self.loadingLabel.setParent(None)
            self.loadingLabel.deleteLater()
            self.loadingLabel = None
            
        # 清除现有的复选框
        for checkbox in self.serverCheckboxes.values():
            checkbox.setParent(None)
            checkbox.deleteLater()
        self.serverCheckboxes.clear()
        
        # 创建新的复选框
        for serverId, config in self.serverConfig.items():
            checkbox = CheckBox(config['name'])
            checkbox.setChecked(config['enabled'])
            # 使用默认参数捕获当前的serverId值
            checkbox.stateChanged.connect(lambda state, sid=serverId: self.toggleServer(sid, state))
            self.serverLayout.addWidget(checkbox)
            self.serverCheckboxes[serverId] = checkbox
    
    def toggleServer(self, serverId, state):
        """切换服务器状态"""
        if serverId in self.serverConfig:
            # PyQt6/PySide6中，选中状态的值为2
            self.serverConfig[serverId]['enabled'] = (state == 2)
            logInfo(f"服务器 {self.serverConfig[serverId]['name']} {'启用' if state == 2 else '禁用'}")
        
    def installPrivateServer(self):
        """安装私服"""
        # 检查是否有服务器被选中
        enabledServers = []
        for config in self.serverConfig.values():
            if config['enabled']:
                enabledServers.append(config)
        
        if not enabledServers:
            InfoBar.warning(
                title='警告',
                content='请至少选择一个服务器！',
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=2000,
                parent=self
            )
            return False
            
        server_names = []
        for s in enabledServers:
            server_names.append(s['name'])
        logInfo(f"开始安装私服，选择的服务器: {', '.join(server_names)}")
        
        # 创建一个包装函数来处理消息回调
        def messageCallback(title, content, position):
            # 在显示消息后重新启用按钮
            self.installButton.setEnabled(True)
            self.showMessageSignal.emit(title, content, position)
        
        success = installPrivateServer(
            self.serverConfig,
            self.log,
            messageCallback
        )
        
        if success:
            self.installButton.setEnabled(False)
            # 安装完成后重新启用按钮
            # 按钮启用操作将在消息回调中执行
    
    def _showMessage(self, title, content, position):
        """在主线程中显示消息"""
        if title == '成功':
            InfoBar.success(
                title=title,
                content=content,
                orient=Qt.Horizontal,
                isClosable=True,
                position=position,
                duration=2000,
                parent=self
            )
        elif title == '警告':
            InfoBar.warning(
                title=title,
                content=content,
                orient=Qt.Horizontal,
                isClosable=True,
                position=position,
                duration=2000,
                parent=self
            )
        else:
            InfoBar.error(
                title=title,
                content=content,
                orient=Qt.Horizontal,
                isClosable=True,
                position=position,
                duration=2000,
                parent=self
            )
    
    def log(self, message):
        """添加日志"""
        logInfo(message)
        
    def addToNavigation(self, mainWindow):
        """添加到导航栏"""
        from qfluentwidgets import NavigationItemPosition
        mainWindow.addSubInterface(
            self, 
            FluentIcon.DOWNLOAD, 
            '私服安装',
            NavigationItemPosition.SCROLL
        )
# coding:utf-8
"""
日志管理器 - 基于Python logging库的日志系统
"""
import logging
from pathlib import Path


class LogManager:
    """日志管理器类"""
    
    def __init__(self):
        self.logger = None
        self.logFile = None
        self.setupLogging()
    
    def setupLogging(self):
        """设置日志系统"""
        # 在项目根目录创建日志文件
        projectRoot = Path(__file__).parent.parent.parent
        self.logFile = projectRoot / "FengAmongUsTool.log"
        
        # 配置根日志记录器
        self.logger = logging.getLogger("FengAmongUsTool")
        self.logger.setLevel(logging.INFO)
        
        # 清除已有的处理器
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)
        
        # 创建格式化器
        formatter = logging.Formatter(
            fmt='[%(asctime)s] [%(levelname)s] - %(message)s',
            datefmt='%H:%M:%S'
        )
        
        # 文件处理器（每次启动时覆盖）
        fileHandler = logging.FileHandler(self.logFile, mode='w', encoding='utf-8')
        fileHandler.setLevel(logging.INFO)
        fileHandler.setFormatter(formatter)
        
        # 控制台处理器
        consoleHandler = logging.StreamHandler()
        consoleHandler.setLevel(logging.INFO)
        consoleHandler.setFormatter(formatter)
        
        # 添加处理器
        self.logger.addHandler(fileHandler)
        self.logger.addHandler(consoleHandler)
        
        # 记录日志系统启动
        self.logger.info("日志系统初始化完成")
    
    def getLogger(self):
        """获取日志记录器"""
        return self.logger
    
    def logInfo(self, message):
        """记录信息级别日志"""
        if self.logger:
            self.logger.info(message)
    
    def logWarning(self, message):
        """记录警告级别日志"""
        if self.logger:
            self.logger.warning(message)
    
    def logError(self, message):
        """记录错误级别日志"""
        if self.logger:
            self.logger.error(message)
    
    def logDebug(self, message):
        """记录调试级别日志"""
        if self.logger:
            self.logger.debug(message)


# 创建全局日志管理器实例
logManagerInstance = LogManager()


def logInfo(message):
    """记录信息级别日志"""
    logManagerInstance.logInfo(message)


def logMessage(message):
    """记录信息级别日志（兼容旧接口）"""
    logManagerInstance.logInfo(message)


def logWarning(message):
    """记录警告级别日志"""
    logManagerInstance.logWarning(message)


def logError(message):
    """记录错误级别日志"""
    logManagerInstance.logError(message)


def getLogger():
    """获取日志记录器"""
    return logManagerInstance.getLogger()
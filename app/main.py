# Among Us Tools v1.0.9 by 忆梦
# 本程序仅供学习交流使用，请勿用于商业用途。
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
import os
import psutil
import random
from datetime import datetime
import urllib.request
import ssl
import tempfile
import shutil
import concurrent.futures
import threading
import logging
import logging.handlers

class AmongUsTools:
    def __init__(self, root):
        self.root = root
        self.root.title("Among Us 私服安装工具箱")
        
        # 设置窗口大小
        self.root.geometry("600x400")
        self.root.resizable(False, False)
        
        # 设置窗口居中显示
        self.center_window()
        
        # 设置样式
        self.root.configure(bg='#f0f0f0')

        # 初始化日志系统
        self.init_logging()

        # 创建选项卡
        self.tabControl = ttk.Notebook(root)
        
        # 创建"私服安装"选项卡
        self.install_tab = tk.Frame(self.tabControl, bg='#f0f0f0')
        self.tabControl.add(self.install_tab, text="私服安装")
        
        # 创建"更多"选项卡
        self.more_tab = tk.Frame(self.tabControl, bg='#f0f0f0')
        self.tabControl.add(self.more_tab, text="更多")
        
        # 默认显示"私服安装"选项卡
        self.tabControl.pack(expand=1, fill="both")
        
        # 创建"私服安装"页的内容
        self.create_install_tab()
        self.create_more_tab()
        
        # 初始化今日人品点击次数
        self.rp_click_count = 0
        # 初始化彩蛋触发次数
        self.rp_egg_trigger_count = random.randint(1, 99)
        # 彩蛋语录
        self.egg_quotes = [
            "你是大笨蛋！",
            "有一个baka正在看我！",
            "作者是忆梦哦！",
            "哈呀哈基米，米呀米记哈~",
            "恭喜你中大奖啦！大奖就是没有大奖！",
            "草飞喵呜！"
        ]
        
        # 存储regioninfo.json文件路径
        self.regioninfo_path = None
        
        # 存储自定义服务器数据
        self.custom_server_data = None
        
        # 存储从远程获取的服务器配置
        self.remote_server_configs = {}
        
        # GitHub仓库地址
        self.github_repo_url = "https://raw.githubusercontent.com/YvonneOfficial/AUT-Servers/main/Servers"
        # 镜像源地址
        self.mirror_repo_urls = [
            "https://ghfast.top/https://raw.githubusercontent.com/YvonneOfficial/AUT-Servers/main/Servers",
            "https://gh-proxy.com/https://raw.githubusercontent.com/YvonneOfficial/AUT-Servers/main/Servers"
        ]
        
    def init_logging(self):
        """初始化日志系统"""
        # 配置日志格式
        log_format = logging.Formatter(
            '[%(levelname)s] %(asctime)s %(message)s', 
            datefmt='%Y/%m/%d %H:%M:%S'
        )
        
        # 创建logger
        self.logger = logging.getLogger('AUTools')
        self.logger.setLevel(logging.DEBUG)
        
        # 创建控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(log_format)
        
        # 添加处理器到logger
        self.logger.addHandler(console_handler)
        
        self.logger.info("AUTools日志系统初始化完成")
        
    def center_window(self):
        """将窗口居中显示"""
        # 强制更新窗口以获取准确的尺寸信息
        self.root.update_idletasks()
        
        # 获取窗口尺寸
        width = 600
        height = 400
        
        # 获取屏幕尺寸
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # 计算居中位置
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        
        # 设置窗口位置和大小
        self.root.geometry(f"{width}x{height}+{x}+{y}")
        
    def create_install_tab(self):
        # 标题
        title_label = tk.Label(self.install_tab, text="Among Us 私服安装", font=("Arial", 18, "bold"), 
                              bg='#f0f0f0', fg='#333333')
        title_label.pack(pady=15)
        
        # 描述标签
        desc_label = tk.Label(self.install_tab, text="选择要添加的服务器源，然后安装到游戏中", 
                             font=("Arial", 10), bg='#f0f0f0', fg='#666666')
        desc_label.pack(pady=5)
        
        # 服务器源选择框架
        self.server_frame = tk.LabelFrame(self.install_tab, text="选择服务器源", padx=20, pady=15, 
                                    font=("Arial", 12, "bold"), bg='#f0f0f0', fg='#333333')
        self.server_frame.pack(pady=20, padx=30, fill="x")
        
        # 服务器源说明
        server_desc = tk.Label(self.server_frame, text="请选择一个或多个服务器源添加到游戏中：", 
                              font=("Arial", 9), bg='#f0f0f0', fg='#555555')
        server_desc.pack(anchor='w', pady=(0, 10))
        
        # 服务器源选择变量
        self.server_vars = {
            "清风": tk.BooleanVar(),
            "帆船": tk.BooleanVar(),
            "核电站": tk.BooleanVar(),
            "碧水港": tk.BooleanVar(),
            "Niko": tk.BooleanVar()
        }
        
        # 初始化复选框引用字典
        self.server_checkbuttons = {}
        self.server_labels = {}
        
        # 创建复选框容器
        self.server_container = tk.Frame(self.server_frame, bg='#f0f0f0')
        self.server_container.pack()
        
        # 创建复选框
        for i, (server_name, var) in enumerate(self.server_vars.items()):
            cb_frame = tk.Frame(self.server_container, bg='#f0f0f0')
            cb_frame.pack(side=tk.LEFT, padx=15)
            
            cb = tk.Checkbutton(cb_frame, variable=var, bg='#f0f0f0', activebackground='#f0f0f0')
            cb.pack()
            self.server_checkbuttons[server_name] = cb  # 保存引用
            
            cb_label = tk.Label(cb_frame, text=server_name, font=("Arial", 10), bg='#f0f0f0')
            cb_label.pack()
            self.server_labels[server_name] = cb_label  # 保存引用
        
        # 初始化时禁用服务器选择
        self.disable_server_selection()
        
        # 按钮框架
        button_frame = tk.Frame(self.install_tab, bg='#f0f0f0')
        button_frame.pack(pady=30)
        
        # 载入数据按钮 - 与开始安装按钮样式一致
        load_btn = tk.Button(button_frame, text="载入数据", command=self.load_data, 
                            bg="#4CAF50", fg="white", font=("Arial", 12, "bold"), 
                            width=12, height=1, relief=tk.RAISED, bd=2)
        load_btn.pack(side=tk.LEFT, padx=15)
        
        # 开始安装按钮
        install_btn = tk.Button(button_frame, text="开始安装", command=self.install_servers, 
                               bg="#4CAF50", fg="white", font=("Arial", 12, "bold"), 
                               width=12, height=1, relief=tk.RAISED, bd=2)
        install_btn.pack(side=tk.LEFT, padx=15)
        
        # 状态标签框架
        status_frame = tk.Frame(self.install_tab, bg='#f0f0f0')
        status_frame.pack(side=tk.BOTTOM, fill='x', pady=15)
        
        # 状态标签
        self.status_label = tk.Label(status_frame, text="请先载入数据", fg="gray", 
                                    bg='#f0f0f0', font=("Arial", 9))
        self.status_label.pack()
        
    def disable_server_selection(self):
        """禁用服务器选择框"""
        for server_name in self.server_vars.keys():
            self.server_checkbuttons[server_name].config(state=tk.DISABLED)
            self.server_labels[server_name].config(fg='#aaaaaa')  # 灰色文字表示禁用状态
        
    def enable_server_selection(self):
        """启用服务器选择框"""
        for server_name in self.server_vars.keys():
            self.server_checkbuttons[server_name].config(state=tk.NORMAL)
            self.server_labels[server_name].config(fg='#000000')  # 黑色文字表示启用状态
        
    def create_more_tab(self):
        # 更多页面内容
        title_label = tk.Label(self.more_tab, text="更多功能", font=("Arial", 18, "bold"), 
                              bg='#f0f0f0', fg='#333333')
        title_label.pack(pady=20)
        
        # 创建画布用于装饰性分隔线
        canvas = tk.Canvas(self.more_tab, height=2, bg='#f0f0f0', highlightthickness=0)
        canvas.pack(fill='x', padx=50, pady=10)
        canvas.create_line(0, 1, 500, 1, fill='#cccccc', width=2)
        
        # 功能按钮框架
        button_frame = tk.Frame(self.more_tab, bg='#f0f0f0')
        button_frame.pack(pady=20, expand=True)
        
        # 今日人品按钮
        rp_btn = tk.Button(button_frame, text="今日人品", command=self.check_personality,
                          bg="#FFA500", fg="white", font=("Arial", 12, "bold"),
                          width=20, height=2, relief=tk.RAISED, bd=2)
        rp_btn.pack(pady=10)
        
        # 小游戏按钮
        game_btn = tk.Button(button_frame, text="小游戏", command=self.mini_game,
                           bg="#2196F3", fg="white", font=("Arial", 12, "bold"),
                           width=20, height=2, relief=tk.RAISED, bd=2)
        game_btn.pack(pady=10)
        
        # 修复旧版黑屏按钮
        fix_btn = tk.Button(button_frame, text="修复旧版黑屏", command=self.fix_black_screen,
                           bg="#9E9E9E", fg="white", font=("Arial", 12, "bold"),
                           width=20, height=2, relief=tk.RAISED, bd=2)
        fix_btn.pack(pady=10)
        
        # 添加按钮点击事件日志
        rp_btn.bind("<Button-1>", lambda e: self.logger.info("用户点击了今日人品按钮"))
        game_btn.bind("<Button-1>", lambda e: self.logger.info("用户点击了小游戏按钮"))
        fix_btn.bind("<Button-1>", lambda e: self.logger.info("用户点击了修复旧版黑屏按钮"))
        
    def check_personality(self):
        """检查今日人品功能"""
        self.logger.info("用户点击今日人品按钮")
        # 增加点击次数
        self.rp_click_count += 1
        
        # 检查是否触发彩蛋
        egg_triggered = False
        if self.rp_click_count >= self.rp_egg_trigger_count:
            # 重置计数器
            self.rp_click_count = 0
            self.rp_egg_trigger_count = random.randint(1, 99)
            # 标记彩蛋已触发
            egg_triggered = True
            self.logger.debug("触发彩蛋：用户点击次数达到随机触发次数")
        
        # 检查是否触发"不要再点我啦!"彩蛋
        nag_egg_triggered = False
        if self.rp_click_count > 5:
            nag_egg_triggered = True
            self.logger.debug("触发连续点击彩蛋：用户连续点击超过5次")
            
        # 检查是否触发100次以上的特殊彩蛋
        special_egg_triggered = False
        if self.rp_click_count > 100:
            special_egg_triggered = True
            self.logger.debug("触发100次以上特殊彩蛋：用户连续点击超过100次")
        
        # 获取AUTools文件夹路径
        username = os.getenv('USERNAME')
        folder_path = f"C:\\Users\\{username}\\AppData\\Local\\AUTools"
        
        # 如果文件夹不存在则创建
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
            self.logger.debug(f"创建AUTools文件夹: {folder_path}")
            
        file_path = os.path.join(folder_path, "rp.json")
        today = datetime.now().strftime("%Y/%m/%d")
        
        # 获取每日一言或彩蛋语录
        if special_egg_triggered:
            # 使用100次以上的特殊语录
            hitokoto = "你是无敌的无敌的大笨蛋！"
            self.logger.debug("使用100次以上特殊语录")
        elif egg_triggered:
            # 使用彩蛋语录
            hitokoto = random.choice(self.egg_quotes)
            self.logger.debug("使用彩蛋语录替换每日一言")
        else:
            # 获取每日一言
            try:
                import urllib.request
                import ssl
                
                # 创建不验证SSL证书的上下文（某些环境下可能需要）
                ssl_context = ssl.create_default_context()
                ssl_context.check_hostname = False
                ssl_context.verify_mode = ssl.CERT_NONE
                
                # 获取每日一言
                hitokoto_url = "https://v1.hitokoto.cn/?encode=text"
                request = urllib.request.Request(hitokoto_url)
                response = urllib.request.urlopen(request, context=ssl_context, timeout=5)
                hitokoto = response.read().decode('utf-8')
                self.logger.debug("成功获取每日一言")
            except Exception as e:
                hitokoto = "今日无言"
                self.logger.warning(f"获取每日一言失败: {str(e)}")
        
        # 如果文件存在
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    
                # 解析文件内容
                time_line = lines[0].strip() if len(lines) > 0 else ""
                rp_line = lines[1].strip() if len(lines) > 1 else ""
                
                # 检查时间是否为今日
                if time_line.startswith("time="):
                    stored_time = time_line.split("=")[1]
                    if stored_time == today:
                        # 今日已生成人品值
                        if rp_line.startswith("rp="):
                            rp_value = rp_line.split("=")[1]
                            self.logger.info(f"用户今日人品值: {rp_value}")
                            # 根据是否触发连续点击彩蛋决定标题
                            if nag_egg_triggered:
                                messagebox.showinfo("不要再点我啦！", f"你今日的人品是 {rp_value}！\n\n{hitokoto}")
                            else:
                                messagebox.showinfo("今日人品", f"你今日的人品是 {rp_value}！\n\n{hitokoto}")
                            return
                
                # 不是今日或者文件格式不正确，重新生成
                rp_value = str(random.randint(0, 100))
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(f"time={today}\n")
                    f.write(f"rp={rp_value}\n")
                    
                self.logger.info(f"重新生成用户今日人品值: {rp_value}")
                # 根据是否触发连续点击彩蛋决定标题
                if nag_egg_triggered:
                    messagebox.showinfo("不要再点我啦！", f"你今日的人品是 {rp_value}！\n\n{hitokoto}")
                else:
                    messagebox.showinfo("今日人品", f"你今日的人品是 {rp_value}！\n\n{hitokoto}")
                
            except Exception as e:
                # 文件读取或解析出错，重新生成
                self.logger.error(f"读取人品值文件出错: {str(e)}")
                rp_value = str(random.randint(0, 100))
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(f"time={today}\n")
                    f.write(f"rp={rp_value}\n")
                    
                self.logger.info(f"重新生成用户今日人品值: {rp_value}")
                # 根据是否触发连续点击彩蛋决定标题
                if nag_egg_triggered:
                    messagebox.showinfo("不要再点我啦！", f"你今日的人品是 {rp_value}！\n\n{hitokoto}")
                else:
                    messagebox.showinfo("今日人品", f"你今日的人品是 {rp_value}！\n\n{hitokoto}")
        else:
            # 文件不存在，创建新文件
            rp_value = str(random.randint(0, 100))
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(f"time={today}\n")
                f.write(f"rp={rp_value}\n")
                
            self.logger.info(f"首次生成用户今日人品值: {rp_value}")
            # 根据是否触发连续点击彩蛋决定标题
            if nag_egg_triggered:
                messagebox.showinfo("不要再点我啦！", f"你今日的人品是 {rp_value}！\n\n{hitokoto}")
            else:
                messagebox.showinfo("今日人品", f"你今日的人品是 {rp_value}！\n\n{hitokoto}")
            
    def mini_game(self):
        """小游戏功能"""
        self.logger.info("用户点击小游戏按钮")
        # 创建小游戏选择窗口
        game_window = tk.Toplevel(self.root)
        game_window.title("小游戏")
        game_window.geometry("300x200")
        game_window.resizable(False, False)
        game_window.configure(bg='#f0f0f0')
        
        # 窗口居中
        game_window.update_idletasks()
        width = 300
        height = 200
        x = (game_window.winfo_screenwidth() // 2) - (width // 2)
        y = (game_window.winfo_screenheight() // 2) - (height // 2)
        game_window.geometry(f"{width}x{height}+{x}+{y}")
        
        # 标题
        title_label = tk.Label(game_window, text="选择小游戏", font=("Arial", 16, "bold"), 
                              bg='#f0f0f0', fg='#333333')
        title_label.pack(pady=20)
        
        # 贪吃蛇按钮
        snake_btn = tk.Button(game_window, text="贪吃蛇", command=lambda: self.start_snake_game(game_window),
                             bg="#4CAF50", fg="white", font=("Arial", 12, "bold"),
                             width=15, height=2, relief=tk.RAISED, bd=2)
        snake_btn.pack(pady=10)
        
    def fix_black_screen(self):
        """修复旧版黑屏功能"""
        self.logger.info("用户点击修复旧版黑屏按钮")
        # 显示警告对话框
        warning_result = messagebox.askyesno(
            "警告",
            "该操作将根据您当前的游戏设置生成适用于旧版的设置文件，可能存在一定风险。\n\n是否继续？",
            icon='warning'
        )
        
        if not warning_result:
            self.logger.info("用户取消修复旧版黑屏操作")
            return
            
        try:
            # 获取游戏设置文件路径
            appdata_local_low = os.path.expandvars(r"%LOCALAPPDATA%\..\LocalLow")
            settings_path = os.path.join(appdata_local_low, "Innersloth", "Among Us", "settings.amogus")
            
            # 检查当前设置文件是否存在
            if not os.path.exists(settings_path):
                self.logger.warning("当前设置文件不存在")
                messagebox.showerror("错误", "未找到当前设置文件，请先运行游戏以生成设置文件")
                return
                
            # 读取当前设置文件
            with open(settings_path, 'r', encoding='utf-8') as f:
                current_settings = json.load(f)
                
            self.logger.debug("成功读取当前设置文件")
            
            # 转换为旧版设置
            old_version_settings = self.convert_to_old_settings(current_settings)
            
            # 备份原文件（如果存在）
            if os.path.exists(settings_path + ".backup"):
                os.remove(settings_path + ".backup")
            os.rename(settings_path, settings_path + ".backup")
            self.logger.debug("已备份原设置文件")
            
            # 写入旧版设置
            with open(settings_path, 'w', encoding='utf-8') as f:
                json.dump(old_version_settings, f, ensure_ascii=False, indent=2)
            
            self.logger.info("成功生成并写入旧版设置文件")
            messagebox.showinfo("成功", "已根据您的当前设置生成适用于旧版的游戏配置！\n原文件已备份为 settings.amogus.backup")
        except Exception as e:
            self.logger.error(f"修复旧版黑屏失败: {str(e)}")
            messagebox.showerror("错误", f"操作失败: {str(e)}")

    def convert_to_old_settings(self, new_settings):
        """
        将新版设置转换为旧版设置
        """
        self.logger.debug("开始转换设置文件格式")
        
        # 复制基础设置
        old_settings = {}
        
        # 复制通用设置部分
        if "gameplay" in new_settings:
            old_settings["gameplay"] = new_settings["gameplay"].copy()
            
        if "accessibility" in new_settings:
            old_settings["accessibility"] = new_settings["accessibility"].copy()
            
        if "audio" in new_settings:
            old_settings["audio"] = new_settings["audio"].copy()
            
        if "video" in new_settings:
            old_settings["video"] = new_settings["video"].copy()
            
        if "language" in new_settings:
            old_settings["language"] = new_settings["language"].copy()
            
        # 处理输入设置（移除inputData）
        if "input" in new_settings:
            old_settings["input"] = new_settings["input"].copy()
            # 移除新版特有的inputData字段
            if "inputData" in old_settings["input"]:
                del old_settings["input"]["inputData"]
                
        # 处理多人游戏设置（移除新版特有的字段并使用旧版选项值）
        if "multiplayer" in new_settings:
            old_settings["multiplayer"] = new_settings["multiplayer"].copy()
            # 移除新版特有的字段
            new_multiplayer_fields = [
                "filterDictionary", 
                "classicFilterSet", 
                "hnsFilterSet"
            ]
            
            for field in new_multiplayer_fields:
                if field in old_settings["multiplayer"]:
                    del old_settings["multiplayer"][field]
            
            # 使用旧版的选项值替换新版的选项值
            old_settings["multiplayer"]["normalHostOptions"] = "B1UAAAEPAAABAAEAAIA/AACAPwAAwD8AAHBBAQECAQAAAAMBDwAAAHgAAAABAAEBAAAEBQAAAAMAAAAKCAIAAAACAAAPBQQAAAADAAA8CgADAAAAAgAAHg8="
            old_settings["multiplayer"]["normalSearchOptions"] = "B1UAAAEKAAABAHcAAIA/AACAPwAAwD8AAHBBAQECAQAAAAMBDwAAAHgAAAABAAEBAAAEBQAAAAMAAAAKCAIAAAACAAAPBQQAAAADAAA8CgADAAAAAgAAHg8="
            old_settings["multiplayer"]["hideNSeekHostOptions"] = "Bz8AAAIPAAEAAAAAAIA/AACAPwAAwD8BAQIBAQAAAAAASEMzM7M+AACAPgEBAABIQpqZmT8BAP////8AAMBAAABAQA=="
            old_settings["multiplayer"]["hideNSeekSearchOptions"] = "Bz8AAAIPAAEAAAAAAIA/AACAPwAAwD8BAQIBAQAAAAAASEMzM7M+AACAPgEBAABIQpqZmT8BAP////8AAMBAAABAQA=="
                    
        # 设置数据版本
        old_settings["dataVersion"] = 1
        
        self.logger.debug("设置文件格式转换完成")
        return old_settings
        
    def start_snake_game(self, parent_window):
        """启动贪吃蛇游戏"""
        self.logger.info("用户选择启动贪吃蛇游戏")
        # 关闭选择窗口
        parent_window.destroy()
        
        # 创建贪吃蛇游戏窗口
        snake_game = SnakeGame()
        
    def load_data(self):
        self.logger.info("用户点击载入数据按钮")
        # 询问用户选择方式
        choice = messagebox.askquestion("选择载入方式", "是否使用默认路径自动载入regioninfo.json文件？\n\n是：自动选择\n否：手动选择", icon='question')
        
        if choice == 'yes':
            self.auto_select()
        elif choice == 'no':
            self.manual_select()
        
    def auto_select(self):
        self.logger.debug("用户选择自动载入regioninfo.json文件")
        # 默认路径
        appdata_local_low = os.path.expandvars(r"%LOCALAPPDATA%\..\LocalLow")
        regioninfo_path = os.path.join(appdata_local_low, "Innersloth", "Among Us", "regioninfo.json")
        
        if os.path.exists(regioninfo_path):
            self.regioninfo_path = regioninfo_path
            self.status_label.config(text=f"已加载: {os.path.basename(regioninfo_path)}", fg="green")
            self.enable_server_selection()  # 启用服务器选择
            self.logger.info(f"成功加载regioninfo.json文件: {regioninfo_path}")
            messagebox.showinfo("成功", f"已成功加载regioninfo.json文件\n路径: {regioninfo_path}")
        else:
            self.status_label.config(text="未找到regioninfo.json文件", fg="red")
            self.logger.warning(f"未在默认路径找到regioninfo.json文件: {regioninfo_path}")
            messagebox.showerror("错误", f"未在默认路径找到regioninfo.json文件\n请确认文件是否存在:\n{regioninfo_path}")
            
    def manual_select(self):
        self.logger.debug("用户选择手动载入regioninfo.json文件")
        file_path = filedialog.askopenfilename(
            title="选择regioninfo.json文件",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            if os.path.basename(file_path).lower() == "regioninfo.json":
                self.regioninfo_path = file_path
                self.status_label.config(text=f"已加载: {os.path.basename(file_path)}", fg="green")
                self.enable_server_selection()  # 启用服务器选择
                self.logger.info(f"成功手动加载regioninfo.json文件: {file_path}")
                messagebox.showinfo("成功", f"已成功加载regioninfo.json文件\n路径: {file_path}")
            else:
                self.status_label.config(text="请选择正确的regioninfo.json文件", fg="red")
                self.logger.warning(f"用户选择了错误的文件: {file_path}")
                messagebox.showerror("错误", "请选择正确的regioninfo.json文件")
        else:
            self.status_label.config(text="未选择文件", fg="red")
            self.logger.info("用户未选择任何文件")
            
    def fetch_server_configs(self, selected_servers):
        """从GitHub获取服务器配置"""
        self.logger.info(f"开始获取服务器配置，用户选择的服务器: {selected_servers}")
        
        server_files = {
            "清风": "QingFeng.json",
            "帆船": "FanChuan.json",
            "核电站": "HeDianZhan.json",
            "碧水港": "BiShuiGang.json",
            "Niko": "Niko.json"
        }
        
        # 创建不验证SSL证书的上下文
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        self.remote_server_configs = {}
        
        # 尝试连接原始GitHub仓库
        repo_urls = [self.github_repo_url] + self.mirror_repo_urls
        
        def fetch_from_source(args):
            """从单个源获取配置"""
            repo_url, server_name, filename, ssl_context = args
            try:
                url = f"{repo_url}/{filename}"
                request = urllib.request.Request(url)
                response = urllib.request.urlopen(request, context=ssl_context, timeout=5)
                config_data = json.loads(response.read().decode('utf-8'))
                return server_name, config_data, repo_url
            except Exception as e:
                return server_name, None, repo_url
        
        # 只获取用户选择的服务器配置
        for server_name in selected_servers:
            if server_name not in server_files:
                self.logger.warning(f"未知的服务器: {server_name}")
                continue
                
            filename = server_files[server_name]
            self.logger.debug(f"正在获取服务器 {server_name} 的配置...")
            
            # 构建所有尝试参数
            fetch_args = [(repo_url, server_name, filename, ssl_context) for repo_url in repo_urls]
            
            # 使用线程池并发尝试所有源
            with concurrent.futures.ThreadPoolExecutor(max_workers=len(repo_urls)) as executor:
                future_to_url = {executor.submit(fetch_from_source, args): args[0] for args in fetch_args}
                
                # 等待第一个成功的结果
                config_data = None
                successful_url = None
                for future in concurrent.futures.as_completed(future_to_url):
                    _, data, url = future.result()
                    if data is not None:
                        config_data = data
                        successful_url = url
                        break  # 使用第一个成功的结果
                
                # 如果所有源都失败了
                if config_data is None:
                    self.logger.error(f"无法从任何源获取服务器 {server_name} 的配置")
                    messagebox.showerror("错误", f"无法从任何源获取服务器 {server_name} 的配置")
                    return False
                    
                self.remote_server_configs[server_name] = config_data
                self.logger.info(f"服务器 {server_name} 的配置获取成功，使用源: {successful_url}")
                
                # 如果使用的不是主源，可以考虑提示用户
                if successful_url != self.github_repo_url:
                    self.logger.info(f"服务器 {server_name} 的配置通过镜像源 {successful_url} 获取")
        
        self.logger.info(f"所有选中服务器配置获取完成: {list(self.remote_server_configs.keys())}")
        return True
            
    def install_servers(self):
        if not self.regioninfo_path:
            self.logger.warning("用户未载入regioninfo.json文件")
            self.status_label.config(text="请先载入数据", fg="red")
            messagebox.showerror("错误", "请先载入regioninfo.json文件")
            return
            
        # 检查是否有选中的服务器
        selected_servers = [name for name, var in self.server_vars.items() if var.get()]
        if not selected_servers:
            self.logger.warning("用户未选择任何服务器")
            self.status_label.config(text="请选择至少一个服务器", fg="red")
            messagebox.showerror("错误", "请选择至少一个服务器")
            return
            
        self.logger.info(f"用户开始安装服务器，选中的服务器: {selected_servers}")
        
        # 显示警告对话框
        warning_result = messagebox.askyesno(
            "警告",
            "该操作可能会导致你的服务器数据出现错误/被重新排版，推荐备份后再继续安装！\n\n是否继续安装？",
            icon='warning'
        )
        
        if not warning_result:
            self.logger.info("用户取消了安装操作")
            self.status_label.config(text="安装已取消", fg="gray")
            return
            
        # 从远程获取服务器配置
        self.status_label.config(text="正在获取服务器配置...", fg="orange")
        self.root.update_idletasks()  # 更新界面
            
        if not self.fetch_server_configs(selected_servers):
            self.status_label.config(text="获取服务器配置失败", fg="red")
            return
            
        # 检查是否有运行中的Among Us进程
        among_us_processes = [p for p in psutil.process_iter(['pid', 'name']) if p.info['name'] == 'Among Us.exe']
        if among_us_processes:
            self.logger.info("检测到运行中的Among Us进程")
            result = messagebox.askyesno("警告", "检测到Among Us正在运行，是否关闭游戏进程以继续安装？")
            if result:
                try:
                    for proc in among_us_processes:
                        proc.terminate()
                        proc.wait(timeout=5)  # 等待最多5秒
                    self.logger.info("成功关闭Among Us进程")
                    messagebox.showinfo("成功", "已关闭Among Us进程，请重新启动游戏以应用更改")
                except Exception as e:
                    self.logger.error(f"关闭进程时出错: {str(e)}")
                    messagebox.showerror("错误", f"关闭进程时出错: {str(e)}")
                    return
            else:
                # 用户选择不关闭进程，继续进行安装
                self.logger.info("用户选择不关闭Among Us进程，继续安装")
                pass
                
        # 执行attrib命令移除regioninfo.json文件的只读属性
        try:
            import subprocess
            subprocess.run(['attrib', '-r', self.regioninfo_path], check=True, capture_output=True)
            self.logger.debug("成功移除regioninfo.json的只读属性")
        except Exception as e:
            # 即使attrib命令执行失败也继续安装流程
            self.logger.warning(f"移除regioninfo.json只读属性时出错: {str(e)}")
            pass  # 不中断安装过程
                
        # 读取regioninfo.json文件
        try:
            with open(self.regioninfo_path, 'r', encoding='utf-8') as f:
                region_data = json.load(f)
            self.logger.debug("成功读取regioninfo.json文件")
        except Exception as e:
            self.logger.error(f"读取regioninfo.json文件失败: {str(e)}")
            self.status_label.config(text="读取regioninfo.json文件失败", fg="red")
            messagebox.showerror("错误", f"读取regioninfo.json文件失败: {str(e)}")
            return
            
        # 添加选中的服务器配置
        installed_servers = []  # 记录成功安装的服务器
        duplicate_servers = []  # 记录重复的服务器
        
        for server_name in selected_servers:
            if server_name in self.remote_server_configs:
                # 使用从远程获取的配置
                configs = self.remote_server_configs[server_name]
                # 确保configs是列表格式
                if not isinstance(configs, list):
                    configs = [configs]
                    
                for config in configs:
                    # 检查是否已存在相同的服务器配置
                    existing = False
                    for existing_region in region_data.get("Regions", []):
                        if (existing_region.get("Name") == config["Name"] and 
                            existing_region.get("PingServer") == config["PingServer"]):
                            existing = True
                            duplicate_servers.append(config["Name"])
                            break
                    
                    # 如果不存在，则添加
                    if not existing:
                        region_data.setdefault("Regions", []).append(config)
                        # 记录安装的服务器名称，避免重复
                        if server_name not in installed_servers:
                            installed_servers.append(server_name)
        
        # 写入修改后的数据到regioninfo.json文件
        try:
            with open(self.regioninfo_path, 'w', encoding='utf-8') as f:
                json.dump(region_data, f, ensure_ascii=False, indent=2)
            self.logger.info(f"成功写入regioninfo.json文件，新增服务器: {installed_servers}, 重复服务器: {duplicate_servers}")
                
            # 构建安装结果信息
            result_message = ""
            if installed_servers:
                result_message += f"已成功安装以下服务器:\n" + "\n".join(installed_servers) + "\n\n"
                
            if duplicate_servers:
                result_message += f"以下服务器已存在，未重复安装:\n" + "\n".join(duplicate_servers)
                
            if not result_message:
                result_message = "没有新的服务器需要安装"
                
            self.status_label.config(text=f"安装完成：{len(installed_servers)} 个新服务器，{len(duplicate_servers)} 个重复服务器", fg="green")
            messagebox.showinfo("安装结果", result_message)
            self.logger.info(f"安装完成：{len(installed_servers)} 个新服务器，{len(duplicate_servers)} 个重复服务器")
        except Exception as e:
            self.logger.error(f"写入regioninfo.json文件失败: {str(e)}")
            self.status_label.config(text="写入regioninfo.json文件失败", fg="red")
            messagebox.showerror("错误", f"写入regioninfo.json文件失败: {str(e)}")

        # 清理远程配置缓存
        self.remote_server_configs = {}
        self.logger.debug("清理远程配置缓存")


class SnakeGame:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("贪吃蛇")
        self.window.geometry("600x600")
        self.window.resizable(False, False)
        
        # 游戏参数
        self.cell_size = 20
        self.grid_width = 30  # 600 / 20
        self.grid_height = 30  # 600 / 20
        self.speed = 130  # 略微加快游戏速度（从150毫秒调整到130毫秒）
        self.win_length = 50  # 胜利条件：蛇的长度
        
        # 游戏状态
        self.game_started = False
        self.game_over = False
        self.direction = "Right"  # 初始方向
        self.next_direction = "Right"  # 下一个方向
        
        # 蛇的初始位置（列表存储身体节段的坐标）
        self.snake = [(5, 15), (4, 15), (3, 15)]
        
        # 食物位置
        self.food = self.generate_food()
        
        # 创建画布
        self.canvas = tk.Canvas(self.window, width=600, height=600, bg='#333333')
        self.canvas.pack()
        
        # 显示开始提示
        self.start_text = self.canvas.create_text(
            300, 280, 
            text="按Space开始游戏", 
            fill="white", 
            font=("Arial", 20, "bold")
        )
        
        # 显示游戏说明
        self.instruction_text = self.canvas.create_text(
            300, 320,
            text=f"胜利条件：长度达到 {self.win_length}",
            fill="gray",
            font=("Arial", 12)
        )
        
        # 显示分数
        self.score_text = self.canvas.create_text(
            50, 20,
            text="长度: 3",
            fill="white",
            font=("Arial", 12, "bold")
        )
        
        # 绑定按键事件
        self.window.bind('<space>', self.start_game)
        self.window.bind('<Key>', self.change_direction)
        self.window.focus_set()
        
        # 启动窗口
        self.window.mainloop()
        
    def generate_food(self):
        """生成食物位置"""
        while True:
            food = (random.randint(0, self.grid_width - 1), 
                   random.randint(0, self.grid_height - 1))
            # 确保食物不在蛇身上
            if food not in self.snake:
                return food
        
    def start_game(self, event):
        """开始游戏"""
        if not self.game_started:
            self.game_started = True
            # 删除开始提示文本和说明文本
            self.canvas.delete(self.start_text)
            self.canvas.delete(self.instruction_text)
            # 开始游戏循环
            self.game_loop()
            
    def change_direction(self, event):
        """改变蛇的移动方向"""
        key = event.keysym
        # 防止反向移动
        if key == "Up" and self.direction != "Down":
            self.next_direction = "Up"
        elif key == "Down" and self.direction != "Up":
            self.next_direction = "Down"
        elif key == "Left" and self.direction != "Right":
            self.next_direction = "Left"
        elif key == "Right" and self.direction != "Left":
            self.next_direction = "Right"
            
    def game_loop(self):
        """游戏主循环"""
        if self.game_over:
            return
            
        # 更新方向
        self.direction = self.next_direction
        
        # 移动蛇
        head_x, head_y = self.snake[0]
        
        # 根据方向计算新的头部位置
        if self.direction == "Up":
            new_head = (head_x, head_y - 1)
        elif self.direction == "Down":
            new_head = (head_x, head_y + 1)
        elif self.direction == "Left":
            new_head = (head_x - 1, head_y)
        elif self.direction == "Right":
            new_head = (head_x + 1, head_y)
            
        # 检查碰撞边界
        if (new_head[0] < 0 or new_head[0] >= self.grid_width or 
            new_head[1] < 0 or new_head[1] >= self.grid_height):
            self.end_game()
            return
            
        # 检查碰撞自己
        if new_head in self.snake:
            self.end_game()
            return
            
        # 将新头部添加到蛇身
        self.snake.insert(0, new_head)
        
        # 检查是否吃到食物
        if new_head == self.food:
            # 生成新食物
            self.food = self.generate_food()
            # 更新分数显示
            self.canvas.itemconfig(self.score_text, text=f"长度: {len(self.snake)}")
        else:
            # 没吃到食物，移除尾部
            self.snake.pop()
            
        # 检查是否胜利（蛇身达到指定长度）
        if len(self.snake) >= self.win_length:
            self.win_game()
            return
            
        # 重新绘制游戏画面
        self.draw_game()
        
        # 继续游戏循环
        self.window.after(self.speed, self.game_loop)
        
    def draw_game(self):
        """绘制游戏画面"""
        # 清空画布
        self.canvas.delete("all")
        
        # 绘制网格线（提升视觉效果）
        for i in range(0, 600, self.cell_size):
            self.canvas.create_line(i, 0, i, 600, fill="#444444", width=1)
            self.canvas.create_line(0, i, 600, i, fill="#444444", width=1)
        
        # 绘制蛇身
        for i, (x, y) in enumerate(self.snake):
            # 蛇头使用不同颜色
            if i == 0:
                # 蛇头使用亮绿色
                color = "#00FF00"
                outline = "#00CC00"
            else:
                # 蛇身使用渐变绿色
                color_value = max(100, 255 - i * 3)  # 随着身体节段增加逐渐变暗
                color = f"#00{color_value:02x}00"
                outline = f"#00{max(80, color_value - 20):02x}00"
                
            self.canvas.create_rectangle(
                x * self.cell_size, 
                y * self.cell_size,
                (x + 1) * self.cell_size, 
                (y + 1) * self.cell_size,
                fill=color, 
                outline=outline,
                width=2
            )
            
        # 绘制食物（使用更醒目的颜色）
        food_x, food_y = self.food
        self.canvas.create_oval(
            food_x * self.cell_size + 2, 
            food_y * self.cell_size + 2,
            (food_x + 1) * self.cell_size - 2, 
            (food_y + 1) * self.cell_size - 2,
            fill="#FF4500",
            outline="#FF6347",
            width=2
        )
        
        # 绘制分数
        self.canvas.create_text(
            50, 20,
            text=f"长度: {len(self.snake)}",
            fill="white",
            font=("Arial", 12, "bold")
        )
        
    def end_game(self):
        """游戏结束"""
        self.game_over = True
        self.canvas.create_rectangle(150, 200, 450, 300, fill="black", outline="white", width=2)
        self.canvas.create_text(
            300, 240,
            text=f"游戏结束！",
            fill="red",
            font=("Arial", 20, "bold")
        )
        self.canvas.create_text(
            300, 270,
            text=f"最终长度: {len(self.snake)}",
            fill="white",
            font=("Arial", 14)
        )
        # 2秒后重置游戏
        self.window.after(2000, self.reset_game)
        
    def win_game(self):
        """游戏胜利"""
        self.game_over = True
        self.canvas.create_rectangle(150, 200, 450, 300, fill="black", outline="white", width=2)
        self.canvas.create_text(
            300, 240,
            text=f"恭喜！你赢了！",
            fill="yellow",
            font=("Arial", 20, "bold")
        )
        self.canvas.create_text(
            300, 270,
            text=f"最终长度: {len(self.snake)}",
            fill="white",
            font=("Arial", 14)
        )
        # 2秒后重置游戏
        self.window.after(2000, self.reset_game)
        
    def reset_game(self):
        """重置游戏到初始状态"""
        # 重置游戏状态
        self.game_started = False
        self.game_over = False
        self.direction = "Right"
        self.next_direction = "Right"
        
        # 重置蛇的位置
        self.snake = [(5, 15), (4, 15), (3, 15)]
        
        # 生成新食物
        self.food = self.generate_food()
        
        # 清空画布
        self.canvas.delete("all")
        
        # 重新绘制网格线
        for i in range(0, 600, self.cell_size):
            self.canvas.create_line(i, 0, i, 600, fill="#444444", width=1)
            self.canvas.create_line(0, i, 600, i, fill="#444444", width=1)
        
        # 重新显示开始提示
        self.start_text = self.canvas.create_text(
            300, 280, 
            text="按Space开始游戏", 
            fill="white", 
            font=("Arial", 20, "bold")
        )
        
        # 重新显示游戏说明
        self.instruction_text = self.canvas.create_text(
            300, 320,
            text=f"胜利条件：长度达到 {self.win_length}",
            fill="gray",
            font=("Arial", 12)
        )
        
        # 重新显示分数
        self.score_text = self.canvas.create_text(
            50, 20,
            text="长度: 3",
            fill="white",
            font=("Arial", 12, "bold")
        )


if __name__ == "__main__":
    root = tk.Tk()
    # 在创建应用之前隐藏根窗口
    root.withdraw()
    app = AmongUsTools(root)
    # 显示窗口
    root.deiconify()
    root.mainloop()

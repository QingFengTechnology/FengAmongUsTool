# 贡献指南

## 快速开始

> [!Note]
> 在开发前请先确保你有 Python 基础，并了解如何使用 git。

首先需要先确保你的开发环境有以下内容：
- Git
- Python 3.13
- Pip 25

使用下方命令来 clone 项目并以源码模式启动工具箱：

```bash

git clone git@github.com:QingFengTechnology/FengAmongUsTool.git

cd FengAmongUsTool

# 如果你不使用虚拟环境，请跳过下方命令

python -m venv venv

venv/Scripts/Activate

# 如果你不使用虚拟环境，请跳过上方命令

pip install -r requirements.txt

python app/main.py

```

这将 clone 项目并使用虚拟环境安装依赖，最后启动工具箱。

> [!Note]
> 如果你想要向工具箱做出贡献，你应当 fork 此项目到你自己的 Github 账户再 clone 自己仓库来进行开发。

## 程序构建

为方便构建，我们制作了 `build.bat` 文件来帮助你快速构建工具箱。\
你可以通过下方命令来执行构建脚本：

```bash

venv/Scripts/Activate # 如果你不使用虚拟环境，请跳过此命令

./build.bat

```

构建脚本会自动编译工具箱并将可执行文件打包到 dist 目录下，同时生成压缩包 `FengAmongUsTool.zip`。

如果构建脚本无法工作，也可以执行下方命令来手动编译：

```bash

pyinstaller main.spec --noconfirm

```

这将直接使用我们已经配置好的 spec 文件来编译工具箱，编译完成后你可以在 dist 目录下找到可执行文件。
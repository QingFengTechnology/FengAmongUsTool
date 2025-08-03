# 贡献指南

## 快速开始

> [!Note]
> 在开发前请先确保你有 Python 基础，并了解如何使用 git。

首先需要先确保你的开发环境有以下内容：
- Git
- Python
- Pip

对于 Python 版本，目前我使用的是 v3.13.5，我建议你使用 v3.13.x 版本，最大程度避免因环境问题导致的异常。\
对于 git 和 pip 则不做要求，建议始终保持最新稳定版本。

使用下方命令来 clone 项目并以源码模式启动工具箱：

```bash

git clone git@github.com:QingFengTechnology/FengAmongUsTool.git

cd FengAmongUsTool

python -m venv venv

pip install -r requirements.txt

python main.py

```

这将 clone 项目并使用虚拟环境安装依赖，最后启动工具箱。

> [!Note]
> 如果你想要向工具箱做出贡献，你应当 fork 此项目到你自己的 Github 账户再 clone 自己仓库来进行开发。
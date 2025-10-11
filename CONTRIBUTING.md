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

venv/Scripts/Activate

pip install -r requirements.txt

python app/main.py

```

这将 clone 项目并使用虚拟环境安装依赖，最后启动工具箱。

> [!Note]
> 如果你想要向工具箱做出贡献，你应当 fork 此项目到你自己的 Github 账户再 clone 自己仓库来进行开发。

## 开发规范

为保持代码一致性，我们要求您在开发时：
- 使用[小驼峰命名法](https://baike.baidu.com/item/lowerCamelCase/18434330)命名文件、函数。
- 使用[大驼峰命名法](https://baike.baidu.com/item/%E5%B8%95%E6%96%AF%E5%8D%A1%E5%91%BD%E5%90%8D%E6%B3%95/9464494)命名其他内容，例如类名、变量等。
- 将变量放在`/app/function/variableConfig.py`中，将通用函数放在`/app/function/funcUtils.py`中，将主模块放在`/app/module`文件夹中。
  - 如果功能较为庞大但不是一个独立模块，你也可以在`/app/function`文件夹中新建一个 py 文件。
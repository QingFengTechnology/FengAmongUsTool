# coding:utf-8
"""Among Us 配置切换辅助函数"""
import json
import logging
import os
import shutil
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Optional

from ..function.variableConfig import NEW_HOST_OPTIONS, OLD_HOST_OPTIONS

logger = logging.getLogger("FengAmongUsTool")


def getSettingsPath() -> Optional[Path]:
    """获取 Among Us 设置文件路径"""
    if appdata := os.getenv('APPDATA'):
        return Path(appdata).parent / 'LocalLow' / 'Innersloth' / 'Among Us' / 'settings.amogus'
    return None


def loadSettings(path: Path) -> dict:
    """加载配置文件"""
    with path.open('r', encoding='utf-8') as fp:
        return json.load(fp)


def saveSettings(path: Path, data: dict) -> None:
    """原子方式写入配置文件"""
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile('w', encoding='utf-8', dir=path.parent, delete=False) as tmp_fp:
        json.dump(data, tmp_fp, ensure_ascii=False, indent=2)
        tmp_fp.flush()
        os.fsync(tmp_fp.fileno())
    try:
        os.replace(tmp_fp.name, path)
    except Exception:
        os.remove(tmp_fp.name)
        raise


def backupSettings(source: Path) -> Path:
    """创建带时间戳的备份文件，并清理旧备份"""
    backup_dir = source.parent
    prefix = 'settings.amogus.bak'

    for existing in backup_dir.glob(f'{prefix}*'):
        try:
            existing.unlink()
            logger.info('已删除旧备份: %s', existing)
        except Exception as exc:
            logger.warning('删除旧备份 %s 失败: %s', existing, exc)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = backup_dir / f'{prefix}.{timestamp}'
    shutil.copy2(source, backup_path)
    logger.info('配置备份已创建: %s', backup_path)
    return backup_path


def applyOldConfig(data: dict) -> None:
    """调整配置以兼容旧版本"""
    input_section = data.setdefault('input', {})
    input_section.pop('inputData', None)

    multiplayer = data.setdefault('multiplayer', {})
    multiplayer.update(OLD_HOST_OPTIONS)
    for extra_key in ('filterDictionary', 'classicFilterSet', 'hnsFilterSet'):
        multiplayer.pop(extra_key, None)


def applyNewConfig(data: dict) -> None:
    """调整配置以适配新版本"""
    input_section = data.setdefault('input', {})
    input_section['inputData'] = {'initialization': 'initialized'}

    multiplayer = data.setdefault('multiplayer', {})
    multiplayer.update(NEW_HOST_OPTIONS)
    multiplayer.setdefault('filterDictionary', {})
    multiplayer['classicFilterSet'] = {'GameMode': 1, 'Filters': []}
    multiplayer['hnsFilterSet'] = {'GameMode': 2, 'Filters': []}

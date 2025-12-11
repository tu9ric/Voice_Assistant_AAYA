# -*- mode: python ; coding: utf-8 -*-

import PyInstaller.config
import os
from PyInstaller.utils.hooks import collect_submodules

# ВАЖНО: имя главного файла
main_script = 'main.py'

# Собираем все скрытые модули (динамические импорты из actions и др.)
hidden = []
hidden += collect_submodules('actions')
hidden += collect_submodules('core')
hidden += collect_submodules('utils')
hidden += ['webbrowser']   # фикс твоей ошибки
hidden += ['importlib']    # для надёжности

# Файлы, которые должны попасть внутрь exe
datas = [
    ('commands.json', '.'),  # JSON рядом с main.py
    ('actions', 'actions'),
    ('core', 'core'),
    ('utils', 'utils'),
]

a = Analysis(
    [main_script],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hidden,
    hookspath=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    name='main',
    debug=False,
    strip=False,
    upx=False,
    console=False  # ставим False, т. к. GUI
)


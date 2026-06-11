# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_data_files

datas = [('commands.json', '.'), ('todo', 'todo')]
datas += collect_data_files('customtkinter')
datas += collect_data_files('edge_tts')
datas += collect_data_files('pygame')


a = Analysis(
    ['aaya_shell.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=['actions.apps', 'actions.calculator', 'actions.fun', 'actions.sites', 'actions.system', 'actions.tools', 'actions.translator', 'actions.todo_actions', 'core.processor', 'core.tts', 'core.hotkeys', 'core.notifier', 'core.platform_context', 'todo.todo_gui', 'todo.todo_store', 'todo.todo_api', 'todo.todo_client', 'todo.models', 'todo.notes_tab', 'todo.paths', 'todo.tasks.tasks_tab', 'todo.tasks.task_card', 'todo.tasks.task_form', 'todo.tasks.task_details', 'todo.tasks.task_utils', 'todo.tasks.task_widgets', 'todo.tasks.reminder_widget', 'todo.tasks.subtasks_widget', 'todo.calendar.calendar_tab', 'todo.calendar.agenda_view', 'todo.calendar.month_view', 'todo.calendar.date_picker', 'todo.calendar.calendar_utils', 'todo.calendar.task_details', 'speech_recognition', 'pyaudio', 'keyboard', 'pystray', 'PIL', 'winotify', 'windows_toasts', 'edge_tts', 'pygame'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='AAYA',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='AAYA',
)

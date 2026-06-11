import os
import shutil
import subprocess
import sys


APP_NAME = "AAYA"
MAIN_FILE = "aaya_shell.py"


def run(command):
    print()
    print(" ".join(command))
    subprocess.check_call(command)


def remove_if_exists(path):
    if os.path.exists(path):
        print(f"Удаляю: {path}")

        if os.path.isdir(path):
            shutil.rmtree(path)
        else:
            os.remove(path)


def main():
    project_dir = os.path.dirname(
        os.path.abspath(__file__)
    )

    os.chdir(project_dir)

    remove_if_exists("build")
    remove_if_exists("dist")
    remove_if_exists(f"{APP_NAME}.spec")

    command = [
        sys.executable,
        "-m",
        "PyInstaller",

        "--noconfirm",
        "--clean",

        # ВАЖНО:
        # Для customtkinter стабильнее onedir, а не onefile.
        "--onedir",

        # Без консоли.
        # Если при тесте нужно увидеть ошибки — временно убери эту строку.
        "--windowed",

        "--name",
        APP_NAME,

        # Данные проекта
        "--add-data",
        "commands.json;.",

        "--add-data",
        "todo;todo",

        # Собрать данные customtkinter
        "--collect-data",
        "customtkinter",

        # Собрать данные edge_tts / pygame, если нужны
        "--collect-data",
        "edge_tts",

        "--collect-data",
        "pygame",

        # Скрытые импорты динамических actions
        "--hidden-import",
        "actions.apps",

        "--hidden-import",
        "actions.calculator",

        "--hidden-import",
        "actions.fun",

        "--hidden-import",
        "actions.sites",

        "--hidden-import",
        "actions.system",

        "--hidden-import",
        "actions.tools",

        "--hidden-import",
        "actions.translator",

        "--hidden-import",
        "actions.todo_actions",

        "--hidden-import",
        "core.processor",

        "--hidden-import",
        "core.tts",

        "--hidden-import",
        "core.hotkeys",

        "--hidden-import",
        "core.notifier",

        "--hidden-import",
        "core.platform_context",

        "--hidden-import",
        "todo.todo_gui",

        "--hidden-import",
        "todo.todo_store",

        "--hidden-import",
        "todo.todo_api",

        "--hidden-import",
        "todo.todo_client",

        "--hidden-import",
        "todo.models",

        "--hidden-import",
        "todo.notes_tab",

        "--hidden-import",
        "todo.paths",

        "--hidden-import",
        "todo.tasks.tasks_tab",

        "--hidden-import",
        "todo.tasks.task_card",

        "--hidden-import",
        "todo.tasks.task_form",

        "--hidden-import",
        "todo.tasks.task_details",

        "--hidden-import",
        "todo.tasks.task_utils",

        "--hidden-import",
        "todo.tasks.task_widgets",

        "--hidden-import",
        "todo.tasks.reminder_widget",

        "--hidden-import",
        "todo.tasks.subtasks_widget",

        "--hidden-import",
        "todo.calendar.calendar_tab",

        "--hidden-import",
        "todo.calendar.agenda_view",

        "--hidden-import",
        "todo.calendar.month_view",

        "--hidden-import",
        "todo.calendar.date_picker",

        "--hidden-import",
        "todo.calendar.calendar_utils",

        "--hidden-import",
        "todo.calendar.task_details",

        "--hidden-import",
        "speech_recognition",

        "--hidden-import",
        "pyaudio",

        "--hidden-import",
        "keyboard",

        "--hidden-import",
        "pystray",

        "--hidden-import",
        "PIL",

        "--hidden-import",
        "winotify",

        "--hidden-import",
        "windows_toasts",

        "--hidden-import",
        "edge_tts",

        "--hidden-import",
        "pygame",

        MAIN_FILE
    ]

    run(command)

    exe_path = os.path.join(
        project_dir,
        "dist",
        APP_NAME,
        f"{APP_NAME}.exe"
    )

    print()
    print("========================================")
    print("Сборка завершена.")
    print(f"EXE: {exe_path}")
    print("========================================")


if __name__ == "__main__":
    main()
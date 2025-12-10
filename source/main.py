import customtkinter as ctk
from gui import AssistantGUI


def main():
    # Настройка темы CustomTkinter (должно быть ДО создания окна!)
    ctk.set_appearance_mode("dark")       # варианты: "light" / "dark" / "system"
    ctk.set_default_color_theme("blue")   # варианты: "blue" / "dark-blue" / "green"

    # Создаём окно CTk
    root = ctk.CTk()
    root.title("Голосовой ассистент AAYA")
    root.geometry("820x650")

    # Исправление цвета фона окна (иначе тёмная тема выглядит сломанно)
    root.configure(fg_color=ctk.ThemeManager.theme["CTkFrame"]["fg_color"])

    # Инициализируем GUI ассистента
    AssistantGUI(root)

    # Запускаем приложение
    root.mainloop()


if __name__ == "__main__":
    main()

import tkinter as tk
from tkinter import ttk
from tkinter import font 

try:
    from ctypes import windll
    windll.shcore.SetProcessDpiAwareness(1)
except ImportError:
    pass

from db_manager import DatabaseManager
from gui_table_view import TableView
import gui_reports

class App(tk.Tk):
    def __init__(self, db_manager):
        super().__init__()
        self.db = db_manager
        
        self.title("Система управления библиотекой")
        self.geometry("400x450")


        try:
            default_font = font.nametofont("TkDefaultFont")
            default_font.configure(family="Segoe UI", size=9)
            self.option_add("*Font", default_font)
        except tk.TclError:
            print("Шрифт 'Segoe UI' не найден. Будет использован шрифт по умолчанию.")
        

        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(expand=True, fill=tk.BOTH)

        tables_frame = ttk.LabelFrame(main_frame, text="Управление таблицами")
        tables_frame.pack(fill=tk.X, pady=10)

        table_names = ["libraries", "themes", "books", "readers", "subscriptions", "employees"]
        for name in table_names:
            ttk.Button(tables_frame, text=name.replace('_', ' ').title(), command=lambda n=name: self.open_table_view(n)).pack(fill=tk.X, padx=5, pady=2)

        reports_frame = ttk.LabelFrame(main_frame, text="Отчеты")
        reports_frame.pack(fill=tk.X, pady=10)

        ttk.Button(reports_frame, text="Отчет: Книги-должники", command=lambda: gui_reports.show_overdue_books_report(self, self.db)).pack(fill=tk.X, padx=5, pady=2)
        ttk.Button(reports_frame, text="Отчет: Популярные авторы", command=lambda: gui_reports.show_popular_authors_report(self, self.db)).pack(fill=tk.X, padx=5, pady=2)
        ttk.Button(reports_frame, text="Отчет: Активность библиотек", command=lambda: gui_reports.show_library_activity_report(self, self.db)).pack(fill=tk.X, padx=5, pady=2)

        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def open_table_view(self, table_name):
        TableView(self, table_name, self.db)

    def on_closing(self):
        print("Закрытие соединения с базой данных...")
        self.db.close()
        self.destroy()

if __name__ == '__main__':
    db_manager = DatabaseManager()
    
    if db_manager.conn:
        app = App(db_manager)
        app.mainloop()
    else:
        print("Не удалось запустить приложение из-за ошибки подключения к БД.")
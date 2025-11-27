import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime 

def center_window(win):
    win.update_idletasks()
    width = win.winfo_width()
    height = win.winfo_height()

    if win.master:
        parent_geometry = win.master.geometry().split('+')
        parent_width_height = parent_geometry[0].split('x')
        parent_x = int(parent_geometry[1])
        parent_y = int(parent_geometry[2])
        parent_width = int(parent_width_height[0])
        parent_height = int(parent_width_height[1])
        x = parent_x + (parent_width // 2) - (width // 2)
        y = parent_y + (parent_height // 2) - (height // 2)
        win.geometry(f'{width}x{height}+{x}+{y}')
    else: 
        x = (win.winfo_screenwidth() // 2) - (width // 2)
        y = (win.winfo_screenheight() // 2) - (height // 2)
        win.geometry(f'{width}x{height}+{x}+{y}')


class ReportDialog(tk.Toplevel):
    def __init__(self, parent, title):
        super().__init__(parent)
        self.title(title)
        self.result = None
        self.transient(parent)
        self.grab_set()

        self.form_frame = ttk.LabelFrame(self, text="Параметры отчета")
        self.form_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        self.create_widgets()
        
        btn_frame = ttk.Frame(self)
        btn_frame.pack(pady=5)
        ttk.Button(btn_frame, text="Сформировать", command=self.on_ok).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Отмена", command=self.destroy).pack(side=tk.LEFT, padx=5)

        center_window(self)

    def create_widgets(self):
        pass

    def on_ok(self):
        self.destroy()

class ReportViewer(tk.Toplevel):

    def __init__(self, parent, title, columns, data, totals=None):
        super().__init__(parent)
        self.title(title)
        self.geometry("800x500")

        tree_frame = ttk.Frame(self)
        tree_frame.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

        tree = ttk.Treeview(tree_frame, columns=columns, show='headings')
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=120)
        tree.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)

        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
        vsb.pack(side='right', fill='y')
        tree.configure(yscrollcommand=vsb.set)
        
        for row in data:
            tree.insert('', 'end', values=row)

        if totals:
            totals_frame = ttk.LabelFrame(self, text="Итоги")
            totals_frame.pack(fill=tk.X, padx=10, pady=5)
            for key, value in totals.items():
                ttk.Label(totals_frame, text=f"{key}: {value}").pack(anchor='w')


        center_window(self)


class OverdueBooksDialog(ReportDialog):
    def create_widgets(self):
        ttk.Label(self.form_frame, text="ФИО читателя (LIKE):").grid(row=0, column=0, sticky='w', padx=5)
        self.reader_name_entry = ttk.Entry(self.form_frame, width=30)
        self.reader_name_entry.grid(row=0, column=1, pady=5)

        ttk.Label(self.form_frame, text="Сортировать по:").grid(row=1, column=0, sticky='w', padx=5)
        self.sort_var = tk.StringVar(value="Дням просрочки")
        self.sort_menu = ttk.Combobox(self.form_frame, textvariable=self.sort_var, 
                                      values=["Дням просрочки", "ФИО читателя", "Названию книги"], state="readonly")
        self.sort_menu.grid(row=1, column=1, pady=5)

    def on_ok(self):
        self.result = {
            'reader_name': self.reader_name_entry.get(),
            'sort_by': self.sort_var.get()
        }
        super().on_ok()


class PopularAuthorsDialog(ReportDialog):
    def create_widgets(self):
        ttk.Label(self.form_frame, text="Дата выдачи от (ДД.ММ.ГГГГ):").grid(row=0, column=0, sticky='w', padx=5)
        self.start_date_entry = ttk.Entry(self.form_frame, width=30)
        self.start_date_entry.grid(row=0, column=1, pady=5)
        self.start_date_entry.insert(0, datetime.now().strftime('01.01.%Y'))


        ttk.Label(self.form_frame, text="Дата выдачи до (ДД.ММ.ГГГГ):").grid(row=1, column=0, sticky='w', padx=5)
        self.end_date_entry = ttk.Entry(self.form_frame, width=30)
        self.end_date_entry.grid(row=1, column=1, pady=5)
        self.end_date_entry.insert(0, datetime.now().strftime('%d.%m.%Y'))

    def on_ok(self):
        start_date_str = self.start_date_entry.get()
        end_date_str = self.end_date_entry.get()

        try:
            start_date_sql = datetime.strptime(start_date_str, '%d.%m.%Y').strftime('%Y-%m-%d')
            end_date_sql = datetime.strptime(end_date_str, '%d.%m.%Y').strftime('%Y-%m-%d')
        except ValueError:
            messagebox.showerror("Ошибка формата", "Неверный формат даты. Используйте ДД.ММ.ГГГГ.")
            return 

        self.result = {
            'start_date': start_date_sql,
            'end_date': end_date_sql
        }
        super().on_ok()


class LibraryActivityDialog(ReportDialog):
    def create_widgets(self):
        ttk.Label(self.form_frame, text="Сортировать по:").grid(row=0, column=0, sticky='w', padx=5)
        self.sort_var = tk.StringVar(value="Книг на руках")
        self.sort_menu = ttk.Combobox(self.form_frame, textvariable=self.sort_var, 
                                      values=["Названию библиотеки", "Всего книг", "Книг на руках", "Книг в наличии"], state="readonly")
        self.sort_menu.grid(row=0, column=1, pady=5)

    def on_ok(self):
        self.result = {'sort_by': self.sort_var.get()}
        super().on_ok()


def show_overdue_books_report(parent, db):
    dialog = OverdueBooksDialog(parent, "Отчет: Книги-должники")
    parent.wait_window(dialog)
    params = dialog.result
    if not params: return
    query = """
    SELECT r.full_name, b.title, s.give_date, (CURRENT_DATE - s.give_date) AS days_overdue
    FROM subscriptions s
    JOIN readers r ON s.reader_id = r.reader_id
    JOIN books b ON s.book_id = b.book_id
    WHERE s.return_date IS NULL AND (CURRENT_DATE - s.give_date) > 30
    """
    query_params = []
    if params['reader_name']:
        query += " AND r.full_name ILIKE %s"
        query_params.append(f"%{params['reader_name']}%")
    sort_map = {"Дням просрочки": 'days_overdue DESC', "ФИО читателя": 'r.full_name ASC', "Названию книги": 'b.title ASC'}
    query += f" ORDER BY {sort_map.get(params['sort_by'], '4 DESC')}"
    data = db.execute_query(query, tuple(query_params), fetch="all")
    if data is None: return
    totals = {"Всего книг в просрочке": len(data)}
    ReportViewer(parent, "Отчет: Книги-должники", ["ФИО читателя", "Название книги", "Дата выдачи", "Дней на руках"], data, totals)

def show_popular_authors_report(parent, db):
    dialog = PopularAuthorsDialog(parent, "Отчет: Популярные авторы")
    parent.wait_window(dialog)
    params = dialog.result
    if not params: return
    query = """
    SELECT b.author, COUNT(s.sub_id) AS borrow_count
    FROM subscriptions s JOIN books b ON s.book_id = b.book_id
    WHERE s.give_date BETWEEN %s AND %s
    GROUP BY b.author ORDER BY borrow_count DESC LIMIT 20;
    """
    data = db.execute_query(query, (params['start_date'], params['end_date']), fetch="all")
    if data is None: return
    totals = {"Всего выдач за период (топ 20 авторов)": sum(row[1] for row in data)}
    ReportViewer(parent, "Отчет: Популярные авторы", ["Автор", "Количество выдач"], data, totals)

def show_library_activity_report(parent, db):
    dialog = LibraryActivityDialog(parent, "Отчет: Активность библиотек")
    parent.wait_window(dialog)
    params = dialog.result
    if not params: return
    query = """
    SELECT l.name, SUM(b.quantity) + COUNT(s.sub_id) AS total_books, COUNT(s.sub_id) AS on_loan, SUM(b.quantity) AS available
    FROM libraries l
    LEFT JOIN books b ON l.library_id = b.library_id
    LEFT JOIN subscriptions s ON b.book_id = s.book_id AND s.return_date IS NULL
    GROUP BY l.name
    """
    sort_map = {"Названию библиотеки": 'l.name', "Всего книг": 'total_books DESC', "Книг на руках": 'on_loan DESC', "Книг в наличии": 'available DESC'}
    query += f" ORDER BY {sort_map.get(params['sort_by'], '3 DESC')}"
    data = db.execute_query(query, fetch="all")
    if data is None: return
    totals = {
        "Всего книг": sum(row[1] for row in data if row[1]),
        "Всего на руках": sum(row[2] for row in data if row[2]),
        "Всего в наличии": sum(row[3] for row in data if row[3])
    }
    ReportViewer(parent, "Отчет: Активность библиотек", ["Библиотека", "Всего экз.", "На руках", "В наличии"], data, totals)
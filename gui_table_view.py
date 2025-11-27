import tkinter as tk
from tkinter import ttk, messagebox
from db_manager import DatabaseManager
from gui_record_dialog import RecordDialog

class TableView(tk.Toplevel):
    def __init__(self, parent, table_name, db_manager):
        super().__init__(parent)
        self.db = db_manager
        self.table_name = table_name
        self.columns = self.db.get_column_names(self.table_name)

        if not self.columns:
            messagebox.showerror("Ошибка получения данных", f"Не удалось получить структуру таблицы '{self.table_name}'.")
            self.destroy()
            return

        self.title(f"Управление таблицей: {table_name}")
        self.geometry("1000x600")

        top_frame = ttk.Frame(self)
        top_frame.pack(fill=tk.X, padx=10, pady=5)

        self.setup_filters(top_frame)
        self.setup_buttons(top_frame) 
        
        self.tree_frame = ttk.Frame(self)
        self.tree_frame.pack(expand=True, fill=tk.BOTH, padx=10, pady=5)
        
        self.tree = ttk.Treeview(self.tree_frame, columns=self.columns, show='headings')
        for col in self.columns:
            self.tree.heading(col, text=col.replace('_', ' ').title())
            self.tree.column(col, width=100)
        
        self.tree.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
        
        vsb = ttk.Scrollbar(self.tree_frame, orient="vertical", command=self.tree.yview)
        vsb.pack(side='right', fill='y')
        self.tree.configure(yscrollcommand=vsb.set)

        self.foreign_keys = self.get_foreign_keys_info()
        self.load_data()

    def setup_filters(self, parent):
        filter_frame = ttk.LabelFrame(parent, text="Фильтры и Сортировка")
        filter_frame.pack(fill=tk.X)

        ttk.Label(filter_frame, text="Поле для поиска:").grid(row=0, column=0, padx=5, pady=5)
        default_search_col = self.columns[1] if len(self.columns) > 1 else self.columns[0]
        self.search_col_var = tk.StringVar(value=default_search_col)
        self.search_col_menu = ttk.Combobox(filter_frame, textvariable=self.search_col_var, values=self.columns)
        self.search_col_menu.grid(row=0, column=1, padx=5, pady=5)
        self.search_entry = ttk.Entry(filter_frame)
        self.search_entry.grid(row=0, column=2, padx=5, pady=5)
        ttk.Button(filter_frame, text="Поиск", command=lambda: self.load_data(like=True)).grid(row=0, column=3, padx=5)

        ttk.Label(filter_frame, text="Сортировать по:").grid(row=1, column=0, padx=5, pady=5)
        self.sort_col_var = tk.StringVar(value=self.columns[0])
        self.sort_col_menu = ttk.Combobox(filter_frame, textvariable=self.sort_col_var, values=self.columns)
        self.sort_col_menu.grid(row=1, column=1, padx=5, pady=5)
        self.sort_order_var = tk.StringVar(value="ASC")
        self.sort_order_menu = ttk.Combobox(filter_frame, textvariable=self.sort_order_var, values=["ASC", "DESC"])
        self.sort_order_menu.grid(row=1, column=2, padx=5, pady=5)
        ttk.Button(filter_frame, text="Применить", command=self.load_data).grid(row=1, column=3, padx=5)
        ttk.Button(filter_frame, text="Сбросить", command=self.reset_filters).grid(row=1, column=4, padx=5)

    def setup_buttons(self, parent):
        button_frame = ttk.LabelFrame(parent, text="Действия")
        button_frame.pack(fill=tk.X, pady=(10,0))
        ttk.Button(button_frame, text="Добавить", command=self.open_add_dialog).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(button_frame, text="Изменить", command=self.open_edit_dialog).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(button_frame, text="Удалить", command=self.delete_record).pack(side=tk.LEFT, padx=5, pady=5)
        
    def get_foreign_keys_info(self):
        if self.table_name == 'books':
            return {'library_id': ('libraries', 'library_id', 'name'), 'theme_id': ('themes', 'theme_id', 'theme_name')}
        elif self.table_name == 'subscriptions':
            return {'book_id': ('books', 'book_id', 'title'), 'reader_id': ('readers', 'reader_id', 'full_name')}
        elif self.table_name == 'employees':
            return {'library_id': ('libraries', 'library_id', 'name')}
        return {}
    
    def load_data(self, like=False):
        for i in self.tree.get_children(): self.tree.delete(i)
        query = f"SELECT * FROM {self.table_name}"
        params = []
        search_val = self.search_entry.get()
        if search_val:
            query += f" WHERE {self.search_col_var.get()}::text ILIKE %s"
            params.append(f"%{search_val}%")
        query += f" ORDER BY {self.sort_col_var.get()} {self.sort_order_var.get()}"
        data = self.db.execute_query(query, tuple(params), fetch="all")
        if data:
            for row in data:
                self.tree.insert('', 'end', values=[str(v) if v is not None else "" for v in row])

    def open_add_dialog(self):
        columns_for_add = self.columns[1:] 
        dialog = RecordDialog(self, title=f"Добавить запись в '{self.table_name}'", columns=columns_for_add, db_manager=self.db, foreign_keys=self.foreign_keys)
        self.wait_window(dialog)
        if dialog.result:
            self.add_record(dialog.result)

    def add_record(self, data_dict):
        cols = list(data_dict.keys())
        vals = list(data_dict.values())
        placeholders = ', '.join(['%s'] * len(cols))
        query = f"INSERT INTO {self.table_name} ({', '.join(cols)}) VALUES ({placeholders})"
        if self.db.execute_query(query, tuple(vals)):
            messagebox.showinfo("Успех", "Запись успешно добавлена.")
            self.load_data()
        else:
            messagebox.showerror("Ошибка", "Не удалось добавить запись.")

    def open_edit_dialog(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Внимание", "Выберите запись для изменения.")
            return
        
        item_values = self.tree.item(selected_item[0])['values']
        initial_data = {col: val for col, val in zip(self.columns, item_values)}
        
        columns_for_edit = self.columns[1:]
        dialog = RecordDialog(self, title=f"Изменить запись в '{self.table_name}'", columns=columns_for_edit, db_manager=self.db, foreign_keys=self.foreign_keys, initial_data=initial_data)
        self.wait_window(dialog)

        if dialog.result:
            self.update_record(dialog.result, initial_data[self.columns[0]])

    def update_record(self, new_data, record_id):
        pk_col = self.columns[0]
        set_clauses = [f"{col} = %s" for col in new_data.keys()]
        values = list(new_data.values())
        values.append(record_id)
        
        query = f"UPDATE {self.table_name} SET {', '.join(set_clauses)} WHERE {pk_col} = %s"
        if self.db.execute_query(query, tuple(values)):
            messagebox.showinfo("Успех", "Запись успешно обновлена.")
            self.load_data()
        else:
            messagebox.showerror("Ошибка", "Не удалось обновить запись.")

    def delete_record(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Внимание", "Выберите запись для удаления.")
            return
        if not messagebox.askyesno("Подтверждение", "Вы уверены, что хотите удалить выбранную запись?"):
            return
        
        item_values = self.tree.item(selected_item[0])['values']
        pk_col = self.columns[0]
        pk_val = item_values[0]

        query = f"DELETE FROM {self.table_name} WHERE {pk_col} = %s"
        if self.db.execute_query(query, (pk_val,)):
            messagebox.showinfo("Успех", "Запись успешно удалена.")
            self.load_data()
        else:
            messagebox.showerror("Ошибка", "Не удалось удалить запись.")
    
    def reset_filters(self):
        self.search_entry.delete(0, tk.END)
        default_search_col = self.columns[1] if len(self.columns) > 1 else self.columns[0]
        self.search_col_var.set(default_search_col)
        self.sort_col_var.set(self.columns[0])
        self.sort_order_var.set("ASC")
        self.load_data()
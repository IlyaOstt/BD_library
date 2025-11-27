import tkinter as tk
from tkinter import ttk, messagebox

class RecordDialog(tk.Toplevel):
    def __init__(self, parent, title, columns, db_manager, foreign_keys={}, initial_data=None):
        super().__init__(parent)
        self.transient(parent)
        self.title(title)
        self.db = db_manager
        self.foreign_keys = foreign_keys
        self.columns = columns
        self.initial_data = initial_data

        self.result = None
        self.entries = {}

        form_frame = ttk.Frame(self, padding="10")
        form_frame.pack(expand=True, fill=tk.BOTH)

        self.create_form(form_frame)

        if self.initial_data:
            self.populate_form()

        btn_frame = ttk.Frame(self)
        btn_frame.pack(pady=10)

        ttk.Button(btn_frame, text="Сохранить", command=self.on_ok).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Отмена", command=self.destroy).pack(side=tk.LEFT, padx=5)

        self.grab_set()

        self.resizable(True, True)
        self.minsize(400, 200)

    def create_form(self, parent_frame):
        for i, col in enumerate(self.columns):
            ttk.Label(parent_frame, text=col.replace('_', ' ').title()).grid(row=i, column=0, padx=5, pady=5, sticky='w')
            
            if col in self.foreign_keys:
                table, pk, display_col = self.foreign_keys[col]
                query = f"SELECT {pk}, {display_col} FROM {table} ORDER BY {display_col}"
                choices_data = self.db.execute_query(query, fetch="all")
                
                entry = ttk.Combobox(parent_frame, state="readonly")
                if choices_data:
                    entry['values'] = [f"{name} ({id})" for id, name in choices_data]
                    entry.choices_map = {f"{name} ({id})": id for id, name in choices_data}
                    entry.choices_reverse_map = {id: f"{name} ({id})" for id, name in choices_data}
                self.entries[col] = entry
            else:
                entry = ttk.Entry(parent_frame)
                self.entries[col] = entry
            
            entry.grid(row=i, column=1, padx=5, pady=5, sticky='ew')
        
        parent_frame.grid_columnconfigure(1, weight=1)

    def populate_form(self):
        for col, value in self.initial_data.items():
            if col not in self.entries: continue
            
            entry = self.entries[col]
            entry.config(state='normal')
            if isinstance(entry, ttk.Combobox):
                display_value = entry.choices_reverse_map.get(int(value))
                if display_value:
                    entry.set(display_value)
            else:
                entry.insert(0, value if value is not None else "")

    def on_ok(self):
        data = {}
        for col, entry in self.entries.items():
            value = None
            if isinstance(entry, ttk.Combobox):
                value = entry.choices_map.get(entry.get())
            else:
                value = entry.get()
            
            if not value and col in self.foreign_keys:
                messagebox.showwarning("Ошибка ввода", f"Поле '{col.title()}' обязательно для заполнения.")
                return
            
            data[col] = value if value else None

        self.result = data
        self.destroy()
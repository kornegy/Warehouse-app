import tkinter as tk
import json
import re
from tkinter import ttk, messagebox, Toplevel

class WarehouseApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Seznam skladů")
        self.root.geometry("1000x800")

        self.style = ttk.Style()
        self.available_themes = self.style.theme_names()
        self.current_theme = tk.StringVar(value=self.style.theme_use())

        self.warehouses = []
        self.data = []
        self.items_data = []

        # self.create_menu()
        self.create_widgets()
        self.load_data()

        # Предполагается, что у вас уже существует Frame, например self.menu_frame
        about_button = tk.Button(self.root, text="About us", command=self.show_about_window, font=("Arial", 8))
        about_button.pack(side="left", padx=5, pady=5)

    def show_about_window(self):
        about_window = Toplevel(self.root)  # Создаём дочернее окно
        about_window.title("About WarehouseApp")
        about_window.geometry("400x340")  # Размер окна

        description = (
            "Program 'WarehouseApp' je nástroj pro správu skladových zásob a řízení logistiky.\n\n"
            "Created by: Nazar Koval(KOV0393)\n\n"
            "Hlavní funkce programu:\n"
            "- Přidávání, aktualizace a mazání záznamů o produktech.\n"
            "- Přesouvání produktů mezi sklady s možností nastavení množství a jednotek.\n"
            "- Ukládání a načítání dat z externích souborů pro snadnou zálohu a obnovu.\n"
            "- Pohodlné vyhledávání a třídění produktů podle různých kritérií.\n"
            "- Správa seznamu skladů, přidávání nových skladů a jejich úprava.\n"
            "- Přizpůsobení vzhledu aplikace změnou témat (motivů).\n\n"
            "Aplikace je vhodná pro malé a střední firmy, které chtějí efektivněji spravovat své sklady a produkty, "
            "minimalizovat chyby a zjednodušit každodenní operace."
        )

        label = tk.Label(about_window, text=description, justify="left", wraplength=380)
        label.pack(pady=10, padx=10)

        close_button = tk.Button(about_window, text="Exit", command=about_window.destroy)
        close_button.pack(pady=10)


    def change_theme(self):
        self.style.theme_use(self.current_theme.get())

    def validate_integer(self, event):
        widget = event.widget
        text = widget.get()

        #allows only int and symblos
        if re.search(r"[A-Za-zА-Яа-яЁё]", text):
            widget.delete(0, "end")

    def on_tree_select(self, event):
        selected_item = self.tree.selection()
        if selected_item:
            item_id = selected_item[0]
            values = self.tree.item(item_id, "values")

            if values:
                field_mapping = {
                    "ID": 0,
                    "Název": 1,
                    "Typ": 2,
                    "Kapacita": 4,
                }

                for field, index in field_mapping.items():
                    if field in self.entries:
                        self.entries[field].delete(0, tk.END)
                        self.entries[field].insert(0, values[index])

                adresa_index = 3
                if len(values) > adresa_index:
                    adresa_value = values[adresa_index]
                    self.fill_address_entries(adresa_value)

    def fill_address_entries(self, adresa_value):
        try:
            parts = adresa_value.split(",")

            ulice_cislo = parts[0].strip() if len(parts) > 0 else ""
            mesto = parts[1].strip() if len(parts) > 1 else ""
            psc = parts[2].strip() if len(parts) > 2 else ""
            stat = parts[3].strip() if len(parts) > 3 else ""

            if " " in ulice_cislo:
                ulice, cislo = ulice_cislo.rsplit(" ", 1)  #delime ulice a cislo
            else:
                ulice, cislo = ulice_cislo, ""

            self.entries["Ulice"].delete(0, tk.END)
            self.entries["Ulice"].insert(0, ulice)

            self.entries["Č.p."].delete(0, tk.END)
            self.entries["Č.p."].insert(0, cislo)

            self.entries["Město"].delete(0, tk.END)
            self.entries["Město"].insert(0, mesto)

            self.entries["PSČ"].delete(0, tk.END)
            self.entries["PSČ"].insert(0, psc)

            self.entries["Stát"].delete(0, tk.END)
            self.entries["Stát"].insert(0, stat)

        except Exception as e:
            print(f"Ошибка при обработке адреса: {e}")

    def create_widgets(self):
        tab_control = ttk.Notebook(self.root)
        tab_warehouses = ttk.Frame(tab_control)
        tab_items = ttk.Frame(tab_control)
        tab_control.add(tab_warehouses, text="Sklady")
        tab_control.add(tab_items, text="Položky skladu")
        tab_control.pack(expand=1, fill="both")

        settings_frame = ttk.LabelFrame(tab_warehouses, text="Nastavení")
        settings_frame.pack(fill="x", padx=10, pady=5)

        # -- polozky skladu --
        search_label = ttk.LabelFrame(tab_items, text="Vyhledavani")
        search_label.pack(fill="x", padx=10, pady=5)

        ttk.Label(search_label, text="Najit dle pole:").pack(side="left", padx=5)
        self.search_field = ttk.Combobox(search_label, values=["ID", "Nazev", "Sklad"])
        self.search_field.pack(side="left")

        ttk.Label(search_label, text="Hledaný výraz:").pack(side="left", padx=5)
        self.search_entry = ttk.Entry(search_label)
        self.search_entry.pack(side="left", padx=5)

        btn_search = ttk.Button(search_label, text="Vyhledat", command=self.search_item)
        btn_search.pack(side="left", padx=5)

        columns = ("ID", "Zkratka", "Název", "Popis", "Sklad", "Umístění", "Množství", "Jednotka")
        self.tree_items = ttk.Treeview(tab_items, columns=columns, show="headings")
        for col in columns:
            self.tree_items.heading(col, text=col)
            self.tree_items.column(col, width=100)
        self.tree_items.pack(expand=1, fill="both", padx=10, pady=5)

        details_frame = ttk.LabelFrame(tab_items, text="Údaje položky")
        details_frame.pack(fill="x", padx=10, pady=5)

        input_frame = ttk.Frame(details_frame)
        input_frame.pack(fill="x")

        left_frame = ttk.Frame(input_frame)
        left_frame.pack(side="left", padx=10, fill="x", expand=True)

        right_frame = ttk.Frame(input_frame)
        right_frame.pack(side="left", padx=10, fill="x", expand=True)

        self.entries_item = {}
        left_labels = ["ID", "Zkratka", "Název", "Popis"]
        right_labels = ["Sklad",  "Umístění", "Množství", "Jednotka"]

        #LEFT FRAME
        ttk.Label(left_frame, text="ID").grid(row=0, column=0, sticky="e", padx=5, pady=2)
        self.entries_item["ID"] = ttk.Entry(left_frame, width=50)
        self.entries_item["ID"].grid(row=0, column=1, sticky="ew", padx=5, pady=2)
        self.entries_item["ID"].bind("<KeyRelease>", self.validate_integer)

        ttk.Label(left_frame, text="Zkratka").grid(row=1, column=0, sticky="e", padx=5, pady=2)
        self.entries_item["Zkratka"] = ttk.Entry(left_frame, width=50)
        self.entries_item["Zkratka"].grid(row=1, column=1, sticky="ew", padx=5, pady=2)

        ttk.Label(left_frame, text="Název").grid(row=2, column=0, sticky="e", padx=5, pady=2)
        self.entries_item["Název"] = ttk.Entry(left_frame, width=50)
        self.entries_item["Název"].grid(row=2, column=1, sticky="ew", padx=5, pady=2)

        ttk.Label(left_frame, text="Popis").grid(row=3, column=0, sticky="e", padx=5, pady=2)
        self.entries_item["Popis"] = ttk.Entry(left_frame, width=50)
        self.entries_item["Popis"].grid(row=3, column=1, sticky="ew", padx=5, pady=2)

        #RIGHT FRAME
        ttk.Label(right_frame, text="Sklad").grid(row=0, column=0, sticky="e", padx=5, pady=2)
        self.entries_item["Sklad"] = ttk.Entry(right_frame, width=50)
        self.entries_item["Sklad"].grid(row=0, column=1, sticky="ew", padx=5, pady=2)

        ttk.Label(right_frame, text="Umístění").grid(row=1, column=0, sticky="e", padx=5, pady=2)
        self.entries_item["Umístění"] = ttk.Entry(right_frame, width=50)
        self.entries_item["Umístění"].grid(row=1, column=1, sticky="ew", padx=5, pady=2)

        ttk.Label(right_frame, text="Množství").grid(row=2, column=0, sticky="e", padx=5, pady=2)
        self.entries_item["Množství"] = ttk.Entry(right_frame, width=50)
        self.entries_item["Množství"].grid(row=2, column=1, sticky="ew", padx=5, pady=2)
        self.entries_item["Množství"].bind("<KeyRelease>", self.validate_integer)

        ttk.Label(right_frame, text="Jednotka").grid(row=3, column=0, sticky="e", padx=5, pady=2)
        self.entries_item["Jednotka"] = ttk.Entry(right_frame, width=50)
        self.entries_item["Jednotka"].grid(row=3, column=1, sticky="ew", padx=5, pady=2)

        btn_frame = ttk.Frame(input_frame)
        btn_frame.pack(side="left", padx=10, fill="y")

        btn_add_item = ttk.Button(btn_frame, text="Přidat", command=self.add_item)
        btn_add_item.pack(pady=5)

        btn_edit = ttk.Button(btn_frame, text="Upravit", command=self.update_item)
        btn_edit.pack(pady=5)

        btn_delete = ttk.Button(btn_frame, text="Odstranit", command=self.delete_item)
        btn_delete.pack(pady=5)

        transfer_frame = ttk.LabelFrame(tab_items, text="Převod položky")
        transfer_frame.pack(fill="x", padx=10, pady=5)

        transfer_left = ttk.Frame(transfer_frame)
        transfer_left.pack(side="left", padx=10, fill="x", expand=True)

        transfer_right = ttk.Frame(transfer_frame)
        transfer_right.pack(side="left", padx=10, fill="x", expand=True)

        ttk.Label(transfer_left, text="Ze skladu:").pack(anchor="w")
        self.from_warehouse = ttk.Combobox(transfer_left)
        self.from_warehouse.pack(fill="x", pady=2)

        ttk.Label(transfer_left, text="Na sklad:").pack(anchor="w")
        self.to_warehouse = ttk.Combobox(transfer_left)
        self.to_warehouse.pack(fill="x", pady=2)

        ttk.Label(transfer_right, text="Množství:").pack(anchor="w")
        self.transfer_quantity = ttk.Entry(transfer_right, width=10)
        self.transfer_quantity.pack(fill="x", pady=2)
        self.transfer_quantity.bind("<KeyRelease>", self.validate_integer)

        ttk.Label(transfer_right, text="Jednotka:").pack(anchor="w")
        self.transfer_unit = ttk.Entry(transfer_right, width=10)
        self.transfer_unit.pack(fill="x", pady=2)

        btn_transfer = ttk.Button(transfer_frame, text="Převést", command=self.transfer_item)
        btn_transfer.pack(side="bottom", pady=40)


        # -- sklad --
        display_frame = ttk.LabelFrame(tab_warehouses, text="Zobrazení")
        display_frame.pack(fill="x", padx=10, pady=5)

        display_frame.columnconfigure(3, weight=1)

        ttk.Label(display_frame, text="Změna tématu:").grid(row=0, column=4, padx=5, pady=5, sticky="e")
        theme_dropdown = ttk.Combobox(display_frame, textvariable=self.current_theme, values=self.available_themes,
                                      state="readonly")
        theme_dropdown.grid(row=0, column=5, padx=5, pady=5, sticky="e")
        theme_dropdown.bind("<<ComboboxSelected>>", lambda e: self.change_theme())

        ttk.Label(display_frame, text="Limit kapacity").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.limit_var = tk.IntVar(value=10)
        limit_options = [10, 20, 50, 100]
        limit_dropdown = ttk.Combobox(display_frame, textvariable=self.limit_var, values=limit_options,
                                      state="readonly")
        limit_dropdown.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        limit_dropdown.bind("<<ComboboxSelected>>", lambda e: self.update_table())

        ttk.Label(display_frame, text="Řazení").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.sort_var = tk.StringVar(value="ID")
        sort_options = ["ID", "Název", "Typ", "Kapacita"]
        sort_dropdown = ttk.Combobox(display_frame, textvariable=self.sort_var, values=sort_options, state="readonly")
        sort_dropdown.grid(row=0, column=3, padx=5, pady=5, sticky="w")
        sort_dropdown.bind("<<ComboboxSelected>>", lambda e: self.update_table())

        columns = ("ID", "Název", "Typ", "Adresa", "Kapacita")
        self.tree = ttk.Treeview(tab_warehouses, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col, command=lambda c=col: self.sort_by_column(c))
            self.tree.column(col, width=100)
        self.tree.pack(expand=1, fill="both", padx=10, pady=5)
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)


        details_frame = ttk.LabelFrame(tab_warehouses, text="Údaje skladu")
        details_frame.pack(fill="x", padx=10, pady=5)

        info_frame = ttk.LabelFrame(details_frame, text="Zakladni info")
        info_frame.grid(row=0, column=0, padx=10, pady=5, sticky="nsew")

        self.entries = {}
        labels = ["ID", "Název", "Typ", "Kapacita", "Popis"]
        entry_widths = {"ID": 10, "Kapacita": 10, "Název": 50, "Typ": 50, "Popis": 50}

        for i, lbl in enumerate(labels):
            ttk.Label(info_frame, text=lbl).grid(row=i, column=0, sticky="e", padx=5, pady=2)

            if lbl == "Popis":
                entry = tk.Text(info_frame, width=entry_widths[lbl], height=3)
                entry.grid(row=i, column=1, columnspan=2, sticky="ew", padx=5, pady=2)
            else:
                entry = ttk.Entry(info_frame, width=entry_widths[lbl])
                entry.grid(row=i, column=1, columnspan=2, sticky="ew", padx=5, pady=2)

            self.entries[lbl] = entry
            if lbl in ["ID", "Kapacita"]:
                entry.bind("<KeyRelease>", self.validate_integer)

        info_frame.columnconfigure(1, weight=1)

        address_frame = ttk.LabelFrame(details_frame, text="Adresa")
        address_frame.grid(row=0, column=1, padx=10, pady=5, sticky="nsew")

        ttk.Label(address_frame, text="Ulice").grid(row=0, column=0, sticky="e", padx=5, pady=2)
        self.entries["Ulice"] = ttk.Entry(address_frame, width=25)
        self.entries["Ulice"].grid(row=0, column=1, sticky="ew", padx=5, pady=2)

        ttk.Label(address_frame, text="Č.p.").grid(row=0, column=2, sticky="w", padx=5, pady=2)
        self.entries["Č.p."] = ttk.Entry(address_frame, width=8)
        self.entries["Č.p."].grid(row=0, column=3, sticky="w", padx=5, pady=2)
        self.entries["Č.p."].bind("<KeyRelease>", self.validate_integer)

        ttk.Label(address_frame, text="Město").grid(row=1, column=0, sticky="e", padx=5, pady=2)
        self.entries["Město"] = ttk.Entry(address_frame, width=30)
        self.entries["Město"].grid(row=1, column=1, columnspan=3, sticky="ew", padx=5, pady=2)

        ttk.Label(address_frame, text="PSČ").grid(row=2, column=0, sticky="e", padx=5, pady=2)
        self.entries["PSČ"] = ttk.Entry(address_frame, width=15)
        self.entries["PSČ"].grid(row=2, column=1, sticky="w", padx=5, pady=2)
        self.entries["PSČ"].bind("<KeyRelease>", self.validate_integer)

        ttk.Label(address_frame, text="Stát").grid(row=3, column=0, sticky="e", padx=5, pady=2)
        self.entries["Stát"] = ttk.Entry(address_frame, width=30)
        self.entries["Stát"].grid(row=3, column=1, columnspan=3, sticky="ew", padx=5, pady=2)

        address_frame.columnconfigure(1, weight=1)

        status_bar = ttk.Label(self.root, text="Author: KOV0393", relief="sunken", anchor="w")
        status_bar.pack(side="bottom", fill="x")

        btn_frame = ttk.Frame(details_frame)
        btn_frame.grid(row=0, column=2, padx=10, pady=5, sticky="ns")

        btn_edit = ttk.Button(btn_frame, text="Upravit", command=self.update_warehouse)
        btn_edit.grid(row=2, column=0, pady=5, padx=5)

        btn_delete = ttk.Button(btn_frame, text="Odstranit", command=self.delete_warehouse)
        btn_delete.grid(row=3, column=0, pady=5, padx=5)

        btn_add = ttk.Button(btn_frame, text="Přidat", command=self.add_warehouse)
        btn_add.grid(row=1,column=0, padx=5, pady=5)


    def update_table(self):
        print(f"Updating table with limit: {self.limit_var.get()} and sorting by: {self.sort_var.get()}")

    def search_item(self):
        field = self.search_field.get()
        value = self.search_entry.get().lower()

        for item in self.tree_items.get_children():
            self.tree_items.delete(item)

        for item in self.items_data:
            if value in str(item[field]).lower():
                self.tree_items.insert("", "end", values=tuple(item.values()))

    def add_item(self):
        new_item = {key: self.entries_item[key].get() for key in self.entries_item}
        self.items_data.append(new_item)
        self.refresh_items_table()

    def update_item(self):
        selected_item = self.tree_items.selection()
        if not selected_item:
            messagebox.showwarning("Upozornění", "Vyberte položku k úpravě.")
            return

        item_index = self.tree_items.index(selected_item)
        updated_item = {key: self.entries_item[key].get() for key in self.entries_item}
        self.items_data[item_index] = updated_item
        self.refresh_items_table()

    def delete_item(self):
        selected_item = self.tree_items.selection()
        if not selected_item:
            messagebox.showwarning("Upozornění", "Vyberte položku k odstranění.")
            return

        item_index = self.tree_items.index(selected_item)
        del self.items_data[item_index]
        self.refresh_items_table()

    def transfer_item(self):
        from_wh = self.from_warehouse.get()
        to_wh = self.to_warehouse.get()
        quantity = self.transfer_quantity.get()

        if not quantity.isdigit() or int(quantity) <= 0:
            messagebox.showwarning("Upozornění", "Zadejte platné množství.")
            return

        messagebox.showinfo("Úspěch", f"Položka byla přesunuta ze skladu {from_wh} do {to_wh}.")

    def refresh_items_table(self):
        self.tree_items.delete(*self.tree_items.get_children())
        for item in self.items_data:
            self.tree_items.insert("", "end", values=tuple(item.values()))


    def sort_by_column(self, column):
        try:
            # Safely sort by column with fallback in case keys are missing
            self.data.sort(key=lambda x: x.get(column, ""))
        except KeyError as e:
            print(f"KeyError: {e} - Make sure all data items have the key '{column}'")
        self.refresh_table()

    def add_warehouse(self):
        new_entry = {}
        for key, widget in self.entries.items():
            if isinstance(widget, tk.Text):
                new_entry[key] = widget.get("1.0", "end").strip()
            else:
                new_entry[key] = widget.get()  # Читаем текст из Entry
        self.data.append(new_entry)
        self.refresh_table()
        self.save_data()
        self.update_warehouse_list()


    def update_warehouse(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Upozornění", "Vyberte sklad k úpravě.")
            return


        item_index = self.tree.index(selected_item)
        updated_entry = {
            key: self.entries[key].get("1.0", "end").strip() if isinstance(self.entries[key], tk.Text) else
            self.entries[key].get()
            for key in self.entries
        }
        self.data[item_index] = updated_entry
        self.refresh_table()
        self.update_warehouse_list()


    def delete_warehouse(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Upozornění", "Vyberte sklad k odstranění.")
            return

        item_index = self.tree.index(selected_item)
        del self.data[item_index]

        self.refresh_table()
        self.save_data()
        self.update_warehouse_list()

    def refresh_table(self):
        self.tree.delete(*self.tree.get_children())
        for item in self.data:
            self.tree.insert("", "end", values=(
                item["ID"], item["Název"], item["Typ"],
                f"{item['Ulice']}, {item['Č.p.']}, {item['Město']}, {item['PSČ']}, {item['Stát']}",
                item["Kapacita"]
            ))

    def update_warehouse_list(self):
        self.warehouses = [self.tree.item(child)["values"][1] for child in self.tree.get_children()]
        self.from_warehouse["values"] = self.warehouses
        self.to_warehouse["values"] = self.warehouses


    def save_data(self):
        with open("warehouses.json", "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=4)
        with open("items.json", "w", encoding="utf-8") as f:
            json.dump(self.items_data, f, ensure_ascii=False, indent=4)

    def load_data(self):
        try:
            with open("warehouses.json", "r", encoding="utf-8") as f:
                self.data = json.load(f)
            with open("items.json", "r", encoding="utf-8") as f:
                self.items_data = json.load(f)
        except FileNotFoundError:
            self.data = []
            self.items_data = []

        self.refresh_table()
        self.update_warehouse_list()

if __name__ == "__main__":
    root = tk.Tk()
    app = WarehouseApp(root)
    root.iconbitmap("icon.ico")
    root.minsize(950, 600)
    root.mainloop()

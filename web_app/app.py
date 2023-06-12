import customtkinter
from web_app.ingest_page import IngestPage
from web_app.db_managment_page import DBManagerPage
from web_app.analysis_page.analysis_page import AnalysisPage
from database import DataBase
import os

customtkinter.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme(os.path.join('web_app', 'my_theme.json'))


class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self.db = DataBase()

        # configure window
        self.title("Accounts Manager")
        self.geometry(f"{1600}x{1000}")
        customtkinter.set_widget_scaling(1.2)

        # create 2x2 grid system
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # create tabview
        self.page_classes = {'Ingest': IngestPage, 'DB Management': DBManagerPage, 'Analysis': AnalysisPage}
        self.pages = {key: None for key in self.page_classes}
        self.tabview = customtkinter.CTkTabview(self, command=self._on_tab_select)
        self.tabview.grid(row=0, column=0, columnspan=2, padx=20, pady=(0, 20), sticky="nsew")

        for key in self.page_classes:
            self.tabview.add(key)
            self.tabview.tab(key).grid_rowconfigure(0, weight=1)
            self.tabview.tab(key).grid_columnconfigure(0, weight=1)

        self.tabview.set('Ingest')
        self._on_tab_select()

    def _on_tab_select(self):
        key = self.tabview.get()
        page_class = self.page_classes[key]

        for k , page in self.pages.items():
            if k != key and page is not None:
                page.destroy()
                self.pages[k] = None

        self.pages[key] = page_class(self.tabview.tab(key), self.db)
        self.pages[key].grid(row=0, column=0, columnspan=2, padx=0, pady=0, sticky="nsew")


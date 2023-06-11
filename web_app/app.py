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
        self.pages = {'Ingest': IngestPage, 'DB Management': DBManagerPage, 'Analysis': AnalysisPage}
        self.tabview = customtkinter.CTkTabview(self)
        self.tabview.grid(row=0, column=0, columnspan=2, padx=20, pady=(0, 20), sticky="nsew")
        self.setup_tabs()

    def setup_tabs(self):
        for key, page_class in self.pages.items():
            self.tabview.add(key)
            self.tabview.tab(key).grid_rowconfigure(0, weight=1)
            self.tabview.tab(key).grid_columnconfigure(0, weight=1)

            self.pages[key] = page_class(self.tabview.tab(key), self.db)
            self.pages[key].grid(row=0, column=0, columnspan=2, padx=0, pady=0, sticky="nsew")

        # self.tabview.set('Analysis')  # TODO: remove added for dev purposes only

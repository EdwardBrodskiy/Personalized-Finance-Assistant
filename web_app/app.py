import tkinter
import tkinter.messagebox
import customtkinter
from web_app.ingest_page import IngestPage
from database import DataBase


customtkinter.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme("my_theme.json")  # Themes: "blue" (standard), "green", "dark-blue"


class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self.db = DataBase()

        # configure window
        self.title("Accounts Manager")
        self.geometry(f"{1200}x{700}")
        customtkinter.set_widget_scaling(1.2)

        # create 2x2 grid system
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # create tabview
        self.tabview = customtkinter.CTkTabview(self)
        self.tabview.grid(row=0, column=0, columnspan=2, padx=20, pady=(0, 20), sticky="nsew")
        self.tabview.add("Ingest")
        self.tabview.add("DB Management")
        self.tabview.add("Analysis")

        self.ingest_page = self.setup_ingest_tab()

    def setup_ingest_tab(self):
        self.tabview.tab('Ingest').grid_rowconfigure(0, weight=1)
        self.tabview.tab('Ingest').grid_columnconfigure(0, weight=1)

        ingest_page = IngestPage(self.tabview.tab('Ingest'), self.db)
        ingest_page.grid(row=0, column=0, columnspan=2, padx=0, pady=0, sticky="nsew")
        return ingest_page


if __name__ == "__main__":
    app = App()
    app.mainloop()

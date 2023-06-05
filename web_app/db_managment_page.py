import customtkinter

from web_app.menu import Menu


class DBManagerPage(customtkinter.CTkFrame):
    def __init__(self, master, db, **kwargs):
        super().__init__(master, **kwargs)

        self.db = db

        self.menu = Menu(self,{
            'run_on_main': (
                'Toggle',
                'Run operations on main database',
                {
                    'command': self.run_on_main
                }
            )
        })

        self.menu.pack()

    def run_on_main(self):
        print('ooo')

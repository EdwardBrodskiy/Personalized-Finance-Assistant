import customtkinter
from database import DataBase
from web_app.menu import Menu
import shutil
from os.path import join

from web_app.notification import Notification
from web_app.warninig_popup import WarningPopup


class DBManagerPage(customtkinter.CTkFrame):
    def __init__(self, master, db: DataBase, **kwargs):
        super().__init__(master, **kwargs)

        self.db = db
        self.menus = customtkinter.CTkFrame(self)

        self.menus.pack()

        self.main_menu = Menu(self.menus, {
            'run_on_main': (
                'Toggle',
                'Run operations on main database',
                {
                    'command': self.run_on_main
                }
            ),

        }, title='Main')

        self.main_menu.pack(fill='x', padx=5, pady=5)

        self.database_ops_menu = Menu(self.menus, {
            'copy_main_ingested': (
                'Button',
                'Copy ingested from main database',
                {
                    'command': self.copy_main_ingested,
                    'text': 'Run'
                }
            ),
            'copy_main_merged': (
                'Button',
                'Copy merged from main database',
                {
                    'command': self.copy_main_merged,
                    'text': 'Run'
                }
            ),
            'copy_main_both': (
                'Button',
                'Copy merged and ingested from main database',
                {
                    'command': self.copy_main_both,
                    'text': 'Run'
                }
            ),

        }, title='Database Operations')

        self.database_ops_menu.pack(fill='x', padx=5, pady=5)

    # Main actions
    def run_on_main(self):
        toggle_state = self.main_menu.elements['run_on_main'][1].state()
        if toggle_state == 'on':

            check = WarningPopup(self, message='Are you sure you want to operate on main', opta='Yes',
                                 optb='No, go back to safety')
            if check.get_input() == 'Yes':
                self.winfo_toplevel().title('Accounts Manager - RUNNING ON MAIN DATABASE')
                self.db.run_on_main(gui=True)
            else:
                self.main_menu.elements['run_on_main'][1].set_state('off')
        else:
            self.winfo_toplevel().title('Accounts Manager')
            self.db.run_not_on_main()

    # Database Ops actions
    def copy_main_ingested(self):
        Notification(self, 'Ingested copied from main')
        shutil.copy2(join('database', 'protected', 'all.csv'), join('database', 'all.csv'))

    def copy_main_merged(self):
        Notification(self, 'Merged copied from main')
        shutil.copy2(join('database', 'protected', 'merged.csv'), join('database', 'merged.csv'))

    def copy_main_both(self):
        print('copy_main_both')
        self.copy_main_ingested()
        self.copy_main_merged()

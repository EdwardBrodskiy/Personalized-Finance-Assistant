import customtkinter

from configuration import get_filepaths
from database import DataBase
from helper_functions import ensure_dir_exists
from web_app.components.menu import Menu
import shutil
from os.path import join

from web_app.components.notification import Notification
from web_app.popups.warninig_popup import WarningPopup


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

        }, title='Main', load_from_save=False)

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

        }, title='Database Operations', load_from_save=False)

        self.database_ops_menu.pack(fill='x', padx=5, pady=5)

    # Main actions
    def run_on_main(self):
        toggle_state = self.main_menu['run_on_main'].get()
        if toggle_state == 'on':

            check = WarningPopup(self, message='Are you sure you want to operate on main', opta='Yes',
                                 optb='No, go back to safety')
            if check.get_input() == 'Yes':
                self.winfo_toplevel().title('Accounts Manager - RUNNING ON MAIN DATABASE')
                self.db.run_on_main(gui=True)
            else:
                self.main_menu['run_on_main'].set('off')
        else:
            self.winfo_toplevel().title('Accounts Manager')
            self.db.run_not_on_main()

    # Database Ops actions
    def copy_main_ingested(self):
        self.copy_protected('all', 'Ingested')

    def copy_main_merged(self):
        self.copy_protected('merged', 'Merged')

    def copy_protected(self, what, ui_name):
        directory = get_filepaths()['database']
        ensure_dir_exists(join(directory, 'protected'))
        try:
            shutil.copy2(join(directory, 'protected', f'{what}.csv'), join(directory, f'{what}.csv'))
            Notification(self, f'{ui_name} copied from main')
        except FileNotFoundError:
            Notification(self, f'{ui_name} does not exist in main database')

    def copy_main_both(self):
        self.copy_main_ingested()
        self.copy_main_merged()

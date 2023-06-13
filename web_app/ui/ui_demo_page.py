import os
import customtkinter as ctk

from web_app.ui.Button import DemoButtons

ctk.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme(os.path.join('..', 'my_theme.json'))


class UIDemoApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("UI Demo App")
        self.geometry(f"{1600}x{1000}")
        ctk.set_widget_scaling(1.2)

        self.buttons = DemoButtons(self)
        self.buttons.pack(fill='x')


if __name__ == "__main__":
    app = UIDemoApp()
    app.mainloop()

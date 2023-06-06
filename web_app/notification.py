import customtkinter as ctk
from web_app.theme_colors import colors


class Notification(ctk.CTkFrame):
    notifications = []

    def __init__(self, master, message, timeout=6000, **kwargs):
        master = master.winfo_toplevel()
        super().__init__(master, fg_color=colors['primary'], **kwargs)

        # find and take spot
        self.selected_spot = Notification.get_next_free_position()
        Notification.notifications[self.selected_spot] = True

        self.place(x=10, y=10 + self.selected_spot * 50, bordermode='outside')

        label = ctk.CTkLabel(self, text=message, padx=16, pady=16)
        label.pack(fill='both')

        self.after(timeout, self.destroy)

    def destroy(self):
        Notification.notifications[self.selected_spot] = False  # free spot
        super().destroy()

    @staticmethod
    def get_next_free_position():
        if False in Notification.notifications:
            return Notification.notifications.index(False)
        else:
            Notification.notifications.append(False)
            return len(Notification.notifications) - 1

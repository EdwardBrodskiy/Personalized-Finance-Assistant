import customtkinter as ctk

from web_app.theme_colors import colors


# TODO : would be nice to add a feature of  don't add new notification if an identical one is already shown
class Notification(ctk.CTkFrame):
    notifications = []

    def __init__(self, master, message, timeout=4000, **kwargs):
        master = master.winfo_toplevel()
        super().__init__(master, fg_color=colors['primary'], **kwargs)

        # find and take spot
        self.selected_spot = Notification.get_next_free_position()
        Notification.notifications[self.selected_spot] = True

        self.place(x=0, y=10 + self.selected_spot * 50, bordermode='outside')

        label = ctk.CTkLabel(self, text=message, padx=8, pady=8)
        label.pack(fill='both', side='left')

        self.close = ctk.CTkButton(self, text='X', command=self.destroy, width=25)
        self.close.pack(side='left', padx=(0, 8), pady=8)
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

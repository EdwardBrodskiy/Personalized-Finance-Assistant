import customtkinter as ctk

from web_app.theme_colors import colors


# TODO : would be nice to add a feature of  don't add new notification if an identical one is already shown
class Notification(ctk.CTkFrame):
    notifications = []

    def __init__(self, master, message, timeout=4000, **kwargs):
        master = master.winfo_toplevel()
        super().__init__(master, fg_color=colors['primary'], **kwargs)
        self.message = message
        self.count = 1
        self.timeout = timeout
        self.twin = self.check_for_identical()
        if self.twin is not None:
            Notification.notifications[self.twin].increase_count()
            return

        # if first of its kind find and take spot
        self.selected_spot = Notification.get_next_free_position()
        Notification.notifications[self.selected_spot] = self

        self.place(x=0, y=10 + self.selected_spot * 50, bordermode='outside')

        self.label = ctk.CTkLabel(self, text=self.message, padx=8, pady=8)
        self.label.pack(fill='both', side='left')

        self.close = ctk.CTkButton(self, text='X', command=self.destroy, width=25)
        self.close.pack(side='left', padx=(0, 8), pady=8)
        self.death = self.after(self.timeout, self.destroy)
    def increase_count(self):
        self.count += 1
        self.label.configure(text=f'{self.message} x{self.count}')
        self.after_cancel(self.death)
        self.death = self.after(self.timeout, self.destroy)

    def destroy(self):
        Notification.notifications[self.selected_spot] = False  # free spot
        super().destroy()

    def check_for_identical(self):
        for index, notification in enumerate(Notification.notifications):
            if type(notification) is Notification and self.message == notification.message:
                return index
        return None

    @staticmethod
    def get_next_free_position():
        if False in Notification.notifications:
            return Notification.notifications.index(False)
        else:
            Notification.notifications.append(False)
            return len(Notification.notifications) - 1

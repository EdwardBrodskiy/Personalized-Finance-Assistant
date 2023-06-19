import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import GLib, Gtk, Adw


class App(Adw.Application):
    def __init__(self):
        super().__init__(application_id="io.github.edwardbrodskiy.Personalized-Finance-Assistant")
        GLib.set_application_name("Personalized Finance assistant")

        self.win = self.builder.get_object("window")

    def do_activate(self):
        self.win.set_application(self)
        self.win.present

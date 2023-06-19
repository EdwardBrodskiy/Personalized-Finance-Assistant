import argparse
from web_app.app import App

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
            prog="Personalized Financial Assistant",
            description="Personalized Financial Assistant"
            )
    parser.add_argument("--gtk", action="store_true")
    args = parser.parse_args()

    if args.gtk:
        print("Run GTK app")
        pass
    else:
        app = App()
        app.mainloop()

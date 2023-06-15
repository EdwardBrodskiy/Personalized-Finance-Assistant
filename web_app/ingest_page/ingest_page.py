import customtkinter

from classifier.rule_classifier import Classifier
from indexer import index as index_input_data
from web_app.ingest_page.ingest_process import IngestProcess


class IngestPage(customtkinter.CTkFrame):
    def __init__(self, master, db, **kwargs):
        super().__init__(master, **kwargs)

        self.db = db
        self.classifier = Classifier(self.db)
        self.ingest_process_active = False

        # lower controls
        self.lower_controls = customtkinter.CTkFrame(self)
        self.lower_controls.pack(side='bottom', anchor='s', fill='x')

        self.lower_controls.grid_columnconfigure(0, weight=1)

        self.bt_run_indexer = customtkinter.CTkButton(self.lower_controls, text='Run Indexer', command=self.run_indexer)
        self.bt_run_indexer.grid(row=0, column=1, sticky='e')

        self.lb_indexer_result = customtkinter.CTkLabel(self.lower_controls, text='Indexer has not been run yet',
                                                        padx=10, pady=10)
        self.lb_indexer_result.grid(row=0, column=0, sticky='e')

        self.bt_run_classifier = customtkinter.CTkButton(self.lower_controls, text='Run classifier',
                                                         command=self.start_ingest_process)
        self.bt_run_classifier.grid(row=1, column=1, sticky='e')

        self.lb_classifier_result = customtkinter.CTkLabel(self.lower_controls, text='Classifier has not been run yet',
                                                           padx=10, pady=10)
        self.lb_classifier_result.grid(row=1, column=0, sticky='e')

        self.ingest_label = customtkinter.CTkLabel(self, text='Press "Run Classifier" to begin the ingest process.')
        self.ingest_label.pack(side='top')
        self.ingest_process = None

    def start_ingest_process(self):
        if not self.ingest_process_active:
            self.classifier.begin_classification()

            self.lb_classifier_result.configure(
                text=f'Classification in progress please enter the required manual information. '
                     f'{len(self.classifier.automatically_labeled)} classified automatically')
            self.bt_run_classifier.configure(text='Finish and save')

            self.ingest_label.pack_forget()
            self.ingest_process = IngestProcess(self, self.classifier, height=2000)
            self.ingest_process.pack(side='top', fill='both')

            self.ingest_process_active = True
        else:
            self.ingest_process.pack_forget()
            self.ingest_label.pack(side='top')
            self.lb_classifier_result.configure(
                text=f'{len(self.classifier.automatically_labeled)} automatic entries saved and {len(self.classifier.labeled_data)} manual entries saved')

            self.db.add_to_merged(self.classifier.automatically_labeled)
            self.db.add_to_merged(self.classifier.labeled_data)

            self.ingest_process_active = False

    def run_indexer(self):
        new = index_input_data(self.db)
        if len(new):
            self.lb_indexer_result.configure(text=f'Indexer was run successfully producing {len(new)} new rows')
        else:
            self.lb_indexer_result.configure(text=f'Indexer ran but no new rows were added!')

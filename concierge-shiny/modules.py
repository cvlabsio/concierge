from shiny import ui, reactive, render, Inputs, Outputs, Session, module
import shutil
import os
from tqdm import tqdm
from concierge_backend_lib.ingesting import insert
from loaders.pdf import load_pdf

@module.ui
def home_ui():
    return ui.markdown(
        """

        # Data Concierge AI

        AI should be simple, safe, and amazing.

        Concierge is an open-source AI framework built specifically for
        how you use data.

        #### Getting started:  
        1. Create a collecion with Collection Manager  
        2. Load PDF or web data into the collection with the Loader  
        3. Use Prompter to work with Concierge.


        #### Tips for getting the most out of Concierge:
        - You can have as many collections as you want. Organize your data how you'd like!
        - Experiment with the selection options in Prompter. You can have Concierge help you with lots of tasks.
        - If you have any problems, reach out to us via github issues or the contact page on https://dataconcierge.ai


        #### Are you a dev? Want to get even more involved?
        - Create a task file to extend Concierge's capabilities
        - Add enhancer files to have parting thoughts
        - Build a loader to allow new data in Concierge
        - Review our github issues, we would love your input
    """)

@module.ui
def loader_ui():
    return [
        ui.markdown("# Loader"),
        ui.output_ui("ingester"),
        ui.input_action_button(id="ingest", label="Ingest")
    ]

@module.server
def loader_server(input: Inputs, output: Outputs, session: Session, collection, upload_dir):
    @render.ui
    @reactive.event(input.ingest, ignore_none=False, ignore_init=False)
    def ingester():
        if "loader_files" in input:
            files = input.loader_files()
            if files and len(files):
                for file in files:
                    shutil.copyfile(file["datapath"], os.path.join(upload_dir, file["name"]))
                    if file["type"] == 'application/pdf':
                        print(file["name"])
                        pages = load_pdf(upload_dir, file["name"])
                        page_progress = tqdm(total=len(pages))
                        with ui.Progress(1, len(pages)) as p:
                            p.set(0, message=f"{file["name"]}: loading...")
                            for x in insert(pages, collection):
                                p.set(x[0] + 1, message=f"{file["name"]}: page {x[0] + 1} of {x[1]}.")
                                page_progress.n = x[0] + 1
                                page_progress.refresh()
                        page_progress.close()
        return ui.input_file(
            id="loader_files",
            label="Documents",
            multiple=True
        )
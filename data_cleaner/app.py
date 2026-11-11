from textual.app import App, ComposeResult
from textual.containers import Container, Vertical
from textual.widgets import Header, Footer, Button, Static, Input, DataTable, RichLog, SelectionList, Label
from textual.screen import ModalScreen
import matplotlib.pyplot as plt
import seaborn as sns
from src.cleaner_engine import DataCleanerEngine

class OutlierModal(ModalScreen):
    def __init__(self, engine, app_ref):
        super().__init__()
        self.engine = engine
        self.app_ref = app_ref

    def compose(self) -> ComposeResult:
        nums = self.engine.get_column_types()['numeric']
        yield Container(
            SelectionList(*[(n, n) for n in nums], id="col_select"),
            Button("Graficar e IQR", id="iqr_btn"),
            Input(placeholder="Min", id="min_in"),
            Input(placeholder="Max", id="max_in"),
            Button("Filtrar Rango", id="range_btn"),
            id="modal_container"
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        col = self.query_one(SelectionList).selected[0] if self.query_one(SelectionList).selected else None
        if not col: return
        if event.button.id == "iqr_btn":
            plt.figure()
            sns.boxplot(x=self.engine.working_df[col])
            plt.savefig("outlier_plot.png")
            self.engine.filter_outliers(col, method='IQR')
            self.app_ref.refresh_ui("Outliers filtrados por IQR (Gráfico en outlier_plot.png)")
        elif event.button.id == "range_btn":
            self.engine.filter_outliers(col, method='manual', min_val=float(self.query_one("#min_in").value), max_val=float(self.query_one("#max_in").value))
            self.app_ref.refresh_ui("Outliers filtrados por rango manual.")
        self.dismiss()

class TextCleanupModal(ModalScreen):
    def __init__(self, engine, app_ref):
        super().__init__()
        self.engine = engine
        self.app_ref = app_ref

    def compose(self) -> ComposeResult:
        cats = self.engine.get_column_types()['categorical']
        yield Container(
            SelectionList(*[(c, c) for c in cats], id="cat_select"),
            Button("Lower", id="lower"), Button("Upper", id="upper"), Button("Title", id="title"),
            Input(placeholder="Viejo", id="old"), Input(placeholder="Nuevo", id="new"),
            Button("Reemplazar", id="replace"),
            id="modal_container"
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        col = self.query_one(SelectionList).selected[0] if self.query_one(SelectionList).selected else None
        if not col: return
        if event.button.id in ['lower', 'upper', 'title']:
            self.engine.clean_text_column(col, method=event.button.id)
        elif event.button.id == "replace":
            self.engine.replace_value(col, self.query_one("#old").value, self.query_one("#new").value)
        self.app_ref.refresh_ui(f"Texto aplicado a {col}")
        self.dismiss()

class DataCleanerApp(App):
    CSS = """
    #modal_container { align: center middle; background: $surface; border: round white; width: 60; height: 30; }
    #log { height: 8; border: round white; }
    #data-table { height: 20; border: round white; }
    Button { margin: 1; }
    """

    def __init__(self):
        super().__init__()
        self.engine = DataCleanerEngine()

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(Input(placeholder="Ruta", id="file_path"), Button("Cargar", id="load_btn"), id="home_screen")
        yield Container(
            Button("Nulos", id="null_btn"), Button("Cols", id="col_btn"), Button("Dupes", id="dupe_btn"),
            Button("Outliers", id="out_btn"), Button("Texto", id="txt_btn"), Input(placeholder="Nombre archivo export", id="save_in"), Button("Exportar", id="save_btn"),
            DataTable(id="data_table"), RichLog(id="log"),
            id="dashboard_screen"
        )
        yield Footer()

    def on_mount(self) -> None: self.query_one("#dashboard_screen").display = False

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "load_btn":
            self.engine.load_data(self.query_one("#file_path", Input).value)
            self.query_one("#home_screen").display = False
            self.query_one("#dashboard_screen").display = True
            self.refresh_ui("Cargado.")
        elif event.button.id == "out_btn": self.push_screen(OutlierModal(self.engine, self))
        elif event.button.id == "txt_btn": self.push_screen(TextCleanupModal(self.engine, self))
        elif event.button.id == "save_btn":
            path = self.query_one("#save_in", Input).value
            self.engine.save_data(path)
            self.refresh_ui(f"Guardado en {path}. Shape original: {self.engine.original_df.shape} Final: {self.engine.working_df.shape}")
        # ... (otros botones 5A, 5B, 5C ya implementados anteriormente)

    def refresh_ui(self, msg):
        log = self.query_one("#log", RichLog)
        log.write(msg)
        table = self.query_one("#data_table", DataTable)
        table.clear()
        df = self.engine.get_preview()
        if df is not None:
            table.add_columns(*df.columns.tolist())
            for row in df.itertuples(index=False): table.add_row(*row)

if __name__ == "__main__":
    app = DataCleanerApp()
    app.run()


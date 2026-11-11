import pandas as pd
import os

class DataCleanerEngine:
    def __init__(self):
        self.original_df = None
        self.working_df = None

    def load_data(self, file_path):
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"El archivo {file_path} no existe.")
        
        if file_path.endswith('.csv'):
            self.original_df = pd.read_csv(file_path)
        elif file_path.endswith(('.xls', '.xlsx')):
            self.original_df = pd.read_excel(file_path)
        else:
            raise ValueError("Formato no soportado. Use CSV o Excel.")
        
        self.working_df = self.original_df.copy()
        return True

    def get_info(self):
        if self.working_df is None:
            return None
        return {
            "shape": self.working_df.shape,
            "dtypes": self.working_df.dtypes
        }

    def get_preview(self, n=5):
        if self.working_df is None:
            return None
        return self.working_df.head(n)

    def get_missing_data(self):
        if self.working_df is None: return None
        missing = self.working_df.isnull().sum()
        missing = missing[missing > 0]
        total_rows = len(self.working_df)
        
        # Simulación de dropna
        rows_after_dropna = len(self.working_df.dropna())
        lost_rows = total_rows - rows_after_dropna
        lost_pct = (lost_rows / total_rows) * 100 if total_rows > 0 else 0
        
        return {
            "missing_counts": missing.to_dict(),
            "lost_rows": lost_rows,
            "lost_pct": lost_pct
        }

    def apply_dropna(self, subset=None):
        self.working_df.dropna(subset=subset, inplace=True)

    def get_redundant_columns(self):
        if self.working_df is None: return None
        to_drop = []
        
        # Categóricas con un nivel / Numéricas con un valor
        for col in self.working_df.columns:
            if self.working_df[col].nunique() <= 1:
                to_drop.append(col)
                
        # Duplicadas (columnas con mismos valores)
        df_T = self.working_df.T
        duplicated = df_T.duplicated()
        to_drop.extend(df_T[duplicated].index.tolist())
        
        return list(set(to_drop))

    def get_duplicates(self):
        if self.working_df is None: return None
        return self.working_df[self.working_df.duplicated()]

    def drop_duplicates(self):
        if self.working_df is None: return
        self.working_df.drop_duplicates(inplace=True)

    def get_outlier_stats(self, column):
        if self.working_df is None or column not in self.working_df.columns: return None
        col = self.working_df[column]
        Q1 = col.quantile(0.25)
        Q3 = col.quantile(0.75)
        IQR = Q3 - Q1
        return {
            "min": col.min(), "max": col.max(),
            "Q1": Q1, "Q3": Q3,
            "lower": Q1 - 1.5 * IQR, "upper": Q3 + 1.5 * IQR
        }

    def clean_text_column(self, column, method='strip'):
        if self.working_df is None or column not in self.working_df.columns: return
        if method == 'lower': self.working_df[column] = self.working_df[column].astype(str).str.lower()
        elif method == 'upper': self.working_df[column] = self.working_df[column].astype(str).str.upper()
        elif method == 'title': self.working_df[column] = self.working_df[column].astype(str).str.title()
        elif method == 'strip': self.working_df[column] = self.working_df[column].astype(str).str.strip()

    def get_value_counts(self, column):
        if self.working_df is None or column not in self.working_df.columns: return None
        return self.working_df[column].value_counts()

    def replace_value(self, column, old_val, new_val):
        if self.working_df is None or column not in self.working_df.columns: return
        self.working_df[column] = self.working_df[column].replace(old_val, new_val)

    def save_data(self, output_path):
        if self.working_df is None: return False
        self.working_df.to_csv(output_path, index=False)
        return True

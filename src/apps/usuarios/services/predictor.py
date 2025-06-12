import pandas as pd
import joblib
import os

# Ruta al modelo entrenado
MODELO_PATH = os.path.join("src", "modelos", "modelo_random_forest_notas.pkl")

# Función para predecir notas futuras
def predecir_nota_final(df_parcial: pd.DataFrame) -> pd.DataFrame:
    if not os.path.exists(MODELO_PATH):
        raise FileNotFoundError(f"No se encontró el modelo en {MODELO_PATH}")

    modelo = joblib.load(MODELO_PATH)

    # Verificamos que existan las columnas necesarias
    required_cols = ["total_evaluaciones", "evaluaciones_registradas", "promedio_actual"]
    if not all(col in df_parcial.columns for col in required_cols):
        raise ValueError(f"El DataFrame debe contener las columnas: {required_cols}")

    # Seleccionamos características
    X = df_parcial[required_cols]

    # Predicción
    df_parcial["nota_predicha"] = modelo.predict(X)
    df_parcial["estado_predicho"] = df_parcial["nota_predicha"].apply(lambda n: "Aprobado" if n >= 51 else "Reprobado")

    return df_parcial

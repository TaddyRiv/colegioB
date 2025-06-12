import pandas as pd
import psycopg2
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error
import joblib
import os

# --- Configuración ---
DB_PARAMS = {
    "host": "localhost",
    "port": 5432,
    "database": "TU_BASE",
    "user": "TU_USUARIO",
    "password": "TU_PASSWORD"
}

MODELO_PATH = os.path.join("src", "modelos", "modelo_random_forest_notas.pkl")

# --- Consulta SQL ---
SQL = """
SELECT
    u.id AS estudiante_id,
    u.nombre AS estudiante_nombre,
    c.nombre AS curso,
    g.nombre AS gestion,
    m.nombre AS materia,
    COUNT(DISTINCT e.id) AS total_evaluaciones,
    COUNT(n.id) AS evaluaciones_registradas,
    AVG(n.nota) AS promedio_actual,
    CASE 
        WHEN COUNT(n.id) = COUNT(DISTINCT e.id) THEN AVG(n.nota)
        ELSE NULL
    END AS nota_final,
    CASE 
        WHEN COUNT(n.id) = COUNT(DISTINCT e.id) THEN TRUE
        ELSE FALSE
    END AS completo
FROM
    usuarios_nota n
JOIN usuarios_evaluacion e ON n.evaluacion_id = e.id
JOIN usuarios_asignacion a ON e.asignacion_id = a.id
JOIN usuarios_materia m ON a.materia_id = m.id
JOIN usuarios_gestion g ON a.gestion_id = g.id
JOIN usuarios_inscripcion i ON n.inscripcion_id = i.id
JOIN usuarios_user u ON i.estudiante_id = u.id
JOIN usuarios_curso c ON i.curso_id = c.id
WHERE
    i.gestion_id = a.gestion_id
GROUP BY
    u.id, u.nombre, c.nombre, g.nombre, m.nombre
ORDER BY
    g.nombre, c.nombre, m.nombre, u.nombre;
"""

def entrenar_modelo():
    print("Conectando a la base de datos...")
    conn = psycopg2.connect(**DB_PARAMS)
    df = pd.read_sql(SQL, conn)
    conn.close()
    print(f"Datos obtenidos: {len(df)} filas")

    df_entrenamiento = df[df["completo"] == True].copy()
    X = df_entrenamiento[["total_evaluaciones", "evaluaciones_registradas", "promedio_actual"]]
    y = df_entrenamiento["nota_final"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    print("Entrenando modelo...")
    modelo = RandomForestRegressor(n_estimators=100, random_state=42)
    modelo.fit(X_train, y_train)

    y_pred = modelo.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    print(f"Error absoluto medio: {mae:.2f}")

    os.makedirs(os.path.dirname(MODELO_PATH), exist_ok=True)
    joblib.dump(modelo, MODELO_PATH)
    print(f"Modelo guardado en: {MODELO_PATH}")

if __name__ == "__main__":
    entrenar_modelo()

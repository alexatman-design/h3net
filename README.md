# h3net - Proyecto de predicción de inflación INPC

Este proyecto recopila datos históricos del Índice Nacional de Precios al Consumidor (INPC), entrena un modelo de regresión lineal simple (mínimos cuadrados) y predice la inflación para los próximos períodos mensual, bimestral, trimestral y semestral.

## Fuente de los datos

El script actualmente obtiene los datos de la API del Banco Mundial (indicador `FP.CPI.TOTL` – Índice de precios al consumidor (2010 = 100)) para México. Si prefieres usar los datos oficiales del INEGI, reemplaza el enlace de descarga en `src/fetch_inpc.py` por el enlace CSV directo del INEGI.

## Requisitos

Instala las dependencias:

```bash
pip install -r requirements.txt
```

## Uso

Ejecuta el pipeline completo:

```bash
python src/update.py
```

Esto hará lo siguiente:
1. Descargará los datos más recientes del INPC.
2. Preprocesará los datos (garantizando frecuencia mensual).
3. Entrenará un modelo de regresión lineal (tiempo como predictor).
4. Generará predicciones para los próximos 1, 2, 3 y 6 meses.
5. Guardará las predicciones en `results/predictions.csv`.
6. (Opcional) Creará una gráfica simple del INPC histórico y el pronóstico guardada como `results/forecast.png`.

## Cómo leer las predicciones

Abre `results/predictions.csv` (o visualízalo directamente en GitHub). El archivo contiene tres columnas:

| Columna | Significado |
|---------|-------------|
| `horizon_months` | Número de meses hacia adelante para los que se realiza la predicción (1, 2, 3, 6). |
| `predicted_inpc` | Valor pronosticado del índice INPC para ese mes futuro. |
| `cumulative_inflation_pct` | Inflación (o deflación) acumulada esperada entre el último INPC conocido y el mes pronosticado, expresada en porcentaje. <br>Fórmula: <br>`((predicted_inpc / last_known_inpc) – 1) × 100` |

- Un valor **negativo** de `cumulative_inflation_pct` indica que el modelo espera que el INPC disminuya (deflación) respecto a hoy.
- Un valor **positivo** indica un aumento esperado de precios (inflación).

### Ejemplo

Si el último INPC conocido es 191.45 y el pronóstico para 1 mes adelante es 171.68, entonces:

```
inflación acumulada = (171.68 / 191.45 – 1) × 100 ≈ –10.33 %
```

Esto sugiere una **deflación del 10.33 %** durante el próximo mes.

## Visualización

Tras ejecutar `src/update.py`, se genera una gráfica `results/forecast.png` que muestra:
- El INPC histórico (línea azul).
- Los puntos de pronóstico para los próximos 1, 2, 3 y 6 meses (marcadores rojos).
- Líneas discontinuas que conectan el último punto histórico con cada predicción para visualizar la tendencia.

Puedes ver la imagen directamente en GitHub bajo `results/forecast.png` o descargarla.

## Estructura del proyecto

```
h3net/
├─ data/                # Datos descargados y procesados
│   ├─ inpc_raw.csv     # Serie descargada
│   └─ inpc_processed.csv# Serie mensual limpia
├─ src/
│   ├─ fetch_inpc.py    # Descarga los datos (API del Banco Mundial por defecto)
│   ├─ preprocess.py    # Asegura frecuencia mensual
│   ├─ model.py         # Entrenamiento y carga del modelo de regresión lineal
│   ├─ predict.py       # Lógica de predicción (usado por update.py)
│   ├─ plot.py          # Crea la gráfica de pronóstico
│   └─ update.py        # Orquestador del pipeline
├─ models/              # Modelo entrenado y fecha de referencia
│   ├─ linreg.pkl
│   └─ linreg_baseline.txt
├─ results/
│   ├─ predictions.csv  # Tabla de pronósticos
│   └─ forecast.png     # Gráfica (se crea después de la primera ejecución)
├─ notebooks/           # Análisis exploratorio opcional
└─ requirements.txt
```

## Personalización

- **Cambiar el horizonte de predicción:** edita la lista `horizons = [1,2,3,6]` en `src/predict.py`.
- **Agregar características (p. ej., estacionalidad):** modifica `src/preprocess.py`.
- **Reemplazar el modelo:** usa otro algoritmo en `src/model.py` y ajusta `src/update.py` según corresponda.
- **Utilizar datos oficiales del INEGI:** sustituye la URL en `src/fetch_inpc.py` por el enlace CSV directo del INEGI.

## Licencia

MIT
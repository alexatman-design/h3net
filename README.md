# h3net - Proyecto de predicción de inflación en México basado en el INPC

Este proyecto recopila datos históricos del Índice Nacional de Precios al Consumidor (INPC), entrena un modelo de regresión lineal simple (mínimos cuadrados) y predice la inflación para los próximos períodos mensual, bimestral, trimestral, semestral y anual (hasta 12 meses).

## Fuente de los datos

El proyecto **usa un archivo CSV local** que debe colocarse en la carpeta `data/` con el nombre `inpc_raw.csv`. Este archivo debe contener al menos dos columnas: `date` (fecha) y `inpc` (valor del índice). El modelo se entrena únicamente con los últimos **36 meses** (3 años) de datos disponibles. Cada vez que se agrega un mes nuevo de datos, se elimina el mes más antiguo del conjunto, manteniendo siempre una ventana móvil de exactamente 36 meses. Esto garantiza que el modelo siempre se entrene con la información más reciente sin acumular datos indefinidamente.

El proyecto está diseñado para utilizar los datos oficiales del INPC publicados por el INEGI (www.inegi.org.mx). Para comenzar rápidamente, el repositorio incluye un archivo de ejemplo con datos desde enero 2023 hasta el mes actual. Para usar datos oficiales, reemplace este archivo con los datos del INPC obtenidos directamente del INEGI.

## Requisitos

Instala las dependencias:

```bash
pip install -r requirements.txt
```

## Uso

Hay tres formas de ejecutar el pipeline:

### 1. Ejecutar el script principal

```bash
python src/update.py
```

Esto hará lo siguiente:
1. Cargará y validará el CSV local (`data/inpc_raw.csv`).
2. Preprocesará los datos (garantizando frecuencia mensual).
3. Seleccionará automáticamente los últimos 36 meses (3 años) de datos para entrenar el modelo, descartando el mes más antiguo al agregar uno nuevo.
4. Entrenará un modelo de regresión lineal (tiempo como predictor).
5. Generará predicciones para los próximos 1, 2, 3, 6 y 12 meses.
6. Guardará las predicciones en `results/predictions.csv`, incluyendo:
   - `base_month`: mes del último INPC conocido (ej. 2026-08).
   - `forecast_month`: mes objetivo de cada horizonte (ej. 2026-09 para 1 mes adelante).
   - `predicted_inpc`: valor pronosticado del INPC para ese mes futuro.
   - `cumulative_inflation_pct`: inflación (o deflación) acumulada esperada entre el `base_month` y el `forecast_month`, expresada en porcentaje.
7. (Opcional) Creará una gráfica simple del INPC histórico y el pronóstico guardada como `results/forecast.png`.

### 2. Usar la función de Python directamente

Si prefieres llamar a una función desde otro script o desde una consola interactiva, puedes usar la función `run_predictions` definida en `src/pipeline.py`:

```python
from src.pipeline import run_predictions

# Ejecuta el pipeline usando el CSV predeterminado (data/inpc_raw.csv)
predicciones = run_predictions()
print(predicciones)
```

También puedes especificar una ruta diferente al CSV:

```python
predicciones = run_predictions(csv_path="ruta/a/tu/inpc.csv")
```

La función devuelve un `pandas.DataFrame` con las columnas:
- `horizon_months`
- `base_month`
- `forecast_month`
- `predicted_inpc`
- `cumulative_inflation_pct`

Además, como efecto secundario, guarda el archivo `results/predictions.csv` y la gráfica `results/forecast.png`.

### 3. Ejecutar el watchdog automático (opcional)

Si deseas que el sistema verifique automáticamente la aparición de nuevos datos y ejecute el pipeline sin intervención manual, puedes usar el script `src/auto_update.py`. Este script se ejecuta en segundo plano y, cada día entre el 1 y el 3 de cada mes, verifica si el CSV contiene datos para el mes actual. Si es así, ejecuta el pipeline y luego espera hasta el próximo día para evitar ejecuciones duplicadas.

Para iniciar el watchdog:

```bash
nohup python src/auto_update.py &
```

Puedes ajustar la frecuencia de consulta mediante la variable de entorno `AUTO_UPDATE_INTERVAL_HOURS` (por defecto 24 horas). Por ejemplo, para consultar cada 6 horas durante los primeros días del mes:

```bash
AUTO_UPDATE_INTERVAL_HOURS=6 nohup python src/auto_update.py &
```

El watchdog seguirá ejecutándose hasta que lo detengas (por ejemplo, con `kill %1` o `pkill -f auto_update.py`).

## Cómo leer las predicciones

Abre `results/predictions.csv` (o visualízalo directamente en GitHub). El archivo contiene cinco columnas:

| Columna | Significado |
|---------|-------------|
| `horizon_months` | Número de meses hacia adelante para los que se hace la predicción (1, 2, 3, 6 y 12). |
| `base_month` | Mes del último INPC conocido (formato YYYY-MM). Este es el mes de referencia desde el cual se calcula la inflación. |
| `forecast_month` | Mes objetivo de la predicción (formato YYYY-MM). |
| `predicted_inpc` | Valor pronosticado del INPC para ese mes futuro. |
| `cumulative_inflation_pct` | Inflación (o deflación) acumulada esperada entre `base_month` y `forecast_month`, expresada en porcentaje. <br>Fórmula: <br>`((predicted_inpc / last_known_inpc) – 1) × 100` donde `last_known_inpc` es el valor del INPC en `base_month`. |

### Ejemplo de interpretación

Supongamos que después de ejecutar el pipeline obtienes:

```
horizon_months,base_month,forecast_month,predicted_inpc,cumulative_inflation_pct
1,2026-08,2026-09,116.45,0.21
2,2026-08,2026-10,116.83,0.53
3,2026-08,2026-11,117.21,0.86
6,2026-08,2027-02,118.34,1.83
12,2026-08,2027-08,120.60,3.77
```

- **Último INPC conocido** (`base_month` = 2026-08) corresponde a **agosto 2026**.
- La fila con `horizon_months = 1` te da el pronóstico para **septiembre 2026** (`forecast_month` = 2026-09):
  - `predicted_inpc` = 116.45
  - `cumulative_inflation_pct` = **+0.21 %**
  → Se espera que entre agosto y septiembre de 2026 los precios suban aproximadamente **0,21 %**.
- La fila con `horizon_months = 2` corresponde a **octubre 2026**, con una inflación acumulada esperada de **+0,53 %** respecto a agosto 2026.
- La fila con `horizon_months = 3` corresponde a **noviembre 2026**, con una inflación acumulada esperada de **+0,86 %** respecto a agosto 2026.
- La fila con `horizon_months = 6` corresponde a **febrero 2027**, con una inflación acumulada esperada de **+1,83 %** respecto a agosto 2026.
- La fila con `horizon_months = 12` corresponde a **agosto 2027**, con una inflación acumulada esperada de **+3,77 %** respecto a agosto 2026.

Un valor **negativo** en `cumulative_inflation_pct` indicaría **deflación** (caída de precios) respecto al mes de referencia.

## Visualización

Tras ejecutar `src/update.py` (o llamar a `run_predictions` o dejar que `auto_update.py` lo haga), se genera una gráfica `results/forecast.png` que muestra:
- El INPC histórico (línea azul).
- Los puntos de pronóstico para los próximos 1, 2, 3, 6 y 12 meses (marcadores rojos).
- Líneas discontinuas que conectan el último punto histórico con cada predicción para visualizar la tendencia.

Puedes ver la imagen directamente en GitHub bajo `results/forecast.png` o descargarla.

## Estructura del proyecto

```
h3net/
├─ data/                # Aquí colocas tu CSV de INPC mensual
│   └─ inpc_raw.csv     # CSV con columnas date,inpc,estimated (se actualiza al cargar)
├─ src/
│   ├─ fetch_inpc.py    # Valida, carga y estima meses faltantes si es necesario
│   ├─ preprocess.py    # Asegura frecuencia mensual
│   ├─ model.py         # Entrenamiento y carga del modelo de regresión lineal
│   ├─ predict.py       # Lógica de predicción (usado por update.py y pipeline.py)
│   ├─ plot.py          # Crea la gráfica de pronóstico
│   ├─ update.py        # Orquestador del pipeline (uso desde línea de comandos)
│   ├─ pipeline.py      # Función `run_predictions` para uso programático
│   └─ auto_update.py   # Watchdog automático que ejecuta el pipeline cuando aparecen nuevos datos
├─ models/              # Modelo entrenado y fecha de referencia (ventana de 3 años)
│   ├─ linreg.pkl
│   └─ linreg_baseline.txt
├─ results/
│   ├─ predictions.csv  # Tabla de pronósticos con meses de referencia y objetivo
│   └─ forecast.png     # Gráfica (se crea después de la primera ejecución)
├─ notebooks/           # Análisis exploratorio opcional
└─ requirements.txt
```

## Personalización

- **Cambiar el horizonte de predicción:** edita la lista `horizons = [1,2,3,6,12]` en `src/predict.py`, `src/pipeline.py` y `src/update.py`.
- **Agregar características (p. ej., estacionalidad):** modifica `src/preprocess.py`.
- **Reemplazar el modelo:** usa otro algoritmo en `src/model.py` y ajusta `src/update.py`, `src/pipeline.py` y `src/auto_update.py` según corresponda.
- **Utilizar tu propio CSV:** coloca el archivo con tus datos mensuales en `data/inpc_raw.csv` (debe tener columnas `date` y `inpc`). El script manejará la lectura, validación y estimación de meses faltantes.

## Licencia

MIT

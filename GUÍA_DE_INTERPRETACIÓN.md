# Guía de interpretación de las predicciones del proyecto h3net

Este documento explica paso a paso cómo leer y entender la tabla de resultados `results/predictions.csv` que se genera al ejecutar el pipeline.

---

## 1. ¿Qué contiene el archivo predictions.csv?

Después de correr `python src/update.py` obtendrás un archivo con esta estructura:

```
horizon_months,base_month,forecast_month,predicted_inpc,cumulative_inflation_pct
1,2026-08,2026-09,116.442928,0.199583
2,2026-08,2026-10,116.818959,0.523159
3,2026-08,2026-11,117.194989,0.846734
6,2026-08,2027-02,118.323079,1.817460
```

Cada fila corresponde a un horizonte de predicción distinto.

| Columna | Significado | Fórmula / detalle |
|---------|-------------|-------------------|
| **horizon_months** | Número de meses hacia adelante para los que se hace la predicción. `1` = próximo mes, `2` = mes siguiente, etc. hasta `12` = un año adelante. | Simplemente el índice del horizonte. |
| **base_month** | Mes del último INPC conocido (el dato más reciente de tu archivo de entrada). Formato `YYYY-MM`. Este es el mes de referencia desde el cual se calcula la inflación. | Extraído de la última fila de `data/inpc_processed.csv`. |
| **forecast_month** | Mes objetivo de la predicción (el mes al que se pronostica). Formato `YYYY-MM`. Se calcula sumando `horizon_months` al `base_month`. | `forecast_month = base_month + horizon_months`. |
| **predicted_inpc** | Valor pronosticado del Índice Nacional de Precios al Consumidor (INPC) para ese mes futuro (`forecast_month`). | El INPC es un índice donde el año base (2010) vale 100. Un número mayor indica precios más altos que en el año base. |
| **cumulative_inflation_pct** | Inflación (o deflación) acumulada esperada entre el **`base_month`** y el **`forecast_month`**, expresada en porcentaje. | `((predicted_inpc / last_known_inpc) – 1) × 100` donde `last_known_inpc` es el valor real del INPC en `base_month`. |

---

## 2. Cómo obtener el último INPC conocido

El último INPC conocido es el valor del INPC correspondiente a la última fila de tu archivo de datos procesados (`data/inpc_processed.csv`). Puedes verlo así:

```bash
tail -1 data/inpc_processed.csv
```

Ejemplo de salida:
```
2026-08-01,115.932144
```
En este caso el último INPC conocido es **115.93** (agosto 2026) y aparecerá como `base_month = 2026-08` en la tabla.

---

## 3. Ejemplo práctico de interpretación

Supongamos que después de ejecutar el pipeline obtienes:

```
horizon_months,base_month,forecast_month,predicted_inpc,cumulative_inflation_pct
1,2026-08,2026-09,116.442928,0.199583
2,2026-08,2026-10,116.818959,0.523159
3,2026-08,2026-11,117.194989,0.846734
6,2026-08,2027-02,118.323079,1.817460
12,2026-08,2027-08,119.500000,3.100000
```

Y tu último INPC conocido (de `data/inpc_processed.csv`) es **115.932144** (agosto 2026).

### Fila 1 – Predicción mensual (septiembre 2026)
- `base_month` = 2026-08 (agosto 2026)  
- `forecast_month` = 2026-09 (septiembre 2026)  
- `predicted_inpc` = 116.442928  
- Inflación acumulada = 0.199583 %  
  Esto significa que el modelo espera que entre **agosto y septiembre de 2026** los precios suban aproximadamente **0,20 %**.  
  En términos prácticos: si una canasta de bienes costaba $100 en agosto, se espera que cueste alrededor de **$100.20** en septiembre.

### Fila 2 – Predicción bimestral (octubre 2026)
- `forecast_month` = 2026-10  
- Inflación acumulada = 0.523159 %  
  Esperado aumento de precios entre **agosto y octubre de 2026** de **0,52 %**.

### Fila 3 – Predicción trimestral (noviembre 2026)
- `forecast_month` = 2026-11  
- Inflación acumulada = 0.846734 %  
  Esperado aumento entre **agosto y noviembre de 2026** de **0,85 %**.

### Fila 4 – Predicción semestral (febrero 2027)
- `forecast_month` = 2027-02  
- Inflación acumulada = 1.817460 %  
  Esperado aumento entre **agosto de 2026 y febrero de 2027** de **1,82 %**.

---

## 4. Qué significa un valor negativo

Si la columna `cumulative_inflation_pct` muestra un número **negativo**, el modelo predice una **deflación** (caída de precios) respecto al `base_month`.

Ejemplo:
```
horizon_months,base_month,forecast_month,predicted_inpc,cumulative_inflation_pct
1,2026-08,2026-09,114.50,-1.23
```
Interpretación: se espera que el INPC baje un **1,23 %** en el próximo mes (deflación leve).

---

## 5. Cómo usar esta información

- **Planificación de gastos personales o familiares:** Si esperas inflación del 0,5 % en los próximos dos meses, puedes ajustar tu presupuesto anticipando un ligero aumento en el costo de vida.
- **Decisiones de inversión:** Una inflación esperada alta puede influir en la elección de instrumentos que protejan contra la pérdida de poder adquisitivo (por ejemplo, instrumentos indexados a inflación).
- **Análisis de tendencias:** Comparar las predicciones de distintos horizontes permite ver si se espera que la inflación se acelere, mantenga constante o disminuya a lo largo del tiempo.

---

## 6. ¿Dónde encontrar la gráfica de predicción?

El pipeline también genera `results/forecast.png`. Esta imagen muestra:

- Línea azul: evolución histórica del INPC (desde la fecha más antigua de tu dataset hasta el último mes conocido, es decir, el `base_month`).
- Puntos rojos: valores pronosticados para cada horizonte (1, 2, 3, 6 meses) correspondientes a cada `forecast_month`.
- Líneas discontinuas rojas: conectan el último punto histórico (`base_month`) con cada predicción para visualizar la tendencia.

Puedes abrir este archivo directamente desde GitHub (en la carpeta `results/`) o descargarlo para verlo con cualquier visor de imágenes.

---

## 7. Resumen rápido para no expertos

1. **Ejecuta** `python src/update.py` (una vez que tienes los datos en `data/`).  
2. **Abre** `results/predictions.csv`.  
3. Mira la fila con `horizon_months = 1` → eso es el pronóstico para el **próximo mes** (`forecast_month`).  
4. La columna `base_month` te indica de qué mes se parte (último dato conocido).  
5. La columna `cumulative_inflation_pct` te dice cuánto se espera que suban o bajen los precios en porcentaje entre esos dos meses.  
6. Si el número es positivo → precios subirán (inflación).  
   Si es negativo → precios bajarán (deflación).  
7. Usa la gráfica `forecast.png` para ver la tendencia completa.

---

### ¡Listo! Con esta guía cualquiera, incluso sin conocimientos técnicos, podrá entender qué significa cada número y cómo utilizarlo para tomar decisiones informadas.

Si tienes alguna duda adicional, no dudes en preguntar. 🚀
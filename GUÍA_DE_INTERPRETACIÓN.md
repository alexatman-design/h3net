# Guía de interpretación de las predicciones del proyecto h3net

Este documento explica paso a paso cómo leer y entender la tabla de resultados `results/predictions.csv` que se genera al ejecutar el pipeline.

---

## 1. ¿Qué contiene el archivo predictions.csv?

Después de correr `python src/update.py` obtendrás un archivo con esta estructura:

```
horizon_months,predicted_inpc,cumulative_inflation_pct
1,116.377280,0.143093
2,116.748670,0.462675
3,117.120060,0.782258
6,118.234231,1.741006
```

Cada fila corresponde a un horizonte de predicción distinto.

| Columna | Significado | Fórmula / detalle |
|---------|-------------|-------------------|
| **horizon_months** | Número de meses hacia adelante para los que se hace la predicción. `1` = próximo mes, `2` = mes siguiente, etc. | Simplemente el índice del horizonte. |
| **predicted_inpc** | Valor pronosticado del Índice Nacional de Precios al Consumidor (INPC) para ese mes futuro. | El INPC es un índice donde el año base (2010) vale 100. Un número mayor indica precios más altos que en el año base. |
| **cumulative_inflation_pct** | Inflación (o deflación) acumulada esperada entre el **último INPC conocido** (el último dato de tu archivo de entrada) y el mes del horizonte, expresada en porcentaje. | `((predicted_inpc / last_known_inpc) – 1) × 100` |

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
En este caso el último INPC conocido es **115.93** (agosto 2026).

---

## 3. Ejemplo práctico de interpretación

Supongamos que después de ejecutar el pipeline obtienes:

```
horizon_months,predicted_inpc,cumulative_inflation_pct
1,116.377280,0.143093
2,116.748670,0.462675
3,117.120060,0.782258
6,118.234231,1.741006
```

Y tu último INPC conocido (de `data/inpc_processed.csv`) es **115.932144** (agosto 2026).

### Fila 1 – Predicción mensual (septiembre 2026)
- `predicted_inpc` = 116.377280  
- Inflación acumulada = 0.143093 %  
  Esto significa que el modelo espera que entre **agosto y septiembre de 2026** los precios suban aproximadamente **0,14 %**.  
  En términos prácticos: si una canasta de bienes costaba $100 en agosto, se espera que cueste alrededor de **$100.14** en septiembre.

### Fila 2 – Predicción bimestral (octubre 2026)
- `predicted_inpc` = 116.748670  
- Inflación acumulada = 0.462675 %  
  Esperado aumento de precios entre **agosto y octubre de 2026** de **0,46 %**.

### Fila 3 – Predicción trimestral (noviembre 2026)
- `predicted_inpc` = 117.120060  
- Inflación acumulada = 0.782258 %  
  Esperado aumento entre **agosto y noviembre de 2026** de **0,78 %**.

### Fila 4 – Predicción semestral (febrero 2027)
- `predicted_inpc` = 118.234231  
- Inflación acumulada = 1.741006 %  
  Esperado aumento entre **agosto de 2026 y febrero de 2027** de **1,74 %**.

---

## 4. Qué significa un valor negativo

Si la columna `cumulative_inflation_pct` muestra un número **negativo**, el modelo predice una **deflación** (caída de precios) respecto al último mes conocido.

Ejemplo:
```
horizon_months,predicted_inpc,cumulative_inflation_pct
1,114.50,-1.23
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

- Línea azul: evolución histórica del INPC (desde la fecha más antigua de tu dataset hasta el último mes conocido).
- Puntos rojos: valores pronosticados para cada horizonte (1, 2, 3, 6 meses).
- Líneas discontinuas rojas: conectan el último punto histórico con cada predicción para visualizar la tendencia.

Puedes abrir este archivo directamente desde GitHub (en la carpeta `results/`) o descargarlo para verlo con cualquier visor de imágenes.

---

## 7. Resumen rápido para no expertos

1. **Ejecuta** `python src/update.py` (una vez que tienes los datos en `data/`).  
2. **Abre** `results/predictions.csv`.  
3. Mira la fila con `horizon_months = 1` → eso es el pronóstico para el **próximo mes**.  
4. La columna `cumulative_inflation_pct` te dice cuánto se espera que suban o bajen los precios en porcentaje respecto a hoy.  
5. Si el número es positivo → precios subirán (inflación).  
   Si es negativo → precios bajarán (deflación).  
6. Usa la gráfica `forecast.png` para ver la tendencia completa.

---

### ¡Listo! Con esta guía cualquiera, incluso sin conocimientos técnicos, podrá entender qué significa cada número y cómo utilizarlo para tomar decisiones informadas.

Si tienes alguna duda adicional, no dudes en preguntar. 🚀
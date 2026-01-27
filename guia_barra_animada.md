# Resumen de Visualización con R y Plotly

A continuación se detallan las instrucciones sobre el código y los tipos de gráficos descritos en las Prácticas 4 y 5.

## Práctica 4: Creación de Múltiples Gráficos (Dashboard)

En este ejercicio se utilizan las librerías `plotly` y `dplyr` para crear un dashboard que combina 8 gráficas de barras y un mapa.

### 1. Preparación y Mapa (Gráfico `plot_geo`)
* **Datos:** Se utiliza el dataframe `state.x77`. [cite_start]Se debe calcular la densidad de cada estado dividiendo la columna `Population` entre la columna `Area` y asignar el resultado a una variable (ej. `density`)[cite: 10, 11].
* **Configuración del Mapa:**
    * [cite_start]Se define la proyección como 'Albers USA'[cite: 9].
    * [cite_start]Se crea un gráfico de tipo `plot_geo` asignando la densidad al parámetro `z`[cite: 12].
    * [cite_start]**Etiquetas:** `locations = state.abb` y `locationmode = 'USA-states'`[cite: 12].
    * [cite_start]**Interacción:** El nombre del estado (`state.name`) debe aparecer al pasar el ratón por encima[cite: 12].

### 2. Gráficos de Barras (Iteración de variables)
* [cite_start]**Proceso:** Se extrae la lista de nombres de columnas de `state.x77` (variable `vars`) para generar un gráfico por cada columna[cite: 13, 14].
* **Configuración del Gráfico:**
    * [cite_start]**Ejes:** Los valores de la columna se asignan al parámetro `x` (`x=state.x77[,var]`) y el nombre del estado al parámetro `y`[cite: 14].
    * [cite_start]**Orientación:** Horizontal[cite: 14].
    * [cite_start]**Estilo:** Se oculta la leyenda, se eliminan las etiquetas del eje Y, y el `hovermode` se configura en `y` para mostrar el nombre del estado al pasar el ratón[cite: 15].

### 3. Composición (Subplots Anidados)
Para lograr la disposición final, se crean subplots anidados:
1.  [cite_start]**Subplot Interno:** Contiene la lista de gráficos de barras con un margen de 0.01 entre ellas[cite: 17].
2.  [cite_start]**Subplot Externo:** Combina el subplot interno (barras) con el mapa generado anteriormente[cite: 18].
    * [cite_start]**Disposición:** Dos filas con proporciones del 30% (primera fila) y 70% (segunda fila), con un margen de 0.1 entre ellas[cite: 19].
    * [cite_start]**Leyenda:** En el `layout()`, la leyenda del subplot interno se coloca en la posición $y=1$ y la barra de colores del mapa en la posición $y=0.5$[cite: 20, 21].

---

## Práctica 5: Gráficos Animados y la Barra de Tiempo

[cite_start]Esta práctica se centra en mostrar la evolución temporal usando `plotly`, `dplyr`, `purrr` y `WDI`[cite: 46, 47].

### ⭐️ EL COMPONENTE CLAVE: La Barra de Animación (`frame`)

La "barra de abajo" (slider con botón de Play) que permite ver cómo cambian los datos no se crea con un comando visual extra, sino **mapeando una variable temporal al atributo `frame`**.

* **¿Cómo funciona?**
  Al asignar una variable (como el `year` o un identificador creado) al parámetro `frame` dentro de la función de Plotly (ej. `plot_ly(..., frame = ~year)`), la librería genera automáticamente:
  1.  El botón de **Play/Pause**.
  2.  La **barra deslizante (slider)** con las etiquetas de tiempo.
* **Comportamiento:**
  Plotly divide los datos en "fotogramas" basándose en los valores únicos de la columna asignada a `frame`. [cite_start]Al pulsar Play, el gráfico recorre esos valores secuencialmente, actualizando la posición de los puntos o líneas[cite: 59, 60, 79].

### Ejercicio 1 y 2: Scatter Plot Animado (Puntos que se mueven)
* **Gráfico Base:**
    * [cite_start]El tamaño de los puntos es proporcional a la población (`pop`) y los colores representan la región[cite: 53, 55].
    * [cite_start]Transparencia de 0.5 para ver superposiciones[cite: 56].
* **Animación (El `frame`):**
    * Se anima la gráfica por años (`year`).
    * [cite_start]**Efecto:** Conforme avanza la barra de tiempo, la posición de los puntos se actualiza automáticamente para reflejar los datos de ese año específico[cite: 59, 60].
    * [cite_start]**Personalización:** Se puede personalizar el texto que aparece sobre la barra de animación (el contador de años grande de fondo)[cite: 61, 62].

### Ejercicio 3: Animación de Líneas (El rastro histórico)
Animar líneas (`add_lines`) es más complejo que animar puntos porque la línea debe "recordar" su pasado para dibujarse progresivamente. Si solo usáramos `frame = ~year` directamente, veríamos un segmento de línea saltando, no creciendo.

#### Fase 1: Preparación de los datos (El truco del acumulado)
Para que la barra de tiempo muestre el crecimiento de la línea, necesitamos "engañar" al `frame`:
1.  [cite_start]**Dividir (`split()`):** Separar los datos por año[cite: 70].
2.  **Acumular (`accumulate()`):** Esta es la clave. [cite_start]Para el año 2000, los datos deben contener lo de 1999 + 2000. Para 2001, lo de 1999 + 2000 + 2001. Se usa `~bind_rows(.x,y)` para esto[cite: 71].
3.  [cite_start]**Identificador de Frame:** Se crea una nueva columna llamada explícitamente `frame` que contiene estos bloques acumulados (`bind_rows(.id="frame")`)[cite: 74].

#### Fase 2: Generación del Gráfico
* **Mapeo:**
    * [cite_start]Eje X: Año (`year`)[cite: 77].
    * [cite_start]Eje Y: Importaciones (`import`)[cite: 78].
    * **Animación:** Se asigna `frame = ~frame` (la columna acumulada creada antes). [cite_start]Esto hace que, al mover la barra, Plotly dibuje todo el historial hasta ese punto[cite: 79].
    * [cite_start]**Color:** País (`country`)[cite: 80].
---
name: Andén
description: Señalética de distribución para una interfaz operativa local
colors:
  forest: "#244c3b"
  lime: "#d9ed9e"
  bg: "#f7f9f7"
  paper: "#ffffff"
  ink: "#20362d"
  muted: "#5b6b61"
  line: "#dce5de"
  side: "#eaf0eb"
  danger: "#973e36"
typography:
  headline:
    fontFamily: "Rubik, sans-serif"
    fontSize: "30px"
    fontWeight: 700
    lineHeight: 1.2
    letterSpacing: "-0.035em"
  title:
    fontFamily: "Rubik, sans-serif"
    fontSize: "18px"
    fontWeight: 700
    letterSpacing: "-0.02em"
  body:
    fontFamily: "Rubik, sans-serif"
    fontSize: "14px"
    fontWeight: 400
    lineHeight: 1.55
  label:
    fontFamily: "Rubik, sans-serif"
    fontSize: "12px"
    fontWeight: 400
rounded:
  badge: "4px"
  field: "6px"
  button: "7px"
  nav: "8px"
  parcel: "9px"
  container: "10px"
  panel: "12px"
spacing:
  compact: "8px"
  control: "10px"
  group: "18px"
  section: "24px"
components:
  button-primary:
    backgroundColor: "{colors.forest}"
    textColor: "{colors.paper}"
    rounded: "{rounded.button}"
    padding: "10px 15px"
    typography: "{typography.label}"
  button-neutral:
    backgroundColor: "{colors.paper}"
    textColor: "{colors.ink}"
    rounded: "{rounded.button}"
    padding: "10px 15px"
  button-lime:
    backgroundColor: "{colors.lime}"
    textColor: "{colors.forest}"
    rounded: "{rounded.button}"
    padding: "10px 15px"
  button-danger:
    backgroundColor: "{colors.paper}"
    textColor: "{colors.danger}"
    rounded: "{rounded.button}"
    padding: "10px 15px"
  field:
    backgroundColor: "{colors.paper}"
    textColor: "{colors.ink}"
    rounded: "{rounded.field}"
    padding: "10px 11px"
  nav-active:
    backgroundColor: "{colors.forest}"
    textColor: "{colors.paper}"
    rounded: "{rounded.nav}"
    padding: "11px 13px"
  badge:
    rounded: "{rounded.badge}"
    padding: "4px 7px"
  parcel:
    backgroundColor: "{colors.paper}"
    textColor: "{colors.ink}"
    rounded: "{rounded.parcel}"
    padding: "13px 12px"
---
# Design System: Andén

## Overview

**Creative North Star: "Señalética de distribución"**

Andén toma la señalética de distribución como mundo visual: superficies claras, verde bosque, tipografía Rubik local y trazos precisos. La jerarquía se construye con espaciado y peso; no usa imágenes decorativas ni indicadores inventados.

La interfaz es compacta y operativa. Los estados tienen nombre además de color, las acciones explicitan su destino y los datos de demostración permanecen identificados, incluso en móvil. La elección confirmada del usuario es un tablero de bultos y estados construido directamente en código; esa primera pantalla no obliga a convertir otras vistas en tableros.

**Key Characteristics:**
- Superficies de tiza y salvia con acciones en bosque.
- Rubik regular y bold, números tabulares en tablas.
- Detalle y transición como controles independientes.

## Colors

### Primary
Bosque identifica navegación activa y acciones principales. Lima acompaña acciones destacadas y selección de texto.

### Neutral
Tiza es el fondo general; papel, las superficies de trabajo. Salvia diferencia navegación y contenedores. Tinta sostiene lectura; muted sirve a contexto secundario y line separa regiones.

El rojo de danger señala acciones destructivas y errores. Los seis estados usan puntos específicos en tonos gris, ocre, azul, violeta, verde y terracota junto a su nombre; esos colores de dominio no forman una segunda jerarquía de acciones.

**The Estado legible Rule.** Cada estado lleva un nombre visible; el color acompaña y no reemplaza esa información.

## Typography

Rubik se sirve localmente en regular y bold, con sans-serif de respaldo. El título principal usa headline y baja a 26 px en móvil. Los títulos de sección usan title; texto base usa body y controles usan label. Los metadatos compactos usan 10–11 px. Las tablas y cantidades emplean números tabulares; los subtítulos limitan su ancho a 70ch.

**The Jerarquía por peso Rule.** Usar Rubik regular para lectura y bold para títulos e identificadores; sostener la jerarquía con espacio antes de agregar decoración.

## Layout

La estructura usa navegación lateral persistente de 208 px y contenido flexible; la cabecera mide como mínimo 70 px. El contenido tiene márgenes laterales de 34 px. A 1050 px la navegación baja a 176 px, los márgenes a 24 px y las composiciones dobles pasan a una columna.

A 650 px la navegación se vuelve horizontal con scroll, los márgenes bajan a 18 px y los formularios quedan en una columna. La etiqueta de demo sigue visible arriba a la derecha. El tablero tiene seis carriles, separación de 12 px y ancho mínimo de 1120 px; en móvil son carriles de 220 px y ancho mínimo de 1380 px. El scroll horizontal pertenece al tablero o a la tabla, no al documento. A partir de 1700 px el tablero elimina su ancho mínimo, amplía separación a 16 px y respira con márgenes de 45 px.

## Elevation & Depth

Fondos, bordes finos y separación producen profundidad cotidiana. Las tarjetas de bulto elevan su posición 2 px al hover y cambian el borde; no agregan sombra. Diálogo y toast usan las sombras registradas en el sidecar. El diálogo atenúa y desenfoca el fondo.

**The Plano operativo Rule.** Las superficies de trabajo se separan por tono y bordes; las sombras quedan para el diálogo y la notificación superpuesta.

## Shapes

Esquinas suaves, con radios diferenciados por escala: badges compactos, campos, botones, navegación y tarjetas; los paneles usan el radio mayor reutilizable. Los puntos de estado son círculos de 7 px. Iconografía de línea mediante SVG, con trazos precisos; no se usan imágenes decorativas.

## Components

### Buttons
Acciones compactas con altura mínima de 40 px. Primario bosque, neutro papel, destacado lima y destructivo en texto rojo sobre botón neutro. Hover oscurece el primario y tiñe el neutro. Los botones pequeños miden al menos 32 px. Disabled reduce opacidad y muestra espera.

### Inputs / Fields
Campos con borde fino, labels visibles y altura mínima de 42 px. El foco cambia el borde; el foco visible general usa contorno de 3 px y separación de 3 px. La búsqueda aplica ese contorno al conjunto mediante focus-within. Cantidades y pagos permiten filas agregables y selectores por nombre.

### Navigation
Cada enlace combina icono SVG y nombre; la opción activa invierte bosque y papel. En móvil mantiene los nombres y permite desplazamiento horizontal. Tabs usan subrayado de 2 px para selección.

### Chips
Badges compactos de fondo tenue y texto legible; variantes de éxito y advertencia acompañan su texto. Los puntos de estado nunca funcionan como única etiqueta.

### Cards / Containers
Tarjetas de bulto blancas con borde, ruta, contenido e información secundaria. Abrir detalle y ejecutar el siguiente paso son botones independientes. Paneles y tablas agrupan información con bordes y fondo papel; las tablas tienen scroll propio y números tabulares.

### Detail dialog and feedback
El diálogo tiene nombre accesible, botón de cierre, cierre con Escape, foco nativo, recorrido e historial del bulto. Solo ofrece la siguiente transición permitida. Errores quedan dentro del formulario; toast informa resultado. La baja lógica pide confirmación explícita. Los reportes incluyen período, sucursal, CSV y vacío real.

La entrada del contenido dura 300 ms, el hover de tarjeta 150 ms y el toast 200 ms. Con reduced-motion se desactivan animaciones y transiciones.

## Do's and Don'ts

### Do:
- **Do** mantener labels visibles, foco visible y enlace de salto.
- **Do** mostrar carga, éxito y error cerca de la operación, con errores dentro del formulario.
- **Do** conservar nombres de estados, acciones explícitas y señal de demo visible.
- **Do** respetar reduced-motion y el scroll propio de tablero y tablas.

### Don't:
- **Don't** agregar imágenes decorativas ni métricas inventadas.
- **Don't** unir apertura del detalle y transición en un único control.
- **Don't** ofrecer drag-and-drop que omita las reglas de State.

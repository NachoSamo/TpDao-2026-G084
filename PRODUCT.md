# TP DAO G084
<!-- impeccable:product-schema 1 -->

## Platform
web

## Users
Operarios del CD, encargados de locales y vendedores. El grupo G084 usa la aplicación para demostrar y defender el TP integrador de DAO.

## Product Purpose
Gestionar catálogo, stock, reposición, bultos, remitos, recepción, ventas y devoluciones. Solo mercadería verificada habilita venta.

## Capabilities and Constraints
Reutilizar los servicios Python, DAO SQLite, State y Observer existentes. Cuatro reportes y exportación CSV. Operación local sin autenticación ni pagos reales. Mantener los supuestos aceptados en docs/implementacion.md y documentar web como reemplazo de interfaz. No publicar ni desplegar.

## Operating Context
El usuario eligió tablero de bultos por estados como pantalla principal. Necesita abrir una URL y recorrer todos los procesos sin escribir IDs manualmente.

## Evidence on Hand
Esquema, servicios, demo y pruebas en distribucion/ y tests/. Datos de demostración identificados como tales, sin métricas comerciales inventadas.

## Product Principles
- Hacer visible el próximo paso permitido de cada bulto.
- Elegir productos y sucursales por nombre.
- Guardar cada operación completa o revertirla.
- No confundir presencia física con stock vendible.

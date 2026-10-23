# Texto para compartir con el grupo

Quedó preparada en la rama `rama-juani` una implementación funcional del TP con interfaz web: tablero de bultos por estado, catálogo, inventario, reposición/remitos, ventas con pagos divididos, devoluciones y los cuatro reportes con CSV. Mantiene Python + SQLite con DAO, State para los bultos y Observer para stock bajo. Strategy no se implementó.

Quedaron estos docs para revisar:

- `docs/pruebas-y-decisiones.md`: cómo levantarlo y probarlo paso a paso, por qué se tomaron las decisiones y qué registros guarda cada operación.
- `docs/patrones-de-diseno.md`: explicación de State, Observer y DAO, dónde están en el código, diagramas y Mermaid editable. También están los `.mmd` en `docs/diagramas/`.
- `docs/defensa.md`: qué pide el TP, cómo lo cubre la app y un recorrido para explicar el flujo, los patrones y la persistencia.
- `docs/persistencia.md`: cómo se genera y conserva la base, respaldos y qué diferencia hay entre subir a GitHub y tener una app compartida.
- `docs/registro-pruebas.md`: verificaciones realizadas y límites de lo probado.

No subí el `.db`: cada uno genera su demo local con los mismos datos desde el código. En el README están los comandos; no hay que instalar paquetes para ejecutar la web.

La idea es que la probemos y revisemos entre los tres antes de darla por lista. Falta validar con la cátedra la recepción parcial de remitos, el alcance mínimo de compras y el formato de interfaz/entrega. No está mergeado a `main` ni desplegado. El push está pendiente de habilitar el permiso de escritura del repo para `juaniarrigoni`.

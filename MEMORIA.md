# Memoria de sesión — TP DAO G084

## 2026-10-23 — Codex — Web Andén, documentación y rama de Juan

- Interfaz principal reemplazada por web local con tablero de bultos elegido por el usuario. API Python stdlib, servicios/State/Observer y SQLite conservados. HTML/CSS/JS y Rubik local OFL, sin dependencias de ejecución externas.
- Demo visual con 10 bultos/3 locales; launcher macOS actualizado a web. Servidor en 127.0.0.1:8080, base demo-anden.db (no versionada).
- Verificación: 25 tests dominio/HTTP verdes; E2E Chromium con seis rutas, catálogo, ciclo logístico, mínimo/Observer, venta multiproducto/pagos, devolución y cuatro reportes/CSV. Capturas desktop/móvil sin overflow del documento. Sin prueba Windows.
- Corregidos listener de formularios con control name=id, nombres accesibles, favicon y cuatro ajustes visuales. Registro de alcance/límites en docs/registro-pruebas.md.
- Usuario pidió subir a una rama “rama juani”: nombre Git válido rama-juani. Docs nuevos pruebas-y-decisiones.md, patrones-de-diseno.md con Mermaid y .mmd, persistencia.md, defensa.md ampliado y mensaje-grupo.md. Sin merge ni deploy.
- Persistencia decidida: esquema y seeds versionados; cada integrante genera su .db local, excluido junto con journals/WAL/SHM. No hay base compartida ni migraciones de tablas existentes.
- Push bloqueado: git push -u origin rama-juani devuelve 403 “Permission denied to juaniarrigoni”; GitHub connector create_branch también 403 “Resource not accessible by integration”. Commit de implementación/docs 9844b3722a8515136a288fee356466c302690164, rama solo local; pendiente permiso colaborador/invitación. No se creó fork ni PR.
- Pendiente: subir con git push -u origin rama-juani tras habilitar permisos, revisión del grupo y cátedra de remitos mixtos, alcance compras y formato de entrega; revisar límites de DAO genérico, idempotencia de ventas, cancelaciones, login y despliegue.

## 2026-10-23 — Codex — Implementación integral inicial

- Usuario autorizó un agente para implementar el TP completo con los supuestos de stock, mixtos, rechazos y devoluciones previamente propuestos.
- Se creó `distribucion/`: modelos State/Observer, esquema/DAO SQLite, servicios transaccionales, catálogo, compras mínimas, logística, ventas/devoluciones, cuatro reportes y UI ttk con consultas/CSV.
- Demo reproducible y 17 tests de integración, todos verdes con Python 3.12 y 3.14. Compilación OK. Smoke ttk con construcción completa/tablas/reportes OK usando runtime bundled Python 3.12 fuera del sandbox (el Python del sistema no tiene `_tkinter`). Sin validación manual visual completa ni Windows.
- README explica ejecución macOS/Windows. `docs/implementacion.md` documenta decisiones/límites y `docs/defensa.md` guía la defensa. Actualizados stack, negocio y secuencias; se preservó el material previo.
- Sin dependencias externas, sin commits, push ni publicación. Bases demo temporales fuera del repo.
- Pendiente: revisión del grupo, prueba visual con Python/Tk instalado localmente, confirmar con cátedra remitos mixtos/Tkinter/formato de entrega. No hay cancelación de bultos/órdenes, autenticación, pagos reales ni facturación fiscal.

# Diagramas de secuencia — propuesta para validar

Estos diagramas muestran mensajes entre objetos para casos concretos. Complementan el diagrama de clases (estructura), el DER (persistencia) y la máquina de estados (transiciones).

Los servicios y DAO están implementados en `distribucion/`; estos diagramas conservan nombres conceptuales para explicar las colaboraciones. Se usa precio de lista; Strategy queda fuera del alcance inicial.

## 1. Registrar una venta y avisar stock bajo — Observer

Ejemplo: quedan 11 unidades, se venden 2 y el mínimo es 10. Venta, cobros, comprobante, stock, movimientos y eventual reposición deben confirmarse juntos; cualquier error revierte la operación completa. La UI recibe el resultado después del commit.

```mermaid
sequenceDiagram
    actor Vendedor
    participant UI as PantallaVentas
    participant Servicio as ServicioVentas
    participant DAO as DAOVentasInventario
    participant Venta as venta:Venta
    participant Stock as stock:Stock
    participant Observer as generador:GeneradorReposicionAutomatica
    participant Orden as orden:OrdenReposicion
    participant DB as SQLite

    Vendedor->>UI: confirmar productos y medios de pago
    UI->>Servicio: registrar_venta(sucursal, items, pagos)
    Servicio->>DB: BEGIN
    Servicio->>DAO: cargar productos, precios y stocks
    DAO->>DB: SELECT
    DB-->>DAO: datos actuales
    DAO-->>Servicio: objetos del dominio
    Servicio->>Venta: agregar detalles y cobros
    Servicio->>Venta: validar total y suma de cobros
    loop Cada producto vendido
        Servicio->>Stock: disponibleParaVenta()
        Stock-->>Servicio: cantidad vendible
    end
    alt Datos inválidos, cobros distintos al total o stock insuficiente
        Servicio->>DB: ROLLBACK
        Servicio-->>UI: error de validación
    else Venta válida
        loop Cada producto vendido
            Servicio->>Stock: egresar(cantidad)
            Stock->>Stock: descontar y crear MovimientoStock
            opt Stock queda bajo mínimo
                Stock->>Observer: stockBajoMinimo(stock)
                Observer->>Orden: consolidar necesidad pendiente
                Note over Observer,Orden: Propuesta: descontar lo ya pedido para no duplicar reposición
            end
        end
        Servicio->>Venta: emitir comprobante
        Servicio->>DAO: guardar venta, cobros, comprobante y cambios
        DAO->>DB: INSERT / UPDATE parametrizados
        Servicio->>DB: COMMIT
        Servicio-->>UI: venta confirmada y comprobante
    end
    Note over Servicio,DB: Ante error de persistencia: ROLLBACK y descartar objetos modificados
```

## 2. Recibir y verificar un bulto — State

Recepción y verificación son acciones distintas. Primero el bulto pasa de En tránsito a Recibido. Después, el estado Recibido permite verificar o rechazar. Cada bulto verificado habilita su contenido; el remito resume los resultados y puede ser parcialmente aceptado. Interpretación pendiente de cátedra.

```mermaid
sequenceDiagram
    actor Encargado
    participant UI as Pantalla de recepcion
    participant Servicio as ServicioLogistica
    participant Bulto as bulto - BultoContenedor
    participant Estado as estadoActual - EstadoBulto
    participant Remito as remito - Remito
    participant Stock as stockLocal - Stock
    participant DAO as DAOLogisticaInventario

    Note over Servicio,DAO: Cada operacion se guarda en una transaccion atomica
    Encargado->>UI: Registrar llegada del bulto
    UI->>Servicio: recibir_bulto(id, precinto_integro)
    Servicio->>DAO: cargar_bulto_y_remito(id)
    DAO-->>Servicio: bulto y remito
    Servicio->>Bulto: recibir()
    Bulto->>Estado: recibir(bulto)

    alt El estado permite recibir
        Estado->>Bulto: cambiar_estado(EstadoRecibido)
        Bulto->>Bulto: registrar CambioEstadoBulto
        Bulto-->>Servicio: transicion realizada
        Servicio->>DAO: guardar recepcion, bulto e historial
        DAO-->>Servicio: operacion confirmada
        Servicio-->>UI: Recepcion registrada sin ingresar stock
    else Transicion no permitida
        Estado-->>Bulto: error de estado
        Bulto-->>Servicio: error de estado
        Servicio-->>UI: Informar error sin guardar cambios
    end

    Note over Encargado,DAO: La revision posterior es una operacion independiente
    Encargado->>UI: Confirmar revision del precinto
    UI->>Servicio: verificar_bulto(id)
    Servicio->>DAO: cargar_bulto_recepcion_y_remito(id)
    DAO-->>Servicio: objetos actualizados

    alt El bulto esta Recibido
        alt El precinto esta integro
            Servicio->>Bulto: verificar()
            Bulto->>Estado: verificar(bulto)
            Estado->>Bulto: cambiar_estado(EstadoVerificado)
        else El precinto esta roto
            Servicio->>Bulto: rechazar(motivo)
            Bulto->>Estado: rechazar(bulto, motivo)
            Estado->>Bulto: cambiar_estado(EstadoRechazado)
        end
        Bulto->>Bulto: registrar CambioEstadoBulto
        Bulto-->>Servicio: transicion realizada
        Servicio->>Remito: actualizarEstadoSegunBultos()
        Remito-->>Servicio: estado actualizado
        opt Bulto verificado
            loop Productos del bulto verificado
                Servicio->>Stock: ingresarVerificado(cantidad)
                Stock->>Stock: registrar MovimientoStock
            end
        end
        Servicio->>DAO: guardar estados, historial y movimientos juntos
        DAO-->>Servicio: operacion confirmada
        Servicio-->>UI: Mostrar resultado de la revision
    else El bulto no esta Recibido
        Servicio-->>UI: Informar error sin guardar cambios
    end
    Note over Servicio,DAO: Si falla el guardado se revierte toda la operacion
    Note over Bulto,Stock: Un bulto rechazado nunca ingresa stock vendible
```

**Decisión implementada:** verificación individual; solo el bulto correcto ingresa stock. El remito resume los bultos y queda parcialmente aceptado si hay resultados mixtos. Validar esta interpretación con la cátedra. Rechazo no implica merma ni existe estado adicional Disponible.

## Cómo usarlo en Mermaid

Copiar el contenido de cada bloque, desde `sequenceDiagram`, en Mermaid Live o Mermaid Chart. Son dos diagramas independientes. No se publicó ni se modificó ningún diagrama remoto.

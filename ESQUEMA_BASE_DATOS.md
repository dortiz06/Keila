# Esquema Entidad-Relación - Sistema de Recursos Humanos

## Diagrama de Base de Datos

```
┌─────────────────────────────────────────────────────────────────────┐
│                         SISTEMA DE RECURSOS HUMANOS                  │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────┐
│       User          │  (Django Auth)
│─────────────────────│
│ • id (PK)           │
│ • username          │
│ • email             │
│ • first_name        │
│ • last_name         │
└─────────────────────┘
          │
          │ 1:1
          ▼
┌─────────────────────────────────────────────┐
│                 Perfil                       │
│─────────────────────────────────────────────│
│ • id (PK)                                    │
│ • usuario_id (FK) → User                     │
│ • tipo_perfil (EMPLEADO, JEFE_AREA, RH,     │
│   SISTEMAS, ADMIN)                           │
│ • numero_empleado (UNIQUE)                   │
│ • fecha_contratacion                        │
│ • departamento_id (FK) → Departamento        │
│ • supervisor_id (FK) → Perfil               │
│ • puesto                                      │
│ • activo                                      │
│ • telefono                                    │
│ • fecha_nacimiento                           │
│ • salario                                     │
│ • direccion                                   │
│ • dias_vacaciones_anuales                   │
│ • dias_vacaciones_usados                    │
│ • dias_vacaciones_extraordinarios            │
│ • dias_vacaciones_acumulados                │
│ • ultimo_reset_vacaciones                   │
│ • fecha_creacion                             │
│ • fecha_actualizacion                        │
└─────────────────────────────────────────────┘
          │
          │ N:1              │ N:1
          ▼                  ▼
┌──────────────────┐  ┌──────────────────┐
│  Departamento    │  │ SolicitudVacac.  │
│──────────────────│  │──────────────────│
│ • id (PK)        │  │ • id (PK)         │
│ • nombre (UNIQUE)│  │ • empleado_id (FK)│
│ • descripcion    │  │ • fecha_inicio    │
│ • jefe_id (FK)   │  │ • fecha_fin       │
│   → Perfil       │  │ • dias_solicitados│
│ • activo         │  │ • tipo            │
└──────────────────┘  │ • estado          │
                      │ • motivo          │
                      │ • aprobado_por_   │
                      │   jefe_id (FK)    │
                      │ • aprobado_por_   │
                      │   rh_id (FK)      │
                      │ • comentarios_jefe│
                      │ • comentarios_rh  │
                      │ • fecha_solicitud │
                      │ • fecha_aprob_    │
                      │   jefe            │
                      │ • fecha_aprob_rh  │
                      └──────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                    MÓDULO DE EQUIPOS Y TICKETS IT                    │
└─────────────────────────────────────────────────────────────────────┘

┌──────────────────┐
│ CategoriaEquipo  │
│──────────────────│
│ • id (PK)        │
│ • nombre         │
│ • descripcion     │
│ • activo         │
└──────────────────┘
          │
          │ 1:N
          ▼
┌────────────────────────────────────┐
│            Equipo                 │
│────────────────────────────────────│
│ • id (PK)                         │
│ • categoria_id (FK)                │
│ • marca                           │
│ • modelo                          │
│ • numero_serie (UNIQUE)           │
│ • codigo_inventario (UNIQUE)      │
│ • estado (DISPONIBLE, ASIGNADO,   │
│   EN_REPARACION, DADO_DE_BAJA)    │
│ • fecha_adquisicion               │
│ • observaciones                   │
│ • fecha_creacion                  │
│ • fecha_actualizacion            │
└────────────────────────────────────┘
          │
          │ 1:N
          ▼
┌────────────────────────────────────┐
│       AsignacionEquipo            │
│────────────────────────────────────│
│ • id (PK)                         │
│ • equipo_id (FK) → Equipo         │
│ • empleado_id (FK) → Perfil       │
│ • asignado_por_id (FK) → Perfil   │
│ • fecha_asignacion                │
│ • fecha_devolucion                │
│ • condicion_entrega               │
│ • condicion_devolucion            │
│ • observaciones                   │
│ • fecha_creacion                  │
│ • fecha_actualizacion            │
└────────────────────────────────────┘

┌────────────────────────────────────┐
│            Ticket                  │
│────────────────────────────────────│
│ • id (PK)                         │
│ • codigo (UNIQUE, TKT-YYYYMMDD-XXX)│
│ • empleado_id (FK) → Perfil       │
│ • asignado_a_id (FK) → Perfil     │
│ • tipo (HARDWARE, SOFTWARE, RED,  │
│   ACCESO, OTRO)                   │
│ • area                            │
│ • dispositivo                     │
│ • prioridad (BAJA, MEDIA, ALTA,   │
│   URGENTE)                        │
│ • descripcion                     │
│ • estado (PENDIENTE, EN_PROCESO,  │
│   RESUELTO, CANCELADO)            │
│ • solucion                        │
│ • fecha_creacion                  │
│ • fecha_asignacion                │
│ • fecha_resolucion                │
│ • fecha_actualizacion            │
└────────────────────────────────────┘

┌──────────────────┐
│ ConfiguracionSistema│
│──────────────────│
│ • id (PK)        │
│ • nombre         │
│ • valor          │
│ • descripcion    │
└──────────────────┘
```

## Relaciones Detalladas

### 1. USER ↔ PERFIL (1:1)
- **Tipo:** Uno a Uno (OneToOne)
- **Relación:** Cada usuario de Django tiene un único perfil en el sistema
- **Cardinalidad:** 1:1
- **Comportamiento:** Si se elimina User, se elimina Perfil (CASCADE)

### 2. PERFIL ↔ DEPARTAMENTO (N:1)
- **Tipo:** Muchos a Uno (ManyToOne)
- **Relación:** Cada empleado pertenece a un departamento
- **Cardinalidad:** N:1
- **Comportamiento:** Si se elimina Departamento, Perfil.departamento = NULL (SET_NULL)

### 3. PERFIL ↔ PERFIL (N:1) - AUTO-REFERENCIA
- **Tipo:** Muchos a Uno - Relación Supervisor
- **Relación:** Cada empleado puede tener un supervisor
- **Cardinalidad:** N:1
- **Comportamiento:** Si se elimina supervisor, Perfil.supervisor = NULL (SET_NULL)

### 4. DEPARTAMENTO ↔ PERFIL (1:N)
- **Tipo:** Uno a Muchos
- **Relación:** Un departamento tiene un jefe
- **Cardinalidad:** 1:N (jefe)
- **Comportamiento:** Si se elimina el jefe, Departamento.jefe = NULL (SET_NULL)

### 5. PERFIL ↔ SOLICITUDVACACIONES (1:N)
- **Tipo:** Uno a Muchos
- **Relación:** Un empleado puede tener múltiples solicitudes de vacaciones
- **Cardinalidad:** 1:N
- **Relaciones adicionales:**
  - Aprobado por Jefe (aprobado_por_jefe) → Perfil
  - Aprobado por RH (aprobado_por_rh) → Perfil

### 6. CATEGORIAEQUIPO ↔ EQUIPO (1:N)
- **Tipo:** Uno a Muchos
- **Relación:** Cada equipo pertenece a una categoría
- **Cardinalidad:** 1:N
- **Comportamiento:** PROTECT (no se puede eliminar categoría si tiene equipos)

### 7. EQUIPO ↔ ASIGNACIONEQUIPO (1:N)
- **Tipo:** Uno a Muchos
- **Relación:** Cada equipo puede tener múltiples asignaciones (historial)
- **Cardinalidad:** 1:N
- **Comportamiento:** CASCADE (si se elimina equipo, se eliminan asignaciones)

### 8. PERFIL ↔ ASIGNACIONEQUIPO (1:N)
- **Tipo:** Uno a Muchos
- **Relación:** Cada empleado puede tener múltiples asignaciones de equipos
- **Cardinalidad:** 1:N
- **Relaciones adicionales:**
  - asignado_por (quien asignó) → Perfil

### 9. PERFIL ↔ TICKET (1:N)
- **Tipo:** Uno a Muchos
- **Relación:** Cada empleado puede crear múltiples tickets
- **Cardinalidad:** 1:N
- **Relaciones adicionales:**
  - asignado_a (quien resuelve) → Perfil

## Atributos Clave

### Tipos de Perfil (tipo_perfil)
- EMPLEADO: Empleado regular
- JEFE_AREA: Jefe de área
- RH: Recursos Humanos
- SISTEMAS: Personal de IT/Sistemas
- ADMIN: Administrador

### Estados de Solicitud de Vacaciones
- PENDIENTE_JEFE: Esperando aprobación del jefe
- APROBADO_JEFE: Aprobado por jefe
- RECHAZADO_JEFE: Rechazado por jefe
- PENDIENTE_RH: Esperando aprobación de RH
- APROBADO_RH: Aprobado por RH
- RECHAZADO_RH: Rechazado por RH
- CANCELADO: Cancelado

### Tipos de Vacaciones
- NORMAL: Vacación normal
- EXTRAORDINARIA: Vacación extraordinaria
- EMERGENCIA: Vacación de emergencia

### Estados de Equipos
- DISPONIBLE: Disponible para asignar
- ASIGNADO: Asignado a un empleado
- EN_REPARACION: En reparación
- DADO_DE_BAJA: Dado de baja

### Estados de Tickets
- PENDIENTE: Esperando asignación
- EN_PROCESO: En proceso de resolución
- RESUELTO: Resuelto
- CANCELADO: Cancelado

### Tipos de Tickets
- HARDWARE: Problema de hardware
- SOFTWARE: Problema de software
- RED: Problema de red/conectividad
- ACCESO: Problema de acceso/permisos
- OTRO: Otro tipo

### Prioridades de Tickets
- BAJA: Baja prioridad
- MEDIA: Prioridad media
- ALTA: Alta prioridad
- URGENTE: Urgente

## Índices y Constraints

### Unique Constraints
- User.username
- Perfil.numero_empleado
- Departamento.nombre
- Equipo.numero_serie
- Equipo.codigo_inventario
- SolicitudVacaciones (implícito por lógica de negocio)
- Ticket.codigo

### Foreign Keys
- Perfil.usuario → User
- Perfil.departamento → Departamento
- Perfil.supervisor → Perfil (auto-referencia)
- Departamento.jefe → Perfil
- SolicitudVacaciones.empleado → Perfil
- SolicitudVacaciones.aprobado_por_jefe → Perfil
- SolicitudVacaciones.aprobado_por_rh → Perfil
- Equipo.categoria → CategoriaEquipo
- AsignacionEquipo.equipo → Equipo
- AsignacionEquipo.empleado → Perfil
- AsignacionEquipo.asignado_por → Perfil
- Ticket.empleado → Perfil
- Ticket.asignado_a → Perfil

## Flujos de Datos

### 1. Flujo de Vacaciones
```
Empleado → SolicitudVacaciones → Estado PENDIENTE_JEFE
    ↓
Jefe → Aprueba/Rechaza → Estado APROBADO_JEFE o RECHAZADO_JEFE
    ↓
RH → Aprueba/Rechaza → Estado APROBADO_RH o RECHAZADO_RH
    ↓
Sistema → Actualiza dias_vacaciones_usados del Perfil
```

### 2. Flujo de Asignación de Equipos
```
Equipo (Estado: DISPONIBLE) → AsignacionEquipo (fecha_asignacion)
    ↓
Equipo (Estado: ASIGNADO)
    ↓
Devolución → AsignacionEquipo (fecha_devolucion)
    ↓
Equipo (Estado: DISPONIBLE)
```

### 3. Flujo de Tickets
```
Empleado → Ticket (Estado: PENDIENTE)
    ↓
Sistemas → Asignar → Ticket (Estado: EN_PROCESO, asignado_a)
    ↓
Resolver → Ticket (Estado: RESUELTO, fecha_resolucion)
```

## Propiedades Calculadas

### Perfil
- `dias_vacaciones_disponibles`: Calcula días disponibles según antigüedad y días usados
- `dias_vacaciones_extraordinarios_disponibles`: Para empleados con menos de 1 año
- `antiguedad_anos`: Calcula años de antigüedad
- `antiguedad_detallada`: Antigüedad con años y meses
- `dias_vacaciones_segun_antiguedad`: Calcula días según tabla de antigüedad
- `calcular_dias_acumulados_hasta_hoy`: Días acumulados hasta hoy
- `calcular_total_disponible_proyectado`: Total de días disponibles proyectados

### Departamento
- `empleados_count`: Cuenta empleados activos del departamento

### Equipo
- `asignacion_actual`: Retorna la asignación activa
- `empleado_asignado`: Empleado que tiene el equipo asignado

### AsignacionEquipo
- `esta_activa`: Verifica si la asignación está activa

### Ticket
- `tiempo_respuesta`: Tiempo desde creación hasta asignación
- `tiempo_resolucion`: Tiempo desde creación hasta resolución

## Señales (Signals)

### post_save - User → Perfil
Cuando se crea un User, se crea automáticamente un Perfil asociado con valores por defecto.


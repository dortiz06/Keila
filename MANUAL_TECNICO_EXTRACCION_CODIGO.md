# MANUAL TÉCNICO - EXTRACCIÓN DE INFORMACIÓN DEL CÓDIGO FUENTE
## Sistema GK - Sistema de Gestión de RR.HH. y TI para Grupo Keila

**Versión del Documento:** 1.0  
**Fecha de Generación:** 2024  
**Idioma:** Español Mexicano Corporativo  
**Nivel Técnico:** Usuarios Finales + Técnicos

---

## ÍNDICE

1. [ESTRUCTURA GENERAL DEL SISTEMA](#1-estructura-general-del-sistema)
2. [MÓDULO DE RECURSOS HUMANOS (RR.HH.)](#2-módulo-de-recursos-humanos-rrhh)
3. [MÓDULO DE SOPORTE TI (TICKETS)](#3-módulo-de-soporte-ti-tickets)
4. [MÓDULO DE INVENTARIO Y EQUIPOS](#4-módulo-de-inventario-y-equipos)
5. [DASHBOARD Y MÉTRICAS](#5-dashboard-y-métricas)
6. [SEGURIDAD Y AUTENTICACIÓN](#6-seguridad-y-autenticación)
7. [NOTIFICACIONES Y ALERTAS](#7-notificaciones-y-alertas)
8. [DATOS Y EJEMPLOS](#8-datos-y-ejemplos)
9. [VALIDACIONES Y RESTRICCIONES](#9-validaciones-y-restricciones)
10. [FUNCIONALIDADES AVANZADAS](#10-funcionalidades-avanzadas)

---

## 1. ESTRUCTURA GENERAL DEL SISTEMA

### A) Módulos Principales

#### **1. Módulo de Empleados (RR.HH.)**
- **Nombre del módulo:** `empleados`
- **Descripción funcional:** Gestión integral de empleados, perfiles, departamentos y vacaciones
- **Rutas de acceso:**
  - `/empleados/` - Lista de empleados
  - `/usuarios/` - Gestión de usuarios
  - `/usuarios/crear/` - Crear nuevo usuario
  - `/usuarios/<id>/editar/` - Editar perfil de usuario
  - `/perfil/` - Ver perfil de usuario
- **Permisos requeridos:**
  - **Empleados:** Solo lectura de su propio perfil
  - **Jefes de Área:** Lectura de empleados asignados directamente como supervisor
  - **RH:** Lectura de todos los empleados
  - **Sistemas/Admin:** Lectura y edición completa de todos los empleados

#### **2. Módulo de Vacaciones**
- **Nombre del módulo:** `vacaciones` (dentro de `empleados`)
- **Descripción funcional:** Sistema completo de solicitud, aprobación y gestión de vacaciones
- **Rutas de acceso:**
  - `/vacaciones/` - Mis vacaciones (empleado)
  - `/vacaciones/solicitar/` - Solicitar nuevas vacaciones
  - `/vacaciones/solicitudes-jefe/` - Solicitudes pendientes para jefe
  - `/vacaciones/solicitudes-rh/` - Solicitudes pendientes para RH
  - `/vacaciones/<id>/aprobar-jefe/` - Aprobar/rechazar como jefe
  - `/vacaciones/<id>/aprobar-admin/` - Aprobar/rechazar como admin
  - `/vacaciones/<id>/aprobar-rh/` - Aprobar/rechazar como RH
  - `/vacaciones/<id>/pdf/` - Generar PDF de formulario de vacaciones
  - `/vacaciones/reporte-mes/` - Reporte mensual de vacaciones
- **Permisos requeridos:**
  - **Empleados/Jefes:** Pueden solicitar vacaciones
  - **Jefes de Área:** Pueden aprobar solicitudes de sus empleados directos
  - **Admin:** Puede aprobar solicitudes de jefes de área
  - **RH:** Aprobación final de todas las solicitudes

#### **3. Módulo de Tickets (Soporte TI)**
- **Nombre del módulo:** `tickets` (dentro de `empleados`)
- **Descripción funcional:** Sistema de tickets para soporte técnico
- **Rutas de acceso:**
  - `/tickets/` - Mis tickets (empleado)
  - `/tickets/crear/` - Crear nuevo ticket
  - `/tickets/<id>/` - Detalle de ticket
  - `/sistemas/tickets/` - Gestión de tickets (Sistemas)
  - `/sistemas/tickets/<id>/asignar/` - Asignar ticket
  - `/sistemas/tickets/<id>/resolver/` - Resolver ticket
- **Permisos requeridos:**
  - **Todos los usuarios:** Pueden crear tickets
  - **Sistemas/Admin:** Pueden gestionar, asignar y resolver tickets

#### **4. Módulo de Inventario de Equipos**
- **Nombre del módulo:** `equipos` (dentro de `empleados`)
- **Descripción funcional:** Gestión de inventario de equipos tecnológicos y asignaciones
- **Rutas de acceso:**
  - `/equipos/` - Mis equipos (empleado)
  - `/sistemas/equipos/` - Inventario completo (Sistemas/Admin/RH)
  - `/sistemas/equipos/agregar/` - Agregar nuevo equipo
  - `/sistemas/equipos/<id>/gestionar/` - Gestionar asignación
  - `/sistemas/equipos/<id>/quitar-asignacion/` - Quitar asignación
  - `/sistemas/equipos/<id>/marcar-disponible/` - Marcar como disponible
  - `/jefe/equipos/` - Vista de inventario para jefes (solo lectura)
- **Permisos requeridos:**
  - **Empleados:** Solo lectura de sus equipos asignados
  - **Jefes:** Solo lectura de equipos de su departamento
  - **Sistemas/Admin/RH:** Gestión completa del inventario

#### **5. Módulo de Departamentos**
- **Nombre del módulo:** `departamentos` (dentro de `empleados`)
- **Descripción funcional:** Gestión de departamentos organizacionales
- **Rutas de acceso:**
  - `/departamentos/` - Lista de departamentos
  - `/departamentos/crear/` - Crear departamento
  - `/departamentos/<id>/` - Ver departamento
  - `/departamentos/<id>/editar/` - Editar departamento
  - `/departamentos/<id>/toggle/` - Activar/desactivar departamento
- **Permisos requeridos:**
  - **RH/Admin:** Gestión completa de departamentos

### B) Flujos de Navegación

#### **Flujo de Login a Dashboard:**
1. Usuario accede a `/` (página de login)
2. Ingresa credenciales (username y password)
3. Sistema autentica y redirige según tipo de perfil:
   - **Admin** → `/administrador/`
   - **RH** → `/rh/`
   - **Jefe de Área** → `/jefe/`
   - **Sistemas** → `/sistemas/`
   - **Empleado** → `/empleado/`

#### **Flujo de Solicitud de Vacaciones (Empleado Normal):**
1. Empleado accede a `/vacaciones/solicitar/`
2. Completa formulario (fechas, tipo, motivo)
3. Sistema valida disponibilidad de días
4. Solicitud se crea con estado `PENDIENTE_JEFE`
5. Jefe de área recibe notificación en su dashboard
6. Jefe aprueba/rechaza → Estado cambia a `APROBADO_JEFE` o `RECHAZADO_JEFE`
7. Si aprobado por jefe → Estado cambia a `PENDIENTE_RH`
8. RH recibe solicitud en su dashboard
9. RH aprueba/rechaza → Estado final `APROBADO_RH` o `RECHAZADO_RH`
10. Si aprobado por RH → Se descuentan días automáticamente

#### **Flujo de Solicitud de Vacaciones (Jefe de Área):**
1. Jefe accede a `/vacaciones/solicitar/`
2. Completa formulario
3. Solicitud se crea con estado `PENDIENTE_ADMIN` (salta aprobación de jefe)
4. Admin aprueba/rechaza → Estado cambia a `PENDIENTE_RH`
5. RH aprueba/rechaza → Estado final

#### **Flujo de Creación de Ticket:**
1. Usuario accede a `/tickets/crear/`
2. Completa formulario (tipo, área, dispositivo, prioridad, descripción)
3. Ticket se crea con estado `PENDIENTE` y código único (TKT-YYYYMMDD-XXX)
4. Ticket aparece en dashboard de Sistemas
5. Técnico de Sistemas asigna ticket a sí mismo → Estado cambia a `EN_PROCESO`
6. Técnico resuelve ticket → Estado cambia a `RESUELTO`
7. Usuario puede ver el estado y solución en `/tickets/<id>/`

### C) Roles y Permisos

#### **Lista Completa de Roles:**

1. **EMPLEADO**
   - Ver su propio perfil
   - Solicitar vacaciones
   - Crear tickets
   - Ver sus equipos asignados
   - Ver sus tickets

2. **JEFE_AREA (Jefe de Área)**
   - Todo lo de EMPLEADO
   - Ver empleados asignados directamente como supervisor
   - Aprobar/rechazar solicitudes de vacaciones de sus empleados
   - Ver equipos de su departamento (solo lectura)
   - Solicitar vacaciones (requiere aprobación de Admin)

3. **RH (Recursos Humanos)**
   - Ver todos los empleados (solo lectura)
   - Aprobar/rechazar solicitudes de vacaciones (aprobación final)
   - Generar reportes de vacaciones (PDF/Excel)
   - Gestionar departamentos
   - Ver inventario de equipos (solo lectura)

4. **SISTEMAS (Sistemas/IT)**
   - Crear y editar usuarios/empleados
   - Gestionar tickets (asignar, resolver)
   - Gestionar inventario de equipos (agregar, asignar, quitar)
   - Ver todos los empleados
   - Crear tickets

5. **ADMIN (Administrador)**
   - Acceso completo a todas las funcionalidades
   - Aprobar solicitudes de vacaciones de jefes de área
   - Gestionar usuarios, empleados, departamentos
   - Ver todos los dashboards y reportes
   - Acceso al panel de administración de Django

#### **Matrix de Permisos por Funcionalidad:**

| Funcionalidad | EMPLEADO | JEFE_AREA | RH | SISTEMAS | ADMIN |
|--------------|----------|-----------|----|----------|-------|
| Ver propio perfil | ✅ | ✅ | ✅ | ✅ | ✅ |
| Ver otros empleados | ❌ | ✅ (solo asignados) | ✅ (todos) | ✅ (todos) | ✅ (todos) |
| Editar empleados | ❌ | ❌ | ❌ | ✅ | ✅ |
| Crear empleados | ❌ | ❌ | ❌ | ✅ | ✅ |
| Solicitar vacaciones | ✅ | ✅ | ❌ | ❌ | ❌ |
| Aprobar vacaciones (jefe) | ❌ | ✅ (solo asignados) | ❌ | ❌ | ❌ |
| Aprobar vacaciones (admin) | ❌ | ❌ | ❌ | ❌ | ✅ (jefes) |
| Aprobar vacaciones (RH) | ❌ | ❌ | ✅ | ❌ | ✅ |
| Crear tickets | ✅ | ✅ | ✅ | ✅ | ✅ |
| Gestionar tickets | ❌ | ❌ | ❌ | ✅ | ✅ |
| Ver equipos propios | ✅ | ✅ | ✅ | ✅ | ✅ |
| Gestionar inventario | ❌ | ❌ | ❌ | ✅ | ✅ |
| Gestionar departamentos | ❌ | ❌ | ✅ | ❌ | ✅ |
| Generar reportes | ❌ | ❌ | ✅ | ❌ | ✅ |

---

## 2. MÓDULO DE RECURSOS HUMANOS (RR.HH.)

### A) Gestión de Vacaciones

#### **Campos del Formulario de Solicitud:**

**Campos Obligatorios:**
- **Fecha de Inicio:** Campo de fecha (formato DD/MM/YYYY)
  - Tipo: DateField
  - Validación: No puede ser más de 7 días en el pasado
  - Widget: Datepicker con formato DD/MM/YYYY

- **Fecha de Fin:** Campo de fecha (formato DD/MM/YYYY)
  - Tipo: DateField
  - Validación: Debe ser posterior a fecha de inicio
  - Widget: Datepicker con formato DD/MM/YYYY

- **Tipo de Vacación:**
  - Opciones:
    - `NORMAL`: Vacación Normal (requiere antigüedad >= 1 año)
    - `EXTRAORDINARIA`: Vacación Extraordinaria (para empleados con < 1 año)
  - Tipo: CharField con choices
  - Validación: Empleados con < 1 año solo pueden solicitar extraordinarias

- **Motivo:** Campo de texto largo
  - Tipo: TextField
  - Widget: Textarea (4 filas)
  - Placeholder: "Describe el motivo de tu solicitud de vacaciones..."

**Campos Calculados Automáticamente:**
- **Días Solicitados:** Se calcula automáticamente excluyendo domingos
  - Método: `SolicitudVacaciones.calcular_dias_laborables()`
  - Excluye domingos del conteo
  - Se actualiza automáticamente al guardar

#### **Validaciones del Sistema:**

1. **Validación de Antigüedad:**
   - Empleados con < 1 año: Solo pueden solicitar vacaciones extraordinarias
   - Empleados con >= 1 año: Pueden solicitar vacaciones normales o extraordinarias

2. **Validación de Días Disponibles:**
   - No se pueden solicitar más días de los disponibles
   - Fórmula: `dias_disponibles = (dias_anuales + dias_acumulados) - dias_usados`
   - Mensaje de error si excede: "No tienes suficientes días de vacaciones disponibles"

3. **Validación de Fechas:**
   - Fecha fin debe ser posterior a fecha inicio
   - No se pueden solicitar vacaciones para fechas anteriores a hace 7 días
   - Excepción: Se permite retroceder hasta 7 días para cambiar faltas por días de vacaciones

4. **Cálculo de Días Laborables:**
   - Excluye domingos del conteo
   - Ejemplo: Si solicita del lunes 1 al domingo 7, cuenta 6 días (excluye el domingo)

#### **Estados Posibles de la Solicitud:**

1. **PENDIENTE_JEFE:** Pendiente de aprobación por jefe de área
2. **PENDIENTE_ADMIN:** Pendiente de aprobación por administrador (solo para jefes de área)
3. **PENDIENTE_RH:** Pendiente de aprobación final por Recursos Humanos
4. **APROBADO_JEFE:** Aprobado por jefe de área, esperando aprobación de RH
5. **APROBADO_ADMIN:** Aprobado por administrador, esperando aprobación de RH
6. **APROBADO_RH:** Aprobado completamente, días descontados
7. **RECHAZADO_JEFE:** Rechazado por jefe de área
8. **RECHAZADO_ADMIN:** Rechazado por administrador
9. **RECHAZADO_RH:** Rechazado por Recursos Humanos
10. **CANCELADO:** Cancelado por el empleado

#### **Flujo de Aprobación:**

**Para Empleados Normales:**
1. Empleado solicita → Estado: `PENDIENTE_JEFE`
2. Jefe aprueba → Estado: `PENDIENTE_RH`
3. RH aprueba → Estado: `APROBADO_RH` (días descontados automáticamente)

**Para Jefes de Área:**
1. Jefe solicita → Estado: `PENDIENTE_ADMIN`
2. Admin aprueba → Estado: `PENDIENTE_RH`
3. RH aprueba → Estado: `APROBADO_RH` (días descontados automáticamente)

**Puntos de Decisión:**
- Jefe puede aprobar o rechazar (con comentario opcional)
- Admin puede aprobar o rechazar (con comentario opcional)
- RH puede aprobar o rechazar (con comentario opcional)
- En cualquier punto de rechazo, la solicitud termina

#### **Cálculo Automático de Días:**

**Tabla de Días por Antigüedad:**
- < 1 año: 12 días (proporcional por mes trabajado)
- 1 año: 12 días
- 2 años: 14 días
- 3 años: 16 días
- 4 años: 18 días
- 5 años: 20 días
- 6-10 años: 22 días
- 11-15 años: 24 días
- 16-20 años: 26 días
- 21-25 años: 28 días
- 26-30 años: 30 días
- 31+ años: 32 días

**Cálculo de Días Disponibles:**
```python
dias_disponibles = (dias_vacaciones_anuales + dias_vacaciones_acumulados) - dias_vacaciones_usados
```

**Días Acumulados:**
- Los días no usados del año anterior se acumulan automáticamente
- No hay límite de acumulación
- Se procesan mediante comando: `python manage.py acumular_mensual`

**Días Extraordinarios:**
- Solo para empleados con < 1 año de antigüedad
- Máximo 5 días extraordinarios disponibles
- Se calculan: `5 - dias_vacaciones_extraordinarios_usados`

### B) Gestión de Usuarios/Empleados

#### **Campos para Crear un Nuevo Empleado:**

**Información de Usuario (Obligatoria):**
- **Username:** Nombre de usuario único (máx. 150 caracteres)
- **Nombre (first_name):** Nombre del empleado (máx. 30 caracteres)
- **Apellidos (last_name):** Apellidos del empleado (máx. 30 caracteres)
- **Email:** Correo electrónico único (validación de formato)
- **Password1:** Contraseña (mínimo 8 caracteres)
- **Password2:** Confirmación de contraseña

**Información de Perfil (Obligatoria):**
- **Tipo de Perfil:** 
  - Opciones: EMPLEADO, JEFE_AREA, RH, SISTEMAS, ADMIN
  - Default: EMPLEADO
- **Número de Empleado:** Código único (máx. 20 caracteres)
  - Validación: Debe ser único en el sistema
  - Formato sugerido: EMP0001, EMP0002, etc.
- **Puesto:** Nombre del puesto (máx. 100 caracteres)
- **Fecha de Contratación:** Fecha de inicio laboral
  - Widget: Datepicker
  - Default: Fecha actual
- **Departamento:** Selección de departamento existente (opcional)

**Información de Perfil (Opcional):**
- **Supervisor:** Jefe de área o administrador asignado
- **Teléfono:** Número de teléfono (máx. 15 caracteres)
- **Fecha de Nacimiento:** Fecha de nacimiento
- **Salario:** Salario del empleado (DecimalField, 10 dígitos, 2 decimales)
- **Dirección:** Dirección completa (máx. 255 caracteres)

**Información de Vacaciones (Automática):**
- **Días de Vacaciones Anuales:** Se calcula automáticamente según antigüedad
- **Días de Vacaciones Usados:** Inicia en 0
- **Días de Vacaciones Acumulados:** Inicia en 0
- **Último Reset de Vacaciones:** Se establece automáticamente

#### **Información que se Muestra en el Perfil:**

**Sección de Información Personal:**
- Nombre completo
- Email
- Teléfono
- Fecha de nacimiento
- Dirección

**Sección de Información Laboral:**
- Número de empleado
- Puesto
- Departamento
- Supervisor
- Fecha de contratación
- Antigüedad (calculada automáticamente)
- Estado (Activo/Inactivo)

**Sección de Vacaciones:**
- Días anuales (según antigüedad)
- Días usados
- Días acumulados del año anterior
- Días disponibles
- Días extraordinarios disponibles (si aplica)

**Sección de Equipos:**
- Lista de equipos asignados actualmente
- Historial de equipos asignados (últimos 10)

**Sección de Tickets:**
- Tickets creados por el empleado
- Estado de cada ticket

#### **Búsqueda y Filtros Disponibles:**

**En Lista de Empleados:**
- **Filtro por Tipo de Perfil:** EMPLEADO, JEFE_AREA, RH, SISTEMAS, ADMIN
- **Filtro por Departamento:** Lista de departamentos activos
- **Búsqueda por Texto:** Busca en:
  - Username
  - Nombre (first_name)
  - Apellidos (last_name)
  - Número de empleado

**Ordenamiento:**
- Por defecto: Ordenado por apellido y nombre
- Se puede ordenar por cualquier columna visible

#### **Exportación de Datos:**

**Reportes de Vacaciones:**
- **Formato PDF:** Genera reporte en formato APA 7
  - Ruta: `/vacaciones/reporte-mes/pdf/`
  - Parámetros: `?mes=X&año=YYYY`
  - Incluye: Resumen estadístico y tabla detallada
- **Formato Excel (.xlsx):** Genera archivo Excel profesional
  - Ruta: `/vacaciones/reporte-mes/excel/`
  - Parámetros: `?mes=X&año=YYYY`
  - Incluye: Resumen, estadísticas y tabla completa con todos los campos
- **Formato CSV (fallback):** Si no está disponible openpyxl
  - Mismo contenido que Excel pero en formato CSV

**Campos Exportados en Reportes:**
- Empleado (nombre completo)
- Número de Empleado
- Departamento
- Puesto
- Fecha Inicio
- Fecha Fin
- Días Solicitados
- Tipo de Vacación
- Estado
- Fecha Solicitud
- Aprobado por Jefe
- Fecha Aprobación Jefe
- Aprobado por RH
- Fecha Aprobación RH
- Motivo

### C) Permisos y Salidas

#### **Diferencia entre Tipos de Solicitud:**

**Vacación Normal:**
- Requiere antigüedad >= 1 año
- Se descuentan de días anuales o acumulados
- Flujo completo de aprobación (Jefe → RH)

**Vacación Extraordinaria:**
- Disponible para empleados con < 1 año
- Máximo 5 días extraordinarios
- Se descuentan de días extraordinarios disponibles
- Flujo completo de aprobación (Jefe → RH)

**Nota:** No existe un módulo separado de "Permisos" o "Pase de Salida" en el sistema actual. Todas las solicitudes se manejan como vacaciones.

---

## 3. MÓDULO DE SOPORTE TI (TICKETS)

### A) Creación de Tickets

#### **Campos del Formulario:**

**Campos Obligatorios:**
- **Tipo de Problema:**
  - Opciones:
    - `HARDWARE`: Problemas con hardware
    - `SOFTWARE`: Problemas con software
    - `RED`: Problemas de red/conectividad
    - `ACCESO`: Problemas de acceso/permisos
    - `OTRO`: Otro tipo de problema
  - Tipo: CharField con choices
  - Widget: Select dropdown

- **Prioridad:**
  - Opciones:
    - `BAJA`: Baja prioridad
    - `MEDIA`: Prioridad media (default)
    - `ALTA`: Alta prioridad
    - `URGENTE`: Urgente
  - Tipo: CharField con choices
  - Default: MEDIA

- **Descripción del Problema:**
  - Tipo: TextField
  - Widget: Textarea (5 filas)
  - Placeholder: "Describe detalladamente el problema..."
  - Obligatorio

**Campos Opcionales:**
- **Área:**
  - Tipo: CharField (máx. 100 caracteres)
  - Placeholder: "Ej: Administración, Ventas, etc."
  - Opcional

- **Dispositivo Afectado:**
  - Tipo: CharField (máx. 100 caracteres)
  - Placeholder: "Ej: Laptop HP, iPhone, etc."
  - Opcional

#### **Generación Automática de Código:**

- **Formato:** `TKT-YYYYMMDD-XXX`
  - Ejemplo: `TKT-20241215-001`
- **Generación:** Automática al crear el ticket
- **Unicidad:** Garantizada por el sistema
- **Secuencia:** Incremental por día (001, 002, 003...)

#### **Asignación de Tickets:**

- **Inicial:** Sin asignar (asignado_a = null)
- **Asignación Manual:** Técnico de Sistemas puede asignarse el ticket
- **Asignación Automática:** No existe asignación automática en el código actual
- **Quién puede asignar:** Solo usuarios con perfil SISTEMAS o ADMIN

### B) Estados del Ticket

#### **Lista Completa de Estados:**

1. **PENDIENTE:** Ticket creado, esperando asignación
2. **EN_PROCESO:** Ticket asignado a técnico, en proceso de resolución
3. **RESUELTO:** Ticket resuelto, solución aplicada
4. **CANCELADO:** Ticket cancelado (no se resolverá)

#### **Transiciones de Estado:**

**Flujo Normal:**
1. `PENDIENTE` → (Asignar) → `EN_PROCESO`
2. `EN_PROCESO` → (Resolver) → `RESUELTO`

**Flujo Alternativo:**
1. `PENDIENTE` → (Cancelar) → `CANCELADO`
2. `EN_PROCESO` → (Cancelar) → `CANCELADO`

#### **Quién Puede Cambiar el Estado:**

- **PENDIENTE → EN_PROCESO:** Solo SISTEMAS/ADMIN (al asignarse)
- **EN_PROCESO → RESUELTO:** Solo SISTEMAS/ADMIN (al resolver)
- **Cualquier estado → CANCELADO:** Solo SISTEMAS/ADMIN

#### **Notificaciones por Cambio de Estado:**

**Nota:** El código actual no muestra implementación de notificaciones por email. Las notificaciones se muestran en el sistema mediante mensajes de Django (messages framework).

### C) Gestión de Tickets (Equipo TI)

#### **Vistas Disponibles:**

**Dashboard de Sistemas:**
- Ruta: `/sistemas/`
- Muestra:
  - Tickets pendientes (contador)
  - Tickets en proceso (contador)
  - Tickets resueltos hoy (contador)
  - Tickets recientes (últimos 10)

**Gestión de Tickets:**
- Ruta: `/sistemas/tickets/`
- Muestra: Lista completa de todos los tickets
- Filtros:
  - Estado: TODOS, PENDIENTE, EN_PROCESO, RESUELTO, CANCELADO
- Ordenamiento: Por fecha de creación (más recientes primero)

#### **Campos Editables por Técnico:**

**Al Asignar Ticket:**
- **Asignado A:** Se asigna automáticamente al técnico que hace clic en "Asignar"
- **Estado:** Cambia automáticamente a `EN_PROCESO`
- **Fecha de Asignación:** Se establece automáticamente

**Al Resolver Ticket:**
- **Estado:** Puede cambiar a `RESUELTO` o `CANCELADO`
- **Solución:** Campo de texto largo para describir la solución aplicada
  - Tipo: TextField
  - Widget: Textarea (5 filas)
  - Placeholder: "Describe la solución aplicada..."
- **Fecha de Resolución:** Se establece automáticamente cuando estado = `RESUELTO`

#### **Opciones de Resolución:**

**Resolver:**
- Estado: `RESUELTO`
- Requiere: Campo "Solución" completado
- Efecto: Fecha de resolución se establece automáticamente

**Cancelar:**
- Estado: `CANCELADO`
- No requiere: Campo "Solución"
- Efecto: Ticket se marca como cancelado

#### **Comentarios/Historial:**

**Nota:** El código actual no muestra un sistema de comentarios o historial de cambios. Solo se registra:
- Fecha de creación
- Fecha de asignación
- Fecha de resolución
- Fecha de actualización (automática)

#### **Tiempo de Respuesta y Resolución:**

**Campos Calculados:**
- **Tiempo de Respuesta:** Diferencia entre fecha_creacion y fecha_asignacion
  - Propiedad: `ticket.tiempo_respuesta`
  - Retorna: timedelta object o None
- **Tiempo de Resolución:** Diferencia entre fecha_creacion y fecha_resolucion
  - Propiedad: `ticket.tiempo_resolucion`
  - Retorna: timedelta object o None

**Nota:** Estos tiempos se calculan pero no se muestran en las vistas actuales del código.

---

## 4. MÓDULO DE INVENTARIO Y EQUIPOS

### A) Catálogo de Equipos

#### **Tipos de Equipos (Categorías):**

**Modelo:** `CategoriaEquipo`
- Campo: `nombre` (CharField, máx. 50 caracteres, único)
- Campo: `descripcion` (TextField, opcional)
- Campo: `activo` (BooleanField, default=True)

**Categorías Predefinidas:** No hay categorías predefinidas en el código. Se deben crear mediante el admin o formulario de creación.

**Ejemplos de Categorías:**
- Laptop
- Desktop
- Monitor
- Celular
- Tablet
- Periféricos (Mouse, Teclado, etc.)
- Impresora
- Router/Switch

#### **Campos de Cada Equipo:**

**Información Básica (Obligatoria):**
- **Categoría:** Relación con CategoriaEquipo (ForeignKey)
- **Marca:** Nombre de la marca (CharField, máx. 50 caracteres)
  - Ejemplo: HP, Apple, Dell, Lenovo
- **Modelo:** Modelo del equipo (CharField, máx. 100 caracteres)
  - Ejemplo: EliteBook 840, MacBook Pro, Latitude 5520
- **Número de Serie:** Número de serie único (CharField, máx. 100 caracteres, único)
  - Validación: Debe ser único en el sistema
- **Código de Inventario:** Código interno único (CharField, máx. 50 caracteres, único)
  - Validación: Debe ser único en el sistema
  - Ejemplo: INV-001, IT-2024-001

**Información Adicional (Obligatoria):**
- **Estado:** Estado actual del equipo
  - Opciones:
    - `DISPONIBLE`: Disponible para asignar
    - `ASIGNADO`: Asignado a un empleado
    - `EN_REPARACION`: En reparación/mantenimiento
    - `DADO_DE_BAJA`: Dado de baja/descartado
  - Default: DISPONIBLE
- **Fecha de Adquisición:** Fecha en que se adquirió el equipo
  - Tipo: DateField
  - Widget: Datepicker

**Información Adicional (Opcional):**
- **Observaciones:** Notas adicionales sobre el equipo
  - Tipo: TextField
  - Widget: Textarea (3 filas)

**Campos Automáticos:**
- **Fecha de Creación:** Timestamp automático
- **Fecha de Actualización:** Timestamp automático (se actualiza en cada modificación)

#### **Estados Posibles:**

1. **DISPONIBLE:**
   - Equipo disponible para asignar
   - No tiene asignación activa
   - Puede ser asignado a cualquier empleado

2. **ASIGNADO:**
   - Equipo asignado a un empleado
   - Tiene una asignación activa (sin fecha_devolucion)
   - No puede ser asignado a otro empleado sin quitar la asignación actual

3. **EN_REPARACION:**
   - Equipo en reparación o mantenimiento
   - Puede ser asignado después de reparación
   - Se puede cambiar a DISPONIBLE o ASIGNADO después de reparación

4. **DADO_DE_BAJA:**
   - Equipo dado de baja o descartado
   - No puede ser asignado
   - Estado final (no se puede cambiar fácilmente)

### B) Asignación de Equipos

#### **Proceso de Asignar Equipo a Empleado:**

**Opción 1: Al Crear el Equipo**
- En el formulario de creación existe campo opcional "Asignar a Empleado"
- Si se selecciona un empleado, se crea la asignación automáticamente
- El estado del equipo cambia automáticamente a `ASIGNADO` (si no está en reparación)

**Opción 2: Asignar Equipo Existente**
- Ruta: `/sistemas/equipos/<id>/gestionar/`
- Formulario: `AsignacionEquipoForm`
- Campos:
  - **Equipo:** Pre-seleccionado (no editable)
  - **Empleado:** Dropdown de empleados activos
  - **Condición al Entregar:** Texto opcional (máx. 200 caracteres)
    - Ejemplo: "Nuevo", "Usado - Buen estado", "Con daños menores"
  - **Observaciones:** Texto opcional
  - **Cambiar Estado del Equipo:** Opcional (si está en reparación, es obligatorio)

#### **Validaciones:**

1. **Equipo Disponible:**
   - Solo se pueden asignar equipos con estado `DISPONIBLE` o `EN_REPARACION`
   - Si está `ASIGNADO`, primero se debe quitar la asignación anterior

2. **Empleado Activo:**
   - Solo se pueden asignar equipos a empleados activos
   - El dropdown solo muestra empleados con `activo=True`

3. **Asignación Anterior:**
   - Si el equipo ya tiene una asignación activa, se cierra automáticamente
   - Se establece `fecha_devolucion` en la asignación anterior
   - Se crea una nueva asignación

#### **Confirmaciones Requeridas:**

- Al asignar: Se muestra mensaje de éxito con código de inventario y nombre del empleado
- Al quitar asignación: Se solicita confirmación del nuevo estado del equipo

### C) Historial y Reportes

#### **Datos que se Guardan del Historial:**

**Modelo:** `AsignacionEquipo`

**Campos:**
- **Equipo:** Relación con Equipo (ForeignKey)
- **Empleado:** Relación con Perfil (ForeignKey)
- **Fecha de Asignación:** Fecha en que se asignó
- **Fecha de Devolución:** Fecha en que se devolvió (null si está activa)
- **Condición al Entregar:** Estado del equipo al momento de asignación
- **Condición al Devolver:** Estado del equipo al momento de devolución
- **Observaciones:** Notas adicionales
- **Asignado Por:** Usuario que realizó la asignación (ForeignKey a Perfil)
- **Fecha de Creación:** Timestamp automático
- **Fecha de Actualización:** Timestamp automático

**Propiedades Calculadas:**
- **esta_activa:** Retorna True si fecha_devolucion es None

#### **Reportes Disponibles:**

**Nota:** El código actual no muestra reportes específicos de equipos. La información se puede ver en:
- Lista de equipos con filtros por estado
- Historial de asignaciones por empleado (en perfil)
- Historial de asignaciones por equipo (en detalle del equipo)

#### **Filtros y Búsquedas:**

**En Inventario de Equipos:**
- **Filtro por Estado:** DISPONIBLE, ASIGNADO, EN_REPARACION, DADO_DE_BAJA
- **Ordenamiento:** Por fecha de adquisición (más recientes primero)

**En Vista de Jefe:**
- Solo muestra equipos asignados a empleados de su departamento
- Filtro por estado disponible

#### **Exportación de Datos:**

**Nota:** El código actual no muestra funcionalidad de exportación de datos de equipos. Solo existe exportación para reportes de vacaciones.

---

## 5. DASHBOARD Y MÉTRICAS

### A) KPIs Mostrados

#### **Dashboard de Administrador (`/administrador/`):**

**Estadísticas de Empleados:**
- **Total de Empleados:** Contador de empleados activos
  - Fuente: `Perfil.objects.filter(activo=True).count()`
- **Total de Departamentos:** Contador de departamentos activos
  - Fuente: `Departamento.objects.filter(activo=True).count()`
- **Empleados por Tipo:**
  - Empleados normales
  - Jefes de área
  - RH
  - Sistemas

**Estadísticas de Vacaciones:**
- **Solicitudes Pendientes (Jefe):** Contador de estado `PENDIENTE_JEFE`
- **Solicitudes Pendientes (Admin):** Contador de estado `PENDIENTE_ADMIN`
- **Solicitudes Pendientes (RH):** Contador de estado `PENDIENTE_RH`
- **Solicitudes Aprobadas (Este Mes):** Contador de `APROBADO_RH` en el mes actual
- **Solicitudes Rechazadas (Este Mes):** Contador de rechazadas en el mes actual

**Estadísticas de Tickets:**
- **Tickets Pendientes:** Contador de estado `PENDIENTE`
- **Tickets en Proceso:** Contador de estado `EN_PROCESO`
- **Tickets Resueltos (Hoy):** Contador de `RESUELTO` con fecha_resolucion = hoy
- **Tickets Cancelados (Hoy):** Contador de `CANCELADO` actualizados hoy

**Estadísticas de Equipos:**
- **Equipos Disponibles:** Contador de estado `DISPONIBLE`
- **Equipos Asignados:** Contador de estado `ASIGNADO`
- **Equipos en Reparación:** Contador de estado `EN_REPARACION`
- **Equipos Dados de Baja:** Contador de estado `DADO_DE_BAJA`
- **Total de Equipos:** Contador total

**Listas Recientes:**
- **Solicitudes Recientes:** Últimas 8 solicitudes pendientes
- **Tickets Recientes:** Últimos 8 tickets (todos)
- **Asignaciones Recientes:** Últimas 5 asignaciones activas

#### **Dashboard de RH (`/rh/`):**

**Estadísticas:**
- **Solicitudes Pendientes:** Contador de estado `PENDIENTE_RH`
- **Aprobadas Este Mes:** Contador de `APROBADO_RH` en el mes actual
- **Rechazadas Este Mes:** Contador de `RECHAZADO_RH` en el mes actual

**Lista:**
- **Solicitudes Pendientes:** Lista completa de solicitudes con estado `PENDIENTE_RH`

#### **Dashboard de Jefe de Área (`/jefe/`):**

**Estadísticas:**
- **Empleados del Departamento:** Contador de empleados asignados directamente como supervisor
- **Solicitudes Pendientes:** Contador de solicitudes de empleados asignados con estado `PENDIENTE_JEFE`
- **Aprobadas Este Mes:** Contador de `APROBADO_JEFE` en el mes actual

**Lista:**
- **Solicitudes Pendientes:** Lista de solicitudes de empleados asignados con estado `PENDIENTE_JEFE`

#### **Dashboard de Empleado (`/empleado/`):**

**Estadísticas Personales:**
- **Días Disponibles:** `perfil.dias_vacaciones_disponibles`
- **Días Usados:** `perfil.dias_vacaciones_usados`
- **Solicitudes Pendientes:** Contador de solicitudes propias con estado pendiente
- **Solicitudes Aprobadas:** Contador de solicitudes propias con estado `APROBADO_RH`
- **Equipos Asignados:** Contador de equipos asignados activamente
- **Tickets Pendientes:** Contador de tickets propios con estado `PENDIENTE` o `EN_PROCESO`

**Listas:**
- **Solicitudes:** Todas las solicitudes del empleado
- **Equipos Asignados:** Últimos 5 equipos asignados activamente
- **Tickets Recientes:** Últimos 5 tickets del empleado

#### **Dashboard de Sistemas (`/sistemas/`):**

**Estadísticas de Tickets:**
- **Tickets Pendientes:** Contador de estado `PENDIENTE`
- **Tickets en Proceso:** Contador de estado `EN_PROCESO`
- **Tickets Resueltos (Hoy):** Contador de `RESUELTO` con fecha_resolucion = hoy

**Estadísticas de Equipos:**
- **Equipos Disponibles:** Contador de estado `DISPONIBLE`
- **Equipos Asignados:** Contador de estado `ASIGNADO`
- **Equipos en Reparación:** Contador de estado `EN_REPARACION`

**Lista:**
- **Tickets Recientes:** Últimos 10 tickets (todos)

### B) Botones de Acceso Rápido

#### **Dashboard de Administrador:**
- **Gestión de Usuarios:** Redirige a `/usuarios/`
- **Gestión de Departamentos:** Redirige a `/departamentos/`
- **Reportes de Vacaciones:** Redirige a `/vacaciones/reporte-mes/`
- **Gestión de Tickets:** Redirige a `/sistemas/tickets/`
- **Inventario de Equipos:** Redirige a `/sistemas/equipos/`

#### **Dashboard de RH:**
- **Solicitudes Pendientes:** Redirige a `/vacaciones/solicitudes-rh/`
- **Reportes de Vacaciones:** Redirige a `/vacaciones/reporte-mes/`
- **Gestión de Departamentos:** Redirige a `/departamentos/`

#### **Dashboard de Jefe:**
- **Solicitudes Pendientes:** Redirige a `/vacaciones/solicitudes-jefe/`
- **Inventario de Equipos:** Redirige a `/jefe/equipos/` (solo lectura)

#### **Dashboard de Empleado:**
- **Solicitar Vacaciones:** Redirige a `/vacaciones/solicitar/`
- **Mis Vacaciones:** Redirige a `/vacaciones/`
- **Crear Ticket:** Redirige a `/tickets/crear/`
- **Mis Tickets:** Redirige a `/tickets/`
- **Mis Equipos:** Redirige a `/equipos/`

#### **Dashboard de Sistemas:**
- **Gestionar Tickets:** Redirige a `/sistemas/tickets/`
- **Inventario de Equipos:** Redirige a `/sistemas/equipos/`
- **Agregar Equipo:** Redirige a `/sistemas/equipos/agregar/`
- **Crear Usuario:** Redirige a `/usuarios/crear/`

### C) Tablas de Datos

#### **Tabla de Empleados:**
**Columnas Mostradas:**
- Foto/Iniciales
- Nombre completo
- Número de empleado
- Departamento
- Puesto
- Tipo de perfil
- Estado (Activo/Inactivo)
- Acciones (Ver, Editar - según permisos)

**Datos:**
- Ordenamiento: Por apellido y nombre
- Filtros: Por tipo de perfil, departamento, búsqueda de texto

#### **Tabla de Solicitudes de Vacaciones:**
**Columnas Mostradas:**
- Empleado
- Departamento
- Período (fecha inicio - fecha fin)
- Días solicitados
- Tipo
- Estado
- Fecha de solicitud
- Acciones (Aprobar/Rechazar - según permisos)

**Datos:**
- Ordenamiento: Por fecha de solicitud (más recientes primero)
- Filtros: Por estado, búsqueda de empleado

#### **Tabla de Tickets:**
**Columnas Mostradas:**
- Código
- Solicitante
- Tipo
- Prioridad
- Estado
- Asignado a
- Fecha de creación
- Acciones (Asignar, Resolver - según permisos)

**Datos:**
- Ordenamiento: Por fecha de creación (más recientes primero)
- Filtros: Por estado

#### **Tabla de Equipos:**
**Columnas Mostradas:**
- Categoría
- Marca
- Modelo
- Código de inventario
- Estado
- Empleado asignado (si aplica)
- Fecha de adquisición
- Acciones (Gestionar, Quitar asignación - según permisos)

**Datos:**
- Ordenamiento: Por fecha de adquisición (más recientes primero)
- Filtros: Por estado

---

## 6. SEGURIDAD Y AUTENTICACIÓN

### A) Login

#### **Método de Autenticación:**
- **Tipo:** Usuario/Contraseña tradicional
- **Framework:** Django Authentication Framework
- **Ruta:** `/` (página principal)
- **Vista:** `auth_views.login_view`

#### **Validaciones de Contraseña:**
- **Largo mínimo:** 8 caracteres (configurado en Django)
- **Validadores aplicados:**
  1. `UserAttributeSimilarityValidator`: No puede ser similar a información del usuario
  2. `MinimumLengthValidator`: Mínimo 8 caracteres
  3. `CommonPasswordValidator`: No puede ser una contraseña común
  4. `NumericPasswordValidator`: No puede ser solo números

#### **Recuperación de Contraseña:**
**Nota:** El código actual no muestra implementación de recuperación de contraseña. Solo existe el sistema de login básico.

#### **Bloqueo por Intentos Fallidos:**
**Nota:** El código actual no muestra implementación de bloqueo por intentos fallidos. Django tiene protección CSRF pero no bloqueo de cuenta.

#### **Mensajes de Error:**
- "Usuario o contraseña incorrectos." - Cuando las credenciales son inválidas
- "Tu cuenta está desactivada." - Cuando el usuario está inactivo
- "Por favor, completa todos los campos." - Cuando faltan campos

### B) Sesión

#### **Tiempo de Sesión Activa:**
- **Duración:** 3600 segundos (1 hora)
- **Configuración:** `SESSION_COOKIE_AGE = 3600` en settings.py

#### **Inactividad (Timeout):**
- **Comportamiento:** La sesión expira después de 1 hora de inactividad
- **Redirección:** Al expirar, el usuario es redirigido al login

#### **Cierre de Sesión:**
- **Ruta:** `/logout/`
- **Vista:** `auth_views.logout_view`
- **Comportamiento:** Cierra la sesión y redirige al login
- **Mensaje:** "Has cerrado sesión exitosamente."

#### **Cambio de Contraseña:**
**Nota:** El código actual no muestra implementación de cambio de contraseña desde la interfaz. Se debe hacer desde el panel de administración de Django o mediante comando.

### C) Roles y Permisos

#### **Matrix de Permisos por Rol:**

Ver sección [1.C) Roles y Permisos](#c-roles-y-permisos) para la matrix completa.

#### **Quién Puede Crear/Editar/Eliminar:**

**Crear Empleados:**
- Solo: SISTEMAS, ADMIN

**Editar Empleados:**
- Solo: SISTEMAS, ADMIN

**Eliminar Empleados:**
- No existe funcionalidad de eliminación física
- Se desactiva el empleado (campo `activo=False`)
- Solo: SISTEMAS, ADMIN

**Crear Departamentos:**
- Solo: RH, ADMIN

**Editar Departamentos:**
- Solo: RH, ADMIN

**Desactivar Departamentos:**
- Solo: RH, ADMIN

**Crear Equipos:**
- Solo: SISTEMAS, ADMIN

**Editar Equipos:**
- Solo: SISTEMAS, ADMIN

**Asignar Equipos:**
- Solo: SISTEMAS, ADMIN, RH

**Resolver Tickets:**
- Solo: SISTEMAS, ADMIN

#### **Restricciones de Datos por Rol:**

**Empleados:**
- Solo ven sus propios datos
- No pueden ver información de otros empleados
- No pueden ver solicitudes de otros

**Jefes de Área:**
- Ven solo empleados asignados directamente como supervisor
- Ven solo solicitudes de sus empleados asignados
- Ven solo equipos de su departamento

**RH:**
- Ven todos los empleados (solo lectura)
- Ven todas las solicitudes
- Ven inventario de equipos (solo lectura)

**Sistemas:**
- Ven todos los empleados (lectura/escritura)
- Ven todos los tickets
- Ven todo el inventario (lectura/escritura)

**Admin:**
- Acceso completo a todo
- Puede ver y modificar cualquier dato

---

## 7. NOTIFICACIONES Y ALERTAS

### A) Notificaciones por Sistema

#### **Notificaciones Implementadas:**

**Nota:** El código actual utiliza el sistema de mensajes de Django (Django Messages Framework) para mostrar notificaciones en la interfaz. No hay implementación de notificaciones por email, SMS u otros canales.

#### **Notificaciones en el Sistema:**

**Vacación Solicitada:**
- Mensaje: "Solicitud de vacaciones enviada exitosamente."
- Tipo: Success
- Se muestra al empleado después de crear la solicitud

**Vacación Aprobada/Rechazada:**
- Mensaje: "Solicitud aprobada exitosamente." o "Solicitud rechazada."
- Tipo: Success o Error
- Se muestra al aprobador después de la acción

**Ticket Creado:**
- Mensaje: "Ticket [código] creado exitosamente."
- Tipo: Success
- Se muestra al usuario después de crear el ticket

**Ticket Asignado:**
- Mensaje: "Ticket [código] asignado correctamente."
- Tipo: Success
- Se muestra al técnico después de asignarse

**Ticket Resuelto:**
- Mensaje: "Ticket [código] actualizado correctamente."
- Tipo: Success
- Se muestra al técnico después de resolver

**Equipo Asignado:**
- Mensaje: "Equipo [código] asignado a [empleado] exitosamente."
- Tipo: Success
- Se muestra después de asignar equipo

**Usuario Creado:**
- Mensaje: "Usuario [username] creado exitosamente."
- Tipo: Success
- Se muestra después de crear usuario

**Perfil Actualizado:**
- Mensaje: "Perfil actualizado exitosamente."
- Tipo: Success
- Se muestra después de editar perfil

### B) Canales de Notificación

#### **En el Sistema (Mensajes Django):**
- **Implementación:** Completa
- **Ubicación:** Parte superior de la página
- **Tipos:** Success, Error, Warning, Info
- **Duración:** Se muestran hasta que el usuario navega a otra página o las cierra manualmente

#### **Email:**
- **Estado:** Configurado pero no implementado
- **Configuración en settings.py:**
  ```python
  EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
  EMAIL_HOST = 'localhost'
  EMAIL_PORT = 587
  EMAIL_USE_TLS = True
  ```
- **Nota:** El backend está configurado para consola (desarrollo). No hay código que envíe emails automáticamente.

#### **SMS:**
- **Estado:** No implementado
- **Nota:** No hay configuración ni código relacionado con SMS.

#### **Otra Forma:**
- **Estado:** No implementado
- **Nota:** Solo existe el sistema de mensajes de Django en la interfaz.

---

## 8. DATOS Y EJEMPLOS

### A) Datos de Ejemplo

#### **Usuario de Prueba:**
**Nota:** El código no incluye datos de ejemplo predefinidos. Se deben crear mediante el admin o formularios.

**Ejemplo de Usuario Admin:**
- Username: `admin`
- Email: `admin@grupokeila.com`
- Tipo: ADMIN
- Se crea mediante: `python manage.py createsuperuser`

**Ejemplo de Usuario Empleado:**
- Username: `juan.perez`
- Nombre: Juan
- Apellidos: Pérez
- Email: `juan.perez@grupokeila.com`
- Número de Empleado: `EMP0001`
- Puesto: Desarrollador
- Departamento: Sistemas
- Tipo: EMPLEADO

#### **Empleados de Ejemplo para las Tablas:**
**No hay datos de ejemplo en el código.** Se deben crear manualmente.

#### **Tickets de Ejemplo:**
**No hay tickets de ejemplo en el código.** Se deben crear mediante el formulario.

**Ejemplo de Ticket:**
- Código: `TKT-20241215-001` (generado automáticamente)
- Tipo: HARDWARE
- Prioridad: ALTA
- Descripción: "Laptop no enciende, pantalla negra"
- Estado: PENDIENTE

#### **Equipos de Ejemplo:**
**No hay equipos de ejemplo en el código.** Se deben crear mediante el formulario.

**Ejemplo de Equipo:**
- Categoría: Laptop
- Marca: HP
- Modelo: EliteBook 840 G8
- Número de Serie: `5CD1234ABC`
- Código de Inventario: `INV-001`
- Estado: DISPONIBLE
- Fecha de Adquisición: 2024-01-15

### B) URLs y Rutas

#### **URL Base del Sistema:**
- Desarrollo: `http://127.0.0.1:8000/` o `http://localhost:8000/`
- Producción: Configurado en `settings.py` (ALLOWED_HOSTS)

#### **Ruta de Login:**
- `/` (raíz del sitio)
- Redirige a dashboard si ya está autenticado

#### **Rutas de Módulos Principales:**

**Dashboard:**
- `/dashboard/` - Redirige según tipo de perfil
- `/administrador/` - Dashboard de administrador
- `/rh/` - Dashboard de RH
- `/jefe/` - Dashboard de jefe
- `/empleado/` - Dashboard de empleado
- `/sistemas/` - Dashboard de sistemas

**Empleados:**
- `/empleados/` - Lista de empleados
- `/usuarios/` - Gestión de usuarios
- `/usuarios/crear/` - Crear usuario
- `/usuarios/<id>/editar/` - Editar perfil
- `/perfil/` - Ver perfil

**Vacaciones:**
- `/vacaciones/` - Mis vacaciones
- `/vacaciones/solicitar/` - Solicitar vacaciones
- `/vacaciones/solicitudes-jefe/` - Solicitudes para jefe
- `/vacaciones/solicitudes-rh/` - Solicitudes para RH
- `/vacaciones/<id>/aprobar-jefe/` - Aprobar como jefe
- `/vacaciones/<id>/aprobar-admin/` - Aprobar como admin
- `/vacaciones/<id>/aprobar-rh/` - Aprobar como RH
- `/vacaciones/<id>/pdf/` - PDF de formulario
- `/vacaciones/reporte-mes/` - Reporte mensual

**Tickets:**
- `/tickets/` - Mis tickets
- `/tickets/crear/` - Crear ticket
- `/tickets/<id>/` - Detalle de ticket
- `/sistemas/tickets/` - Gestión de tickets
- `/sistemas/tickets/<id>/asignar/` - Asignar ticket
- `/sistemas/tickets/<id>/resolver/` - Resolver ticket

**Equipos:**
- `/equipos/` - Mis equipos
- `/sistemas/equipos/` - Inventario completo
- `/sistemas/equipos/agregar/` - Agregar equipo
- `/sistemas/equipos/<id>/gestionar/` - Gestionar asignación
- `/jefe/equipos/` - Inventario para jefe (solo lectura)

**Departamentos:**
- `/departamentos/` - Lista de departamentos
- `/departamentos/crear/` - Crear departamento
- `/departamentos/<id>/` - Ver departamento
- `/departamentos/<id>/editar/` - Editar departamento

#### **Parámetros de URL Importantes:**

**Reporte de Vacaciones:**
- `?mes=X` - Mes (1-12)
- `?año=YYYY` - Año (2000-2100)
- Ejemplo: `/vacaciones/reporte-mes/?mes=12&año=2024`

**Filtros en Listas:**
- `?tipo_perfil=EMPLEADO` - Filtrar por tipo de perfil
- `?departamento=X` - Filtrar por departamento
- `?busqueda=texto` - Búsqueda de texto
- `?estado=PENDIENTE` - Filtrar por estado (tickets, vacaciones, equipos)

---

## 9. VALIDACIONES Y RESTRICCIONES

### Campos Obligatorios vs Opcionales

#### **Formulario de Creación de Usuario:**

**Obligatorios:**
- Username
- Nombre (first_name)
- Apellidos (last_name)
- Email
- Password1
- Password2
- Tipo de Perfil
- Número de Empleado
- Puesto
- Fecha de Contratación

**Opcionales:**
- Departamento
- Supervisor
- Teléfono
- Fecha de Nacimiento
- Salario
- Dirección

#### **Formulario de Solicitud de Vacaciones:**

**Obligatorios:**
- Fecha de Inicio
- Fecha de Fin
- Tipo de Vacación
- Motivo

**Opcionales:**
- Ninguno

#### **Formulario de Creación de Ticket:**

**Obligatorios:**
- Tipo de Problema
- Prioridad
- Descripción del Problema

**Opcionales:**
- Área
- Dispositivo Afectado

#### **Formulario de Creación de Equipo:**

**Obligatorios:**
- Categoría
- Marca
- Modelo
- Número de Serie
- Código de Inventario
- Estado
- Fecha de Adquisición

**Opcionales:**
- Observaciones
- Asignar a Empleado (al crear)
- Condición al Entregar (al crear)

### Validaciones de Formato

#### **Email:**
- Formato: `usuario@dominio.com`
- Validación: Regex Django estándar
- Mensaje de error: "Este correo electrónico ya está registrado." (si duplicado)

#### **Fecha:**
- Formato de entrada: DD/MM/YYYY (en formularios)
- Formato interno: YYYY-MM-DD (ISO)
- Validación: Django DateField
- Mensaje de error: "Formato de fecha inválido."

#### **Número de Empleado:**
- Formato: Alfanumérico (letras mayúsculas, números, guiones)
- Validación JavaScript: `/^[A-Z0-9-]+$/`
- Máximo: 20 caracteres
- Mensaje de error: "El número de empleado debe contener solo letras mayúsculas, números y guiones"

#### **Teléfono:**
- Formato: Números, espacios, guiones, paréntesis, signo +
- Validación JavaScript: `/^[\d\s\-\+\(\)]+$/`
- Máximo: 15 caracteres
- Mensaje de error: "Por favor, ingresa un teléfono válido"

#### **Salario:**
- Formato: Decimal (10 dígitos, 2 decimales)
- Validación: Debe ser número positivo
- Mensaje de error: "El salario debe ser un número positivo"

### Límites

#### **Caracteres Máximos:**
- Username: 150 caracteres
- Nombre: 30 caracteres
- Apellidos: 30 caracteres
- Email: 254 caracteres (límite Django)
- Número de Empleado: 20 caracteres
- Puesto: 100 caracteres
- Teléfono: 15 caracteres
- Dirección: 255 caracteres
- Motivo (vacaciones): Sin límite (TextField)
- Descripción (ticket): Sin límite (TextField)
- Observaciones (equipo): Sin límite (TextField)

#### **Números:**
- Días de Vacaciones: Entero positivo (PositiveIntegerField)
- Salario: Decimal (10 dígitos, 2 decimales)
- Prioridad de Ticket: Opciones predefinidas (no numérico)

### Reglas de Negocio

#### **Vacaciones:**
1. **Antigüedad Mínima:**
   - Empleados con < 1 año: Solo pueden solicitar vacaciones extraordinarias
   - Empleados con >= 1 año: Pueden solicitar vacaciones normales o extraordinarias

2. **Días Disponibles:**
   - No se pueden solicitar más días de los disponibles
   - Fórmula: `(dias_anuales + dias_acumulados) - dias_usados`

3. **Fechas:**
   - Fecha fin debe ser posterior a fecha inicio
   - No se pueden solicitar vacaciones para fechas anteriores a hace 7 días
   - Excepción: Se permite retroceder hasta 7 días para cambiar faltas por días de vacaciones

4. **Cálculo de Días:**
   - Excluye domingos del conteo
   - Se calcula automáticamente al guardar

5. **Flujo de Aprobación:**
   - Empleados normales: Jefe → RH
   - Jefes de área: Admin → RH
   - No se puede aprobar la propia solicitud

#### **Tickets:**
1. **Asignación:**
   - Solo SISTEMAS/ADMIN pueden asignar tickets
   - Un ticket solo puede estar asignado a un técnico a la vez

2. **Resolución:**
   - Solo SISTEMAS/ADMIN pueden resolver tickets
   - Al resolver, se debe completar el campo "Solución"

#### **Equipos:**
1. **Asignación:**
   - Solo se pueden asignar equipos con estado DISPONIBLE o EN_REPARACION
   - Si un equipo está ASIGNADO, primero se debe quitar la asignación anterior
   - Solo se pueden asignar a empleados activos

2. **Estado:**
   - Al asignar, el estado cambia automáticamente a ASIGNADO (si no está en reparación)
   - Al quitar asignación, el estado cambia a DISPONIBLE (si no está en reparación o dado de baja)

#### **Usuarios:**
1. **Creación:**
   - Username debe ser único
   - Email debe ser único
   - Número de empleado debe ser único

2. **Perfil:**
   - Se crea automáticamente al crear usuario (signal)
   - Tipo de perfil default: EMPLEADO

### Mensajes de Error del Sistema

#### **Autenticación:**
- "Usuario o contraseña incorrectos."
- "Tu cuenta está desactivada."
- "Por favor, completa todos los campos."

#### **Validación de Formularios:**
- "Este nombre de usuario ya existe."
- "Este correo electrónico ya está registrado."
- "Este número de empleado ya existe."
- "La fecha de fin debe ser posterior a la fecha de inicio."
- "No puedes solicitar vacaciones para fechas anteriores a hace una semana."
- "No tienes suficientes días de vacaciones disponibles."
- "La fecha de devolución no puede ser anterior a la fecha de asignación."

#### **Permisos:**
- "No tienes permiso para acceder a esta sección."
- "No tienes permiso para realizar esta acción."
- "No puedes aprobar tu propia solicitud de vacaciones."
- "Solo puedes aprobar solicitudes de empleados asignados a tu área."

#### **Operaciones:**
- "No se pudo aprobar la solicitud."
- "No se pudo rechazar la solicitud."
- "El equipo no está disponible para asignar."
- "El equipo no tiene una asignación activa."

---

## 10. FUNCIONALIDADES AVANZADAS

### A) Exportación de Datos

#### **Reportes de Vacaciones:**

**Formato PDF:**
- **Ruta:** `/vacaciones/reporte-mes/pdf/`
- **Parámetros:** `?mes=X&año=YYYY`
- **Formato:** APA 7 (Times New Roman, márgenes estándar)
- **Contenido:**
  - Título: "Reporte de Vacaciones"
  - Período: Mes y año
  - Resumen estadístico (texto)
  - Tabla detallada con:
    - Empleado
    - Departamento
    - Período
    - Días
    - Estado
    - Fecha Solicitud
- **Generación:** ReportLab
- **Descarga:** Inline (abre en navegador) o Attachment (descarga)

**Formato Excel (.xlsx):**
- **Ruta:** `/vacaciones/reporte-mes/excel/`
- **Parámetros:** `?mes=X&año=YYYY`
- **Formato:** Excel profesional con formato
- **Contenido:**
  - Encabezado con título y período
  - Fecha de generación
  - Resumen estadístico en tabla
  - Tabla completa con 15 columnas:
    - Empleado
    - Número de Empleado
    - Departamento
    - Puesto
    - Fecha Inicio
    - Fecha Fin
    - Días Solicitados
    - Tipo de Vacación
    - Estado
    - Fecha Solicitud
    - Aprobado por Jefe
    - Fecha Aprobación Jefe
    - Aprobado por RH
    - Fecha Aprobación RH
    - Motivo
- **Generación:** openpyxl
- **Fallback:** CSV si openpyxl no está disponible

**Formato CSV:**
- **Ruta:** `/vacaciones/reporte-mes/excel/` (fallback)
- **Formato:** CSV con BOM UTF-8 (compatible con Excel)
- **Contenido:** Mismo que Excel pero en formato CSV

### B) Reportes Personalizados

#### **Reporte Mensual de Vacaciones:**
- **Ruta:** `/vacaciones/reporte-mes/`
- **Funcionalidad:**
  - Selección de mes y año
  - Vista previa de solicitudes
  - Estadísticas resumidas:
    - Total de solicitudes
    - Aprobadas
    - Rechazadas
    - Pendientes
    - Total de días aprobados
  - Botones de exportación (PDF/Excel)

### C) Gráficos o Dashboards Analíticos

#### **Dashboards por Rol:**
- **Implementación:** Completa
- **Tipo:** Métricas y contadores (no gráficos)
- **Actualización:** Tiempo real (cada carga de página)
- **Contenido:** Ver sección [5. Dashboard y Métricas](#5-dashboard-y-métricas)

**Nota:** No hay gráficos (charts) implementados en el código actual. Solo métricas numéricas y listas.

### D) Búsqueda Avanzada o Filtros Complejos

#### **Búsqueda en Lista de Empleados:**
- **Campos buscables:**
  - Username
  - Nombre (first_name)
  - Apellidos (last_name)
  - Número de empleado
- **Tipo:** Búsqueda de texto (icontains - case insensitive)
- **Combinación:** Se puede combinar con filtros de tipo de perfil y departamento

#### **Filtros en Solicitudes de Vacaciones:**
- **Por Estado:** PENDIENTE, APROBADO, RECHAZADO, TODAS
- **Por Empleado:** Búsqueda de texto en nombre
- **Combinación:** Se pueden combinar ambos filtros

#### **Filtros en Tickets:**
- **Por Estado:** TODOS, PENDIENTE, EN_PROCESO, RESUELTO, CANCELADO
- **Ordenamiento:** Por fecha de creación (más recientes primero)

#### **Filtros en Equipos:**
- **Por Estado:** DISPONIBLE, ASIGNADO, EN_REPARACION, DADO_DE_BAJA
- **Ordenamiento:** Por fecha de adquisición (más recientes primero)

### E) Automatizaciones

#### **Comandos de Management:**

**1. Acumulación Mensual de Vacaciones:**
- **Comando:** `python manage.py acumular_mensual`
- **Funcionalidad:** Procesa la acumulación mensual de vacaciones para empleados con >= 1 año
- **Frecuencia:** Debe ejecutarse mensualmente (cron job recomendado)
- **Proceso:**
  - Calcula días por mes según antigüedad
  - Agrega días a `dias_vacaciones_acumulados`
  - Solo procesa empleados activos con >= 1 año

**2. Actualización de Vacaciones:**
- **Comando:** `python manage.py actualizar_vacaciones`
- **Funcionalidad:** Actualiza días de vacaciones según antigüedad
- **Frecuencia:** Puede ejecutarse periódicamente

**3. Reset de Vacaciones:**
- **Comando:** `python manage.py reset_vacaciones`
- **Funcionalidad:** Procesa el reset anual de vacaciones
- **Frecuencia:** Debe ejecutarse anualmente (cron job recomendado)
- **Proceso:**
  - Calcula días no usados del año anterior
  - Acumula días no usados
  - Resetea contadores del año
  - Actualiza días anuales según nueva antigüedad

**4. Reporte de Vacaciones:**
- **Comando:** `python manage.py reporte_vacaciones`
- **Funcionalidad:** Genera reporte de vacaciones (probablemente para línea de comandos)
- **Frecuencia:** Según necesidad

#### **Señales (Signals):**

**1. Creación Automática de Perfil:**
- **Signal:** `post_save` en modelo `User`
- **Funcionalidad:** Crea automáticamente un perfil cuando se crea un usuario
- **Valores Default:**
  - Tipo de perfil: EMPLEADO
  - Fecha de contratación: Fecha actual
  - Número de empleado: `EMP{user.id:04d}`
  - Puesto: "Por definir"

**2. Cálculo Automático de Días Solicitados:**
- **Signal:** `save()` en modelo `SolicitudVacaciones`
- **Funcionalidad:** Calcula automáticamente días solicitados excluyendo domingos
- **Método:** `calcular_dias_laborables()`

**3. Actualización de Estado para Jefes:**
- **Signal:** `save()` en modelo `SolicitudVacaciones`
- **Funcionalidad:** Si el empleado es jefe de área, establece estado `PENDIENTE_ADMIN` en lugar de `PENDIENTE_JEFE`

**4. Descuento Automático de Días:**
- **Método:** `aprobar_por_rh()` en modelo `SolicitudVacaciones`
- **Funcionalidad:** Al aprobar por RH, descuenta automáticamente los días usados del perfil del empleado

**5. Actualización Automática de Estado de Equipo:**
- **Signal:** `save()` en modelo `AsignacionEquipo` (implícito en vistas)
- **Funcionalidad:** Al asignar equipo, cambia estado a ASIGNADO. Al quitar asignación, cambia a DISPONIBLE.

**6. Generación Automática de Código de Ticket:**
- **Signal:** `save()` en modelo `Ticket`
- **Funcionalidad:** Genera código único `TKT-YYYYMMDD-XXX` automáticamente

### F) Integraciones con Otros Sistemas

#### **Estado Actual:**
- **No hay integraciones implementadas**
- **Configuración de Email:** Existe pero no se usa (solo backend de consola)

#### **Configuración Preparada:**
- **Email:** Configurado en settings.py pero no implementado
- **Base de datos:** SQLite en desarrollo, puede cambiarse a PostgreSQL/MySQL

### G) API o Webhooks

#### **Estado Actual:**
- **No hay API REST implementada**
- **No hay webhooks implementados**

#### **Endpoints JSON Existentes:**
- **Validar Antigüedad:** `/api/validar-antiguedad/`
  - Método: GET
  - Retorna: JSON con antigüedad, puede_vacaciones_normales, dias_disponibles
  - Autenticación: Requerida (login_required)

### H) Historial de Cambios/Auditoría

#### **Campos de Auditoría en Modelos:**

**Todos los modelos principales tienen:**
- **fecha_creacion:** Timestamp automático al crear
- **fecha_actualizacion:** Timestamp automático al actualizar

**Modelos con Auditoría Específica:**

**SolicitudVacaciones:**
- fecha_solicitud
- fecha_aprobacion_jefe
- fecha_aprobacion_admin
- fecha_aprobacion_rh
- aprobado_por_jefe (ForeignKey)
- aprobado_por_admin (ForeignKey)
- aprobado_por_rh (ForeignKey)
- comentarios_jefe
- comentarios_admin
- comentarios_rh

**Ticket:**
- fecha_creacion
- fecha_asignacion
- fecha_resolucion
- fecha_actualizacion
- asignado_a (ForeignKey)

**AsignacionEquipo:**
- fecha_asignacion
- fecha_devolucion
- fecha_creacion
- fecha_actualizacion
- asignado_por (ForeignKey)

**Nota:** No hay un sistema de historial de cambios detallado (log de cambios). Solo se registran timestamps y usuarios que realizan acciones importantes.

---

## PREGUNTAS COMPLEMENTARIAS - RESPUESTAS

### 1. ¿Existen campos personalizados o configurables por usuario?

**Respuesta:** No. Todos los campos son estándar y no hay funcionalidad de campos personalizados o configurables por usuario.

### 2. ¿El sistema tiene versionamiento o control de cambios?

**Respuesta:** Parcial. Se registran timestamps (fecha_creacion, fecha_actualizacion) y usuarios que realizan acciones importantes (aprobaciones, asignaciones), pero no hay un sistema completo de versionamiento o historial detallado de cambios.

### 3. ¿Hay límites de datos históricos almacenados?

**Respuesta:** No. No hay límites implementados en el código. Todos los datos históricos se almacenan indefinidamente. Se recomienda implementar políticas de retención según necesidades de la empresa.

### 4. ¿Cuáles son los tiempos promedio de respuesta esperados del sistema?

**Respuesta:** No hay tiempos específicos configurados en el código. El sistema calcula tiempos de respuesta y resolución de tickets (propiedades `tiempo_respuesta` y `tiempo_resolucion`) pero no hay métricas o alertas basadas en estos tiempos.

### 5. ¿Existen limitaciones de navegadores o dispositivos?

**Respuesta:** No hay limitaciones explícitas en el código. El sistema utiliza Bootstrap y diseño responsive, por lo que debería funcionar en navegadores modernos. Se recomienda:
- Chrome, Firefox, Safari, Edge (versiones recientes)
- Dispositivos móviles y tablets (responsive design)

### 6. ¿El sistema tiene múltiples idiomas?

**Respuesta:** No. El sistema está configurado para español mexicano (`LANGUAGE_CODE = 'es-mx'`). No hay implementación de internacionalización (i18n) o múltiples idiomas.

### 7. ¿Hay configuraciones de empresa/departamento?

**Respuesta:** Sí, parcialmente. Existe el modelo `ConfiguracionSistema` pero no se usa en el código actual. Los departamentos se gestionan mediante el modelo `Departamento` con campos:
- nombre
- descripcion
- jefe (ForeignKey a Perfil)
- activo

### 8. ¿Cómo se manejan los cambios de roles mientras un usuario está conectado?

**Respuesta:** No hay manejo especial. Si un administrador cambia el rol de un usuario mientras está conectado, el cambio se reflejará en la próxima acción que requiera verificación de permisos. Se recomienda que el usuario cierre sesión y vuelva a iniciar para asegurar que los permisos se actualicen correctamente.

---

## NOTAS IMPORTANTES PARA EL MANUAL DE USUARIO

### 1. **Sistema de Mensajes:**
- Todas las notificaciones se muestran en la parte superior de la página
- Los mensajes desaparecen al navegar a otra página o al cerrarlos manualmente
- Tipos de mensajes: Success (verde), Error (rojo), Warning (amarillo), Info (azul)

### 2. **Navegación:**
- Cada dashboard tiene botones de acceso rápido a las funcionalidades principales
- El menú lateral (si existe) muestra opciones según el tipo de perfil
- Los breadcrumbs ayudan a entender la ubicación actual

### 3. **Formularios:**
- Los campos obligatorios están marcados con asterisco (*) o indicador visual
- Los mensajes de error aparecen debajo de cada campo con problema
- Los formularios tienen validación en tiempo real (JavaScript) y en servidor (Django)

### 4. **Exportación:**
- Los reportes se pueden exportar en PDF o Excel
- El PDF se abre en el navegador, el Excel se descarga
- Los reportes incluyen fecha de generación y período seleccionado

### 5. **Búsqueda y Filtros:**
- Los filtros se pueden combinar (ej: tipo de perfil + departamento + búsqueda de texto)
- La búsqueda de texto busca en múltiples campos simultáneamente
- Los resultados se ordenan por defecto (más recientes primero en la mayoría de casos)

### 6. **Permisos:**
- Si intenta acceder a una funcionalidad sin permisos, verá un error 403
- Los botones y enlaces se ocultan automáticamente si no tiene permisos
- Algunas acciones requieren permisos específicos (ej: solo RH puede aprobar vacaciones finales)

### 7. **Sesión:**
- La sesión expira después de 1 hora de inactividad
- Al expirar, se redirige al login automáticamente
- Se recomienda guardar el trabajo frecuentemente

### 8. **Datos Calculados:**
- Los días de vacaciones se calculan automáticamente según antigüedad
- Los días disponibles se actualizan en tiempo real
- Los días solicitados se calculan automáticamente excluyendo domingos

---

## CONCLUSIÓN

Este documento contiene toda la información extraída del código fuente del Sistema GK. La información está organizada por módulos y funcionalidades, con detalles técnicos, flujos de usuario, validaciones, restricciones y ejemplos.

**Recomendaciones para el Manual de Usuario:**
1. Incluir capturas de pantalla de cada funcionalidad
2. Agregar casos de uso reales con datos de ejemplo
3. Incluir sección de solución de problemas comunes
4. Agregar diagramas de flujo visuales
5. Incluir guías paso a paso con numeración clara
6. Agregar consejos de optimización y mejores prácticas

**Información Adicional Necesaria:**
- Datos de ejemplo reales (usuarios, empleados, tickets, equipos)
- Configuración de producción (URLs, dominios)
- Políticas de la empresa (límites de días, reglas especiales)
- Contactos de soporte técnico

---

**Fin del Documento**


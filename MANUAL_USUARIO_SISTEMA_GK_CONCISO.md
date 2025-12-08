# Manual de Usuario
## Sistema GK - Grupo Keila

**Versión:** 1.0  
**Fecha:** 2024

---

# Índice

1. [Introducción](#1-introducción)
   1.1. [¿Qué es el Sistema GK?](#11-qué-es-el-sistema-gk)

2. [Tipos de Usuario y Sus Funciones](#2-tipos-de-usuario-y-sus-funciones)
   2.1. [Empleado](#21--empleado)
   2.2. [Jefe de Área](#22--jefe-de-área)
   2.3. [Recursos Humanos (RH)](#23--recursos-humanos-rh)
   2.4. [Sistemas/IT](#24--sistemasit)
   2.5. [Administrador](#25--administrador)
   2.6. [Resumen de Funciones por Rol](#26-resumen-de-funciones-por-rol)

3. [Acceso al Sistema](#3-acceso-al-sistema)
   2.1. [Iniciar Sesión](#21-iniciar-sesión)
   2.2. [Cerrar Sesión](#22-cerrar-sesión)

3. [Panel Principal](#3-panel-principal)
   3.1. [Panel de Empleado](#31-panel-de-empleado)
   3.2. [Panel de Sistemas/IT](#32-panel-de-sistemasit)

4. [Gestión de Vacaciones](#4-gestión-de-vacaciones)
   4.1. [Solicitar Vacaciones](#41-solicitar-vacaciones)
   4.2. [Ver Mis Vacaciones](#42-ver-mis-vacaciones)
   4.3. [Aprobar Vacaciones (Jefe/RH)](#43-aprobar-vacaciones-jeferh)

5. [Gestión de Tickets](#5-gestión-de-tickets)
   5.1. [Crear un Ticket](#51-crear-un-ticket)
   5.2. [Gestionar Tickets (Sistemas/IT)](#52-gestionar-tickets-sistemasit)

6. [Gestión de Equipos](#6-gestión-de-equipos)
   6.1. [Ver Inventario (Sistemas/IT)](#61-ver-inventario-sistemasit)
   6.2. [Asignar Equipo](#62-asignar-equipo)
   6.3. [Ver Mis Equipos (Empleado)](#63-ver-mis-equipos-empleado)

7. [Solución de Problemas](#7-solución-de-problemas)

8. [Contacto y Soporte](#8-contacto-y-soporte)

---

# 1. Introducción

## 1.1. ¿Qué es el Sistema GK?

El Sistema GK es una plataforma web para gestionar recursos humanos. Te permite:

- Solicitar y aprobar vacaciones
- Reportar problemas técnicos (tickets)
- Gestionar equipos de trabajo
- Ver información de empleados

---

# 2. Tipos de Usuario y Sus Funciones

El Sistema GK tiene 5 tipos de usuarios, cada uno con permisos y funciones específicas. Es importante entender tu rol para saber qué puedes hacer en el sistema.

## 2.1. 👤 Empleado

**¿Quién es?**: Un empleado regular de la empresa que usa el sistema para gestionar sus vacaciones, reportar problemas técnicos y consultar su información personal.

**Funciones principales**:
- Solicitar vacaciones y ver el estado de sus solicitudes
- Crear tickets de soporte técnico cuando tiene problemas
- Ver los equipos tecnológicos que tiene asignados
- Consultar y editar su información personal
- Ver su historial de vacaciones y días disponibles

**Módulos accesibles**:
- Panel de Empleado (dashboard personal)
- Módulo de Vacaciones (solo solicitar y ver propias)
- Módulo de Tickets (solo crear y ver propios)
- Módulo de Equipos (solo ver asignados)
- Perfil Personal

**Restricciones**:
- ❌ No puede aprobar vacaciones de otros
- ❌ No puede gestionar tickets de otros usuarios
- ❌ No puede ver información de otros empleados
- ❌ No puede asignar o gestionar equipos

---

## 2.2. 👔 Jefe de Área

**¿Quién es?**: Un supervisor o jefe de departamento que tiene la responsabilidad de aprobar las solicitudes de vacaciones de los empleados que están bajo su supervisión directa.

**Funciones principales**:
- Aprobar o rechazar solicitudes de vacaciones de su departamento
- Ver el estado de las solicitudes de su equipo
- Consultar información de empleados de su departamento
- Ver estadísticas de su departamento

**Módulos accesibles**:
- Panel de Jefe de Área
- Módulo de Vacaciones (aprobar solicitudes de su depto)
- Lista de Empleados (solo de su departamento)
- Todas las funciones de Empleado

**Restricciones**:
- ❌ Solo puede aprobar vacaciones de su propio departamento
- ❌ No puede gestionar tickets o equipos
- ❌ No puede crear usuarios o departamentos

---

## 2.3. 👥 Recursos Humanos (RH)

**¿Quién es?**: Personal del área de Recursos Humanos que gestiona toda la información de empleados, departamentos y tiene la aprobación final de las vacaciones.

**Funciones principales**:
- Gestionar información de todos los empleados
- Crear y editar usuarios y perfiles
- Gestionar departamentos
- Aprobar vacaciones (aprobación final después del jefe)
- Generar reportes de vacaciones
- Ver estadísticas generales de la empresa

**Módulos accesibles**:
- Panel de RH
- Gestión de Empleados (completo)
- Gestión de Departamentos
- Módulo de Vacaciones (aprobación final y reportes)
- Todas las funciones de Empleado

**Restricciones**:
- ❌ No puede gestionar tickets de soporte técnico
- ❌ No puede gestionar equipos tecnológicos

---

## 2.4. 💻 Sistemas/IT

**¿Quién es?**: Personal del área de Tecnologías de la Información que gestiona los tickets de soporte técnico y el inventario de equipos tecnológicos.

**Funciones principales**:
- Gestionar todos los tickets de soporte técnico
- Asignar y resolver tickets
- Gestionar inventario de equipos tecnológicos
- Asignar equipos a empleados
- Marcar equipos en reparación o disponibles
- Ver estadísticas de tickets y equipos

**Módulos accesibles**:
- Panel de Sistemas/IT
- Módulo de Tickets (gestión completa)
- Módulo de Equipos (inventario y asignaciones)
- Todas las funciones de Empleado

**Restricciones**:
- ❌ No puede gestionar empleados o departamentos
- ❌ No puede aprobar vacaciones

---

## 2.5. 🔧 Administrador

**¿Quién es?**: Usuario con acceso completo al sistema, puede realizar todas las funciones y gestionar la configuración general.

**Funciones principales**:
- Acceso completo a todas las funciones del sistema
- Gestionar usuarios y permisos
- Aprobar vacaciones (puede hacerlo en cualquier nivel)
- Gestionar tickets y equipos
- Ver estadísticas completas del sistema
- Configurar parámetros generales

**Módulos accesibles**:
- Panel de Administrador
- Todos los módulos sin restricciones
- Configuración del sistema

**Restricciones**:
- Ninguna (acceso completo)

---

## 2.6. Resumen de Funciones por Rol

| Función | Empleado | Jefe | RH | Sistemas | Admin |
|---------|----------|------|-----|----------|-------|
| Solicitar vacaciones | ✅ | ✅ | ✅ | ✅ | ✅ |
| Ver mis vacaciones | ✅ | ✅ | ✅ | ✅ | ✅ |
| Aprobar vacaciones (depto) | ❌ | ✅ | ❌ | ❌ | ✅ |
| Aprobar vacaciones (todas) | ❌ | ❌ | ✅ | ❌ | ✅ |
| Crear tickets | ✅ | ✅ | ✅ | ✅ | ✅ |
| Resolver tickets | ❌ | ❌ | ❌ | ✅ | ✅ |
| Gestionar equipos | ❌ | ❌ | ❌ | ✅ | ✅ |
| Ver todos los empleados | ❌ | ❌ | ✅ | ❌ | ✅ |
| Crear/editar usuarios | ❌ | ❌ | ✅ | ❌ | ✅ |
| Gestionar departamentos | ❌ | ❌ | ✅ | ❌ | ✅ |
| Ver estadísticas completas | ❌ | ❌ | ✅ | ✅ | ✅ |

> **💡 Tip**: Si no estás seguro de qué puedes hacer en el sistema, consulta esta tabla o contacta a tu administrador.

---

# 3. Acceso al Sistema

## 3.1. Iniciar Sesión

1. Abre tu navegador web
2. Ingresa la dirección del sistema
3. Ingresa tu **usuario** y **contraseña**

**[CAPTURA DE PANTALLA: Pantalla de login completa mostrando campos de usuario y contraseña vacíos, con el botón "Iniciar Sesión" visible en la parte inferior, y el logo "Sistema GK" en la parte superior]**

4. Haz clic en **"Iniciar Sesión"**

**[CAPTURA DE PANTALLA: Botón "Iniciar Sesión" resaltado con un círculo rojo señalándolo]**

5. Serás redirigido automáticamente a tu panel según tu tipo de usuario

## 3.2. Cerrar Sesión

1. Haz clic en tu nombre de usuario (esquina superior derecha)
2. Selecciona **"Cerrar Sesión"**

**[CAPTURA DE PANTALLA: Menú desplegable con el nombre del usuario mostrando la opción "Cerrar Sesión" resaltada]**

---

# 4. Panel Principal

## 4.1. Panel de Empleado

Después de iniciar sesión como empleado, verás tu panel personal.

**[CAPTURA DE PANTALLA: Dashboard completo de empleado mostrando en la parte superior las tarjetas con información de vacaciones: "Días Disponibles: 15", "Días Usados: 5", "Acumulado Este Año: 3.5", y en la parte inferior la tabla de "Mis Solicitudes de Vacaciones" con 2 solicitudes visibles, y los botones "Solicitar Vacaciones" y "Generar Ticket" en la parte superior derecha]**

### Información Mostrada

- **Días disponibles**: Cuántos días de vacaciones tienes
- **Días usados**: Días que ya usaste este año
- **Mis solicitudes**: Lista de todas tus solicitudes de vacaciones

### Accesos Rápidos

- **Solicitar Vacaciones**: Crear nueva solicitud
- **Generar Ticket**: Reportar problema técnico

**[CAPTURA DE PANTALLA: Botones de accesos rápidos "Solicitar Vacaciones" (naranja) y "Generar Ticket" (verde) resaltados con círculos rojos]**

---

## 4.2. Panel de Sistemas/IT

El panel de Sistemas muestra información sobre tickets y equipos.

**[CAPTURA DE PANTALLA: Dashboard completo de Sistemas/IT mostrando 4 tarjetas de estadísticas: "1 Tickets Pendientes" (naranja), "0 En Proceso" (azul), "3 Tickets Resueltos Hoy" (verde), "5 Equipos Disponibles" (gris), y en la parte inferior los accesos rápidos "Gestionar Tickets" (naranja) e "Inventario" (azul)]**

### Estadísticas

- **Tickets pendientes**: Problemas sin resolver
- **Tickets en proceso**: Problemas siendo atendidos
- **Equipos disponibles**: Equipos que se pueden asignar

### Accesos Rápidos

- **Gestionar Tickets**: Ver y administrar todos los tickets
- **Inventario**: Ver y gestionar equipos

**[CAPTURA DE PANTALLA: Sección de accesos rápidos con botón naranja "Gestionar Tickets" resaltado con círculo rojo, y botón azul "Inventario" al lado]**

---

# 5. Gestión de Vacaciones

## 5.1. Para Empleados

### 5.1.1. Solicitar Vacaciones

> **👤 Solo para Empleados**

#### Acceso

1. Desde tu panel, haz clic en **"Solicitar Vacaciones"**

**[CAPTURA DE PANTALLA: Panel de empleado con el botón naranja "Solicitar Vacaciones" en la parte superior derecha, resaltado con un círculo rojo]**

O desde el menú: **"Vacaciones"** → **"Solicitar Vacaciones"**

#### Llenar el Formulario

**[CAPTURA DE PANTALLA: Formulario completo de solicitud de vacaciones mostrando: campo "Fecha de Inicio" con calendario desplegado mostrando marzo 2024 con día 15 seleccionado, campo "Fecha de Fin" con día 20 seleccionado, selector "Tipo de Vacación" con "Normal" seleccionado, campo "Motivo" con texto "Vacaciones familiares", campo "Días Solicitados" mostrando "5 días" calculado automáticamente, y el botón "Enviar Solicitud" en la parte inferior]**

1. **Fecha de Inicio**: Selecciona el primer día de tus vacaciones
2. **Fecha de Fin**: Selecciona el último día
3. **Tipo**: Normal o Extraordinaria
4. **Motivo**: Escribe el motivo (opcional)
5. El sistema calcula automáticamente los **días solicitados** (excluyendo domingos)

#### Enviar

1. Revisa la información
2. Haz clic en **"Enviar Solicitud"**

**[CAPTURA DE PANTALLA: Botón azul "Enviar Solicitud" resaltado con círculo rojo]**

3. Verás un mensaje de confirmación

**[CAPTURA DE PANTALLA: Mensaje verde de éxito en la parte superior que dice "Solicitud enviada correctamente. Tu solicitud está pendiente de aprobación."]**

---

### 5.1.2. Ver Mis Vacaciones

> **👤 Solo para Empleados**

1. Desde el menú: **"Vacaciones"** → **"Mis Vacaciones"**

**[CAPTURA DE PANTALLA: Menú lateral con la opción "Vacaciones" expandida mostrando "Mis Vacaciones" resaltada]**

2. Verás una tabla con todas tus solicitudes

**[CAPTURA DE PANTALLA: Tabla completa de solicitudes de vacaciones mostrando columnas: Código, Fecha Inicio, Fecha Fin, Días, Estado, y Acciones, con 3 filas de datos visibles, donde una está en "Pendiente Jefe" (amarillo), otra en "Aprobada" (verde), y otra en "Rechazada" (rojo)]**

### Estados

- **Pendiente**: Esperando aprobación
- **Aprobada**: Ya fue aprobada (puedes descargar PDF)
- **Rechazada**: Fue rechazada

### Ver Detalles

1. Haz clic en **"Ver Detalles"** (ícono de ojo)

**[CAPTURA DE PANTALLA: Botón naranja con ícono de ojo en la columna de acciones, resaltado]**

2. Verás toda la información y podrás descargar el PDF si está aprobada

**[CAPTURA DE PANTALLA: Vista de detalles de solicitud mostrando toda la información: fechas, días, estado "Aprobada por RH", y botón "Descargar PDF" visible]**

---

## 5.2. Para Jefes de Área

### 5.2.1. Aprobar Vacaciones de Mi Departamento

> **👔 Solo para Jefes de Área**

#### Acceso

1. Desde tu panel (Jefe o RH), haz clic en **"Solicitudes Pendientes"**

**[CAPTURA DE PANTALLA: Dashboard de jefe mostrando tarjeta "3 Solicitudes Pendientes" y botón "Ver Solicitudes" resaltado]**

#### Lista de Solicitudes

**[CAPTURA DE PANTALLA: Tabla de solicitudes pendientes mostrando: Empleado, Fechas, Días, y columnas de acciones con botones "Aprobar" (verde) y "Rechazar" (rojo)]**

#### Aprobar

1. Haz clic en **"Aprobar"** (botón verde)

**[CAPTURA DE PANTALLA: Botón verde "Aprobar" resaltado con círculo rojo]**

2. Opcionalmente, agrega comentarios

**[CAPTURA DE PANTALLA: Formulario de aprobación con campo de comentarios y botón "Confirmar Aprobación"]**

3. Haz clic en **"Confirmar Aprobación"**

4. La solicitud pasará al siguiente nivel (RH si eres jefe, o se completará si eres RH)

**[CAPTURA DE PANTALLA: Mensaje de confirmación "Solicitud aprobada correctamente"]**

#### Rechazar

---

## 5.3. Para Recursos Humanos

### 5.3.1. Aprobar Vacaciones Finales

> **👥 Solo para Recursos Humanos**

#### Acceso

1. Haz clic en **"Rechazar"** (botón rojo)
2. Escribe el motivo del rechazo
3. Haz clic en **"Confirmar Rechazo"**

---

# 6. Gestión de Tickets

## 6.1. Para Empleados

### 6.1.1. Crear un Ticket

> **👤 Para: Empleados, Jefes, RH, Sistemas, Admin**

#### Acceso

1. Desde tu panel, haz clic en **"Generar Ticket"**

**[CAPTURA DE PANTALLA: Botón verde "Generar Ticket" en el dashboard de empleado, resaltado]**

#### Llenar el Formulario

**[CAPTURA DE PANTALLA: Formulario completo de crear ticket mostrando: selector "Tipo" con "Hardware" seleccionado, selector "Prioridad" con "Media" seleccionado, campo "Área" con texto "Ventas", campo "Dispositivo" con texto "Laptop HP", campo "Descripción" con texto de ejemplo "La laptop no enciende, muestra pantalla azul", y botón "Crear Ticket" en la parte inferior]**

1. **Tipo**: Hardware, Software, Red, Acceso, Otro
2. **Prioridad**: Baja, Media, Alta, Urgente
3. **Área**: Departamento donde ocurre el problema
4. **Dispositivo**: Equipo afectado
5. **Descripción**: Describe el problema detalladamente

#### Enviar

---

## 6.2. Para Sistemas/IT

### 6.2.1. Gestionar Tickets

> **💻 Solo para Sistemas/IT y Administradores**

1. Revisa la información
2. Haz clic en **"Crear Ticket"**

**[CAPTURA DE PANTALLA: Botón "Crear Ticket" resaltado]**

3. Verás el código de tu ticket

**[CAPTURA DE PANTALLA: Mensaje de éxito mostrando "Ticket creado correctamente. Código: TKT-20240315-001"]**

---

#### Acceso

Desde el Panel Sistemas/IT, en Accesos Rápidos, haz clic en el botón naranja **"Gestionar Tickets"**.

**[CAPTURA DE PANTALLA: Panel Sistemas/IT con botón naranja "Gestionar Tickets" resaltado con círculo rojo señalándolo]**

#### Lista de Tickets

Visualice todos los tickets (Pendientes, En Proceso, Resueltos) en esta lista.

**[CAPTURA DE PANTALLA: Lista completa de tickets mostrando tabla con columnas: Código, Solicitante, Tipo, Prioridad, Estado, Fecha Creación, y Acciones, con 5 filas de datos visibles, y en la parte superior filtros de búsqueda y selectores de estado y prioridad]**

#### Filtros

Puedes filtrar por:
- **Búsqueda**: Código o nombre del solicitante
- **Estado**: Pendiente, En Proceso, Resuelto
- **Prioridad**: Baja, Media, Alta, Urgente

**[CAPTURA DE PANTALLA: Sección de filtros mostrando campo de búsqueda, selector de estado con "Pendiente" seleccionado, y botones "Buscar" y "Limpiar"]**

#### Acciones

Use los botones de acción en la columna 'Acciones' para gestionar cada ticket.

##### A. Ver Detalles

1. Haz clic en el botón naranja con ícono de ojo

**[CAPTURA DE PANTALLA: Botón naranja con ícono de ojo en la columna de acciones, resaltado]**

2. Verás toda la información del ticket

**[CAPTURA DE PANTALLA: Vista de detalles del ticket mostrando: código, solicitante, tipo, prioridad, descripción completa, estado, y botones de acción]**

##### B. Asignarme

El botón verde asigna el ticket a ti.

1. Haz clic en el botón verde con ícono de persona

**[CAPTURA DE PANTALLA: Botón verde con ícono de persona y marca de verificación, resaltado]**

2. El ticket cambiará a **"En Proceso"**

**[CAPTURA DE PANTALLA: Mensaje "Ticket asignado correctamente" y estado cambiado a "En Proceso" en verde]**

##### C. Resolver Ticket

El botón azul resuelve el ticket.

1. Haz clic en el botón azul con ícono de marca de verificación

**[CAPTURA DE PANTALLA: Botón azul con ícono de check, resaltado]**

2. Escribe la **Solución Aplicada**

**[CAPTURA DE PANTALLA: Formulario de resolución con campo de texto grande para "Solución Aplicada" y ejemplo de texto "Se reinició el sistema y se actualizaron los drivers. El problema está resuelto."]**

3. Haz clic en **"Confirmar Resolución"**

4. El ticket cambiará a **"Resuelto"**

**[CAPTURA DE PANTALLA: Ticket con estado "Resuelto" en verde y mensaje de confirmación]**

---

# 7. Gestión de Equipos

## 7.1. Para Sistemas/IT

### 7.1.1. Ver Inventario

> **💻 Solo para Sistemas/IT y Administradores**

#### Acceso

1. Desde el Panel Sistemas, haz clic en **"Inventario"**

**[CAPTURA DE PANTALLA: Botón azul "Inventario" en accesos rápidos del dashboard de Sistemas, resaltado]**

#### Lista de Equipos

**[CAPTURA DE PANTALLA: Tabla completa de inventario mostrando columnas: Categoría, Marca/Modelo, Número de Serie, Código Inventario, Estado, Empleado Asignado, y Acciones, con 8 filas de datos visibles mostrando diferentes estados: Disponible (verde), Asignado (azul), En Reparación (amarillo)]**

#### Filtros

---

### 7.1.2. Asignar Equipo

> **💻 Solo para Sistemas/IT y Administradores**

Puedes filtrar por:
- **Estado**: Disponible, Asignado, En Reparación
- **Categoría**: Laptop, Monitor, Mouse, etc.
- **Búsqueda**: Código, marca o modelo

**[CAPTURA DE PANTALLA: Sección de filtros del inventario con selectores y campo de búsqueda]**

---

#### Seleccionar Equipo

1. En el inventario, encuentra un equipo con estado **"Disponible"**
2. Haz clic en **"Asignar"** (ícono de persona)

**[CAPTURA DE PANTALLA: Botón "Asignar" en la columna de acciones de un equipo disponible, resaltado]**

#### Formulario de Asignación

**[CAPTURA DE PANTALLA: Formulario de asignación mostrando: selector "Empleado" con búsqueda, campo "Fecha de Asignación" con fecha de hoy, campo "Condición al Entregar" con texto "Buen estado", campo "Observaciones" vacío, y botón "Confirmar Asignación"]**

1. **Empleado**: Busca y selecciona el empleado
2. **Fecha de Asignación**: Fecha de entrega
3. **Condición al Entregar**: Estado del equipo
4. **Observaciones**: Información adicional

#### Confirmar

---

## 7.2. Para Empleados

### 7.2.1. Ver Mis Equipos

> **👤 Para: Todos los usuarios**

1. Revisa la información
2. Haz clic en **"Confirmar Asignación"**

**[CAPTURA DE PANTALLA: Botón "Confirmar Asignación" resaltado]**

3. El equipo cambiará a estado **"Asignado"**

**[CAPTURA DE PANTALLA: Mensaje de confirmación y equipo con estado "Asignado" en la tabla]**

---


1. Desde el menú: **"Equipos"** → **"Mis Equipos"**

**[CAPTURA DE PANTALLA: Menú con opción "Mis Equipos" resaltada]**

2. Verás una lista de todos tus equipos asignados

**[CAPTURA DE PANTALLA: Lista de equipos asignados mostrando: Laptop HP ProBook, Monitor Dell 24", Mouse Logitech, con información de fecha de asignación y condición]**

---

# 8. Solución de Problemas

## Problema: No puedo iniciar sesión

**Solución**: Verifica usuario y contraseña. Si olvidaste tu contraseña, contacta a tu administrador o RH.

---

## Problema: Mi solicitud de vacaciones no aparece aprobada

**Solución**: Verifica que esté en estado "Aprobada por RH". Solo las aprobadas por RH pueden descargarse como PDF.

---

## Problema: Mi ticket no fue asignado

**Solución**: Los tickets son asignados por Sistemas/IT. Si es urgente, contacta directamente al área de Sistemas.

---

## Problema: No veo mis equipos

**Solución**: Verifica que los equipos estén en estado "Asignado" en el inventario. Si el problema persiste, contacta a Sistemas.

---

# 9. Contacto y Soporte

Para obtener ayuda:

- **Problemas técnicos**: Crea un ticket desde tu panel
- **Vacaciones**: Contacta a tu jefe o al área de RH
- **Equipos**: Contacta al área de Sistemas/IT
- **Acceso o permisos**: Contacta al Administrador

---

**Sistema GK - Grupo Keila**  
**Versión del Manual:** 1.0  
**Fecha:** 2024

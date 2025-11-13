# 📘 Manual de Usuario
## Sistema de Automatización de Recursos Humanos - Grupo Keila

---

## 📋 Tabla de Contenidos

1. [Introducción](#1-introducción)
2. [Acceso al Sistema](#2-acceso-al-sistema)
3. [Descripción de Módulos](#3-descripción-de-módulos)
4. [Procedimientos por Rol](#4-procedimientos-por-rol)
5. [Solución de Problemas](#5-solución-de-problemas-comunes)
6. [Glosario de Términos](#6-glosario-de-términos)
7. [Apéndices](#7-apéndices)

---

## 1. Introducción

### 1.1 Propósito del Manual

Este manual está diseñado para guiar a los usuarios del Sistema de Automatización de Recursos Humanos del Grupo Keila. Proporciona instrucciones detalladas sobre cómo utilizar todas las funcionalidades del sistema de manera eficiente y efectiva.

### 1.2 Descripción del Sistema

El Sistema de Automatización de Recursos Humanos es una plataforma web desarrollada con Django que permite gestionar de manera integral los recursos humanos de la organización. El sistema incluye módulos para:

- **Gestión de Usuarios y Perfiles**: Administración completa de empleados con diferentes roles y permisos
- **Gestión de Vacaciones**: Sistema de solicitudes y aprobaciones de vacaciones con flujo de trabajo automatizado
- **Gestión de Departamentos**: Organización de la estructura organizacional
- **Sistema de Tickets IT**: Gestión de solicitudes de soporte técnico
- **Gestión de Equipos**: Inventario y asignación de equipos tecnológicos

### 1.3 Roles del Sistema

El sistema cuenta con cinco tipos de perfiles de usuario, cada uno con permisos y funcionalidades específicas:

1. **Administrador (ADMIN)**: Acceso completo a todas las funcionalidades del sistema
2. **Recursos Humanos (RH)**: Gestión de empleados, departamentos y aprobación final de vacaciones
3. **Jefe de Área (JEFE_AREA)**: Aprobación de solicitudes de vacaciones de su departamento
4. **Sistemas/IT (SISTEMAS)**: Gestión de tickets y equipos tecnológicos
5. **Empleado (EMPLEADO)**: Acceso a funcionalidades básicas como solicitar vacaciones y ver su información

### 1.4 Requisitos del Sistema

- **Navegador Web**: Chrome, Firefox, Edge o Safari (versiones recientes)
- **Conexión a Internet**: Requerida para acceder al sistema
- **Resolución Mínima**: 1024x768 píxeles (recomendado 1920x1080)
- **JavaScript**: Debe estar habilitado en el navegador

---

## 2. Acceso al Sistema

### 2.1 URL del Sistema

El sistema está disponible en la siguiente dirección:
```
http://[dirección-del-servidor]/
```

### 2.2 Página de Inicio de Sesión

Al acceder al sistema, se mostrará la página de inicio de sesión con los siguientes campos:

- **Usuario**: Nombre de usuario asignado por el administrador
- **Contraseña**: Contraseña proporcionada por el administrador

### 2.3 Proceso de Inicio de Sesión

1. Ingrese su **nombre de usuario** en el campo correspondiente
2. Ingrese su **contraseña** en el campo correspondiente
3. Haga clic en el botón **"Iniciar Sesión"**
4. El sistema lo redirigirá automáticamente al dashboard correspondiente según su perfil

### 2.4 Recuperación de Contraseña

Si ha olvidado su contraseña, contacte al administrador del sistema o al área de Recursos Humanos para su restablecimiento.

### 2.5 Cerrar Sesión

Para cerrar sesión de forma segura:

1. Haga clic en su nombre de usuario en la esquina superior derecha
2. Seleccione la opción **"Cerrar Sesión"**
3. Confirme la acción si se le solicita

**⚠️ Importante**: Siempre cierre sesión cuando termine de usar el sistema, especialmente si está en una computadora compartida.

---

## 3. Descripción de Módulos

### 3.1 Módulo de Gestión de Usuarios y Perfiles

Este módulo permite administrar la información de todos los empleados del sistema.

#### 3.1.1 Funcionalidades Principales

- Crear nuevos usuarios y perfiles
- Editar información de empleados existentes
- Visualizar lista completa de empleados
- Filtrar y buscar empleados por diferentes criterios
- Gestionar tipos de perfil y permisos

#### 3.1.2 Información del Perfil de Usuario

Cada perfil contiene la siguiente información:

- **Datos Personales**:
  - Nombre completo
  - Fecha de nacimiento
  - Teléfono
  - Dirección

- **Datos Laborales**:
  - Número de empleado
  - Tipo de perfil (rol)
  - Departamento
  - Puesto
  - Fecha de contratación
  - Supervisor
  - Salario

- **Información de Vacaciones**:
  - Días de vacaciones anuales
  - Días de vacaciones usados
  - Días de vacaciones disponibles
  - Días acumulados del año anterior

### 3.2 Módulo de Gestión de Vacaciones

Sistema completo para la solicitud, aprobación y seguimiento de vacaciones.

#### 3.2.1 Tipos de Vacaciones

El sistema maneja tres tipos de vacaciones:

1. **Vacación Normal**: Para empleados con antigüedad de 1 año o más
2. **Vacación Extraordinaria**: Para empleados con menos de 1 año de antigüedad (hasta 5 días)
3. **Vacación de Emergencia**: Para situaciones especiales

#### 3.2.2 Flujo de Aprobación

El flujo de aprobación de vacaciones sigue estos pasos:

```
1. Empleado solicita vacaciones
   ↓
2. Jefe de Área revisa y aprueba/rechaza
   ↓
3. Recursos Humanos revisa y aprueba/rechaza (aprobación final)
   ↓
4. Sistema actualiza días de vacaciones usados
   ↓
5. Se genera formulario PDF (opcional)
```

#### 3.2.3 Cálculo de Días de Vacaciones

El sistema calcula automáticamente los días de vacaciones según la antigüedad del empleado:

| Años de Antigüedad | Días de Vacaciones Anuales |
|-------------------|---------------------------|
| Menos de 1 año    | 12 días (proporcional)    |
| 1 año             | 12 días                   |
| 2 años            | 14 días                   |
| 3 años            | 16 días                   |
| 4 años            | 18 días                   |
| 5 años            | 20 días                   |
| 6-10 años         | 22 días                   |
| 11-15 años        | 24 días                   |
| 16-20 años        | 26 días                   |
| 21-25 años        | 28 días                   |
| 26-30 años        | 30 días                   |
| 31+ años          | 32 días                   |

**Nota**: Los domingos no se cuentan como días laborables en el cálculo de vacaciones.

### 3.3 Módulo de Gestión de Departamentos

Permite organizar la estructura organizacional de la empresa.

#### 3.3.1 Funcionalidades

- Crear nuevos departamentos
- Editar información de departamentos existentes
- Asignar jefes de departamento
- Ver lista de empleados por departamento
- Activar/desactivar departamentos

### 3.4 Módulo de Sistema de Tickets IT

Sistema de gestión de solicitudes de soporte técnico.

#### 3.4.1 Tipos de Tickets

- **Hardware**: Problemas con equipos físicos
- **Software**: Problemas con aplicaciones o sistemas
- **Red/Conectividad**: Problemas de red o conexión
- **Acceso/Permisos**: Solicitudes de acceso o permisos
- **Otro**: Otros tipos de problemas

#### 3.4.2 Prioridades

- **Baja**: Problemas menores que no afectan el trabajo
- **Media**: Problemas que afectan parcialmente el trabajo
- **Alta**: Problemas que afectan significativamente el trabajo
- **Urgente**: Problemas críticos que requieren atención inmediata

#### 3.4.3 Estados de Tickets

- **Pendiente**: Ticket creado, esperando asignación
- **En Proceso**: Ticket asignado a un técnico, en resolución
- **Resuelto**: Ticket solucionado
- **Cancelado**: Ticket cancelado por el solicitante o técnico

### 3.5 Módulo de Gestión de Equipos

Sistema de inventario y asignación de equipos tecnológicos.

#### 3.5.1 Categorías de Equipos

- Laptops
- Computadoras de escritorio
- Monitores
- Tablets
- Teléfonos móviles
- Impresoras
- Otros dispositivos

#### 3.5.2 Estados de Equipos

- **Disponible**: Equipo disponible para asignación
- **Asignado**: Equipo asignado a un empleado
- **En Reparación**: Equipo en mantenimiento o reparación
- **Dado de Baja**: Equipo retirado del inventario

#### 3.5.3 Información de Equipos

Cada equipo registra:
- Categoría
- Marca y modelo
- Número de serie
- Código de inventario
- Fecha de adquisición
- Estado actual
- Observaciones

---

## 4. Procedimientos por Rol

### 4.1 Procedimientos para Empleados

#### 4.1.1 Acceder al Dashboard

1. Inicie sesión en el sistema
2. Será redirigido automáticamente al dashboard de empleado
3. El dashboard muestra:
   - Días de vacaciones disponibles
   - Solicitudes de vacaciones recientes
   - Equipos asignados
   - Tickets de soporte recientes

#### 4.1.2 Solicitar Vacaciones

**Paso a paso:**

1. Desde el dashboard, haga clic en **"Solicitar Vacaciones"** o acceda al menú **"Vacaciones"**
2. Complete el formulario:
   - **Tipo de Vacación**: Seleccione Normal, Extraordinaria o Emergencia
   - **Fecha de Inicio**: Seleccione la fecha de inicio de sus vacaciones
   - **Fecha de Fin**: Seleccione la fecha de fin de sus vacaciones
   - **Motivo**: Describa el motivo de su solicitud
3. El sistema calculará automáticamente los días solicitados (excluyendo domingos)
4. Revise la información y haga clic en **"Enviar Solicitud"**
5. Recibirá un mensaje de confirmación

**Notas importantes:**
- Solo puede solicitar vacaciones normales si tiene 1 año o más de antigüedad
- Los empleados con menos de 1 año pueden solicitar hasta 5 días extraordinarios
- El sistema no permite solicitar más días de los disponibles

#### 4.1.3 Ver Mis Vacaciones

1. Acceda al menú **"Vacaciones"** → **"Mis Vacaciones"**
2. Verá una lista de todas sus solicitudes con:
   - Fechas de inicio y fin
   - Días solicitados
   - Estado actual
   - Fecha de solicitud
3. Puede hacer clic en cualquier solicitud para ver más detalles

#### 4.1.4 Crear un Ticket de Soporte

**Paso a paso:**

1. Acceda al menú **"Tickets"** → **"Crear Ticket"**
2. Complete el formulario:
   - **Tipo**: Seleccione el tipo de problema
   - **Prioridad**: Seleccione la urgencia
   - **Área**: Especifique el área afectada (opcional)
   - **Dispositivo**: Indique el dispositivo afectado (opcional)
   - **Descripción**: Describa detalladamente el problema
3. Haga clic en **"Crear Ticket"**
4. Recibirá un código de ticket único (ejemplo: TKT-20241215-001)

#### 4.1.5 Ver Mis Tickets

1. Acceda al menú **"Tickets"** → **"Mis Tickets"**
2. Verá una lista de todos sus tickets con:
   - Código del ticket
   - Tipo y prioridad
   - Estado actual
   - Fecha de creación
   - Técnico asignado (si aplica)
3. Haga clic en un ticket para ver detalles completos y el estado de la resolución

#### 4.1.6 Ver Mis Equipos Asignados

1. Acceda al menú **"Equipos"** → **"Mis Equipos"**
2. Verá una lista de todos los equipos asignados a usted con:
   - Categoría y descripción del equipo
   - Código de inventario
   - Fecha de asignación
   - Condición al momento de la asignación
3. También puede ver el historial de equipos previamente asignados

#### 4.1.7 Ver Mi Perfil

1. Haga clic en su nombre de usuario en la esquina superior derecha
2. Seleccione **"Mi Perfil"**
3. Verá toda su información personal y laboral
4. Puede ver (pero no editar) su información de vacaciones y antigüedad

### 4.2 Procedimientos para Jefes de Área

#### 4.2.1 Acceder al Dashboard de Jefe

1. Inicie sesión con un perfil de Jefe de Área
2. Será redirigido al dashboard de jefe
3. El dashboard muestra:
   - Solicitudes de vacaciones pendientes de aprobación
   - Estadísticas de empleados en su departamento
   - Solicitudes aprobadas este mes

#### 4.2.2 Aprobar/Rechazar Solicitudes de Vacaciones

**Paso a paso:**

1. Desde el dashboard, verá las solicitudes pendientes
2. Haga clic en **"Ver Solicitud"** o acceda a **"Vacaciones"** → **"Solicitudes Pendientes"**
3. Revise los detalles de la solicitud:
   - Empleado solicitante
   - Fechas de vacaciones
   - Días solicitados
   - Motivo
4. Seleccione una acción:
   - **Aprobar**: La solicitud pasará a Recursos Humanos para aprobación final
   - **Rechazar**: La solicitud será rechazada y el empleado será notificado
5. Agregue un comentario (opcional pero recomendado)
6. Haga clic en **"Confirmar"**
7. El sistema actualizará el estado y notificará al empleado

#### 4.2.3 Ver Todas las Solicitudes

1. Acceda a **"Vacaciones"** → **"Todas las Solicitudes"**
2. Puede filtrar por:
   - Estado (Pendiente, Aprobada, Rechazada)
   - Empleado (búsqueda por nombre)
3. Haga clic en cualquier solicitud para ver detalles completos

#### 4.2.4 Ver Empleados del Departamento

1. Desde el dashboard, puede ver estadísticas de empleados
2. Acceda a **"Empleados"** para ver la lista completa
3. Puede filtrar y buscar empleados según sus necesidades

### 4.3 Procedimientos para Recursos Humanos

#### 4.3.1 Acceder al Dashboard de RH

1. Inicie sesión con un perfil de RH
2. Será redirigido al dashboard de RH
3. El dashboard muestra:
   - Solicitudes de vacaciones pendientes de aprobación final
   - Estadísticas de aprobaciones del mes
   - Resumen de actividades

#### 4.3.2 Crear un Nuevo Usuario

**Paso a paso:**

1. Acceda a **"Usuarios"** → **"Gestionar Usuarios"**
2. Haga clic en el botón **"Crear Nuevo Usuario"**
3. Complete el formulario con la siguiente información:

   **Datos de Usuario:**
   - Nombre de usuario (único)
   - Contraseña temporal
   - Nombre y apellidos
   - Correo electrónico

   **Datos del Perfil:**
   - Tipo de perfil (Empleado, Jefe de Área, RH, Sistemas, Administrador)
   - Número de empleado (único)
   - Departamento
   - Puesto
   - Fecha de contratación
   - Supervisor (opcional)
   - Teléfono
   - Fecha de nacimiento (opcional)
   - Dirección (opcional)
   - Salario (opcional)

4. Revise la información y haga clic en **"Crear Usuario"**
5. El sistema creará el usuario y le asignará los días de vacaciones según su antigüedad

#### 4.3.3 Editar Perfil de Usuario

**Paso a paso:**

1. Acceda a **"Usuarios"** → **"Gestionar Usuarios"**
2. Busque el usuario que desea editar
3. Haga clic en **"Editar"** junto al nombre del usuario
4. Modifique los campos necesarios
5. Haga clic en **"Guardar Cambios"**

**Nota**: Puede editar información personal, laboral y de vacaciones.

#### 4.3.4 Aprobar/Rechazar Solicitudes de Vacaciones (Aprobación Final)

**Paso a paso:**

1. Desde el dashboard, verá las solicitudes pendientes de aprobación final
2. Haga clic en **"Ver Solicitud"** o acceda a **"Vacaciones"** → **"Solicitudes Pendientes"**
3. Revise los detalles completos:
   - Información del empleado
   - Fechas y días solicitados
   - Aprobación del jefe
   - Comentarios del jefe
   - Días disponibles del empleado
4. Seleccione una acción:
   - **Aprobar**: La solicitud será aprobada y los días se descontarán automáticamente
   - **Rechazar**: La solicitud será rechazada
5. Agregue un comentario (opcional)
6. Haga clic en **"Confirmar"**
7. Si aprueba, puede generar el formulario PDF haciendo clic en **"Descargar Formulario"**

#### 4.3.5 Generar Formulario PDF de Vacaciones

1. Después de aprobar una solicitud, verá un enlace **"Descargar Formulario de Vacaciones"**
2. Haga clic en el enlace
3. Se generará y descargará un PDF con el formulario oficial de vacaciones
4. El formulario incluye:
   - Información del empleado
   - Fechas de vacaciones
   - Días solicitados
   - Fecha de presentación (calculada automáticamente, excluyendo domingos)
   - Firma del jefe y RH

#### 4.3.6 Gestionar Departamentos

**Crear un Departamento:**

1. Acceda a **"Departamentos"** → **"Gestionar Departamentos"**
2. Haga clic en **"Crear Departamento"**
3. Complete el formulario:
   - Nombre del departamento
   - Descripción (opcional)
   - Jefe de departamento (opcional, debe ser un perfil de Jefe de Área)
4. Haga clic en **"Crear Departamento"**

**Editar un Departamento:**

1. Acceda a **"Departamentos"** → **"Gestionar Departamentos"**
2. Haga clic en **"Editar"** junto al departamento
3. Modifique la información necesaria
4. Haga clic en **"Guardar Cambios"**

### 4.4 Procedimientos para Personal de Sistemas/IT

#### 4.4.1 Acceder al Dashboard de Sistemas

1. Inicie sesión con un perfil de Sistemas
2. Será redirigido al dashboard de sistemas
3. El dashboard muestra:
   - Tickets pendientes
   - Tickets en proceso
   - Tickets resueltos hoy
   - Equipos disponibles y asignados
   - Equipos en reparación

#### 4.4.2 Gestionar Tickets

**Ver Todos los Tickets:**

1. Acceda a **"Sistemas"** → **"Gestionar Tickets"**
2. Verá una lista de todos los tickets del sistema
3. Puede filtrar por estado (Pendiente, En Proceso, Resuelto, Cancelado)

**Asignar un Ticket:**

1. Desde la lista de tickets, haga clic en **"Asignar"** en el ticket deseado
2. El ticket se asignará automáticamente a usted
3. El estado cambiará a **"En Proceso"**

**Resolver un Ticket:**

**Paso a paso:**

1. Acceda al detalle del ticket haciendo clic en el código
2. Revise la información del problema
3. Haga clic en **"Resolver Ticket"**
4. Complete el formulario:
   - **Estado**: Seleccione Resuelto o Cancelado
   - **Solución Aplicada**: Describa detalladamente la solución
5. Haga clic en **"Guardar"**
6. El sistema registrará la fecha de resolución automáticamente

#### 4.4.3 Gestionar Inventario de Equipos

**Ver Inventario:**

1. Acceda a **"Sistemas"** → **"Inventario de Equipos"**
2. Verá una lista completa de todos los equipos
3. Puede filtrar por estado (Disponible, Asignado, En Reparación, Dado de Baja)

**Agregar un Nuevo Equipo:**

**Paso a paso:**

1. Acceda a **"Sistemas"** → **"Inventario de Equipos"**
2. Haga clic en **"Agregar Equipo"**
3. Complete el formulario:
   - **Categoría**: Seleccione la categoría del equipo
   - **Marca**: Ingrese la marca
   - **Modelo**: Ingrese el modelo
   - **Número de Serie**: Ingrese el número de serie (único)
   - **Código de Inventario**: Ingrese el código de inventario (único)
   - **Estado**: Seleccione el estado inicial (generalmente "Disponible")
   - **Fecha de Adquisición**: Seleccione la fecha
   - **Observaciones**: Agregue cualquier observación relevante
4. Haga clic en **"Guardar Equipo"**

**Asignar un Equipo a un Empleado:**

**Paso a paso:**

1. Acceda a **"Sistemas"** → **"Asignar Equipo"**
2. Complete el formulario:
   - **Equipo**: Seleccione el equipo a asignar (solo equipos disponibles)
   - **Empleado**: Seleccione el empleado
   - **Condición al Entregar**: Describa el estado del equipo al momento de la asignación
   - **Observaciones**: Agregue cualquier observación
3. La fecha de asignación se registrará automáticamente
4. Haga clic en **"Asignar Equipo"**
5. El estado del equipo cambiará automáticamente a **"Asignado"**

**Registrar Devolución de Equipo:**

**Paso a paso:**

1. Acceda a **"Sistemas"** → **"Inventario de Equipos"**
2. Busque el equipo asignado que se va a devolver
3. Haga clic en **"Devolver"** junto al equipo
4. Complete el formulario:
   - **Fecha de Devolución**: Seleccione la fecha
   - **Condición al Devolver**: Describa el estado del equipo al momento de la devolución
   - **Observaciones**: Agregue cualquier observación relevante
5. Haga clic en **"Registrar Devolución"**
6. El estado del equipo cambiará automáticamente a **"Disponible"**

### 4.5 Procedimientos para Administradores

#### 4.5.1 Acceder al Dashboard de Administrador

1. Inicie sesión con un perfil de Administrador
2. Será redirigido al dashboard de administrador
3. El dashboard muestra una vista completa del sistema:
   - Estadísticas de empleados y departamentos
   - Estadísticas de vacaciones
   - Estadísticas de tickets IT
   - Estadísticas de equipos
   - Solicitudes y tickets recientes

#### 4.5.2 Funcionalidades de Administrador

Los administradores tienen acceso completo a todas las funcionalidades del sistema:

- **Gestión de Usuarios**: Crear, editar y gestionar todos los usuarios
- **Gestión de Vacaciones**: Ver y gestionar todas las solicitudes
- **Gestión de Departamentos**: Crear y editar departamentos
- **Gestión de Tickets**: Ver y gestionar todos los tickets
- **Gestión de Equipos**: Gestionar inventario completo
- **Estadísticas**: Acceso a todas las estadísticas del sistema

Los procedimientos son similares a los descritos para RH y Sistemas, pero con acceso completo a todas las funcionalidades.

---

## 5. Solución de Problemas Comunes

### 5.1 Problemas de Acceso

#### No puedo iniciar sesión

**Posibles causas y soluciones:**

1. **Credenciales incorrectas**
   - Verifique que está ingresando el nombre de usuario y contraseña correctos
   - Asegúrese de que no hay espacios adicionales
   - Verifique que el bloqueo de mayúsculas (Caps Lock) no esté activado

2. **Usuario desactivado**
   - Contacte al administrador o al área de RH para verificar el estado de su cuenta

3. **Problemas de conexión**
   - Verifique su conexión a Internet
   - Intente recargar la página (F5 o Ctrl+R)

#### Mensaje de "Permiso Denegado" (Error 403)

**Causa**: Está intentando acceder a una funcionalidad que no está permitida para su perfil.

**Solución**: 
- Verifique que está usando la funcionalidad correcta para su rol
- Si necesita acceso adicional, contacte al administrador

### 5.2 Problemas con Solicitudes de Vacaciones

#### No puedo solicitar vacaciones

**Posibles causas:**

1. **No tiene días disponibles**
   - Verifique sus días disponibles en el dashboard
   - Los días se calculan automáticamente según su antigüedad

2. **No cumple con la antigüedad mínima**
   - Para vacaciones normales, necesita 1 año o más de antigüedad
   - Si tiene menos de 1 año, puede solicitar vacaciones extraordinarias (hasta 5 días)

3. **Fechas inválidas**
   - La fecha de fin debe ser posterior a la fecha de inicio
   - No puede solicitar vacaciones en fechas pasadas

**Solución**: 
- Revise su información de vacaciones en el dashboard
- Contacte a RH si cree que hay un error en sus días disponibles

#### La solicitud no aparece en el sistema

**Causa**: Puede haber un error al guardar la solicitud.

**Solución**:
1. Verifique que completó todos los campos requeridos
2. Intente crear la solicitud nuevamente
3. Si el problema persiste, contacte al área de sistemas

#### Los días calculados no son correctos

**Causa**: El sistema calcula días laborables excluyendo domingos.

**Solución**:
- El cálculo es automático y correcto según las reglas del sistema
- Los domingos no se cuentan como días laborables
- Si tiene dudas, contacte a RH

### 5.3 Problemas con Tickets

#### No puedo crear un ticket

**Posibles causas:**

1. **Campos requeridos incompletos**
   - Asegúrese de completar todos los campos marcados con asterisco (*)

2. **Problema de conexión**
   - Verifique su conexión a Internet
   - Intente recargar la página

**Solución**: 
- Complete todos los campos requeridos
- Intente crear el ticket nuevamente
- Si el problema persiste, contacte al área de sistemas

#### No veo actualizaciones en mi ticket

**Causa**: El técnico puede estar trabajando en el ticket pero aún no lo ha actualizado.

**Solución**:
- Los tickets se actualizan cuando el técnico registra cambios
- Puede contactar al área de sistemas para consultar el estado

### 5.4 Problemas con Equipos

#### No veo mis equipos asignados

**Causa**: Puede que no tenga equipos asignados actualmente.

**Solución**:
- Verifique en la sección "Mis Equipos"
- Si debería tener equipos asignados y no los ve, contacte al área de sistemas

### 5.5 Problemas Técnicos Generales

#### La página no carga correctamente

**Soluciones:**

1. **Limpiar caché del navegador**
   - Chrome/Edge: Ctrl+Shift+Delete
   - Firefox: Ctrl+Shift+Delete
   - Safari: Cmd+Option+E

2. **Recargar la página**
   - F5 o Ctrl+R (Windows/Linux)
   - Cmd+R (Mac)

3. **Probar otro navegador**
   - Si el problema persiste, intente con otro navegador

4. **Verificar JavaScript**
   - Asegúrese de que JavaScript esté habilitado en su navegador

#### Los datos no se guardan

**Soluciones:**

1. **Verificar conexión a Internet**
   - Asegúrese de tener conexión estable

2. **Completar todos los campos requeridos**
   - Los campos marcados con asterisco (*) son obligatorios

3. **Verificar formato de datos**
   - Fechas deben estar en formato correcto
   - Números deben ser válidos

4. **Recargar la página e intentar nuevamente**

### 5.6 Contacto para Soporte

Si después de intentar las soluciones anteriores el problema persiste:

1. **Contacte al área de Sistemas/IT**:
   - Cree un ticket en el sistema
   - Describa detalladamente el problema
   - Incluya capturas de pantalla si es posible

2. **Contacte al área de Recursos Humanos**:
   - Para problemas relacionados con usuarios, vacaciones o departamentos

3. **Contacte al Administrador del Sistema**:
   - Para problemas críticos o de acceso

---

## 6. Glosario de Términos

### A

**Administrador (ADMIN)**: Perfil de usuario con acceso completo a todas las funcionalidades del sistema.

**Antigüedad**: Tiempo que un empleado ha trabajado en la empresa, calculado desde la fecha de contratación.

**Aprobación Final**: Última etapa del proceso de aprobación de vacaciones, realizada por Recursos Humanos.

**Asignación de Equipo**: Proceso de asignar un equipo tecnológico a un empleado.

### B

**Base de Datos**: Almacenamiento centralizado de toda la información del sistema.

### C

**Código de Inventario**: Identificador único asignado a cada equipo en el inventario.

**Código de Ticket**: Identificador único asignado a cada ticket de soporte (formato: TKT-YYYYMMDD-XXX).

### D

**Dashboard**: Panel principal que muestra información resumida y estadísticas según el perfil del usuario.

**Departamento**: Unidad organizacional de la empresa que agrupa empleados por área de trabajo.

**Días Acumulados**: Días de vacaciones no usados del año anterior que se acumulan para el año actual.

**Días Disponibles**: Días de vacaciones que un empleado puede usar actualmente.

**Días Laborables**: Días de la semana excluyendo domingos (lunes a sábado).

### E

**Empleado (EMPLEADO)**: Perfil de usuario básico con acceso a funcionalidades de consulta y solicitud de vacaciones.

**Equipo**: Dispositivo tecnológico registrado en el inventario del sistema (laptops, computadoras, etc.).

**Estado**: Condición actual de una solicitud, ticket o equipo (ej: Pendiente, Aprobado, Asignado).

### F

**Fecha de Contratación**: Fecha en que un empleado comenzó a trabajar en la empresa.

**Fecha de Presentación**: Fecha en que un empleado debe regresar al trabajo después de sus vacaciones (calculada automáticamente, excluyendo domingos).

**Formulario PDF**: Documento oficial generado automáticamente cuando se aprueba una solicitud de vacaciones.

### G

**Gestión**: Administración y control de recursos, procesos o información en el sistema.

### H

**Historial**: Registro de todas las acciones y cambios realizados en el sistema.

### I

**Inventario**: Lista completa de todos los equipos tecnológicos registrados en el sistema.

### J

**Jefe de Área (JEFE_AREA)**: Perfil de usuario con permisos para aprobar solicitudes de vacaciones de su departamento.

### N

**Número de Empleado**: Identificador único asignado a cada empleado en el sistema.

### P

**Perfil**: Información completa de un usuario en el sistema, incluyendo datos personales, laborales y de vacaciones.

**Permisos**: Autorizaciones que determinan qué funcionalidades puede usar cada tipo de perfil.

**Prioridad**: Nivel de urgencia asignado a un ticket de soporte (Baja, Media, Alta, Urgente).

### R

**Recursos Humanos (RH)**: Perfil de usuario con permisos para gestionar empleados, departamentos y aprobar vacaciones.

**Reset de Vacaciones**: Proceso anual que reinicia los contadores de días de vacaciones usados.

### S

**Sistemas/IT (SISTEMAS)**: Perfil de usuario con permisos para gestionar tickets de soporte y equipos tecnológicos.

**Solicitud de Vacaciones**: Petición formal de un empleado para tomar días de descanso.

**Supervisor**: Empleado que supervisa a otro empleado en la estructura organizacional.

### T

**Ticket**: Solicitud de soporte técnico creada por un empleado para resolver un problema tecnológico.

**Tipo de Perfil**: Clasificación del usuario que determina sus permisos y funcionalidades (Empleado, Jefe, RH, Sistemas, Admin).

**Tipo de Vacación**: Clasificación de la solicitud (Normal, Extraordinaria, Emergencia).

### U

**Usuario**: Persona que tiene acceso al sistema con credenciales de inicio de sesión.

### V

**Vacación Extraordinaria**: Tipo de vacación disponible para empleados con menos de 1 año de antigüedad (hasta 5 días).

**Vacación Normal**: Tipo de vacación disponible para empleados con 1 año o más de antigüedad.

**Vacación de Emergencia**: Tipo de vacación para situaciones especiales.

---

## 7. Apéndices

### 7.1 Tabla de Días de Vacaciones por Antigüedad

| Años de Antigüedad | Días Anuales | Acumulación Mensual |
|-------------------|--------------|---------------------|
| < 1 año           | 12 (proporcional) | 1.0 día/mes |
| 1 año             | 12           | 1.0 día/mes |
| 2 años            | 14           | 1.17 días/mes |
| 3 años            | 16           | 1.33 días/mes |
| 4 años            | 18           | 1.5 días/mes |
| 5 años            | 20           | 1.67 días/mes |
| 6-10 años         | 22           | 1.83 días/mes |
| 11-15 años        | 24           | 2.0 días/mes |
| 16-20 años        | 26           | 2.17 días/mes |
| 21-25 años        | 28           | 2.33 días/mes |
| 26-30 años        | 30           | 2.5 días/mes |
| 31+ años          | 32           | 2.67 días/mes |

### 7.2 Flujo de Aprobación de Vacaciones (Diagrama)

```
┌─────────────┐
│  EMPLEADO   │
│  Solicita   │
│  Vacaciones │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ JEFE DE     │
│ ÁREA        │
│ Revisa y    │
│ Aprueba/    │
│ Rechaza     │
└──────┬──────┘
       │
       ▼ (Si Aprobado)
┌─────────────┐
│ RECURSOS    │
│ HUMANOS     │
│ Aprobación  │
│ Final       │
└──────┬──────┘
       │
       ▼ (Si Aprobado)
┌─────────────┐
│  SISTEMA    │
│  Actualiza  │
│  Días       │
│  Usados     │
└─────────────┘
```

### 7.3 Estados de Solicitudes de Vacaciones

| Estado | Descripción |
|--------|-------------|
| PENDIENTE_JEFE | Solicitud creada, esperando aprobación del jefe |
| APROBADO_JEFE | Aprobada por jefe, esperando aprobación de RH |
| RECHAZADO_JEFE | Rechazada por jefe |
| PENDIENTE_RH | Aprobada por jefe, esperando aprobación final de RH |
| APROBADO_RH | Aprobada completamente, días descontados |
| RECHAZADO_RH | Rechazada por RH |
| CANCELADO | Cancelada por el empleado |

### 7.4 Estados de Tickets

| Estado | Descripción |
|--------|-------------|
| PENDIENTE | Ticket creado, esperando asignación |
| EN_PROCESO | Ticket asignado a un técnico, en resolución |
| RESUELTO | Ticket solucionado |
| CANCELADO | Ticket cancelado |

### 7.5 Estados de Equipos

| Estado | Descripción |
|--------|-------------|
| DISPONIBLE | Equipo disponible para asignación |
| ASIGNADO | Equipo asignado a un empleado |
| EN_REPARACION | Equipo en mantenimiento o reparación |
| DADO_DE_BAJA | Equipo retirado del inventario |

### 7.6 Tipos de Tickets

| Tipo | Descripción |
|------|-------------|
| HARDWARE | Problemas con equipos físicos |
| SOFTWARE | Problemas con aplicaciones o sistemas |
| RED | Problemas de red o conectividad |
| ACCESO | Solicitudes de acceso o permisos |
| OTRO | Otros tipos de problemas |

### 7.7 Prioridades de Tickets

| Prioridad | Tiempo de Respuesta Esperado | Descripción |
|-----------|------------------------------|-------------|
| URGENTE | Inmediato | Problemas críticos que detienen el trabajo |
| ALTA | < 4 horas | Problemas que afectan significativamente el trabajo |
| MEDIA | < 24 horas | Problemas que afectan parcialmente el trabajo |
| BAJA | < 72 horas | Problemas menores |

### 7.8 Comandos de Gestión (Para Administradores)

El sistema incluye comandos de gestión que pueden ejecutarse desde la línea de comandos:

**Actualizar Vacaciones:**
```bash
python manage.py actualizar_vacaciones
```

**Acumulación Mensual:**
```bash
python manage.py acumular_mensual
```

**Reset de Vacaciones:**
```bash
python manage.py reset_vacaciones
```

**Reporte de Vacaciones:**
```bash
python manage.py reporte_vacaciones
```

### 7.9 Preguntas Frecuentes (FAQ)

**P: ¿Puedo cancelar una solicitud de vacaciones después de enviarla?**
R: Las solicitudes pueden ser canceladas por el empleado antes de ser aprobadas por RH. Una vez aprobada por RH, debe contactar al área de RH para cancelación.

**P: ¿Qué pasa si uso todos mis días de vacaciones?**
R: No podrá solicitar más vacaciones hasta que se acumulen nuevos días según su antigüedad.

**P: ¿Los días acumulados del año anterior tienen límite?**
R: No, todos los días no usados del año anterior se acumulan sin límite.

**P: ¿Puedo ver el historial de mis solicitudes de vacaciones?**
R: Sí, puede ver todas sus solicitudes en la sección "Mis Vacaciones".

**P: ¿Cómo sé quién está revisando mi ticket?**
R: En el detalle del ticket puede ver el técnico asignado y el estado actual.

**P: ¿Puedo editar mi información personal?**
R: Depende de su perfil. Los empleados pueden ver su información pero no editarla. Contacte a RH para cambios.

**P: ¿Qué hago si mi equipo asignado tiene problemas?**
R: Cree un ticket de tipo "Hardware" describiendo el problema del equipo.

**P: ¿Cuánto tiempo tarda en resolverse un ticket?**
R: Depende de la prioridad. Los tickets urgentes se atienden inmediatamente, mientras que los de baja prioridad pueden tardar hasta 72 horas.

---

## 📞 Información de Contacto

Para soporte técnico o consultas sobre el sistema:

- **Área de Sistemas/IT**: [correo o teléfono]
- **Recursos Humanos**: [correo o teléfono]
- **Administrador del Sistema**: [correo o teléfono]

---

## 📝 Notas Finales

Este manual se actualiza periódicamente para reflejar cambios y mejoras en el sistema. La versión más reciente siempre estará disponible en el sistema.

**Última actualización**: Diciembre 2024

**Versión del Manual**: 1.0

---

*Sistema de Automatización de Recursos Humanos - Grupo Keila*
*Desarrollado con Django*


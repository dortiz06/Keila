# Instrucciones para Redactar: Sección 3 - Gestión y Atención de Tickets de Soporte

## Cuándo Proceder

**Proceder con esta sección cuando:**
- ✅ Ya tienes la Sección 1 (Introducción) completa
- ✅ Ya tienes la Sección 2 (Tipos de Usuario y Sus Funciones) completa
- ✅ Ya tienes la Sección 3 (Acceso al Sistema) completa (si aplica)
- ✅ Tienes acceso a capturas de pantalla del módulo de tickets
- ✅ Entiendes el flujo completo de creación y gestión de tickets

---

## Estructura de la Sección

### Título Principal
```markdown
# 3. Gestión y Atención de Tickets de Soporte
```

### Subsecciones Requeridas

La sección debe dividirse en dos partes principales:

1. **Para Empleados** (y otros usuarios que pueden crear tickets)
2. **Para Sistemas/IT** (personal que gestiona y resuelve tickets)

---

## Estructura Detallada

```markdown
# 3. Gestión y Atención de Tickets de Soporte

## 3.1. Para Empleados (Crear Tickets)

### 3.1.1. Acceso al Módulo
[Instrucciones de acceso]

### 3.1.2. Crear un Nuevo Ticket
[Pasos para crear ticket]

### 3.1.3. Ver Mis Tickets
[Pasos para ver tickets propios]

### 3.1.4. Ver Detalles de un Ticket
[Pasos para ver detalles]

## 3.2. Para Sistemas/IT (Gestionar Tickets)

### 3.2.1. Acceso al Módulo
[Instrucciones de acceso]

### 3.2.2. Lista General de Tickets
[Descripción de la vista]

### 3.2.3. Filtros y Búsqueda
[Uso de filtros]

### 3.2.4. Acciones de Gestión
- A. Ver Detalles
- B. Asignarme
- C. Resolver Ticket
```

---

## Contenido Específico por Subsección

### 3.1.1. Acceso al Módulo (Para Empleados)

**Qué incluir:**
- Cómo llegar al formulario de crear ticket
- Dos formas de acceso (desde panel y desde menú)
- Captura de pantalla del botón o enlace

**Formato:**
```markdown
### 3.1.1. Acceso al Módulo

> **👤 Para**: Empleados, Jefes, RH, Sistemas, Administradores  
> **⏱️ Tiempo estimado**: 1 minuto

1. Desde tu panel de empleado, haz clic en el botón **"Generar Ticket"**

**[CAPTURA DE PANTALLA: Panel de empleado mostrando en la parte superior derecha el botón verde "Generar Ticket" con ícono de ticket, resaltado con un círculo rojo]**

O desde el menú principal, selecciona **"Tickets"** → **"Crear Ticket"**

**[CAPTURA DE PANTALLA: Menú lateral con la opción "Tickets" expandida mostrando "Crear Ticket" resaltada]**
```

---

### 3.1.2. Crear un Nuevo Ticket

**Qué incluir:**
- Descripción de cada campo del formulario
- Explicación de tipos de ticket
- Explicación de prioridades
- Ejemplo de descripción del problema
- Captura del formulario completo
- Captura del botón de enviar

**Formato:**
```markdown
### 3.1.2. Crear un Nuevo Ticket

Verás un formulario para reportar tu problema técnico:

**[CAPTURA DE PANTALLA: Formulario completo de crear ticket mostrando todos los campos: selector "Tipo" con opciones desplegadas (Hardware, Software, Red/Conectividad, Acceso/Permisos, Otro), selector "Prioridad" con opciones (Baja, Media, Alta, Urgente), campo "Área" con texto de ejemplo "Ventas", campo "Dispositivo Afectado" con texto "Laptop HP ProBook", campo "Descripción del Problema" con texto de ejemplo "La laptop no enciende, muestra pantalla azul al iniciar", y el botón "Crear Ticket" en la parte inferior]**

#### Campos del Formulario

1. **Tipo de Problema**: Selecciona el tipo
   - **Hardware**: Problemas con computadoras, impresoras, monitores, etc.
   - **Software**: Problemas con programas, aplicaciones, sistemas
   - **Red/Conectividad**: Problemas de internet, red, WiFi
   - **Acceso/Permisos**: Problemas para acceder a sistemas o archivos
   - **Otro**: Cualquier otro problema técnico

2. **Prioridad**: Selecciona qué tan urgente es
   - **Baja**: No es urgente, puede esperar
   - **Media**: Urgente pero puede esperar algunas horas
   - **Alta**: Necesita atención pronto (mismo día)
   - **Urgente**: Necesita atención inmediata (bloquea trabajo crítico)

3. **Área**: Escribe el área o departamento donde ocurre el problema
   - Ejemplo: "Ventas", "Contabilidad", "Almacén"

4. **Dispositivo Afectado**: Escribe qué equipo tiene el problema
   - Ejemplo: "Laptop HP ProBook", "Impresora Canon", "Monitor Dell"

5. **Descripción del Problema**: Describe detalladamente qué está pasando
   - Incluye: Qué pasó, cuándo empezó, qué intentaste hacer, mensajes de error (si los hay)

**[CAPTURA DE PANTALLA: Campo de descripción con texto de ejemplo completo mostrando una descripción detallada del problema]**

#### Enviar el Ticket

1. Revisa que toda la información sea correcta
2. Haz clic en el botón **"Crear Ticket"**

**[CAPTURA DE PANTALLA: Botón verde "Crear Ticket" resaltado con círculo rojo señalándolo]**

3. Verás un mensaje de confirmación con el código de tu ticket

**[CAPTURA DE PANTALLA: Mensaje verde de éxito en la parte superior que dice "Ticket creado correctamente. Código: TKT-20240315-001. Tu ticket será atendido por el área de Sistemas."]**

> **💡 Tip**: Guarda el código de tu ticket para hacer seguimiento. El código tiene el formato: TKT-YYYYMMDD-XXX
```

---

### 3.1.3. Ver Mis Tickets

**Qué incluir:**
- Cómo acceder a la lista de tickets propios
- Descripción de la tabla
- Explicación de los estados
- Captura de la tabla completa

**Formato:**
```markdown
### 3.1.3. Ver Mis Tickets

1. Desde el menú: **"Tickets"** → **"Mis Tickets"**

**[CAPTURA DE PANTALLA: Menú lateral con la opción "Tickets" expandida mostrando "Mis Tickets" resaltada]**

2. Verás una tabla con todos tus tickets

**[CAPTURA DE PANTALLA: Tabla completa de tickets del empleado mostrando columnas: Código, Tipo, Prioridad, Estado, Fecha Creación, y Acciones, con 4 filas de datos visibles mostrando diferentes estados: uno "Pendiente" (amarillo), uno "En Proceso" (azul), uno "Resuelto" (verde), y uno "Cancelado" (gris)]**

#### Estados de los Tickets

Cada ticket puede tener uno de estos estados:

- **Pendiente** (🟡): Aún no ha sido asignado a nadie
- **En Proceso** (🔵): Ya fue asignado y se está trabajando en él
- **Resuelto** (🟢): El problema ya fue solucionado
- **Cancelado** (⚪): El ticket fue cancelado
```

---

### 3.1.4. Ver Detalles de un Ticket

**Qué incluir:**
- Cómo acceder a los detalles
- Qué información se muestra
- Cómo ver la solución (si está resuelto)
- Captura de la vista de detalles

**Formato:**
```markdown
### 3.1.4. Ver Detalles de un Ticket

1. En la lista de tus tickets, haz clic en el **código del ticket** o en el botón **"Ver Detalles"** (ícono de ojo)

**[CAPTURA DE PANTALLA: Código de ticket "TKT-20240315-001" clickeable y botón naranja con ícono de ojo en la columna de acciones, ambos resaltados]**

2. Verás toda la información del ticket:

**[CAPTURA DE PANTALLA: Vista completa de detalles del ticket mostrando: código del ticket en la parte superior, información del solicitante, tipo y prioridad con badges de color, descripción completa del problema, estado actual "En Proceso", información de asignación (quién lo está atendiendo), fecha de creación, y si está resuelto, la sección "Solución Aplicada" con la descripción de la solución]**

#### Información Mostrada

- **Código del Ticket**: Identificador único
- **Solicitante**: Tu información
- **Tipo y Prioridad**: Con badges de color
- **Descripción del Problema**: Texto completo que escribiste
- **Estado Actual**: Estado en tiempo real
- **Asignado A**: Quién está atendiendo el ticket (si está asignado)
- **Fechas**: Creación, asignación (si aplica), resolución (si aplica)
- **Solución Aplicada**: Descripción de la solución (solo si está resuelto)
```

---

### 3.2.1. Acceso al Módulo (Para Sistemas/IT)

**Qué incluir:**
- Cómo llegar desde el panel de Sistemas
- Captura del botón en el dashboard
- Alternativa desde el menú

**Formato:**
```markdown
## 3.2. Para Sistemas/IT (Gestionar Tickets)

### 3.2.1. Acceso al Módulo

> **💻 Solo para Sistemas/IT y Administradores**

Desde el Panel Sistemas/IT, en Accesos Rápidos, haz clic en el botón naranja **"Gestionar Tickets"** para ver los reportes.

**[CAPTURA DE PANTALLA: Panel Sistemas/IT completo mostrando en la parte superior las tarjetas de estadísticas (Tickets Pendientes, En Proceso, Resueltos Hoy), y en la sección "Accesos Rápidos" el botón naranja "Gestionar Tickets" con ícono de ticket, resaltado con un círculo rojo señalándolo]**

O desde el menú principal: **"Sistemas"** → **"Gestionar Tickets"**

**[CAPTURA DE PANTALLA: Menú lateral con la opción "Sistemas" expandida mostrando "Gestionar Tickets" resaltada]**
```

---

### 3.2.2. Lista General de Tickets

**Qué incluir:**
- Descripción de la vista completa
- Explicación de las columnas
- Diferencia con "Mis Tickets" (aquí se ven todos)
- Captura de la tabla completa

**Formato:**
```markdown
### 3.2.2. Lista General de Tickets

Visualice todos los tickets (Pendientes, En Proceso, Resueltos) en esta lista.

**[CAPTURA DE PANTALLA: Lista completa de tickets mostrando tabla con columnas: Código, Solicitante, Tipo, Prioridad, Estado, Fecha Creación, Asignado A, y Acciones, con 8 filas de datos visibles mostrando diferentes estados y prioridades, y en la parte superior la sección de filtros con campo de búsqueda, selectores de estado y prioridad, y botones "Buscar" y "Limpiar"]**

#### Columnas de la Tabla

- **Código**: Identificador único del ticket (ej: TKT-20240315-001)
- **Solicitante**: Nombre del empleado que reportó el problema
- **Tipo**: Tipo de problema (Hardware, Software, Red, etc.)
- **Prioridad**: Nivel de urgencia (Baja, Media, Alta, Urgente)
- **Estado**: Estado actual (Pendiente, En Proceso, Resuelto, Cancelado)
- **Fecha Creación**: Cuándo se creó el ticket
- **Asignado A**: Quién está atendiendo el ticket (si está asignado)
- **Acciones**: Botones para gestionar el ticket
```

---

### 3.2.3. Filtros y Búsqueda

**Qué incluir:**
- Cómo usar cada filtro
- Ejemplos de búsqueda
- Cómo limpiar filtros
- Captura de la sección de filtros

**Formato:**
```markdown
### 3.2.3. Filtros y Búsqueda

En la parte superior de la lista puedes filtrar los tickets:

**[CAPTURA DE PANTALLA: Sección de filtros mostrando campo de búsqueda con texto "Buscar por código o solicitante...", selector "Estado" con opción "Pendiente" seleccionada, selector "Prioridad" con opción "Alta" seleccionada, y botones "Buscar" (azul) y "Limpiar" (gris)]**

#### Opciones de Filtrado

1. **Búsqueda por Código o Solicitante**: 
   - Escribe en el campo de búsqueda
   - Puedes buscar por código (ej: "TKT-20240315") o por nombre del empleado
   - La búsqueda es en tiempo real

2. **Filtrar por Estado**:
   - Selecciona un estado para ver solo esos tickets
   - Opciones: Todos, Pendiente, En Proceso, Resuelto, Cancelado

3. **Filtrar por Prioridad**:
   - Selecciona una prioridad para ver solo esos tickets
   - Opciones: Todas, Baja, Media, Alta, Urgente

4. **Aplicar Filtros**:
   - Haz clic en **"Buscar"** para aplicar los filtros seleccionados

5. **Limpiar Filtros**:
   - Haz clic en **"Limpiar"** para quitar todos los filtros y ver todos los tickets

> **💡 Tip**: Usa los filtros para encontrar rápidamente tickets pendientes o de alta prioridad que necesitan atención urgente.
```

---

### 3.2.4. Acciones de Gestión

**Qué incluir:**
- Tres acciones principales con iconos
- Pasos detallados para cada acción
- Capturas de cada botón y resultado
- Explicación del flujo de trabajo

**Formato:**
```markdown
### 3.2.4. Acciones de Gestión

Use los botones de acción en la columna 'Acciones' para gestionar el ciclo de vida de cada ticket. El botón verde asigna el ticket, el azul lo resuelve.

**[CAPTURA DE PANTALLA: Columna de acciones de la tabla mostrando los tres botones de acción: botón naranja con ícono de ojo (Ver Detalles), botón verde con ícono de persona y check (Asignarme), botón azul con ícono de check (Resolver), todos visibles en una fila de ejemplo]**

#### A. Ver Detalles

1. Haz clic en el botón naranja con el ícono de ojo

**[CAPTURA DE PANTALLA: Botón naranja con ícono de ojo resaltado con círculo rojo]**

2. Verás toda la información del ticket y podrás ver el historial completo

**[CAPTURA DE PANTALLA: Vista de detalles completa del ticket mostrando toda la información: código, solicitante con información de contacto, tipo y prioridad con badges, descripción completa del problema, estado actual, información de asignación, fechas importantes, y si está resuelto, la sección de solución con botón para editar]**

#### B. Asignarme

El botón verde asigna el ticket a ti para que lo resuelvas.

1. Haz clic en el botón verde con el ícono de persona y marca de verificación

**[CAPTURA DE PANTALLA: Botón verde con ícono de persona y check resaltado con círculo rojo]**

2. El ticket cambiará automáticamente a estado **"En Proceso"** y quedará asignado a ti

**[CAPTURA DE PANTALLA: Mensaje verde de confirmación "Ticket asignado correctamente. El ticket ahora está en estado 'En Proceso'." y en la tabla el estado cambió a "En Proceso" en color azul, y la columna "Asignado A" muestra tu nombre]**

> **⚠️ Importante**: Solo puedes asignarte tickets que estén en estado "Pendiente". Si un ticket ya está asignado a otra persona, deberás contactarla primero.

#### C. Resolver Ticket

El botón azul resuelve el ticket.

1. Primero debes estar asignado al ticket (usar el botón verde "Asignarme")
2. Haz clic en el botón azul con el ícono de marca de verificación

**[CAPTURA DE PANTALLA: Botón azul con ícono de check resaltado con círculo rojo]**

3. Se abrirá un formulario donde debes escribir la **Solución Aplicada**

**[CAPTURA DE PANTALLA: Formulario modal de resolución mostrando campo de texto grande "Solución Aplicada" con texto de ejemplo "Se reinició el sistema y se actualizaron los drivers de la tarjeta gráfica. El problema de pantalla azul está resuelto. Se realizaron pruebas y la laptop funciona correctamente.", y botones "Cancelar" (gris) y "Confirmar Resolución" (azul) en la parte inferior]**

4. Describe detalladamente qué hiciste para resolver el problema:
   - Qué pasos seguiste
   - Qué cambios o reparaciones realizaste
   - Si se necesita seguimiento adicional
   - Cualquier recomendación para el usuario

5. Haz clic en **"Confirmar Resolución"**

**[CAPTURA DE PANTALLA: Botón azul "Confirmar Resolución" resaltado]**

6. El ticket cambiará a estado **"Resuelto"** y el empleado será notificado automáticamente

**[CAPTURA DE PANTALLA: Mensaje verde de confirmación "Ticket resuelto correctamente. El solicitante ha sido notificado." y en la tabla el estado cambió a "Resuelto" en color verde]**

> **💡 Tip**: Sé específico en la solución aplicada. Esto ayuda a otros técnicos si el problema vuelve a ocurrir y permite al usuario entender qué se hizo.
```

---

## Checklist de Contenido

Antes de finalizar la sección, verifica que incluyas:

### Para Empleados
- [ ] Acceso al módulo (desde panel y menú)
- [ ] Formulario completo de crear ticket con todos los campos explicados
- [ ] Tipos de ticket explicados
- [ ] Prioridades explicadas con ejemplos
- [ ] Ejemplo de descripción del problema
- [ ] Cómo ver la lista de tickets propios
- [ ] Estados de tickets explicados
- [ ] Cómo ver detalles de un ticket
- [ ] Cómo ver la solución (si está resuelto)

### Para Sistemas/IT
- [ ] Acceso al módulo desde panel de Sistemas
- [ ] Descripción de la lista general de tickets
- [ ] Explicación de todas las columnas
- [ ] Uso de filtros y búsqueda
- [ ] Acción A: Ver Detalles (con captura)
- [ ] Acción B: Asignarme (con captura y explicación del cambio de estado)
- [ ] Acción C: Resolver Ticket (con formulario de solución y captura)
- [ ] Flujo completo: Pendiente → En Proceso → Resuelto

### Capturas de Pantalla Requeridas
- [ ] Botón "Generar Ticket" en dashboard de empleado
- [ ] Formulario completo de crear ticket
- [ ] Mensaje de confirmación con código de ticket
- [ ] Tabla de "Mis Tickets" del empleado
- [ ] Vista de detalles de ticket (empleado)
- [ ] Botón "Gestionar Tickets" en panel de Sistemas
- [ ] Lista general de tickets con filtros
- [ ] Sección de filtros funcionando
- [ ] Botones de acción (Ver, Asignar, Resolver)
- [ ] Vista de detalles completa (Sistemas)
- [ ] Formulario de resolución
- [ ] Ticket resuelto con estado final

---

## Orden de Redacción Recomendado

1. **Primero**: Redacta la sección 3.1 (Para Empleados)
   - Es más simple y directa
   - Te ayudará a entender el flujo básico

2. **Segundo**: Redacta la sección 3.2 (Para Sistemas/IT)
   - Es más compleja pero complementa la anterior
   - Muestra el flujo completo del ciclo de vida del ticket

3. **Revisión**: Verifica que ambas secciones estén conectadas lógicamente

---

## Ejemplo de Flujo Completo

Para que quede claro, incluye un diagrama de flujo en texto:

```markdown
### Flujo Completo de un Ticket

```
Empleado crea ticket
    ↓
Estado: Pendiente
    ↓
Sistemas/IT ve el ticket
    ↓
Sistemas/IT se asigna (botón verde)
    ↓
Estado: En Proceso
    ↓
Sistemas/IT resuelve (botón azul)
    ↓
Estado: Resuelto
    ↓
Empleado es notificado
    ↓
Empleado ve la solución
```
```

---

## Notas Importantes

1. **Lenguaje**: Usa español mexicano básico, claro y directo
2. **Tono**: Profesional pero amigable
3. **Capturas**: Cada captura debe ser descriptiva y específica
4. **Ejemplos**: Incluye ejemplos prácticos y realistas
5. **Tips**: Agrega tips útiles donde sea relevante
6. **Advertencias**: Incluye advertencias importantes (ej: solo asignar tickets pendientes)

---

## Cuándo Considerar la Sección Completa

La sección está completa cuando:

- ✅ Tiene todas las subsecciones requeridas
- ✅ Cada procedimiento tiene pasos numerados claros
- ✅ Todas las capturas de pantalla están marcadas con descripciones
- ✅ Los tipos de usuario están claramente identificados
- ✅ El flujo completo del ticket está explicado
- ✅ Hay ejemplos prácticos
- ✅ Hay tips y advertencias relevantes
- ✅ El lenguaje es consistente y claro

---

**¡Listo para proceder!** Sigue estas instrucciones paso a paso y tendrás una sección completa y profesional sobre Gestión de Tickets.

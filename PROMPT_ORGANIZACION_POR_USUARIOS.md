# PROMPT COMPLEMENTARIO: Organización por Tipos de Usuario
## Instrucciones para Estructurar Manuales por Roles

---

## Objetivo

Este prompt complementa el **PROMPT_EXPERTO_MANUALES_IA.md** y se enfoca específicamente en:

1. **Organizar el contenido por tipo de usuario**
2. **Explicar claramente cada rol y sus funciones**
3. **Dividir los pasos según el tipo de usuario**
4. **Evitar confusión sobre qué secciones aplican a quién**

---

## Estructura Requerida: Sección de Tipos de Usuario

### Ubicación en el Manual

La sección de **"Tipos de Usuario"** debe ir **inmediatamente después de la Introducción** y **antes de los módulos principales**.

### Estructura de la Sección

```markdown
## 2. Tipos de Usuario y Sus Funciones

### 2.1. Empleado

**¿Quién es?**: Descripción breve del rol

**Funciones principales**:
- Función 1
- Función 2
- Función 3

**Accesos permitidos**:
- Módulo 1
- Módulo 2

**No puede**:
- Acción restringida 1
- Acción restringida 2

### 2.2. Jefe de Área

[Repetir estructura para cada tipo de usuario]
```

---

## Reglas para Explicar Tipos de Usuario

### Información Obligatoria para Cada Tipo

1. **Nombre del Rol**: Título claro
2. **Descripción Breve**: 1-2 líneas explicando quién es
3. **Funciones Principales**: Lista de 3-5 funciones más importantes
4. **Módulos Accesibles**: Qué secciones del sistema puede usar
5. **Acciones Permitidas**: Qué puede hacer específicamente
6. **Restricciones**: Qué NO puede hacer (si aplica)

### Formato de Descripción

✅ **BUENO:**
```
### 2.1. Empleado

**¿Quién es?**: Un empleado regular de la empresa que usa el sistema para gestionar sus vacaciones y reportar problemas técnicos.

**Funciones principales**:
- Solicitar vacaciones
- Ver el estado de sus solicitudes
- Crear tickets de soporte técnico
- Ver sus equipos asignados
- Consultar su información personal

**Accesos permitidos**:
- Panel de Empleado
- Módulo de Vacaciones (solo solicitar y ver propias)
- Módulo de Tickets (solo crear y ver propios)
- Módulo de Equipos (solo ver asignados)
- Perfil Personal

**No puede**:
- Aprobar vacaciones de otros
- Gestionar tickets de otros usuarios
- Ver información de otros empleados
- Asignar equipos
```

❌ **MALO:**
```
### 2.1. Empleado

Es un usuario del sistema.
```

---

## Organización de Procedimientos por Usuario

### Estructura de Módulos

Cada módulo principal debe tener subsecciones organizadas por tipo de usuario cuando sea relevante.

### Formato Recomendado

```markdown
## 4. Gestión de Vacaciones

### 4.1. Para Empleados

#### 4.1.1. Solicitar Vacaciones
[Pasos específicos para empleados]

#### 4.1.2. Ver Mis Vacaciones
[Pasos específicos para empleados]

### 4.2. Para Jefes de Área

#### 4.2.1. Aprobar Vacaciones de Mi Departamento
[Pasos específicos para jefes]

#### 4.2.2. Ver Solicitudes Pendientes
[Pasos específicos para jefes]

### 4.3. Para Recursos Humanos

#### 4.3.1. Aprobar Vacaciones Finales
[Pasos específicos para RH]

#### 4.3.2. Generar Reportes de Vacaciones
[Pasos específicos para RH]
```

### Alternativa: Sección Unificada con Etiquetas

Si prefieres mantener los procedimientos unificados, usa etiquetas claras:

```markdown
## 4. Gestión de Vacaciones

### 4.1. Solicitar Vacaciones

> **👤 Para**: Empleados  
> **⏱️ Tiempo estimado**: 5 minutos

[Pasos del procedimiento]

### 4.2. Aprobar Vacaciones

> **👔 Para**: Jefes de Área y Recursos Humanos  
> **⏱️ Tiempo estimado**: 3 minutos por solicitud

[Pasos del procedimiento]
```

---

## Tabla Comparativa de Funciones

### Incluir una Tabla Resumen

Después de explicar cada tipo de usuario, incluye una tabla comparativa:

```markdown
### 2.6. Resumen de Funciones por Rol

| Función | Empleado | Jefe | RH | Sistemas | Admin |
|---------|----------|------|----|----|----|
| Solicitar vacaciones | ✅ | ✅ | ✅ | ✅ | ✅ |
| Aprobar vacaciones | ❌ | ✅ (solo su depto) | ✅ (todas) | ❌ | ✅ |
| Crear tickets | ✅ | ✅ | ✅ | ✅ | ✅ |
| Resolver tickets | ❌ | ❌ | ❌ | ✅ | ✅ |
| Ver todos los empleados | ❌ | ❌ | ✅ | ❌ | ✅ |
| Gestionar equipos | ❌ | ❌ | ❌ | ✅ | ✅ |
```

---

## Iconos y Etiquetas Visuales

### Usar Iconos para Identificar Roles

Para facilitar la identificación rápida, usa iconos o etiquetas:

```
👤 Empleado
👔 Jefe de Área
👥 Recursos Humanos
💻 Sistemas/IT
🔧 Administrador
```

### Ejemplo de Uso

```markdown
### 4.1. Solicitar Vacaciones

> **👤 Solo para Empleados**

1. [Paso 1]
2. [Paso 2]
```

---

## Flujo de Navegación por Usuario

### Incluir Diagramas de Flujo (Texto)

Para cada tipo de usuario, muestra el flujo típico:

```markdown
### 2.1. Empleado - Flujo Típico de Uso

```
Inicio de Sesión
    ↓
Panel de Empleado
    ↓
┌─────────────────┬─────────────────┐
│ Solicitar       │ Crear Ticket    │
│ Vacaciones      │                  │
└─────────────────┴─────────────────┘
    ↓                    ↓
Ver Estado        Ver Estado
```

---

## Ejemplos de Procedimientos Divididos

### Ejemplo 1: Gestión de Vacaciones

```markdown
## 4. Gestión de Vacaciones

### 4.1. Para Empleados

#### 4.1.1. Solicitar Vacaciones

1. Desde tu panel de empleado, haz clic en **"Solicitar Vacaciones"**

**[CAPTURA DE PANTALLA: Panel de empleado con botón "Solicitar Vacaciones" resaltado]**

2. Llena el formulario con las fechas y motivo

**[CAPTURA DE PANTALLA: Formulario de solicitud de vacaciones]**

3. Haz clic en **"Enviar Solicitud"**

#### 4.1.2. Ver Mis Vacaciones

1. Desde el menú: **"Vacaciones"** → **"Mis Vacaciones"**

**[CAPTURA DE PANTALLA: Menú con opción "Mis Vacaciones"]**

2. Verás todas tus solicitudes con su estado

**[CAPTURA DE PANTALLA: Tabla de solicitudes del empleado]**

### 4.2. Para Jefes de Área

#### 4.2.1. Aprobar Vacaciones de Mi Departamento

> **👔 Solo para Jefes de Área**

1. Desde tu panel de jefe, haz clic en **"Solicitudes Pendientes"**

**[CAPTURA DE PANTALLA: Dashboard de jefe con botón "Solicitudes Pendientes" resaltado]**

2. Verás solo las solicitudes de empleados de tu departamento

**[CAPTURA DE PANTALLA: Tabla de solicitudes pendientes del departamento]**

3. Haz clic en **"Aprobar"** o **"Rechazar"** según corresponda

**[CAPTURA DE PANTALLA: Botones de aprobar y rechazar resaltados]**

### 4.3. Para Recursos Humanos

#### 4.3.1. Aprobar Vacaciones Finales

> **👥 Solo para Recursos Humanos**

1. Desde el panel de RH, haz clic en **"Solicitudes Pendientes"**

**[CAPTURA DE PANTALLA: Dashboard de RH con solicitudes pendientes]**

2. Verás todas las solicitudes que ya fueron aprobadas por los jefes

**[CAPTURA DE PANTALLA: Tabla de solicitudes pendientes de RH]**

3. Haz clic en **"Aprobar"** para dar la aprobación final

**[CAPTURA DE PANTALLA: Botón de aprobar final resaltado]**

4. Al aprobar, el sistema descontará automáticamente los días

**[CAPTURA DE PANTALLA: Mensaje de confirmación y actualización de días]**
```

---

## Advertencias y Notas por Rol

### Incluir Notas Específicas

```markdown
> **⚠️ Importante para Jefes**: Solo puedes aprobar vacaciones de empleados que pertenecen directamente a tu departamento. Si un empleado de otro departamento te aparece, contacta a RH.

> **💡 Tip para RH**: Puedes ver todas las solicitudes del sistema, pero solo debes aprobar las que ya fueron aprobadas por el jefe correspondiente.

> **🔒 Restricción para Empleados**: No puedes ver las solicitudes de vacaciones de otros empleados, solo las tuyas.
```

---

## Checklist para Organización por Usuario

Antes de entregar el manual, verifica:

- [ ] Hay una sección completa explicando cada tipo de usuario
- [ ] Cada tipo de usuario tiene descripción, funciones y restricciones claras
- [ ] Los procedimientos están divididos por tipo de usuario cuando es relevante
- [ ] Hay etiquetas o iconos que identifican para quién es cada procedimiento
- [ ] Hay una tabla comparativa de funciones por rol
- [ ] Los ejemplos de capturas de pantalla muestran la vista correcta para cada tipo de usuario
- [ ] No hay confusión sobre qué secciones aplican a cada rol
- [ ] Los procedimientos que aplican a múltiples roles están claramente marcados

---

## Ejemplo Completo: Sección de Tipos de Usuario

```markdown
## 2. Tipos de Usuario y Sus Funciones

El Sistema GK tiene 5 tipos de usuarios, cada uno con permisos y funciones específicas. Es importante entender tu rol para saber qué puedes hacer en el sistema.

### 2.1. 👤 Empleado

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
- ❌ No puede crear o editar departamentos

**Flujo típico**:
```
Inicio de Sesión
    ↓
Panel de Empleado
    ↓
┌─────────────────┬─────────────────┬─────────────────┐
│ Solicitar       │ Crear Ticket    │ Ver Mis         │
│ Vacaciones      │                 │ Equipos         │
└─────────────────┴─────────────────┴─────────────────┘
```

### 2.2. 👔 Jefe de Área

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
- ❌ No puede aprobar vacaciones de otros departamentos
- ❌ No puede gestionar tickets o equipos
- ❌ No puede crear usuarios o departamentos

**Flujo típico**:
```
Inicio de Sesión
    ↓
Panel de Jefe
    ↓
Ver Solicitudes Pendientes
    ↓
┌─────────────┬─────────────┐
│ Aprobar     │ Rechazar    │
└─────────────┴─────────────┘
```

### 2.3. 👥 Recursos Humanos (RH)

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
- ❌ No puede modificar configuraciones del sistema (solo Admin)

**Flujo típico**:
```
Inicio de Sesión
    ↓
Panel de RH
    ↓
┌──────────────┬──────────────┬──────────────┐
│ Gestionar    │ Aprobar      │ Generar      │
│ Empleados    │ Vacaciones   │ Reportes     │
└──────────────┴──────────────┴──────────────┘
```

### 2.4. 💻 Sistemas/IT

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
- ❌ No puede crear usuarios (excepto si también es Admin)

**Flujo típico**:
```
Inicio de Sesión
    ↓
Panel de Sistemas
    ↓
┌──────────────┬──────────────┐
│ Gestionar    │ Gestionar    │
│ Tickets      │ Equipos      │
└──────────────┴──────────────┘
```

### 2.5. 🔧 Administrador

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

### 2.6. Resumen de Funciones por Rol

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
| Configuración del sistema | ❌ | ❌ | ❌ | ❌ | ✅ |

> **💡 Tip**: Si no estás seguro de qué puedes hacer en el sistema, consulta esta tabla o contacta a tu administrador.
```

---

## Integración con el Prompt Principal

Este prompt complementario debe usarse **junto con** el `PROMPT_EXPERTO_MANUALES_IA.md`. 

### Orden de Aplicación

1. Primero aplica el prompt principal para estructura general
2. Luego aplica este prompt para organización por usuarios
3. Combina ambos para crear un manual completo y bien organizado

### Instrucción de Combinación

Al usar ambos prompts, la estructura final del manual debe ser:

```
1. Portada
2. Índice
3. Introducción
4. Tipos de Usuario y Sus Funciones ← (De este prompt)
5. Acceso al Sistema
6. Panel Principal
7. Módulos Principales (organizados por usuario) ← (De este prompt)
8. Solución de Problemas
9. Contacto y Soporte
```

---

**Este prompt complementario asegura que el manual sea claro sobre qué usuarios pueden hacer qué, y organiza los procedimientos de manera que cada tipo de usuario encuentre fácilmente la información que necesita.**

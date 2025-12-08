# PROMPT PARA PERPLEXITY: Generar Manual de Usuario Completo

## Instrucciones para Perplexity

---

## CONTEXTO

Necesito que generes un **Manual de Usuario completo y profesional** para el **Sistema GK de Grupo Keila**, que es un sistema web de gestión de recursos humanos desarrollado con Django.

## TU TAREA

Genera un manual de usuario completo, profesional y bien diseñado que incluya:

1. **Estructura completa** con todas las secciones necesarias
2. **Diseño moderno y corporativo** usando la identidad visual de Grupo Keila
3. **Espacios claramente marcados** para capturas de pantalla con descripciones detalladas
4. **Organización por tipos de usuario** (Empleado, Jefe, RH, Sistemas, Admin)
5. **Lenguaje claro y conciso** en español mexicano básico
6. **Formato Markdown** listo para convertir a PDF o usar en Canva

---

## PROMPTS QUE DEBES SEGUIR

A continuación te proporcionaré **3 prompts especializados** que debes seguir estrictamente:

### Prompt 1: PROMPT_EXPERTO_MANUALES_IA.md
Este prompt contiene:
- Reglas generales de redacción
- Formato de capturas de pantalla
- Estilo de escritura
- Estructura del documento
- Longitud y concisión

**DEBES SEGUIR TODAS SUS REGLAS**

### Prompt 2: PROMPT_ORGANIZACION_POR_USUARIOS.md
Este prompt contiene:
- Cómo explicar cada tipo de usuario
- Cómo organizar procedimientos por rol
- Formato de tablas comparativas
- Uso de iconos y etiquetas

**DEBES APLICAR SU ESTRUCTURA**

### Prompt 3: IDENTIDAD_VISUAL_GRUPO_KEILA.md
Este prompt contiene:
- Colores corporativos (Azul Rey #0038A8, etc.)
- Tipografías (Montserrat)
- Estilo de diseño (Moderno con secciones destacadas)
- Información del logo

**DEBES APLICAR SU ESTILO VISUAL**

---

## ESTRUCTURA REQUERIDA DEL MANUAL

El manual debe tener esta estructura exacta:

```
1. Portada
   - Título: "Manual de Usuario - Sistema GK"
   - Subtítulo: "Grupo Keila"
   - Versión y fecha

2. Índice
   - Numerado con todas las secciones y subsecciones
   - Con enlaces si es Markdown

3. Introducción
   3.1. ¿Qué es el Sistema GK?
   3.2. Requisitos del Sistema

4. Tipos de Usuario y Sus Funciones
   4.1. 👤 Empleado
   4.2. 👔 Jefe de Área
   4.3. 👥 Recursos Humanos (RH)
   4.4. 💻 Sistemas/IT
   4.5. 🔧 Administrador
   4.6. Tabla Comparativa de Funciones

5. Acceso al Sistema
   5.1. Iniciar Sesión
   5.2. Cerrar Sesión

6. Panel Principal (Dashboard)
   6.1. Panel de Empleado
   6.2. Panel de Jefe de Área
   6.3. Panel de Recursos Humanos
   6.4. Panel de Sistemas/IT
   6.5. Panel de Administrador

7. Gestión de Vacaciones
   7.1. Para Empleados
      7.1.1. Solicitar Vacaciones
      7.1.2. Ver Mis Vacaciones
   7.2. Para Jefes de Área
      7.2.1. Aprobar Vacaciones
   7.3. Para Recursos Humanos
      7.3.1. Aprobar Vacaciones Finales
      7.3.2. Generar Reportes

8. Gestión y Atención de Tickets de Soporte
   8.1. Para Empleados
      8.1.1. Crear un Ticket
      8.1.2. Ver Mis Tickets
   8.2. Para Sistemas/IT
      8.2.1. Gestionar Tickets
      8.2.2. Asignar y Resolver Tickets

9. Gestión de Equipos Tecnológicos
   9.1. Para Sistemas/IT
      9.1.1. Ver Inventario
      9.1.2. Asignar Equipo
   9.2. Para Empleados
      9.2.1. Ver Mis Equipos

10. Gestión de Empleados y Departamentos (Solo RH/Admin)
    10.1. Ver Lista de Empleados
    10.2. Crear Usuario
    10.3. Gestionar Departamentos

11. Solución de Problemas Comunes

12. Contacto y Soporte
```

---

## FORMATO DE CAPTURAS DE PANTALLA

Para CADA captura de pantalla que deba incluirse, usa este formato EXACTO:

```markdown
**[CAPTURA DE PANTALLA: Descripción detallada y específica de lo que debe mostrar la imagen]**
```

### Ejemplos Correctos:

✅ **BUENO:**
```
**[CAPTURA DE PANTALLA: Panel de empleado completo mostrando en la parte superior las tarjetas con información de vacaciones: "Días Disponibles: 15" (verde), "Días Usados: 5" (azul), "Acumulado Este Año: 3.5" (gris), y en la parte inferior la tabla de "Mis Solicitudes de Vacaciones" con 2 solicitudes visibles mostrando estados "Pendiente" y "Aprobada", y los botones "Solicitar Vacaciones" (naranja) y "Generar Ticket" (verde) en la parte superior derecha]**
```

✅ **BUENO:**
```
**[CAPTURA DE PANTALLA: Formulario completo de solicitud de vacaciones mostrando: campo "Fecha de Inicio" con calendario desplegado mostrando marzo 2024 con día 15 seleccionado, campo "Fecha de Fin" con día 20 seleccionado, selector "Tipo de Vacación" con "Normal" seleccionado, campo "Motivo" con texto de ejemplo "Vacaciones familiares", campo "Días Solicitados" mostrando "5 días" calculado automáticamente en color azul, y el botón "Enviar Solicitud" en la parte inferior en color azul corporativo]**
```

❌ **MALO:**
```
**[CAPTURA DE PANTALLA: Pantalla de login]**
```
(No es específico)

### Cuándo Incluir Capturas

Incluye capturas de pantalla en:
- Cada pantalla nueva o sección diferente
- Formularios importantes (con todos los campos visibles)
- Botones o acciones clave (resaltados con círculos rojos en la descripción)
- Resultados de acciones (mensajes de confirmación)
- Tablas con datos de ejemplo
- Menús y navegación

---

## ESTILO Y DISEÑO

### Colores a Usar

- **Azul Rey (Principal)**: `#0038A8`
- **Indigo Profundo (Secundario)**: `#1E3A8A`
- **Azul Vibrante (Acento)**: `#3B82F6`
- **Verde Éxito**: `#16A34A`
- **Naranja Advertencia**: `#F59E0B`
- **Rojo Peligro**: `#DC2626`
- **Gris Azulado**: `#EEF2F7`

### Tipografía

- **Principal**: Montserrat
- **Pesos**: Regular (400), Medium (500), Semi Bold (600), Bold (700)

### Estilo Visual

- **Moderno y con secciones destacadas**
- Usa gradientes en encabezados (azul rey a indigo)
- Bordes redondeados (18px en cards, 999px en botones)
- Sombras sutiles para profundidad
- Espaciado generoso entre secciones

### Elementos Visuales

- Usa iconos para identificar roles: 👤 👔 👥 💻 🔧
- Usa cajas de información para tips y advertencias
- Usa tablas para información comparativa
- Usa listas numeradas para pasos secuenciales

---

## LENGUAJE Y TONO

- **Idioma**: Español mexicano básico
- **Tono**: Profesional pero amigable
- **Persona**: Segunda persona del singular ("tú", "haz clic", "verás")
- **Imperativo**: Usa verbos en imperativo para acciones
- **Conciso**: Ve directo al grano, sin redundancias
- **Claro**: Evita jerga técnica sin explicarla

### Ejemplos de Frases:

✅ "Haz clic en el botón **'Solicitar Vacaciones'** que se encuentra en la parte superior derecha de tu panel."

✅ "Verás una tabla con todas tus solicitudes. Cada fila muestra: **Fecha de Inicio**, **Fecha de Fin**, **Días Solicitados**, y **Estado**."

---

## LONGITUD Y CONCISIÓN

- **Manual completo**: Entre 20-25 páginas (cuando se convierte a PDF)
- **Cada sección principal**: Máximo 3-4 páginas
- **Cada subsección**: Máximo 1-2 páginas
- **Párrafos**: Máximo 3-4 líneas
- **Elimina redundancias**: No repitas la misma información

---

## ESTRUCTURA DE CADA SECCIÓN

Cada sección debe seguir este formato:

```markdown
## X. Título de la Sección

### X.1. Subtítulo

> **👤 Para**: Tipo de usuario  
> **⏱️ Tiempo estimado**: X minutos

[Introducción breve si es necesaria]

#### Paso 1: Acción

1. Descripción del paso

**[CAPTURA DE PANTALLA: Descripción detallada]**

2. Siguiente paso

**[CAPTURA DE PANTALLA: Descripción detallada]**

#### Paso 2: Otra Acción

[Continuar con el mismo formato]
```

---

## INFORMACIÓN DEL SISTEMA

### Módulos Principales:

1. **Gestión de Vacaciones**: Solicitar, aprobar, ver vacaciones
2. **Sistema de Tickets**: Crear, gestionar, resolver tickets de soporte
3. **Gestión de Equipos**: Inventario, asignar, devolver equipos
4. **Gestión de Empleados**: Ver, crear, editar empleados (RH/Admin)
5. **Gestión de Departamentos**: Crear y gestionar departamentos (RH/Admin)

### Tipos de Usuario:

1. **👤 Empleado**: Funcionalidades básicas (solicitar vacaciones, crear tickets, ver información personal)
2. **👔 Jefe de Área**: Aprobar vacaciones de su departamento
3. **👥 Recursos Humanos (RH)**: Gestión completa de empleados, departamentos y aprobación final de vacaciones
4. **💻 Sistemas/IT**: Gestión de tickets y equipos tecnológicos
5. **🔧 Administrador**: Acceso completo a todas las funciones

---

## FORMATO DE SALIDA

### Requisitos:

1. **Formato**: Markdown (.md)
2. **Encabezados**: Usa #, ##, ###, #### según corresponda
3. **Listas**: Numeradas para pasos, con viñetas para opciones
4. **Negritas**: Para énfasis en botones, nombres de campos, acciones
5. **Cajas**: Usa `>` para tips, advertencias e información importante
6. **Tablas**: Para información comparativa
7. **Iconos**: Usa emojis para identificar roles

### Ejemplo de Caja de Información:

```markdown
> **💡 Tip**: Si olvidaste tu contraseña, contacta a tu administrador para que la restablezca.

> **⚠️ Importante**: Solo las solicitudes aprobadas por RH pueden descargarse como PDF.
```

---

## CHECKLIST FINAL

Antes de entregar el manual, verifica:

- [ ] Tiene portada con información completa
- [ ] Tiene índice numerado y completo
- [ ] Todas las secciones están numeradas correctamente
- [ ] Cada paso importante tiene marcador de captura de pantalla
- [ ] Los marcadores de captura son descriptivos y específicos
- [ ] El lenguaje es claro, conciso y en español mexicano básico
- [ ] No hay información redundante
- [ ] Los procedimientos están completos y en orden lógico
- [ ] Hay sección de solución de problemas
- [ ] Hay información de contacto/soporte
- [ ] El manual no excede 25 páginas (aproximadamente)
- [ ] Los tipos de usuario están claramente explicados
- [ ] Los procedimientos están organizados por tipo de usuario
- [ ] Hay tabla comparativa de funciones
- [ ] Se usan los colores corporativos en las descripciones
- [ ] Se menciona la tipografía Montserrat

---

## INSTRUCCIONES ESPECÍFICAS

1. **Lee cuidadosamente** los 3 prompts que te proporcionaré después
2. **Aplica TODAS las reglas** de cada prompt
3. **Genera el manual completo** siguiendo la estructura requerida
4. **Incluye TODAS las capturas de pantalla** con descripciones detalladas
5. **Organiza por tipos de usuario** cuando sea relevante
6. **Usa el estilo corporativo** de Grupo Keila
7. **Mantén el lenguaje simple** y directo
8. **Sé específico** en las descripciones de capturas

---

## EJEMPLO DE SECCIÓN COMPLETA

Aquí tienes un ejemplo de cómo debe verse una sección:

```markdown
## 7. Gestión de Vacaciones

### 7.1. Para Empleados

#### 7.1.1. Solicitar Vacaciones

> **👤 Solo para Empleados**  
> **⏱️ Tiempo estimado**: 5 minutos

##### Acceso

1. Desde tu panel de empleado, haz clic en el botón **"Solicitar Vacaciones"**

**[CAPTURA DE PANTALLA: Panel de empleado mostrando en la parte superior derecha el botón naranja "Solicitar Vacaciones" con ícono de calendario, resaltado con un círculo rojo señalándolo]**

O desde el menú principal, selecciona **"Vacaciones"** → **"Solicitar Vacaciones"**

##### Llenar el Formulario

Verás un formulario con los siguientes campos:

**[CAPTURA DE PANTALLA: Formulario completo de solicitud de vacaciones mostrando: campo "Fecha de Inicio" con calendario desplegado mostrando marzo 2024 con día 15 seleccionado, campo "Fecha de Fin" con día 20 seleccionado, selector "Tipo de Vacación" con "Normal" seleccionado, campo "Motivo" con texto de ejemplo "Vacaciones familiares", campo "Días Solicitados" mostrando "5 días" calculado automáticamente en color azul, y el botón "Enviar Solicitud" en la parte inferior en color azul corporativo #0038A8]**

1. **Fecha de Inicio**: Selecciona el primer día de tus vacaciones
   - Haz clic en el campo de fecha
   - Selecciona el día en el calendario

2. **Fecha de Fin**: Selecciona el último día de tus vacaciones

3. **Tipo de Vacación**:
   - **Normal**: Vacaciones regulares
   - **Extraordinaria**: Para empleados con menos de 1 año

4. **Motivo**: Escribe el motivo de tu solicitud (opcional pero recomendado)

5. El sistema calcula automáticamente los **días solicitados** (excluyendo domingos)

##### Enviar la Solicitud

1. Revisa que toda la información sea correcta
2. Haz clic en el botón **"Enviar Solicitud"**

**[CAPTURA DE PANTALLA: Botón azul "Enviar Solicitud" resaltado con círculo rojo señalándolo]**

3. Verás un mensaje de confirmación

**[CAPTURA DE PANTALLA: Mensaje verde de éxito en la parte superior de la pantalla que dice "Solicitud enviada correctamente. Tu solicitud está pendiente de aprobación." con ícono de check]**
```

---

## COMENZAR

Ahora, después de leer este prompt principal, te proporcionaré los 3 prompts especializados. 

**IMPORTANTE**: 
- Lee cada prompt cuidadosamente
- Aplica TODAS sus reglas
- Genera el manual completo siguiendo TODAS las instrucciones
- No omitas ninguna sección
- Incluye TODAS las capturas de pantalla con descripciones detalladas
- Mantén la consistencia en estilo y formato

**Cuando estés listo, indícame y te proporcionaré los 3 prompts especializados para que generes el manual completo.**

---

**Formato de entrega esperado**: Un archivo Markdown completo con todas las secciones, bien estructurado, con espacios para capturas de pantalla claramente marcados, y listo para convertir a PDF o usar en herramientas de diseño como Canva.

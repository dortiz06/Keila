# Identidad Visual - Grupo Keila
## Guía de Estilo Corporativo para Manuales

---

## 1. Colores Corporativos

### Colores Principales

| Color | Código HEX | Uso |
|-------|------------|-----|
| **Azul Rey (Primary)** | `#0038A8` | Color principal, botones principales, encabezados |
| **Indigo Profundo (Secondary)** | `#1E3A8A` | Color secundario, gradientes, elementos destacados |
| **Azul Vibrante (Accent)** | `#3B82F6` | Acentos, enlaces, elementos interactivos |

### Colores de Soporte

| Color | Código HEX | Uso |
|-------|------------|-----|
| **Gris Azulado Claro (Muted)** | `#EEF2F7` | Fondos suaves, áreas de descanso visual |
| **Borde Sutil** | `#E5E7EB` | Bordes de elementos, separadores |
| **Texto Oscuro** | `#0F172A` | Texto principal, títulos |
| **Fondo Claro** | `#F7F9FB` | Fondos de secciones, cards |

### Colores de Estado

| Color | Código HEX | Uso |
|-------|------------|-----|
| **Éxito (Success)** | `#16A34A` | Confirmaciones, estados positivos, aprobaciones |
| **Advertencia (Warning)** | `#F59E0B` | Alertas, pendientes, atención requerida |
| **Peligro (Danger)** | `#DC2626` | Errores, rechazos, acciones críticas |

### Resumen de Colores para el Manual

```
PRINCIPALES:
- Azul Rey: #0038A8
- Indigo Profundo: #1E3A8A
- Azul Vibrante: #3B82F6

NEUTROS:
- Gris Azulado: #EEF2F7
- Borde: #E5E7EB
- Texto Oscuro: #0F172A

ESTADO:
- Verde Éxito: #16A34A
- Naranja Advertencia: #F59E0B
- Rojo Peligro: #DC2626
```

---

## 2. Tipografías Corporativas

### Tipografía Principal

**Montserrat** - Fuente principal del sistema

- **Familia**: `'Montserrat', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif`
- **Fuente de respaldo**: Arial, sans-serif

### Pesos Disponibles

- **Thin**: 100
- **Extra Light**: 200
- **Light**: 300
- **Regular**: 400 (cuerpo de texto)
- **Medium**: 500 (elementos interactivos, botones)
- **Semi Bold**: 600 (subtítulos, etiquetas)
- **Bold**: 700 (títulos principales)
- **Extra Bold**: 800
- **Black**: 900

### Uso por Elemento

| Elemento | Peso | Tamaño Recomendado |
|----------|------|-------------------|
| Títulos Principales (H1) | 700 (Bold) | 2.5rem - 3rem |
| Subtítulos (H2) | 600 (Semi Bold) | 1.8rem - 2rem |
| Subtítulos Menores (H3) | 600 (Semi Bold) | 1.4rem - 1.6rem |
| Texto de Botones | 500 (Medium) | 1rem |
| Texto del Cuerpo | 400 (Regular) | 1rem - 1.1rem |
| Etiquetas y Labels | 500 (Medium) | 0.9rem - 1rem |

### Resumen de Tipografías

```
PRINCIPAL:
- Montserrat (todas las variantes)

PESOS MÁS USADOS:
- Regular (400): Texto normal
- Medium (500): Botones, etiquetas
- Semi Bold (600): Subtítulos
- Bold (700): Títulos principales
```

---

## 3. Logo

### Ubicación del Logo

El logo de Grupo Keila se encuentra en:
- **Ruta**: `static/images/logos/logo-keila.png`
- **Archivo**: `logo-keila.png`

### Uso del Logo en el Manual

**Recomendación**: Colocar un marcador de imagen para el logo

**Formato sugerido**:
```
**[CAPTURA DE PANTALLA: Logo de Grupo Keila - Logo corporativo completo con el nombre "Grupo Keila" y elementos gráficos, en formato PNG con fondo transparente o sobre fondo blanco]**
```

### Alternativa

Si prefieres incluir el logo directamente en el PDF:
- El archivo está disponible en: `/static/images/logos/logo-keila.png`
- Puedes extraerlo y colocarlo en la portada del manual

### Sello Corporativo

También existe un sello corporativo:
- **Ruta**: `static/images/logos/Sello_keila.png`
- Puede usarse como elemento decorativo o en la portada

---

## 4. Estilo Deseado

### Estilo Actual del Sistema

Basado en el análisis del código, el estilo del Sistema GK es:

**✅ Moderno y con secciones destacadas**

### Características del Estilo

1. **Gradientes**: Uso de gradientes lineales (135deg) en botones y encabezados
   - Ejemplo: `linear-gradient(135deg, #0038A8, #1E3A8A)`

2. **Glassmorphism**: Efectos de vidrio esmerilado en algunos elementos
   - Fondos con `backdrop-filter: blur()`
   - Transparencias con `rgba()`

3. **Sombras Suaves**: Sombras sutiles para profundidad
   - Ejemplo: `box-shadow: 0 10px 30px rgba(2, 6, 23, 0.06)`

4. **Bordes Redondeados**: Esquinas suaves
   - Botones: `border-radius: 999px` (completamente redondeados)
   - Cards: `border-radius: 18px`
   - Inputs: `border-radius: 10px - 12px`

5. **Efectos Hover**: Transiciones suaves en elementos interactivos
   - Transformaciones: `transform: translateY(-2px)`
   - Cambios de sombra y brillo

6. **Espaciado Generoso**: Padding y márgenes amplios para respiración visual

### Aplicación al Manual

Para mantener consistencia con el sistema, el manual debe tener:

- **Encabezados con gradiente azul** (azul rey a indigo)
- **Secciones destacadas** con fondos suaves (gris azulado claro)
- **Botones y elementos interactivos** con bordes redondeados
- **Tipografía Montserrat** en todos los textos
- **Paleta de colores corporativa** consistente
- **Espaciado generoso** entre secciones
- **Sombras sutiles** para profundidad

---

## 5. Resumen Ejecutivo

### Para el Manual de Usuario

```
COLORES:
- Principal: #0038A8 (Azul Rey)
- Secundario: #1E3A8A (Indigo)
- Acento: #3B82F6 (Azul Vibrante)
- Éxito: #16A34A (Verde)
- Advertencia: #F59E0B (Naranja)
- Peligro: #DC2626 (Rojo)

TIPOGRAFÍA:
- Montserrat (Regular 400, Medium 500, Semi Bold 600, Bold 700)

LOGO:
- Marcador de imagen recomendado
- Archivo: logo-keila.png

ESTILO:
- Moderno y con secciones destacadas
- Gradientes, sombras suaves, bordes redondeados
```

---

## 6. Ejemplos de Aplicación

### Encabezado de Sección
```css
background: linear-gradient(135deg, #0038A8, #1E3A8A);
color: white;
font-family: 'Montserrat', sans-serif;
font-weight: 700;
border-radius: 18px;
```

### Botón Principal
```css
background: linear-gradient(135deg, #3B82F6, #0038A8);
color: white;
font-family: 'Montserrat', sans-serif;
font-weight: 500;
border-radius: 999px;
box-shadow: 0 12px 24px rgba(59, 130, 246, 0.35);
```

### Card/Sección
```css
background: #F7F9FB;
border: 1px solid #E5E7EB;
border-radius: 18px;
box-shadow: 0 10px 30px rgba(2, 6, 23, 0.06);
```

---

**Documento generado para**: Manual de Usuario Sistema GK  
**Fecha**: 2024  
**Basado en**: Análisis del código fuente del sistema

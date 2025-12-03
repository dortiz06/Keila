# Glosario y Anexos - Reporte de Estadía Profesional

---

## GLOSARIO

**[TITULO PRINCIPAL]**

### Glosario de Términos Técnicos

El presente glosario contiene las definiciones de los términos técnicos y conceptos clave utilizados a lo largo del desarrollo del sistema de gestión de Recursos Humanos, con el propósito de facilitar la comprensión del documento para lectores de diferentes niveles técnicos.

**[SUBTITULO]**

#### Bootstrap

Framework de código abierto para el desarrollo de interfaces web responsivas, desarrollado por Twitter. Bootstrap proporciona una colección de componentes HTML, CSS y JavaScript predefinidos que permiten crear interfaces de usuario modernas y consistentes de manera eficiente. En el presente proyecto, se utilizó la versión 5.3 para garantizar la compatibilidad multiplataforma y la adaptabilidad del sistema a diferentes dispositivos (Bootstrap Team, 2023).

**[SUBTITULO]**

#### Git

Sistema de control de versiones distribuido diseñado para gestionar cambios en archivos de código fuente durante el desarrollo de software. Git permite rastrear modificaciones, mantener un historial completo de cambios, facilitar la colaboración entre desarrolladores y gestionar múltiples ramas de desarrollo simultáneamente. En el contexto del proyecto, Git se utilizó para mantener un registro estructurado de todas las iteraciones del sistema y permitir la colaboración entre los miembros del equipo (Chacon & Straub, 2023).

**[SUBTITULO]**

#### ORM (Object-Relational Mapping)

Técnica de programación que permite mapear estructuras de bases de datos relacionales a objetos de un lenguaje de programación orientado a objetos. Django ORM, utilizado en el presente proyecto, abstrae las consultas SQL mediante métodos de Python, facilitando la interacción con la base de datos sin necesidad de escribir código SQL directamente. Esta abstracción mejora la mantenibilidad del código y reduce la probabilidad de errores en las consultas (Django Software Foundation, 2024).

**[SUBTITULO]**

#### Responsive Design (Diseño Responsivo)

Enfoque de diseño web que permite que las interfaces se adapten automáticamente a diferentes tamaños de pantalla y dispositivos (computadoras de escritorio, tablets, smartphones). El diseño responsivo utiliza técnicas como media queries, unidades de medida flexibles (rem, em, porcentajes) y layouts adaptativos para garantizar una experiencia de usuario óptima independientemente del dispositivo utilizado. En el sistema desarrollado, se implementó diseño responsivo para asegurar la accesibilidad desde cualquier dispositivo (Marcotte, 2011).

**[SUBTITULO]**

#### Full-Stack

Término que describe el desarrollo completo de una aplicación web, abarcando tanto el front-end (interfaz de usuario) como el back-end (lógica de negocio y base de datos). Un desarrollador full-stack es capaz de trabajar en todas las capas de una aplicación. En el presente proyecto, el desarrollo full-stack se distribuyó entre los miembros del equipo: uno enfocado en el front-end y otro en el back-end, siguiendo una metodología de especialización colaborativa (W3Schools, 2024).

**[SUBTITULO]**

#### venv (Entorno Virtual de Python)

Herramienta que permite crear entornos aislados de Python para proyectos específicos, evitando conflictos entre dependencias de diferentes proyectos. Cada entorno virtual mantiene su propio conjunto de paquetes y versiones, independiente del sistema operativo y de otros proyectos. En el desarrollo del sistema, se utilizó venv para gestionar las dependencias del proyecto (Django, ReportLab, openpyxl) de manera controlada y reproducible (Python Software Foundation, 2024).

**[SUBTITULO]**

#### Liquid Glass (Estilo de Diseño)

Tendencia de diseño de interfaz de usuario caracterizada por efectos visuales que simulan vidrio esmerilado o translúcido. Este estilo utiliza técnicas de CSS como `backdrop-filter`, `blur`, y transparencias para crear elementos visuales con apariencia de vidrio sobre fondos, proporcionando una estética moderna y elegante. En el sistema desarrollado, se implementó el estilo Liquid Glass para mejorar la experiencia visual y mantener una interfaz limpia y profesional (Glassmorphism.io, 2023).

---

## ANEXOS

**[TITULO PRINCIPAL]**

### Descripción de Anexos

Los siguientes anexos complementan el presente reporte de estadía profesional, proporcionando evidencia documental, guías metodológicas y ejemplos técnicos que sustentan el desarrollo y validación del sistema de gestión de Recursos Humanos.

**[SUBTITULO]**

#### Anexo A: Guía de Observación para Validación con Personal de Recursos Humanos

**Descripción:** Este anexo contiene la guía estructurada utilizada durante las sesiones de observación y validación del sistema con el personal de Recursos Humanos de Grupo Keila S.A. de C.V. La guía incluye los criterios de evaluación, las preguntas dirigidas para recopilar retroalimentación cualitativa, y los indicadores de usabilidad que se midieron durante las pruebas de aceptación del sistema.

**Contenido esperado:**
- Criterios de evaluación de usabilidad (facilidad de uso, eficiencia, satisfacción)
- Preguntas abiertas sobre la experiencia del usuario
- Escala de satisfacción (Muy Baja, Baja, Media, Alta, Muy Alta)
- Registro de observaciones sobre el uso del sistema en escenarios reales
- Notas sobre mejoras sugeridas por los usuarios

**Relevancia:** Este anexo proporciona evidencia empírica de la validación cualitativa del sistema y sustenta los resultados de satisfacción del usuario reportados en el Capítulo IV.

**[SUBTITULO]**

#### Anexo B: Pantallas de Manejo de Errores (404 y 500)

**Descripción:** Este anexo presenta las capturas de pantalla y el código fuente de las páginas de error personalizadas implementadas en el sistema. Se incluyen las páginas de error 404 (Página No Encontrada) y 500 (Error del Servidor), diseñadas con el mismo estilo visual del sistema (Liquid Glass) para mantener la coherencia de la experiencia de usuario incluso en situaciones de error.

**Contenido esperado:**
- Captura de pantalla de la página de error 404
- Captura de pantalla de la página de error 500
- Código HTML/CSS de las plantillas de error
- Explicación breve de cómo se implementó el manejo de errores en Django

**Relevancia:** Este anexo demuestra la atención al detalle en el desarrollo del sistema y la consideración de casos extremos, lo cual es un indicador de calidad en el desarrollo de software profesional.

**[SUBTITULO]**

#### Anexo C: Código Fuente del Modelo de Solicitud de Vacaciones (Django ORM)

**Descripción:** Este anexo contiene el código fuente completo del modelo `SolicitudVacaciones` desarrollado en Django, que representa la estructura de datos y la lógica de negocio para el manejo de solicitudes de vacaciones en el sistema. El código incluye los campos del modelo, los métodos personalizados, las relaciones con otros modelos, y los validadores implementados.

**Contenido esperado:**
- Código Python del modelo `SolicitudVacaciones` con comentarios explicativos
- Definición de campos (empleado, fecha_inicio, fecha_fin, dias_solicitados, estado, etc.)
- Métodos del modelo (por ejemplo, `calcular_dias_solicitados()`, `validar_disponibilidad()`)
- Relaciones con otros modelos (ForeignKey, ManyToMany)
- Validaciones personalizadas y restricciones de integridad

**Relevancia:** Este anexo proporciona evidencia técnica del rigor en el desarrollo del back-end y permite a los revisores académicos evaluar la calidad del código y la implementación de la lógica de negocio. Además, sirve como referencia para futuras mejoras o mantenimiento del sistema.

---

## REFERENCIAS

Bootstrap Team. (2023). *Bootstrap 5.3 Documentation*. https://getbootstrap.com/docs/5.3/

Chacon, S., & Straub, B. (2023). *Pro Git: Everything you need to know about Git* (3rd ed.). Apress.

Django Software Foundation. (2024). *Django ORM Documentation*. https://docs.djangoproject.com/en/5.2/topics/db/

Glassmorphism.io. (2023). *Glassmorphism UI Design Trend*. https://glassmorphism.com/

Marcotte, E. (2011). *Responsive Web Design*. A Book Apart.

Python Software Foundation. (2024). *Python venv Documentation*. https://docs.python.org/3/library/venv.html

W3Schools. (2024). *Full Stack Development Guide*. https://www.w3schools.com/whatis/whatis_fullstack.asp

---

**Nota Final:** Los anexos descritos anteriormente deben ser incluidos físicamente en el documento final del reporte de estadía, siguiendo el orden alfabético establecido (Anexo A, Anexo B, Anexo C) y manteniendo la numeración de páginas consecutiva del documento principal.


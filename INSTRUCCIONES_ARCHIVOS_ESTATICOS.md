# 📁 Instrucciones para Solucionar Problemas con Archivos Estáticos

## 🔍 Problema Identificado

Los archivos estáticos (imágenes de fondo, CSS, JavaScript) no se cargan en producción cuando `DEBUG=False`.

## ✅ Soluciones Implementadas

### 1. Modificación de `urls.py`
Se modificó `rh_project/urls.py` para servir archivos estáticos también en producción, no solo en desarrollo.

### 2. Actualización de `settings_production.py`
- Se agregó el dominio `sistemagk.gruaskeila.com.mx` a `ALLOWED_HOSTS`
- Se configuraron correctamente `STATIC_URL` y `MEDIA_URL`
- Se agregaron los orígenes confiables para CSRF

## 🚀 Pasos para Solucionar el Problema en Producción

### Paso 1: Recopilar Archivos Estáticos

En el servidor de producción, ejecuta:

```bash
# Opción 1: Usar el script proporcionado
./collectstatic_production.sh

# Opción 2: Ejecutar manualmente
python manage.py collectstatic --noinput --settings=rh_project.settings_production
```

Este comando copiará todos los archivos de `static/` a `staticfiles/` donde Django los servirá.

### Paso 2: Verificar Permisos

Asegúrate de que el directorio `staticfiles/` tenga los permisos correctos:

```bash
chmod -R 755 staticfiles/
```

### Paso 3: Reiniciar el Servidor

Si usas Passenger o un servidor WSGI, reinicia la aplicación:

```bash
# Para Passenger, toca el archivo passenger_wsgi.py
touch passenger_wsgi.py

# O reinicia el servidor web según tu configuración
```

### Paso 4: Verificar que los Archivos Estén en su Lugar

Verifica que las imágenes existan en `staticfiles/images/dash/`:

```bash
ls -la staticfiles/images/dash/darkBlue.jpg
```

## 🔧 Configuración del Servidor Web (Opcional pero Recomendado)

Para mejor rendimiento, es recomendable que el servidor web (Apache/Nginx) sirva los archivos estáticos directamente en lugar de Django.

### Para Apache (.htaccess)

Actualiza el archivo `.htaccess` con las rutas correctas:

```apache
# Servir archivos estáticos
Alias /static /ruta/completa/a/tu/proyecto/staticfiles
<Directory /ruta/completa/a/tu/proyecto/staticfiles>
    Require all granted
</Directory>

# Servir archivos media
Alias /media /ruta/completa/a/tu/proyecto/media
<Directory /ruta/completa/a/tu/proyecto/media>
    Require all granted
</Directory>
```

### Para Nginx

Agrega estas directivas en tu configuración de Nginx:

```nginx
location /static/ {
    alias /ruta/completa/a/tu/proyecto/staticfiles/;
}

location /media/ {
    alias /ruta/completa/a/tu/proyecto/media/;
}
```

## 🧪 Verificación

Para verificar que los archivos estáticos se están sirviendo correctamente:

1. Abre el navegador en modo desarrollador (F12)
2. Ve a la pestaña "Network" o "Red"
3. Recarga la página
4. Busca las solicitudes a archivos estáticos (imágenes, CSS, JS)
5. Verifica que todas devuelvan código 200 (éxito)

## 📝 Notas Importantes

- **Siempre ejecuta `collectstatic` después de agregar o modificar archivos estáticos**
- Los archivos en `static/` son los archivos fuente
- Los archivos en `staticfiles/` son los que Django sirve en producción
- Si modificas archivos en `static/`, debes ejecutar `collectstatic` nuevamente

## 🐛 Solución de Problemas

### Si las imágenes aún no cargan:

1. Verifica que `STATIC_ROOT` apunte al directorio correcto
2. Verifica que `STATIC_URL` sea `/static/`
3. Verifica los permisos del directorio `staticfiles/`
4. Revisa los logs del servidor para errores
5. Verifica que el servidor web tenga acceso al directorio

### Si ves errores 404:

- Verifica que los archivos existan en `staticfiles/`
- Verifica que las rutas en los templates usen `{% static %}` correctamente
- Verifica que `STATIC_URL` esté configurado correctamente

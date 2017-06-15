# ¿Quién puede participar?

# Como contribuir al proyecto.

## Flujo de trabajo en entorno Develop

La subida de código en la rama develop no implica ejecución CI/CD.
Los tag de CI disponibles son:
- **testrepo-v** testea commit y testea la estructura del repositorio. Ejemplo **testrepo-v0.0.1**
- **testdockerfile-v**: realiza test commit, testea la estructura del repositorio y realiza linters al dockerfile.
- **deploydev-v** testea commit, testea la estructura del repositorio, realiza deploy del código en el entorno de desarrollo y realiza test de despliegue. Ejemplo **deploydev-v0.0.1**.
- **builddev-v** realiza test commit, testea la estructura del repositorio y realiza linters al dockerfile, crea la imagen de stack-sigila con tag sigila-php-develop, limpia imágenes antiguas en el builder, realiza push de la imagen al registry, en el host de develop hace pull a la imagen, se realiza deploy del código en el entorno de desarrollo y realiza test de despliegue. Ejemplo **builddev-v0.0.1**.


## Anexo
Para evitar la ejecución de CI/CD en algún tag/rama, basta con añadir en los comentarios del commit **"[skip ci]"** (sin comillas).

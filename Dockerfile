# Usa la imagen oficial de Locust como base
FROM locustio/locust

# Copia tu archivo de requerimientos al contenedor
COPY packages.txt /

# Instala las dependencias definidas en packages.txt
RUN pip install -r /packages.txt
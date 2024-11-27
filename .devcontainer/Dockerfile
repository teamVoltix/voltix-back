# Usar la imagen base de Python oficial (similar a la del proyecto)
FROM docker.uclv.cu/python:3.12-bookworm

# Instalar dependencias necesarias para desarrollo
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    git \
    vim \
    tesseract-ocr \
    tesseract-ocr-spa \
    && apt-get clean autoclean && \
    apt-get autoremove --yes && \
    rm -rf /var/lib/{apt,dpkg,cache,log}/

# Establecer el directorio de trabajo
WORKDIR /workspace

# Instalar dependencias de Python
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Variables de entorno comunes para desarrollo
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Exponer el puerto usado por Django
EXPOSE 8000

# Comando predeterminado para mantener el contenedor vivo
CMD ["tail", "-f", "/dev/null"]

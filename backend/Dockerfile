# 1. Usamos una computadora virtual que ya trae Python instalado
FROM python:3.12-slim

# 2. Creamos una carpeta de trabajo adentro de la caja llamada "proyecto"
WORKDIR /proyecto

# 3. Copiamos nuestra lista del súper adentro de la caja
COPY requirements.txt .

# 4. Le decimos a la caja que instale todo lo de la lista
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copiamos nuestro código (la carpeta app) adentro de la caja
COPY ./app ./app

# 6. Le decimos qué comando usar para encender nuestro servidor al terminar
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
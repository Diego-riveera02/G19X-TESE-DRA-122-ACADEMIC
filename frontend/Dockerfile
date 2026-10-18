# 1. Usamos Node.js para React
FROM node:22-alpine
# 2. Creamos carpeta de trabajo
WORKDIR /app

# 3. Copiamos los archivos de configuración
COPY package*.json ./

# 4. Instalamos las librerías
RUN npm install

# 5. Copiamos el resto del código
COPY . .

# 6. Comando para encender la página web
CMD ["npm", "run", "dev", "--", "--host"]
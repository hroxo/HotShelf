FROM node:20-alpine

# Ir direto para a pasta onde realmente está o teu código
WORKDIR /frontend/exec

# Copiar apenas ficheiros de dependências primeiro (cache build)
COPY exec/package.json exec/package-lock.json ./

# Instalar dependências
RUN npm ci || npm install

# Copiar resto dos ficheiros do frontend
COPY exec/ .

# Porta do Vite
EXPOSE 5173

# Correr Vite Dev Server
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "5173"]

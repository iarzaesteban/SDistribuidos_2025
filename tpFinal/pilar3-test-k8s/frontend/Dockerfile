# Etapa 1: build de React
FROM node:20-alpine AS build
WORKDIR /app
COPY . .
ARG VITE_COORDINADOR_URL
ENV VITE_COORDINADOR_URL=$VITE_COORDINADOR_URL
RUN npm install && npm run build

# Etapa 2: nginx para servir estáticos
FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx/default.conf /etc/nginx/conf.d/default.conf

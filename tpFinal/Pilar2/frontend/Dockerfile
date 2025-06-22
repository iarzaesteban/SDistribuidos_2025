# Etapa 1: build de React
FROM node:20-alpine AS build
WORKDIR /app
COPY . .
ARG VITE_API_URL
ENV VITE_API_URL=$VITE_API_URL
RUN npm install && npm run build

# Etapa 2: nginx para servir estáticos
FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf

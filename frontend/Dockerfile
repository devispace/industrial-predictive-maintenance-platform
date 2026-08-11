FROM node:24-alpine AS build
WORKDIR /app
RUN corepack enable && corepack prepare pnpm@11.16.0 --activate
COPY package.json pnpm-lock.yaml pnpm-workspace.yaml ./
RUN pnpm install --frozen-lockfile
COPY index.html ./
COPY src ./src
ARG VITE_API_BASE_URL=http://localhost:8080
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL
RUN pnpm run build

FROM nginx:1.29-alpine
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80

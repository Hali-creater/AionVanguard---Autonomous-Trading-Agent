# Stage 1: Build the Go backend
FROM golang:1.21-alpine AS backend-builder
WORKDIR /app
COPY backend/go.mod backend/go.sum ./
RUN go mod download
COPY backend/ ./
RUN CGO_ENABLED=0 GOOS=linux go build -o /server ./...

# Stage 2: Build the React frontend
FROM node:20-alpine AS frontend-builder
WORKDIR /app
COPY frontend/aionvanguard-ui/package.json frontend/aionvanguard-ui/package-lock.json ./
RUN npm install
COPY frontend/aionvanguard-ui/ ./
RUN npm run build

# Stage 3: Create the final image
FROM alpine:latest
WORKDIR /app
COPY --from=backend-builder /server .
COPY --from=frontend-builder /app/dist ./static
EXPOSE 8080
CMD ["/app/server"]

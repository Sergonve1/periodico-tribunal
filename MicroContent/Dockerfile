# Etapa 1: Build
FROM eclipse-temurin:21-jdk AS builder

WORKDIR /workspace
COPY . .
RUN ./gradlew build --no-daemon

# Etapa 2: Imagen final
FROM eclipse-temurin:21-jre

WORKDIR /app
COPY --from=builder /workspace/build/libs/*.jar app.jar

ENTRYPOINT ["java", "-jar", "app.jar"]

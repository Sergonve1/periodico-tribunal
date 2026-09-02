# Etapa 1: Build
FROM eclipse-temurin:21-jdk AS builder

WORKDIR /workspace
COPY . .
RUN ./gradlew build --no-daemon

# Etapa 2: Imagen final
FROM eclipse-temurin:21-jre

WORKDIR /app

# Copiamos el JAR
COPY --from=builder /workspace/build/libs/*.jar app.jar

# Añadimos wait-for-it.sh
ADD https://raw.githubusercontent.com/vishnubob/wait-for-it/master/wait-for-it.sh /wait-for-it.sh
RUN chmod +x /wait-for-it.sh

# Esperamos a MySQL y luego arrancamos la app
ENTRYPOINT ["/wait-for-it.sh", "mysql:3306", "--", "java", "-jar", "app.jar"]

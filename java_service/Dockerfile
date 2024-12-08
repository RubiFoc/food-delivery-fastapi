FROM maven:3.8.5-openjdk-17-slim AS build

WORKDIR /app

COPY pom.xml .
COPY src ./src

RUN mvn clean package -DskipTests

FROM openjdk:17-jdk-slim

WORKDIR /app

COPY --from=build /app/target/java_service-0.0.1-SNAPSHOT.jar /app/java_service.jar
COPY src/main/resources/application.properties /app/application.properties

EXPOSE 8080

CMD ["java", "-jar", "/app/java_service.jar"]

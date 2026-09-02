plugins {
	id("org.springframework.boot") version "3.4.2"
	id("io.spring.dependency-management") version "1.1.7"
	id("java")
}

dependencies {
	implementation("org.springframework.boot:spring-boot-starter-web")
	implementation("org.springframework.boot:spring-boot-starter-validation")
	testImplementation("org.springframework.boot:spring-boot-starter-test")
	testImplementation("org.junit.jupiter:junit-jupiter-api:5.11.4")
	testImplementation("org.mockito:mockito-core:5.15.2")
	testImplementation("org.junit.jupiter:junit-jupiter-engine:5.11.4")
	implementation("org.springframework.boot:spring-boot-starter-data-mongodb")
	implementation("org.mongodb:mongodb-driver-sync:4.11.1")
	implementation("org.mongodb:mongodb-driver-core:4.11.1")
	compileOnly("org.projectlombok:lombok:1.18.36")
	annotationProcessor("org.projectlombok:lombok:1.18.36")
	implementation("javax.annotation:javax.annotation-api:1.3.2")
	implementation("jakarta.annotation:jakarta.annotation-api:2.1.1")
	implementation("com.fasterxml.jackson.core:jackson-core:2.18.3")
	implementation("com.fasterxml.jackson.core:jackson-databind:2.18.3")
	implementation("org.apache.kafka:kafka_2.13:4.0.0")
	// Kafka Spring Boot Starter
	implementation("org.springframework.kafka:spring-kafka")
// https://mvnrepository.com/artifact/org.springframework.boot/spring-boot-starter-data-jpa
	implementation("org.springframework.boot:spring-boot-starter-data-jpa:3.4.4")
	// https://mvnrepository.com/artifact/com.mysql/mysql-connector-j
	implementation("com.mysql:mysql-connector-j:9.2.0")
}

repositories {
	mavenCentral()
}

tasks.withType<Test> {
	useJUnitPlatform()
}
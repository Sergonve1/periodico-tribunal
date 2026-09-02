package project.newspaper.domain;

import jakarta.persistence.Entity;
import jakarta.persistence.EnumType;
import jakarta.persistence.Enumerated;
import jakarta.persistence.Id;
import lombok.Getter;
import lombok.Setter;

import java.time.Instant;

@Getter
@Setter
@Entity
public class CategoryCreationStatus {

    @Id
    private String id;
    private String name;

    @Enumerated(EnumType.STRING)
    private Status status;

    private Instant createdAt;

    public enum Status {
        PENDING,
        COMPLETED,
        FAILED
    }


}
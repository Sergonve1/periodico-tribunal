package project.newspaper.domain;

import jakarta.persistence.Entity;
import jakarta.persistence.EnumType;
import jakarta.persistence.Enumerated;
import jakarta.persistence.Id;
import lombok.*;

@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Entity
public class ArticleCreationStatus {

    public enum Status {
        PENDING, COMPLETED
    }

    @Id
    private String id;
    @Enumerated(EnumType.STRING)
    private Status status;
}

package project.newspaper.domain;

import lombok.*;
import org.springframework.data.annotation.Id;
import org.springframework.data.mongodb.core.mapping.Document;

import java.time.Instant;

@Document(collection = "category")
@Data
@AllArgsConstructor
@NoArgsConstructor
public class Category {
    @Id
    private String id;
    private String name;
    private Instant createdAt;
}
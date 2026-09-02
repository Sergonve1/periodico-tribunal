package project.newspaper.domain;

import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

import java.time.Instant;

@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
public class CategoryCreatedEvent {
    private String id;
    private String category;
    private Instant createdAt;

    // Getters, setters, constructor
}

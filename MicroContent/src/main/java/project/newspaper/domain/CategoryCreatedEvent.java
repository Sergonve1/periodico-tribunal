package project.newspaper.domain;

import lombok.*;

import java.time.Instant;

@Data
@AllArgsConstructor
@NoArgsConstructor
public class CategoryCreatedEvent {
    private String id;
    private String category;
    private Instant createdAt;
}
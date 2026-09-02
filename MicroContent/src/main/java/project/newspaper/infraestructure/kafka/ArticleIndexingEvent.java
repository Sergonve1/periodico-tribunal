package project.newspaper.infraestructure.kafka;

import lombok.Data;

@Data
public class ArticleIndexingEvent {
    private String id;
    private String title;
    private String body;
}

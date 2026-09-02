package project.newspaper.domain;


import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@AllArgsConstructor
@NoArgsConstructor
public class ArticleCreatedEmbeddingEvent {
    private String id;
    private String title;
    private String body;
}

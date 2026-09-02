package project.newspaper.domain;

import lombok.*;

import java.util.*;

@Getter
@Setter
@AllArgsConstructor
@NoArgsConstructor
@Builder
public class ArticleCreatedEvent {

    private String id;
    private String title;
    private String slug;
    private String author;
    private State state;
    private Date creation;
    private Date publication;
    private Date updated;
    private int views;
    private String body;
    private String summary;
    private int version;
    private Set<Category> categories;
    private List<String> multimedias;
}

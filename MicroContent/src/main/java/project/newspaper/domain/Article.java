package project.newspaper.domain;

import com.fasterxml.jackson.annotation.JsonIgnore;
import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.*;
import org.springframework.data.annotation.Id;
import org.springframework.data.mongodb.core.mapping.Document;

import java.util.Date;
import java.util.List;
import java.util.Set;
import java.util.stream.Collectors;

@Document(collection = "article")
@Data
@AllArgsConstructor
@NoArgsConstructor
public class Article {
    @Id
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

    @JsonIgnore // <--- ocultamos la lista de objetos Category
    private Set<Category> categories;

    private List<String> multimedias;

    @JsonProperty("categoria") // <--- mostramos lista de nombres como "category"
    public List<String> getCategoryNames() {
        return categories != null
                ? categories.stream().map(Category::getName).collect(Collectors.toList())
                : List.of();
    }
}

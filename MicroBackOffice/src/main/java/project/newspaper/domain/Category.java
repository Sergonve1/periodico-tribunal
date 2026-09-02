package project.newspaper.domain;

import lombok.Getter;
import lombok.Setter;
import org.springframework.data.annotation.Id;
import org.springframework.data.mongodb.core.mapping.Document;

@Getter
@Setter
@Document(collection = "category")
public class Category {
    @Id
    private String id;
    private String name;

    public Category(String name) {
        this.name = name;
    }

    public Category() { }

}

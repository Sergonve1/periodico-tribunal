package project.newspaper.domain;

import lombok.Data;
import org.springframework.data.annotation.Id;
import org.springframework.data.mongodb.core.mapping.Document;

import java.util.List;
import java.util.Map;

@Data
@Document(collection = "memory")
public class MemoryDocument {

    @Id
    private String id;

    private List<Map<String, String>> history;
}

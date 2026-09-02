package project.newspaper.application;

import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import project.newspaper.domain.*;

import java.util.*;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
public class ArticleApplicationService {

    private final ArticleCreationStatusRepository statusRepository;
    private final ObjectMapper objectMapper;

    public ArticleCreatedEvent createAndSaveArticle(Map<String, Object> request) {
        String id = UUID.randomUUID().toString();

        // Guardar el estado inicial como PENDING
        ArticleCreationStatus status = new ArticleCreationStatus(id, ArticleCreationStatus.Status.PENDING);
        statusRepository.save(status);

        // Convertir lista de nombres de categoría a Set<Category>
        List<String> categorias = objectMapper.convertValue(
                request.get("category"),
                objectMapper.getTypeFactory().constructCollectionType(List.class, String.class)
        );

        Set<Category> categories = categorias.stream()
                .map(Category::new) // usa el constructor Category(String name)
                .collect(Collectors.toSet());

        // Convertir multimedias
        List<String> multimedias = objectMapper.convertValue(
                request.get("multimedias"),
                objectMapper.getTypeFactory().constructCollectionType(List.class, String.class)
        );

        // Crear el evento
        ArticleCreatedEvent event = ArticleCreatedEvent.builder()
                .id(id)
                .title((String) request.get("title"))
                .slug((String) request.get("slug"))
                .author((String) request.get("author"))
                .state(State.valueOf((String) request.get("state")))
                .creation(new Date())
                .publication(parseDate(request.get("publication")))
                .updated(new Date())
                .views((int) request.getOrDefault("views", 0))
                .body((String) request.get("body"))
                .summary((String) request.get("summary"))
                .version((int) request.getOrDefault("version", 1))
                .categories(categories)
                .multimedias(multimedias)
                .build();

        return event;
    }

    private Date parseDate(Object obj) {
        try {
            long timestamp = Long.parseLong(obj.toString());
            return new Date(timestamp);
        } catch (Exception e) {
            return null;
        }
    }
}

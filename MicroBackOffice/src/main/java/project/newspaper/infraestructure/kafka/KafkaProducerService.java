package project.newspaper.infraestructure.kafka;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.*;
import org.springframework.kafka.core.KafkaTemplate;
import org.springframework.stereotype.Service;
import project.newspaper.domain.ArticleCreatedEvent;
import project.newspaper.domain.CategoryCreatedEvent;

@Service
@RequiredArgsConstructor
public class KafkaProducerService {

    private final KafkaTemplate<String, String> kafkaTemplate;
    private final ObjectMapper objectMapper;

    public void sendCategoryCreatedEvent(CategoryCreatedEvent event) {
        try {
            String json = objectMapper.writeValueAsString(event);
            kafkaTemplate.send("backoffice.category.created", json);
        } catch (JsonProcessingException e) {
            throw new RuntimeException("Error serializing event", e);
        }
    }
    public void sendArticleCreatedEvent(ArticleCreatedEvent event) {
        try {
            String json = objectMapper.writeValueAsString(event);
            kafkaTemplate.send("backoffice.article.created", json);
        } catch (JsonProcessingException e) {
            throw new RuntimeException("Error serializing article event", e);
        }
    }
}


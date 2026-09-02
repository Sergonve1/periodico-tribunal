package project.newspaper.infraestructure.kafka;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.RequiredArgsConstructor;
import org.springframework.kafka.annotation.KafkaListener;
import org.springframework.kafka.core.KafkaTemplate;
import org.springframework.stereotype.Service;
import project.newspaper.domain.Category;
import project.newspaper.domain.CategoryCreatedEvent;
import project.newspaper.domain.CategoryRepository;

@Service
@RequiredArgsConstructor
public class CategoryCreatedListener {

    private final CategoryRepository repository;
    private final KafkaTemplate<String, String> kafkaTemplate;
    private final ObjectMapper objectMapper;

    @KafkaListener(topics = "backoffice.category.created", groupId = "content", containerFactory = "kafkaListenerContainerFactory")
    public void listen(String message) throws JsonProcessingException {
        CategoryCreatedEvent event = objectMapper.readValue(message, CategoryCreatedEvent.class);

        Category category = new Category();
        category.setId(event.getId());
        category.setName(event.getCategory());
        category.setCreatedAt(event.getCreatedAt());
        repository.save(category);

        kafkaTemplate.send("content.category.created.confirmation", event.getId());
    }
}

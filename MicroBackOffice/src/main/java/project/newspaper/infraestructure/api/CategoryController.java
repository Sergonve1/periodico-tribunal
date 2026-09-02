package project.newspaper.infraestructure.api;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.kafka.core.KafkaTemplate;
import org.springframework.web.bind.annotation.*;
import project.newspaper.application.CategoryApplicationService;
import project.newspaper.domain.CategoryCreatedEvent;
import project.newspaper.domain.CategoryCreationStatus;
import project.newspaper.domain.CategoryCreationStatusRepository;
import java.time.Instant;
import java.util.Map;
import java.util.UUID;

@RestController
@RequiredArgsConstructor
@RequestMapping("/api/v1/admin/articles/category")
public class CategoryController {

    private final KafkaTemplate<String, String> kafkaTemplate;
    private final ObjectMapper objectMapper;
    private final CategoryCreationStatusRepository repository;
    private final CategoryApplicationService categoryApplicationService;

    @PostMapping
    public ResponseEntity<Void> crearCategoria(@RequestBody Map<String, String> request) throws JsonProcessingException {

        String name = request.get("name");

        CategoryCreatedEvent event = categoryApplicationService.createAndSaveCategory(name);

        kafkaTemplate.send("backoffice.category.created", objectMapper.writeValueAsString(event));

        return ResponseEntity.accepted()
                .header("Location", "/api/v1/admin/articles/category/status/" + event.getId())
                .build();
    }

    @GetMapping("/status/{id}")
    public ResponseEntity<String> getStatus(@PathVariable String id) {
        return repository.findById(id)
                .map(s -> ResponseEntity.ok(s.getStatus().name()))
                .orElse(ResponseEntity.notFound().build());
    }


}
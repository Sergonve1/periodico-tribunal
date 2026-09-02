package project.newspaper.infraestructure.api;


import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.kafka.core.KafkaTemplate;
import org.springframework.web.bind.annotation.*;
import project.newspaper.application.ArticleApplicationService;
import project.newspaper.domain.ArticleCreatedEvent;
import project.newspaper.domain.ArticleCreationStatusRepository;

import java.util.Map;

@RestController
@RequiredArgsConstructor
@RequestMapping("/api/v1/admin/articles/")
public class ArticleController {

    private final KafkaTemplate<String, String> kafkaTemplate;
    private final ObjectMapper objectMapper;
    private final ArticleCreationStatusRepository repository;
    private final ArticleApplicationService articleApplicationService;

    @PostMapping
    public ResponseEntity<Void> crearArticulo(@RequestBody Map<String, Object> request) throws JsonProcessingException {

        ArticleCreatedEvent event = articleApplicationService.createAndSaveArticle(request);

        kafkaTemplate.send("backoffice.article.created", objectMapper.writeValueAsString(event));



        return ResponseEntity.accepted()
                .header("Location", "/api/v1/admin/articles/status/" + event.getId())
                .build();
    }

    @GetMapping("/status/{id}")
    public ResponseEntity<String> getStatus(@PathVariable String id) {
        return repository.findById(id)
                .map(s -> ResponseEntity.ok(s.getStatus().name()))
                .orElse(ResponseEntity.notFound().build());
    }
}

package project.newspaper.infraestructure.api;


import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.kafka.core.KafkaTemplate;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@RestController
@RequiredArgsConstructor
@RequestMapping("/api/v1/questions")
public class QuestionController {

    private final KafkaTemplate<String, String> kafkaTemplate;
    private final ObjectMapper objectMapper;

    private static final String TOPIC = "user.question.asked";

    @PostMapping
    public ResponseEntity<Void> askQuestion(@RequestBody Map<String, Object> body) throws JsonProcessingException {
        String question = (String) body.get("question");

        if (question == null || question.isBlank()) {
            return ResponseEntity.badRequest().build();
        }

        kafkaTemplate.send(TOPIC, objectMapper.writeValueAsString(Map.of("question", question)));

        return ResponseEntity.accepted().build();
    }
}

package project.newspaper.infraestructure.api;

import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import project.newspaper.domain.MemoryDocument;
import project.newspaper.domain.MemoryRepository;

import java.util.*;

@RestController
@RequiredArgsConstructor
@RequestMapping("/api/v1/memory")
public class MemoryController {

    private final MemoryRepository memoryRepository;

    @GetMapping
    public ResponseEntity<Map<String, Object>> getMemory() {
        List<MemoryDocument> all = memoryRepository.findAll();

        if (all.isEmpty()) {
            return ResponseEntity.ok(Map.of("history", List.of()));
        }

        // suponemos que el último insertado es el último por _id (ObjectId timestamp)
        MemoryDocument latest = all.get(all.size() - 1);
        return ResponseEntity.ok(Map.of("history", latest.getHistory()));
    }
}

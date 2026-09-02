package project.newspaper.application;

import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import project.newspaper.domain.CategoryCreatedEvent;
import project.newspaper.domain.CategoryCreationStatus;
import project.newspaper.domain.CategoryCreationStatusRepository;

import java.time.Instant;
import java.util.UUID;

@Service
@RequiredArgsConstructor
public class CategoryApplicationService {

    private final CategoryCreationStatusRepository repository;

    public CategoryCreatedEvent createAndSaveCategory(String name) {
        String id = UUID.randomUUID().toString();
        Instant createdAt = Instant.now();

        CategoryCreationStatus status = new CategoryCreationStatus();
        status.setId(id);
        status.setName(name);
        status.setCreatedAt(createdAt);
        status.setStatus(CategoryCreationStatus.Status.PENDING);
        repository.save(status);

        return new CategoryCreatedEvent(id, name, createdAt);
    }
}
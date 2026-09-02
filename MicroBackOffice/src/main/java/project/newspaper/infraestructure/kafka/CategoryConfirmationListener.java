package project.newspaper.infraestructure.kafka;

import lombok.RequiredArgsConstructor;
import org.springframework.kafka.annotation.KafkaListener;
import org.springframework.stereotype.Component;
import project.newspaper.domain.CategoryCreationStatus;
import project.newspaper.domain.CategoryCreationStatusRepository;

@Component
@RequiredArgsConstructor
public class CategoryConfirmationListener {

    private final CategoryCreationStatusRepository repository;

    @KafkaListener(topics = "content.category.created.confirmation", groupId = "backoffice")
    public void confirmCreation(String id) {
        repository.findById(id).ifPresent(status -> {
            status.setStatus(CategoryCreationStatus.Status.COMPLETED);
            repository.save(status);
        });
    }
}

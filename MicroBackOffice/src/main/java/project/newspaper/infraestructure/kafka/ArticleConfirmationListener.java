package project.newspaper.infraestructure.kafka;

import lombok.RequiredArgsConstructor;
import org.springframework.kafka.annotation.KafkaListener;
import org.springframework.stereotype.Component;
import project.newspaper.domain.ArticleCreationStatus;
import project.newspaper.domain.ArticleCreationStatusRepository;

@Component
@RequiredArgsConstructor
public class ArticleConfirmationListener {

    private final ArticleCreationStatusRepository repository;

    @KafkaListener(topics = "content.article.created.confirmation", groupId = "backoffice")
    public void confirmCreation(String id) {
        repository.findById(id).ifPresent(status -> {
            status.setStatus(ArticleCreationStatus.Status.COMPLETED);
            repository.save(status);
        });
    }
}

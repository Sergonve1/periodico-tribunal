package project.newspaper.infraestructure.kafka;


import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.RequiredArgsConstructor;
import org.springframework.kafka.annotation.KafkaListener;
import org.springframework.kafka.core.KafkaTemplate;
import org.springframework.stereotype.Service;
import project.newspaper.domain.Article;
import project.newspaper.domain.ArticleCreatedEmbeddingEvent;
import project.newspaper.domain.ArticleCreatedEvent;
import project.newspaper.domain.ArticleRepository;

@Service
@RequiredArgsConstructor
public class ArticleCreatedListener {

    private final ArticleRepository repository;
    private final KafkaTemplate<String, String> kafkaTemplate;
    private final ObjectMapper objectMapper;

    @KafkaListener(topics = "backoffice.article.created", groupId = "content", containerFactory = "kafkaListenerContainerFactory")
    public void listen(String message) throws JsonProcessingException {
        ArticleCreatedEvent event = objectMapper.readValue(message, ArticleCreatedEvent.class);

        Article article = new Article();
        article.setId(event.getId());
        article.setTitle(event.getTitle());
        article.setSlug(event.getSlug());
        article.setAuthor(event.getAuthor());
        article.setState(event.getState());
        article.setCreation(event.getCreation());
        article.setPublication(event.getPublication());
        article.setUpdated(event.getUpdated());
        article.setViews(event.getViews());
        article.setBody(event.getBody());
        article.setSummary(event.getSummary());
        article.setVersion(event.getVersion());
        article.setCategories(event.getCategories());
        article.setMultimedias(event.getMultimedias());

        repository.save(article);

        // Primero se indexa
        ArticleIndexingEvent indexingEvent = new ArticleIndexingEvent();
        indexingEvent.setId(article.getId());
        indexingEvent.setTitle(article.getTitle());
        indexingEvent.setBody(article.getBody());

        kafkaTemplate.send("content.article.index", objectMapper.writeValueAsString(indexingEvent));

        // Luego se confirma la creación
        kafkaTemplate.send("content.article.created.confirmation", event.getId());


    
        ArticleCreatedEmbeddingEvent embeddingEvent = new ArticleCreatedEmbeddingEvent(
            article.getId(),
            article.getTitle(),
            article.getBody()
        );
        
        kafkaTemplate.send("article.created.embedding", objectMapper.writeValueAsString(embeddingEvent));
        
    }
}

package project.newspaper.infraestructure.kafka.config;

import org.apache.kafka.clients.admin.NewTopic;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.kafka.config.TopicBuilder;

@Configuration
public class KafkaTopicConfig {

    @Bean
    public NewTopic backofficeCategoryCreatedTopic() {
        return TopicBuilder.name("backoffice.category.created")
                .partitions(3)
                .replicas(1)
                .build();
    }

    @Bean
    public NewTopic backofficeArticleCreatedTopic() {
        return TopicBuilder.name("backoffice.article.created")
                .partitions(3)
                .replicas(1)
                .build();
    }
    @Bean
    public NewTopic articleCreatedEmbeddingTopic() {
        return TopicBuilder.name("article.created.embedding")
                .partitions(1)
                .replicas(1)
                .build();
    }
    @Bean
    public NewTopic userQuestionAskedTopic() {
        return TopicBuilder.name("user.question.asked")
                .partitions(1)
                .replicas(1)
                .build();
}

}

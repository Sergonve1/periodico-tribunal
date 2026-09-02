package project.newspaper.application;

import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import project.newspaper.domain.Article;
import project.newspaper.domain.ArticleRepository;

@Service
@RequiredArgsConstructor
public class ArticleService {

    private final ArticleRepository repository;

    public void storeArticle(Article article) {
        repository.save(article);
    }
}

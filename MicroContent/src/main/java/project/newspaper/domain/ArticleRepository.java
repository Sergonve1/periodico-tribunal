package project.newspaper.domain;

import org.springframework.data.domain.Sort;
import org.springframework.data.mongodb.repository.MongoRepository;
import org.springframework.stereotype.Repository;
import java.util.List;

@Repository
public interface ArticleRepository extends MongoRepository<Article, String> {

    List<Article> findByCategories_NameIgnoreCase(String categoryName);
    List<Article> findByCategories_NameIgnoreCase(String categoria, Sort sort);

}

package project.newspaper.domain;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.repository.CrudRepository;

public interface ArticleCreationStatusRepository extends JpaRepository<ArticleCreationStatus, String> {
}

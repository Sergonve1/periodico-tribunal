package project.newspaper.domain;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface CategoryCreationStatusRepository extends JpaRepository<CategoryCreationStatus, String> {}
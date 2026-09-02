package project.newspaper.domain;

import org.springframework.data.mongodb.repository.MongoRepository;
import org.springframework.stereotype.Repository;


@Repository
public interface MemoryRepository extends MongoRepository<MemoryDocument, String> {
}

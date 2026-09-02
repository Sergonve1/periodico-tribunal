package project.newspaper.application;

import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import project.newspaper.domain.Category;
import project.newspaper.domain.CategoryRepository;

import java.time.Instant;
import java.util.List;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
public class CategoryService {
    private final CategoryRepository repository;

    public void storeCategory(String name, Instant createdAt) {
        Category category = new Category(); // o con builder si usás lombok @Builder
        category.setName(name);
        category.setCreatedAt(createdAt);
        repository.save(category);
    }

    public List<String> getAllCategoryNames() {
        return repository.findAll()
                .stream()
                .map(Category::getName)
                .collect(Collectors.toList());
    }


}
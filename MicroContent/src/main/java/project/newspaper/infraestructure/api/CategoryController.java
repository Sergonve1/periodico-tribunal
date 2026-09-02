package project.newspaper.infraestructure.api;

import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import project.newspaper.application.CategoryService;

import java.util.List;

@RestController
@RequiredArgsConstructor
@RequestMapping("/categorias")
public class CategoryController {

    private final CategoryService categoryService;

    @GetMapping
    public List<String> getAllCategoryNames() {
        return categoryService.getAllCategoryNames();
    }
}
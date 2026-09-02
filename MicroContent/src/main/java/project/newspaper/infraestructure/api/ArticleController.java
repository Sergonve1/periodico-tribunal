package project.newspaper.infraestructure.api;

import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.Sort;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.server.ResponseStatusException;
import project.newspaper.domain.Article;
import project.newspaper.domain.ArticleRepository;

import java.util.List;
import java.util.stream.Collectors;

@RestController
@RequiredArgsConstructor
@RequestMapping("/articulos")
public class ArticleController {

    private final ArticleRepository articleRepository;

    // Endpoint: GET /articulos
    @GetMapping
    public List<Article> getAllArticles() {
        return articleRepository.findAll();
    }

    // Endpoint: GET /articulos/categoria/{categoria}
    @GetMapping("/categoria/{categoria}")
    public List<Article> getByCategoria(@PathVariable String categoria) {
        return articleRepository
                .findByCategories_NameIgnoreCase(categoria, Sort.by(Sort.Direction.DESC, "creation"))
                .stream()
                .limit(30)
                .collect(Collectors.toList());
    }


    @GetMapping("/ultimos")
    public List<Article> obtenerUltimosArticulos() {
        return articleRepository
                .findAll(Sort.by(Sort.Direction.DESC, "creation"))
                .stream()
                .limit(30)
                .collect(Collectors.toList());
    }

    @GetMapping("/{id}")
    public Article getArticleById(@PathVariable String id) {
        return articleRepository.findById(id).orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND));
    }

}

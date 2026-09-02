package project.newspaper.domain;

import lombok.Getter;

@Getter
public enum State {

    DRAFT("The document is being edited"),
    REWIEW("The document is in revision"),
    PUBLISHED("The document is publicly available"),
    ARCHIVED("The document is stored and not publicly accessible");

    private final String descripcion;

    State(String descripcion) {
        this.descripcion = descripcion;
    }

}

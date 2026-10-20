package example.catalog;

import javax.validation.constraints.NotBlank;

public class Product {
    @NotBlank
    private String name;

    public String getName() { return name; }
    public void setName(String name) { this.name = name; }
}

package example.orders;

import javax.validation.constraints.Positive;

public class OrderRequest {
    @Positive
    private int quantity;

    public int getQuantity() { return quantity; }
    public void setQuantity(int quantity) { this.quantity = quantity; }
}

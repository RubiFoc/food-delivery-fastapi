package com.example.java_service.entity;

import jakarta.persistence.*;
import lombok.Getter;
import lombok.Setter;

@Setter
@Getter
@Entity
@Table(name = "order_dish_association")
public class OrderDishAssociation {

    // Геттеры и сеттеры
    @EmbeddedId
    private OrderDishAssociationId id;

    @ManyToOne
    @MapsId("orderId")
    @JoinColumn(name = "order_id")
    private Order order;

    @ManyToOne
    @MapsId("dishId")
    @JoinColumn(name = "dish_id")
    private Dish dish;

    private Integer quantity;

}

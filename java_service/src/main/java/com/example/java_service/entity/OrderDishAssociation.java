package com.example.java_service.entity;

import jakarta.persistence.*;

@Entity
@Table(name = "order_dish_association")
public class OrderDishAssociation {
    @Id
    @ManyToOne
    @JoinColumn(name = "order_id")
    private Order order;

    @Id
    @ManyToOne
    @JoinColumn(name = "dish_id")
    private Dish dish;

    private Integer quantity;
}
package com.example.java_service.entity;

import jakarta.persistence.*;

@Entity
@Table(name = "cart_dish_association")
public class CartDishAssociation {
    @Id
    @ManyToOne
    @JoinColumn(name = "cart_id")
    private Cart cart;

    @Id
    @ManyToOne
    @JoinColumn(name = "dish_id")
    private Dish dish;

    private Integer quantity;
}
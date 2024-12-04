package com.example.java_service.entity;

import jakarta.persistence.*;

import java.util.List;

@Entity
@Table(name = "dish_category")
public class DishCategory {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, length = 50)
    private String name;

    @OneToMany(mappedBy = "category")
    private List<Dish> dishes;
}
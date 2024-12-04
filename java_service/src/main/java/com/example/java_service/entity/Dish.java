package com.example.java_service.entity;

import jakarta.persistence.*;

@Entity
@Table(name = "dish")
public class Dish {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, length = 50)
    private String name;

    @Column(nullable = false)
    private Float price;

    @Column(nullable = false)
    private Float weight;

    @ManyToOne
    @JoinColumn(name = "category_id", nullable = false)
    private DishCategory category;

    @ManyToOne
    @JoinColumn(name = "restaurant_id", nullable = false)
    private Restaurant restaurant;

    private Float rating;

    private Integer numberOfMarks = 0;

    private Float profit;

    private Float timeOfPreparing;

    private String imagePath;

}
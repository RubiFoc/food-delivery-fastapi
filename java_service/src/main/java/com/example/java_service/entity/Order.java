package com.example.java_service.entity;

import jakarta.persistence.*;
import lombok.Getter;

import java.util.Date;
import java.util.List;

@Entity
@Table(name = "\"order\"")
public class Order {
    @Getter
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Getter
    @Column(nullable = false)
    private Float price;
    @Getter
    @Column(nullable = false)
    private Float weight;
    @Getter
    @Column(nullable = false)
    private Date timeOfCreation;
    @Getter
    @ManyToOne
    @JoinColumn(name = "restaurant_id", nullable = false)
    private Restaurant restaurant;
    @Getter
    @Column(nullable = false)
    private String location;
    @Getter
    @ManyToOne
    @JoinColumn(name = "courier_id")
    private Courier courier;
    @Getter
    @ManyToOne
    @JoinColumn(name = "kitchen_worker_id")
    private KitchenWorker kitchenWorker;
    @Getter
    private Date timeOfDelivery;
    @Getter
    private Date expectedTimeOfDelivery;
    @Getter
    @OneToMany(mappedBy = "order", cascade = CascadeType.ALL, orphanRemoval = true)
    private List<OrderDishAssociation> dishes;
    @Getter
    @ManyToOne
    @JoinColumn(name = "customer_id")
    private Customer customer;
    @Getter
    @OneToOne(mappedBy = "order", cascade = CascadeType.ALL, orphanRemoval = true)
    private OrderStatus status;

}
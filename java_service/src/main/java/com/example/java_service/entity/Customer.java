package com.example.java_service.entity;

import jakarta.persistence.*;

import java.util.List;

@Entity
@Table(name = "customer")
public class Customer {
    @Id
    @OneToOne
    @JoinColumn(name = "user_id")
    private User user;

    private Float balance = 0.0f;

    private String location;

    @ManyToOne
    @JoinColumn(name = "role_id")
    private Role role;

    @OneToMany(mappedBy = "customer", cascade = CascadeType.ALL, orphanRemoval = true)
    private List<Cart> cart;
}
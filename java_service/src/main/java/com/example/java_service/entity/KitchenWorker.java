package com.example.java_service.entity;

import jakarta.persistence.*;

import java.util.List;

@Entity
@Table(name = "kitchen_worker")
public class KitchenWorker {
    @Id
    @OneToOne
    @JoinColumn(name = "user_id")
    private User user;

    @ManyToOne
    @JoinColumn(name = "role_id")
    private Role role;

    @OneToMany(mappedBy = "kitchenWorker", cascade = CascadeType.ALL, orphanRemoval = true)
    private List<Order> orders;
}
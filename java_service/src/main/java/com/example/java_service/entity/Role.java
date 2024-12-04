package com.example.java_service.entity;


import jakarta.persistence.*;

import java.util.List;

@Entity
@Table(name = "role")
public class Role {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, length = 50)
    private String name;

    @Column(columnDefinition = "json")
    private String permissions;

    @OneToMany(mappedBy = "role", cascade = CascadeType.ALL, orphanRemoval = true)
    private List<User> users;

    @OneToMany(mappedBy = "role")
    private List<Courier> couriers;

    @OneToMany(mappedBy = "role")
    private List<Customer> customers;

    @OneToMany(mappedBy = "role")
    private List<KitchenWorker> kitchenWorkers;

    @OneToMany(mappedBy = "role")
    private List<Admin> admins;
}
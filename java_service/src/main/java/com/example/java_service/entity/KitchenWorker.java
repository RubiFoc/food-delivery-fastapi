package com.example.java_service.entity;

import jakarta.persistence.*;
import lombok.Getter;

import java.util.List;

@Entity
@Table(name = "kitchen_worker")
public class KitchenWorker {
    @Getter
    @Id
    private Long id;

    @Getter
    @OneToOne
    @MapsId
    @JoinColumn(name = "id")
    private User user;

    @Getter
    @ManyToOne
    @JoinColumn(name = "role_id")
    private Role role;

    @Getter
    @OneToMany(mappedBy = "kitchenWorker", cascade = CascadeType.ALL, orphanRemoval = true)
    private List<Order> orders;
}
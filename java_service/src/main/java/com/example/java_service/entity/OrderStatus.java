package com.example.java_service.entity;

import jakarta.persistence.*;

@Entity
@Table(name = "order_status")
public class OrderStatus {
    @Id
    @OneToOne
    @JoinColumn(name = "order_id")
    private Order order;

    private Boolean isPrepared = false;

    private Boolean isDelivered = false;
}
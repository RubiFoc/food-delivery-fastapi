package com.example.java_service.entity;

import jakarta.persistence.*;
import lombok.Getter;
import lombok.Setter;

@Setter
@Getter
@Entity
@Table(name = "order_status")
public class OrderStatus {

    // Геттеры и сеттеры
    @Id
    @OneToOne
    @JoinColumn(name = "order_id")
    private Order order;

    private Boolean isPrepared;
    private Boolean isDelivered;

    // Конструктор по умолчанию для инициализации значений
    public OrderStatus() {
        this.isPrepared = false;
        this.isDelivered = false;
    }

}

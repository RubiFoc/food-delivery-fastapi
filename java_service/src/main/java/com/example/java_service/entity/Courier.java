package com.example.java_service.entity;

import jakarta.persistence.*;
import lombok.Getter;

import java.util.List;

@Entity
@Table(name = "courier")
public class Courier {
    @Id
    @OneToOne
    @JoinColumn(name = "user_id")
    private User user;

    private Float rating;

    private Integer numberOfMarks = 0;

    @Getter
    private Float rate = 0.1f;

    private String location;

    @ManyToOne
    @JoinColumn(name = "role_id")
    private Role role;

    @OneToMany(mappedBy = "courier", cascade = CascadeType.ALL, orphanRemoval = true)
    private List<Order> orders;

}
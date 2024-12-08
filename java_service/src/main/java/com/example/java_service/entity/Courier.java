package com.example.java_service.entity;

import jakarta.persistence.*;
import lombok.Getter;

import java.util.List;

@Entity
@Table(name = "courier")
public class Courier {

    @Getter
    @Id
    private Long id;

    @Getter
    @OneToOne
    @MapsId
    @JoinColumn(name = "id")
    private User user;


    @Getter
    @Column(nullable = true)
    private Float rating;

    @Getter
    @Column(name = "number_of_marks", nullable = false)
    private Integer numberOfMarks;

    @Getter
    @Column(nullable = false)
    private Float rate;

    @Getter
    @Column(nullable = false)
    private String location;
    @Getter
    @ManyToOne
    @JoinColumn(name = "role_id", nullable = false)
    private Role role;
    @Getter
    @OneToMany(mappedBy = "courier", cascade = CascadeType.ALL, orphanRemoval = true)
    private List<Order> orders;

}

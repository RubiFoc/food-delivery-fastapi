package com.example.java_service.entity;

import jakarta.persistence.*;
import lombok.Getter;

import java.util.Date;

@Entity
@Table(name = "\"user\"")
public class User {
    @Getter
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false, unique = true)
    private String email;

    @Getter
    @Column(nullable = false)
    private String username;

    @Getter
    @Column(name = "hashed_password", nullable = false)
    private String hashedPassword;

    @Getter
    @ManyToOne
    @JoinColumn(name = "role_id", nullable = false)
    private Role role;

    @Getter
    @Column(name = "registration_date", nullable = false)
    private Date registrationDate;

    @Getter
    @Column(name = "is_active", nullable = false)
    private Boolean isActive;

    @Getter
    @Column(name = "is_superuser", nullable = false)
    private Boolean isSuperuser;

    @Getter
    @Column(name = "is_verified", nullable = false)
    private Boolean isVerified;

    @Getter
    @OneToOne(mappedBy = "user", cascade = CascadeType.ALL, orphanRemoval = true)
    private Courier courier;

    @Getter
    @OneToOne(mappedBy = "user", cascade = CascadeType.ALL, orphanRemoval = true)
    private Customer customer;

    @Getter
    @OneToOne(mappedBy = "user", cascade = CascadeType.ALL, orphanRemoval = true)
    private KitchenWorker kitchenWorker;
}

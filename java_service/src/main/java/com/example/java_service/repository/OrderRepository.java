package com.example.java_service.repository;

import com.example.java_service.entity.Courier;
import com.example.java_service.entity.Order;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface OrderRepository extends JpaRepository<Order, Long> {
    List<Order> findByCourier(Courier courier);
}
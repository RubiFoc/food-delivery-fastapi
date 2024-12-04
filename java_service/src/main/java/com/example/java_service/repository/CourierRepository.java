package com.example.java_service.repository;


import com.example.java_service.entity.Courier;
import org.springframework.data.jdbc.repository.query.Query;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface CourierRepository extends JpaRepository<Courier, Long> {
    @Query("SELECT c FROM Courier c ORDER BY c.rating DESC")
    List<Courier> findTopCourier();
}

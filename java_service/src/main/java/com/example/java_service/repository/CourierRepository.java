package com.example.java_service.repository;

import com.example.java_service.entity.Courier;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.Query;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface CourierRepository extends JpaRepository<Courier, Long> {
    @Query("SELECT c FROM Courier c JOIN FETCH c.user u ORDER BY COALESCE(c.rating, 0) DESC")
    List<Courier> findTopCourier(Pageable pageable);
}

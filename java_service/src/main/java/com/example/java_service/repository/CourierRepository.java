package com.example.java_service.repository;

import com.example.java_service.entity.Courier;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.Date;
import java.util.List;

@Repository
public interface CourierRepository extends JpaRepository<Courier, Long> {

    @Query("SELECT c FROM Courier c " +
            "JOIN c.user u " +
            "JOIN c.orders o " +
            "WHERE o.timeOfCreation BETWEEN :startDate AND :endDate " +
            "GROUP BY c.id, u.id " +
            "ORDER BY COALESCE(c.rating, 0) DESC")
    List<Courier> findTopCourierByPeriod(Pageable pageable, @Param("startDate") Date startDate, @Param("endDate") Date endDate);

}

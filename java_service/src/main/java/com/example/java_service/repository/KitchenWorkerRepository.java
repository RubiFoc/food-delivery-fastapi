package com.example.java_service.repository;

import com.example.java_service.entity.KitchenWorker;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Repository;

import java.util.Date;
import java.util.List;

@Repository
public interface KitchenWorkerRepository extends JpaRepository<KitchenWorker, Long> {

    @Query("""
        SELECT k 
        FROM KitchenWorker k 
        LEFT JOIN k.orders o 
        WHERE o.timeOfCreation BETWEEN :startDate AND :endDate 
        GROUP BY k 
        ORDER BY COUNT(o) DESC
    """)
    List<KitchenWorker> findTopKitchenWorkerByPeriod(Pageable pageable, Date startDate, Date endDate);
}

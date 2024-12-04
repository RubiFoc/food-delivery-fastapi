package com.example.java_service.repository;

import com.example.java_service.entity.KitchenWorker;
import org.springframework.data.jdbc.repository.query.Query;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface KitchenWorkerRepository extends JpaRepository<KitchenWorker, Long> {
    @Query("SELECT k FROM KitchenWorker k ORDER BY size(k.orders) DESC")
    List<KitchenWorker> findTopKitchenWorker();
}

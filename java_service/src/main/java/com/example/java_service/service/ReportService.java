package com.example.java_service.service;

import com.example.java_service.entity.Courier;
import com.example.java_service.entity.KitchenWorker;
import com.example.java_service.entity.Order;
import com.example.java_service.repository.CourierRepository;
import com.example.java_service.repository.KitchenWorkerRepository;
import com.example.java_service.repository.OrderRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.domain.PageRequest;
import org.springframework.stereotype.Service;
import org.springframework.data.domain.Pageable;
import org.springframework.data.domain.PageRequest;


import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

@Service
public class ReportService {

    @Autowired
    private CourierRepository courierRepository;

    @Autowired
    private KitchenWorkerRepository kitchenWorkerRepository;

    @Autowired
    private OrderRepository orderRepository;

    public Courier getTopCourier() {
        Pageable pageable = PageRequest.of(0, 1); // Первая страница, один результат
        List<Courier> couriers = courierRepository.findTopCourier(pageable);
        return couriers.isEmpty() ? null : couriers.get(0);
    }


    public KitchenWorker getTopKitchenWorker() {
        Pageable pageable = PageRequest.of(0, 1); // Первая страница, один результат
        List<KitchenWorker> workers = kitchenWorkerRepository.findTopKitchenWorker(pageable);
        return workers.isEmpty() ? null : workers.get(0);
    }


    public float calculateCourierPay(Courier courier) {
        if (courier == null) return 0;

        List<Order> orders = orderRepository.findByCourier(courier);
        float totalPay = 0;
        for (Order order : orders) {
            totalPay += order.getPrice() * courier.getRate(); // Pay per order
        }
        return totalPay;
    }

    // Новый метод для расчёта выплат всем курьерам
    public Map<Courier, Float> calculateAllCourierPay() {
        List<Courier> couriers = courierRepository.findAll();
        return couriers.stream()
                .collect(Collectors.toMap(
                        courier -> courier,
                        this::calculateCourierPay
                ));
    }

}

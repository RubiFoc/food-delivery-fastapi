package com.example.java_service.service;

import com.example.java_service.entity.Courier;
import com.example.java_service.entity.KitchenWorker;
import com.example.java_service.entity.Order;
import com.example.java_service.repository.CourierRepository;
import com.example.java_service.repository.KitchenWorkerRepository;
import com.example.java_service.repository.OrderRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class ReportService {

    @Autowired
    private CourierRepository courierRepository;

    @Autowired
    private KitchenWorkerRepository kitchenWorkerRepository;

    @Autowired
    private OrderRepository orderRepository;

    public Courier getTopCourier() {
        List<Courier> couriers = courierRepository.findTopCourier();
        return couriers.isEmpty() ? null : couriers.get(0);
    }

    public KitchenWorker getTopKitchenWorker() {
        List<KitchenWorker> workers = kitchenWorkerRepository.findTopKitchenWorker();
        return workers.isEmpty() ? null : workers.get(0);
    }

    public float calculateCourierPay(Courier courier) {
        List<Order> orders = orderRepository.findByCourier(courier);
        float totalPay = 0;
        for (Order order : orders) {
            totalPay += order.getPrice() * courier.getRate(); // Платим по проценту от заказа
        }
        return totalPay;
    }
}

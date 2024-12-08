package com.example.java_service.service;

import com.example.java_service.entity.Courier;
import com.example.java_service.entity.KitchenWorker;
import com.example.java_service.entity.Order;
import com.example.java_service.repository.CourierRepository;
import com.example.java_service.repository.KitchenWorkerRepository;
import com.example.java_service.repository.OrderRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;

import java.util.Calendar;
import java.util.Date;
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

    private Date calculateStartDate(String period) {
        Calendar calendar = Calendar.getInstance();
        switch (period) {
            case "month":
                calendar.add(Calendar.MONTH, -1);
                break;
            case "half-year":
                calendar.add(Calendar.MONTH, -6);
                break;
            case "year":
            default:
                calendar.add(Calendar.YEAR, -1);
                break;
        }
        return calendar.getTime();
    }

    public Courier getTopCourier(String period) {
        Date startDate = calculateStartDate(period);
        Pageable pageable = PageRequest.of(0, 1);
        List<Courier> couriers = courierRepository.findTopCourierByPeriod(pageable, startDate, new Date());
        return couriers.isEmpty() ? null : couriers.get(0);
    }

    public KitchenWorker getTopKitchenWorker(String period) {
        Date startDate = calculateStartDate(period);
        Pageable pageable = PageRequest.of(0, 1);
        List<KitchenWorker> workers = kitchenWorkerRepository.findTopKitchenWorkerByPeriod(pageable, startDate, new Date());
        return workers.isEmpty() ? null : workers.get(0);
    }

    public Map<Courier, Float> calculateAllCourierPay(String period) {
        Date startDate = calculateStartDate(period);
        List<Courier> couriers = courierRepository.findAll();
        return couriers.stream()
                .collect(Collectors.toMap(
                        courier -> courier,
                        courier -> calculateCourierPay(courier, startDate)
                ));
    }

    private float calculateCourierPay(Courier courier, Date startDate) {
        List<Order> orders = orderRepository.findByCourierAndTimeOfCreationAfter(courier, startDate);
        float totalPay = 0;
        for (Order order : orders) {
            totalPay += order.getPrice() * courier.getRate();
        }
        return totalPay;
    }
}

package com.example.java_service.controller;

import com.example.java_service.entity.Courier;
import com.example.java_service.entity.KitchenWorker;
import com.example.java_service.service.ReportService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;

import java.util.Map;

import org.springframework.web.bind.annotation.RequestParam;

@Controller
public class ReportController {

    private final ReportService reportService;

    @Autowired
    public ReportController(ReportService reportService) {
        this.reportService = reportService;
    }

    @GetMapping("/reports")
    public String getReportPage(@RequestParam(name = "period", required = false, defaultValue = "year") String period, Model model) {
        Courier topCourier = reportService.getTopCourier(period);
        KitchenWorker topKitchenWorker = reportService.getTopKitchenWorker(period);
        Map<Courier, Float> courierPayments = reportService.calculateAllCourierPay(period);

        model.addAttribute("topCourier", topCourier != null ? topCourier : new Courier());
        model.addAttribute("topKitchenWorker", topKitchenWorker != null ? topKitchenWorker : new KitchenWorker());
        model.addAttribute("courierPayments", courierPayments);

        return "reports";
    }
}

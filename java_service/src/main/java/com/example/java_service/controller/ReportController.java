package com.example.java_service.controller;

import com.example.java_service.entity.Courier;
import com.example.java_service.entity.KitchenWorker;
import com.example.java_service.service.ReportService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;

@Controller
public class ReportController {

    @Autowired
    private ReportService reportService;

    @GetMapping("/reports")
    public String getReportPage(Model model) {
        // Получаем данные для отчета
        Courier topCourier = reportService.getTopCourier();
        KitchenWorker topKitchenWorker = reportService.getTopKitchenWorker();

        // Добавляем данные в модель
        model.addAttribute("topCourier", topCourier);
        model.addAttribute("topKitchenWorker", topKitchenWorker);

        // Возвращаем имя шаблона для отображения
        return "reports";
    }
}

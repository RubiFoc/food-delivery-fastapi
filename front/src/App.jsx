import React, {useEffect, useState} from 'react';
import axios from 'axios';
import {BrowserRouter as Router, Route, Routes} from "react-router-dom";
import Login from "./components/Login.jsx";
import Register from "./components/Register.jsx";
import MainPage from "./components/MainPage.jsx";
import RegisterAdmin from "./components/RegisterAdmin.jsx";
import CourierWorkerRegister from "./components/CourierWorkerRegister.jsx";
import KitchenOrders from "./components/KitchenOrders.jsx";
import CreateOrder from "./components/CreateOrder.jsx";

const App = () => {
    const [dishes, setDishes] = useState([]);
    const [categories, setCategories] = useState([]);
    const [cart, setCart] = useState([]);

    return (
        <div>
            <Router>
                <Routes>
                    <Route path="/" element={<MainPage/>}/>
                    <Route path="/login" element={<Login/>}/>
                    <Route path="/register" element={<Register/>}/>
                    <Route path="/admin/register" element={<RegisterAdmin/>}/>
                    <Route path="/register/courier_or_worker" element={<CourierWorkerRegister/>}/>
                    <Route path="/kitchen_orders" element={<KitchenOrders/>}/>
                    <Route path="/create_order" element={<CreateOrder/>}/>


                </Routes>
            </Router>
        </div>
    );
};

export default App;

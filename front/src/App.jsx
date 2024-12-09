import React, {useEffect, useState} from 'react';
import axios from 'axios';
import {BrowserRouter as Router, Route, Routes} from "react-router-dom";
import Login from "./components/Login.jsx";
import Register from "./components/Register.jsx";
import MainPage from "./components/MainPage.jsx";
import RegisterAdmin from "./components/RegisterAdmin.jsx";
import CourierWorkerRegister from "./components/CourierWorkerRegister.jsx";
import KitchenOrders from "./components/KitchenOrders.jsx";
import CourierPage from "./components/CourierPage.jsx";
import OrderPage from "./components/OrderPage.jsx";
import AddBalance from "./components/AddBalance.jsx";
import './index.css'
import UpdateLocation from "./components/UpdateLocation.jsx";
import AdminPanel from "./components/AdminPanel.jsx";

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
                    <Route path="/create_order" element={<OrderPage/>}/>
                    <Route path="/add_balance" element={<AddBalance/>}/>
                    <Route path="/courier/take_order" element={<CourierPage/>}/>
                    <Route path="/customer/location" element={<UpdateLocation/>}/>
                    <Route path="/admin" element={<AdminPanel/>}/>

                </Routes>
            </Router>
        </div>
    );
};

export default App;

import React, { useEffect, useState } from 'react';
import axios from 'axios';
import DishList from './components/DishList.jsx';
import Cart from './components/Cart.jsx';
import OrderForm from './components/OrderFrom.jsx';
import {BrowserRouter as Router, Route, Routes} from "react-router-dom";
import Login from "./components/Login.jsx";

const App = () => {
  const [dishes, setDishes] = useState([]);
  const [categories, setCategories] = useState([]);
  const [cart, setCart] = useState([]);

// useState  useEffect(() => {
//     // Получаем данные о блюдах и категориях с API
//     async function fetchDishes() {
//       try {
//         const dishesResponse = await axios.get('/api/dishes');
//         setDishes(dishesResponse.data);
//       } catch (error) {
//         console.error('Ошибка при загрузке данных:', error);
//       }
//     }
//
//     async function fetchCategories() {
//       try {
//         const categoriesResponse = await axios.get('/api/dish-categories');
//         setCategories(categoriesResponse.data);
//       } catch (error) {
//         console.error('Ошибка при получении категорий:', error);
//       }
//     }
//
//     fetchDishes();
//     fetchCategories();
//   }, []);
//
//   // Функция для добавления блюда в корзину
//   const addToCart = (dish) => {
//     setCart([...cart, dish]);
//   };
//
//   // Функция для оформления заказа
//   const placeOrder = async () => {
//     try {
//       const orderData = {
//         dishes: cart,
//         total_price: cart.reduce((acc, dish) => acc + dish.price, 0),
//       };
//
//       await axios.post('/api/orders', orderData);
//       alert('Ваш заказ принят!');
//     } catch (error) {
//       console.error('Ошибка при отправке заказа:', error);
//     }
//   };

  return (
    <div>
      <Router>
        <Routes>
        <Route path="/login" element={<Login/>}/>
          </Routes>
      </Router>
    </div>
  );
};

export default App;
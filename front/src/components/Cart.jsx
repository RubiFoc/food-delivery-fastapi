import React from 'react';

const Cart = ({ cart }) => {
  return (
    <div>
      <h2>Корзина</h2>
      <ul>
        {cart.map((dish, index) => (
          <li key={index}>
            {dish.name} - {dish.price} ₽
          </li>
        ))}
      </ul>
      <p>Общая стоимость: {cart.reduce((acc, dish) => acc + dish.price, 0)} ₽</p>
    </div>
  );
};

export default Cart;

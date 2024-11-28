import React from 'react';

const OrderForm = ({ placeOrder }) => {
  return (
    <div>
      <button onClick={placeOrder}>Оформить заказ</button>
    </div>
  );
};

export default OrderForm;

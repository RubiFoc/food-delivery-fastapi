import React, { useState, useEffect } from 'react';

const CreateOrderPage = () => {
  const [cartItems, setCartItems] = useState([]);
  const [orderStatus, setOrderStatus] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Загружаем корзину пользователя при монтировании компонента
  useEffect(() => {
    const fetchCart = async () => {
      try {
        const response = await fetch('/cart', {
          method: 'GET',
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('authToken')}`, // Токен аутентификации
          }
        });

        if (!response.ok) {
          throw new Error('Failed to fetch cart');
        }

        const data = await response.json();
        setCartItems(data.dishes || []);
      } catch (error) {
        setOrderStatus('Ошибка при загрузке корзины.');
      }
    };

    fetchCart();
  }, []);

  // Обработчик для отправки заказа
  const handleSubmitOrder = async () => {
    if (cartItems.length === 0) {
      setOrderStatus('Корзина пуста.');
      return;
    }

    setIsSubmitting(true);
    setOrderStatus('');

    try {
      // Отправляем запрос на создание заказа
      const response = await fetch('/cart/create-order', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('authToken')}`, // Токен аутентификации
        },
        body: JSON.stringify({}), // Пустое тело, так как все данные берутся с сервера
      });

      if (!response.ok) {
        const errorData = await response.json();
        setOrderStatus(`Ошибка: ${errorData.detail || 'Неизвестная ошибка'}`);
        return;
      }

      const orderData = await response.json();
      setOrderStatus('Заказ успешно создан!');
      setCartItems([]); // Очищаем корзину после оформления заказа
    } catch (error) {
      setOrderStatus('Ошибка при оформлении заказа.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div>
      <h1>Оформление заказа</h1>

      {orderStatus && <div>{orderStatus}</div>}

      {cartItems.length > 0 ? (
        <>
          <ul>
            {cartItems.map((item, index) => (
              <li key={index}>
                {item.dish.name} - {item.quantity} шт.
                <span>Цена: {item.dish.price * item.quantity} руб.</span>
              </li>
            ))}
          </ul>
          <button onClick={handleSubmitOrder} disabled={isSubmitting}>
            {isSubmitting ? 'Оформление заказа...' : 'Оформить заказ'}
          </button>
        </>
      ) : (
        <p>В вашей корзине нет товаров.</p>
      )}
    </div>
  );
};

export default CreateOrderPage;

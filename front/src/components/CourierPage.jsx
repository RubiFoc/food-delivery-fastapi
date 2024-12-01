import React, { useState, useEffect } from 'react';

const CourierPage = () => {
  const [orders, setOrders] = useState([]);
  const [assignedOrders, setAssignedOrders] = useState([]);  // State для взятых заказов
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [token, setToken] = useState('');
  const [courierLocation, setCourierLocation] = useState('');

  useEffect(() => {
    const storedToken = localStorage.getItem('token');
    if (storedToken) {
      setToken(storedToken);
      fetchOrders(storedToken);        // Получение доступных заказов
      fetchAssignedOrders(storedToken); // Получение взятых заказов
    } else {
      setError('Token not found');
      setLoading(false);
    }
  }, []);

  // Функция для получения доступных заказов
  const fetchOrders = async (token) => {
    try {
      const response = await fetch('http://127.0.0.1:8000/courier/orders/not_delivered', {
        method: 'GET',
        headers: {
          'accept': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setOrders(data);
      } else {
        throw new Error(`Error ${response.status}: Unable to fetch orders`);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // Функция для получения взятых заказов
  const fetchAssignedOrders = async (token) => {
    try {
      const response = await fetch('http://127.0.0.1:8000/courier/orders/assigned', {
        method: 'GET',
        headers: {
          'accept': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setAssignedOrders(data);
      } else {
        throw new Error(`Error ${response.status}: Unable to fetch assigned orders`);
      }
    } catch (err) {
      setError(err.message);
    }
  };

  // Обработка взятия заказа
  const handleTakeOrder = async (orderId) => {
    if (!courierLocation) {
      alert('Please enter your location.');
      return;
    }

    try {
      const response = await fetch(`http://127.0.0.1:8000/courier/orders/${orderId}/take?courier_location=${encodeURIComponent(courierLocation)}`, {
        method: 'POST',
        headers: {
          'accept': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
      });

      if (response.ok) {
        alert(`Order ${orderId} taken successfully!`);
        fetchOrders(token);          // Обновление списка доступных заказов
        fetchAssignedOrders(token);  // Обновление списка взятых заказов
      } else {
        const errorData = await response.json();
        throw new Error(`Error ${response.status}: ${errorData.detail || 'Unknown error'}`);
      }
    } catch (err) {
      setError(err.message);
    }
  };

  // Обработка доставки заказа
const handleDeliverOrder = async (orderId) => {
  try {
    const response = await fetch(`http://127.0.0.1:8000/courier/${orderId}/deliver`, {
      method: 'PUT',
      headers: {
        'Accept': 'application/json',
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        order_id: orderId,
        is_prepared: true,
        is_delivered: true,
      }),
    });

    if (response.ok) {
      // Обновляем список взятых заказов после успешной доставки
      alert(`Order ${orderId} delivered successfully!`);
      fetchAssignedOrders(token); // Обновление списка взятых заказов
    } else {
      console.error('Failed to deliver the order');
    }
  } catch (error) {
    console.error('Error:', error);
  }
};

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <div>
      <h2>Available Orders</h2>
      <div>
        <label htmlFor="courierLocation">Courier Location: </label>
        <input
          type="text"
          id="courierLocation"
          value={courierLocation}
          onChange={(e) => setCourierLocation(e.target.value)}
          placeholder="Enter your location"
        />
      </div>

      <ul>
        {orders.map((order) => (
          <li key={order.order_id}>
            Order ID: {order.order_id}, Prepared: {order.is_prepared ? 'Yes' : 'No'}
            {!order.is_delivered && !order.is_taken && (
              <button onClick={() => handleTakeOrder(order.order_id)}>Take Order</button>
            )}
          </li>
        ))}
      </ul>

      <h2>Assigned Orders</h2>
      {assignedOrders.length === 0 ? (
        <p>No orders assigned.</p>
      ) : (
        <ul>
          {assignedOrders.map((order) => (
            <li key={order.order_id}>
              Order ID: {order.order_id}, Prepared: {order.is_prepared ? 'Yes' : 'No'}, Delivered: {order.is_delivered ? 'Yes' : 'No'}
              {!order.is_delivered && (
                <button onClick={() => handleDeliverOrder(order.order_id)}>Mark as Delivered</button>
              )}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default CourierPage;

import React, { useState, useEffect } from 'react';
import './styles/AdminPanel.css';

function Orders({ token }) {
    const [orders, setOrders] = useState([]);
    const [error, setError] = useState('');
    const [updatingOrderId, setUpdatingOrderId] = useState(null);

    useEffect(() => {
        fetchOrders();
    }, []);

    const fetchOrders = async () => {
        try {
            const response = await fetch('http://127.0.0.1:8000/admins/order_statuses', {
                headers: { 'Authorization': `Bearer ${token}` },
            });

            if (response.ok) {
                const data = await response.json();
                setOrders(data);
            } else {
                setError('Не удалось загрузить заказы');
            }
        } catch (err) {
            console.error('Ошибка при загрузке заказов:', err);
            setError('Ошибка загрузки заказов');
        }
    };

    const handleUpdateOrderStatus = async (orderId, updatedStatus) => {
        try {
            const response = await fetch(`http://127.0.0.1:8000/admins/order_status/${orderId}`, {
                method: 'PUT',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(updatedStatus),
            });

            if (response.ok) {
                fetchOrders(); // Перезагружаем список заказов после обновления
                setUpdatingOrderId(null);
            } else {
                setError('Не удалось обновить статус заказа');
            }
        } catch (err) {
            console.error('Ошибка при обновлении статуса заказа:', err);
            setError('Ошибка обновления статуса заказа');
        }
    };

    const handleStatusChange = (orderId, field) => {
        setOrders(prevOrders =>
            prevOrders.map(order =>
                order.order_id === orderId
                    ? { ...order, [field]: !order[field] }
                    : order
            )
        );
    };

    return (
        <div className="orders-container">
            <h1 className="page-title">Заказы</h1>
            {error && <p className="error-message">{error}</p>}
            <div className="table-container">
                <table className="orders-table">
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Статус приготовления</th>
                            <th>Статус доставки</th>
                            <th>Действия</th>
                        </tr>
                    </thead>
                    <tbody>
                        {orders.map(order => (
                            <tr key={order.order_id}>
                                <td>{order.order_id}</td>
                                <td>{order.is_prepared ? 'Готов' : 'Не готов'}</td>
                                <td>{order.is_delivered ? 'Доставлен' : 'Не доставлен'}</td>
                                <td>
                                    <button
                                        className="edit-btn"
                                        onClick={() => setUpdatingOrderId(order.order_id)}
                                    >
                                        Изменить статус
                                    </button>
                                    {updatingOrderId === order.order_id && (
                                        <div className="status-update">
                                            <label>
                                                Статус приготовления:
                                                <input
                                                    type="checkbox"
                                                    checked={order.is_prepared}
                                                    onChange={() => handleStatusChange(order.order_id, 'is_prepared')}
                                                />
                                            </label>
                                            <label>
                                                Статус доставки:
                                                <input
                                                    type="checkbox"
                                                    checked={order.is_delivered}
                                                    onChange={() => handleStatusChange(order.order_id, 'is_delivered')}
                                                />
                                            </label>
                                            <button
                                                className="save-btn"
                                                onClick={() => handleUpdateOrderStatus(order.order_id, {
                                                    is_prepared: order.is_prepared,
                                                    is_delivered: order.is_delivered
                                                })}
                                            >
                                                Сохранить изменения
                                            </button>
                                        </div>
                                    )}
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
}

export default Orders;

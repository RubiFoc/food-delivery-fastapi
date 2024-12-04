import { useEffect, useState } from 'react';
import { Button, Card, message, Spin, Modal } from 'antd';
import './styles/KitchenOrders.css';

function KitchenOrders() {
    const [orders, setOrders] = useState([]);
    const [loading, setLoading] = useState(false);
    const [updatingOrderId, setUpdatingOrderId] = useState(null);
    const [orderDetails, setOrderDetails] = useState(null);
    const [isModalVisible, setIsModalVisible] = useState(false);

    const getAuthToken = () => {
        return localStorage.getItem('token');
    };

    const fetchOrders = async () => {
        setLoading(true);
        try {
            const token = getAuthToken();
            const response = await fetch('http://127.0.0.1:8000/kitchen_worker/orders/not_ready', {
                method: 'GET',
                headers: {
                    'Accept': 'application/json',
                    'Authorization': `Bearer ${token}`,
                },
                credentials: 'include',
            });
            if (!response.ok) {
                throw new Error('Failed to fetch orders');
            }
            const data = await response.json();
            setOrders(data);
        } catch (error) {
            console.error(error);
            message.error('Ошибка при загрузке заказов');
        } finally {
            setLoading(false);
        }
    };

    const markAsPrepared = async (orderId) => {
        setUpdatingOrderId(orderId);
        setLoading(true);
        try {
            const token = getAuthToken();
            const response = await fetch(`http://127.0.0.1:8000/kitchen_worker/${orderId}/prepare`, {
                method: 'PUT',
                headers: {
                    'Accept': 'application/json',
                    'Authorization': `Bearer ${token}`,
                },
                credentials: 'include',
            });
            if (!response.ok) {
                throw new Error('Failed to update order');
            }
            message.success(`Заказ ${orderId} отмечен как выполненный`);
            fetchOrders();
        } catch (error) {
            console.error(error);
            message.error('Ошибка при обновлении заказа');
        } finally {
            setLoading(false);
            setUpdatingOrderId(null);
        }
    };

    const fetchOrderDetails = async (orderId) => {
        try {
            const token = getAuthToken();
            const response = await fetch(`http://127.0.0.1:8000/kitchen_worker/orders/${orderId}`, {
                method: 'GET',
                headers: {
                    'Accept': 'application/json',
                    'Authorization': `Bearer ${token}`,
                },
            });
            if (!response.ok) {
                throw new Error('Failed to fetch order details');
            }
            const data = await response.json();
            setOrderDetails(data);
            setIsModalVisible(true);
        } catch (error) {
            console.error(error);
            message.error('Ошибка при загрузке деталей заказа');
        }
    };

    const closeModal = () => {
        setIsModalVisible(false);
        setOrderDetails(null);
    };

    const handleLogout = () => {
        localStorage.removeItem('token');
        window.location.href = '/login';
    };

    useEffect(() => {
        fetchOrders();
    }, []);

    return (
        <div className="orders-container">
            <div className="orders-header">
                <h1>Невыполненные заказы</h1>
                {loading ? (
                    <Spin size="large" className="loading-spinner" />
                ) : (
                    <div className="orders-grid">
                        {orders.length === 0 ? (
                            <p className="no-orders-text">Нет невыполненных заказов</p>
                        ) : (
                            orders.map(order => (
                                <Card key={order.order_id} className="order-card">
                                    <p className="order-id">Заказ ID: {order.order_id}</p>
                                    <p>Статус: {order.is_prepared ? 'Готов' : 'Не готов'}</p>
                                    <Button
                                        type="primary"
                                        className={`action-btn ${updatingOrderId === order.order_id ? 'processing' : ''}`}
                                        onClick={() => markAsPrepared(order.order_id)}
                                        disabled={updatingOrderId === order.order_id || order.is_prepared}
                                    >
                                        {updatingOrderId === order.order_id ? 'Обрабатывается...' : 'Выполнен'}
                                    </Button>
                                    <Button
                                        type="default"
                                        className="action-btn"
                                        onClick={() => fetchOrderDetails(order.order_id)}
                                    >
                                        Подробнее
                                    </Button>
                                </Card>
                            ))
                        )}
                    </div>
                )}
            </div>

            <Modal
                title="Детали заказа"
                visible={isModalVisible}
                onCancel={closeModal}
                footer={null}
            >
                <div>
                    <h3>Блюда в заказе:</h3>
                    {orderDetails?.dishes && orderDetails.dishes.length > 0 ? (
                        orderDetails.dishes.map(dish => (
                            <div key={dish.dish.id} className="dish-details">
                                <span>{dish.dish.name} (x{dish.quantity})</span>
                                <span>Цена: {dish.dish.price} руб.</span>
                            </div>
                        ))
                    ) : (
                        <p>Нет блюд в заказе</p>
                    )}
                </div>
            </Modal>

            <Button
                type="default"
                className="logout-btn"
                onClick={handleLogout}
            >
                Выход
            </Button>
        </div>
    );
}

export default KitchenOrders;

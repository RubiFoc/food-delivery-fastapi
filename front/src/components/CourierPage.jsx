import React, {useState, useEffect} from 'react';
import {Button, Modal, message, Spin} from 'antd';
import Header from './Header'; // Импорт компонента Header
import './styles/CourierPage.css';

const CourierPage = () => {
    const [orders, setOrders] = useState([]);
    const [assignedOrders, setAssignedOrders] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [token, setToken] = useState('');
    const [courierLocation, setCourierLocation] = useState('');
    const [orderInfo, setOrderInfo] = useState(null);
    const [isModalVisible, setIsModalVisible] = useState(false);
    const [currentOrderId, setCurrentOrderId] = useState(null);
    const [isAuthenticated, setIsAuthenticated] = useState(false); // Для проверки аутентификации
    const [roleId, setRoleId] = useState(2); // Роль курьера

    useEffect(() => {
        const storedToken = localStorage.getItem('token');
        if (storedToken) {
            setToken(storedToken);
            setIsAuthenticated(true); // Пользователь аутентифицирован
            fetchOrders(storedToken);
            fetchAssignedOrders(storedToken);
        } else {
            setError('Токен не найден');
            setLoading(false);
        }
    }, []);

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
                throw new Error(`Ошибка ${response.status}: Не удалось получить заказы`);
            }
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

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
                throw new Error(`Ошибка ${response.status}: Не удалось получить назначенные заказы`);
            }
        } catch (err) {
            setError(err.message);
        }
    };

    const fetchOrderInfo = async (orderId) => {
        try {
            const response = await fetch(`http://127.0.0.1:8000/courier/orders/${orderId}/info`, {
                method: 'GET',
                headers: {
                    'Accept': 'application/json',
                    'Authorization': `Bearer ${token}`,
                },
            });

            if (response.ok) {
                const data = await response.json();
                setOrderInfo(data);
                setCurrentOrderId(orderId);
                setIsModalVisible(true);
            } else {
                throw new Error(`Ошибка ${response.status}: Не удалось получить информацию о заказе`);
            }
        } catch (err) {
            setError(err.message);
        }
    };

    const closeModal = () => {
        setIsModalVisible(false);
        setOrderInfo(null);
    };

    const handleTakeOrder = async (orderId) => {
        if (!courierLocation) {
            alert('Пожалуйста, укажите ваше местоположение.');
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
                alert(`Заказ ${orderId} успешно принят!`);
                fetchOrders(token);
                fetchAssignedOrders(token);
            } else {
                const errorData = await response.json();
                throw new Error(`Ошибка ${response.status}: ${errorData.detail || 'Неизвестная ошибка'}`);
            }
        } catch (err) {
            setError(err.message);
        }
    };

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
                alert(`Заказ ${orderId} успешно доставлен!`);
                fetchAssignedOrders(token); // Обновить назначенные заказы
            } else {
                console.error('Не удалось доставить заказ');
            }
        } catch (error) {
            console.error('Ошибка:', error);
        }
    };

    if (loading) return <div className="courier-loading-spinner"><Spin size="large"/></div>;
    if (error) return <div className="courier-error-message">Ошибка: {error}</div>;

    return (
        <div className="courier-page">
            {/* Добавляем Header */}
            <Header
                isAuthenticated={isAuthenticated}
                handleLogout={() => {
                    localStorage.removeItem('token');
                    setIsAuthenticated(false);
                    setToken('');
                }}
                role_id={roleId} // Роль курьера
            />
            <div className="courier-header">
                <h1>Заказы Курьера</h1>
                <div className="courier-location">
                    <label htmlFor="courierLocation">Местоположение курьера: </label>
                    <input
                        type="text"
                        id="courierLocation"
                        value={courierLocation}
                        onChange={(e) => setCourierLocation(e.target.value)}
                        placeholder="Введите ваше местоположение"
                    />
                </div>
            </div>

            <div className="orders-container">
                {/* Доступные заказы */}
                <div className="orders-section">
                    <h2>Доступные заказы</h2>
                    <div className="orders-grid">
                        {orders.map((order) => (
                            order.is_prepared &&
                            <div key={order.order_id} className="order-card">
                                <p><strong>Номер заказа:</strong> {order.order_id}</p>
                                <p><strong>Готовность:</strong> {order.is_prepared ? 'Да' : 'Нет'}</p>
                                <Button className="action-btn" onClick={() => handleTakeOrder(order.order_id)}>
                                    Принять заказ
                                </Button>
                                <Button className="action-btn" onClick={() => fetchOrderInfo(order.order_id)}>
                                    Просмотр деталей
                                </Button>
                            </div>
                        ))}
                    </div>
                </div>

                <hr className="orders-separator"/>

                {/* Назначенные заказы */}
                <div className="orders-section">
                    <h2>Назначенные заказы</h2>
                    <div className="orders-grid">
                        {assignedOrders
                            .sort((a, b) => a.is_delivered - b.is_delivered) // Сортировка по полю is_delivered
                            .map((order) => (
                                <div key={order.order_id} className="order-card">
                                    <p><strong>Номер заказа:</strong> {order.order_id}</p>
                                    <p><strong>Готовность:</strong> {order.is_prepared ? 'Да' : 'Нет'}</p>
                                    <p><strong>Доставлено:</strong> {order.is_delivered ? 'Да' : 'Нет'}</p>

                                    {/* Отображаем кнопку "Отметить как доставленный" только для недоставленных заказов */}
                                    {!order.is_delivered && (
                                        <Button className="action-btn"
                                                onClick={() => handleDeliverOrder(order.order_id)}>
                                            Отметить как доставленный
                                        </Button>
                                    )}

                                    <Button className="action-btn" onClick={() => fetchOrderInfo(order.order_id)}>
                                        Просмотр деталей
                                    </Button>
                                </div>
                            ))}
                    </div>
                </div>

            </div>

            <Modal
                title="Детали заказа"
                visible={isModalVisible}
                onCancel={closeModal}
                footer={null}
                className="order-modal"
            >
                <div className="modal-content">
                    {orderInfo ? (
                        <>
                            <p><strong>Стоимость:</strong> {orderInfo.cost}</p>
                            <p><strong>Дата создания:</strong> {orderInfo.creation_date}</p>
                            <p><strong>Вес:</strong> {orderInfo.weight}</p>
                            <p><strong>Местоположение:</strong> {orderInfo.location}</p>
                        </>
                    ) : (
                        <p>Загружаем детали заказа...</p>
                    )}
                </div>
            </Modal>
        </div>
    );
}

export default CourierPage;

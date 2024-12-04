import { useEffect, useState } from 'react';
import { Button, Card, message } from 'antd';
import 'tailwindcss/tailwind.css';

function KitchenOrders() {
    const [orders, setOrders] = useState([]);
    const [loading, setLoading] = useState(false);
    const [token, setToken] = useState(localStorage.getItem('token'));

    const fetchOrders = async () => {
        setLoading(true);
        try {
            const response = await fetch('http://127.0.0.1:8000/kitchen_worker/orders/not_ready', {
                method: 'GET',
                headers: {
                    'Accept': 'application/json',
                    'Authorization': `Bearer ${token}`,
                },
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
        setLoading(true);
        try {
            const response = await fetch(`http://127.0.0.1:8000/kitchen_worker/${orderId}/prepare`, {
                method: 'PUT',
                headers: {
                    'Accept': 'application/json',
                    'Authorization': `Bearer ${token}`,
                },
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
        }
    };

    useEffect(() => {
        fetchOrders();
    }, [token]);

    return (
        <div className="min-h-screen flex items-center justify-center bg-gray-100">
            <div className="max-w-4xl w-full p-6">
                <h1 className="text-3xl font-bold text-center mb-8">Невыполненные заказы</h1>
                {loading ? (
                    <p className="text-center text-gray-500">Загрузка...</p>
                ) : (
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        {orders.length === 0 ? (
                            <p className="col-span-2 text-center text-gray-500">Нет невыполненных заказов</p>
                        ) : (
                            orders.map(order => (
                                <Card key={order.order_id} className="shadow-md">
                                    <p className="text-lg font-semibold">Заказ ID: {order.order_id}</p>
                                    <p>Статус: {order.is_prepared ? 'Готов' : 'Не готов'}</p>
                                    <Button
                                        type="primary"
                                        className={`mt-4 w-full ${loading ? 'bg-gray-400 cursor-not-allowed' : ''}`}
                                        onClick={() => markAsPrepared(order.order_id)}
                                        disabled={loading || order.is_prepared}
                                    >
                                        {loading ? 'Обрабатывается...' : 'Выполнен'}
                                    </Button>
                                </Card>
                            ))
                        )}
                    </div>
                )}
            </div>
        </div>
    );
}

export default KitchenOrders;

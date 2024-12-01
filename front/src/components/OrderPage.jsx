import { useEffect, useState } from 'react';
import { Button, Card, message, Spin } from 'antd';
import { useNavigate } from 'react-router-dom';
import 'tailwindcss/tailwind.css';

function OrderPage() {
    const [cart, setCart] = useState([]);  // Убедитесь, что cart всегда массив
    const [totalPrice, setTotalPrice] = useState(0);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [isAuthenticated, setIsAuthenticated] = useState(false);
    const [token, setToken] = useState(localStorage.getItem('token'));
    const navigate = useNavigate();

    // Проверка аутентификации
    useEffect(() => {
        const checkAuth = async () => {
            if (!token) {
                setIsAuthenticated(false);
                return;
            }
            try {
                const response = await fetch('http://127.0.0.1:8000/auth/me', {
                    method: 'GET',
                    headers: {
                        'Authorization': `Bearer ${token}`,
                    },
                });

                if (response.ok) {
                    setIsAuthenticated(true);
                    fetchCart(); // Получение корзины при успешной аутентификации
                } else {
                    setIsAuthenticated(false);
                }
            } catch (error) {
                console.error('Authentication check failed:', error);
                setIsAuthenticated(false);
            }
        };
        checkAuth();
    }, [token]);

    // Функция для получения информации о блюде по dish_id
    const fetchDishDetails = async (dish_id) => {
        const response = await fetch(`http://127.0.0.1:8000/api/dishes/${dish_id}`, {
            method: 'GET',
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
            },
        });
        if (!response.ok) {
            throw new Error('Failed to fetch dish details');
        }
        return response.json();
    };

    // Функция для получения корзины
    const fetchCart = async () => {
        setLoading(true);
        try {
            const response = await fetch('http://127.0.0.1:8000/api/cart', {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${token}`,
                },
            });

            if (!response.ok) throw new Error('Failed to fetch cart');
            const data = await response.json();
            const updatedCart = await Promise.all(
                data.dishes.map(async (item) => {
                    const dishDetails = await fetchDishDetails(item.dish_id);
                    return {
                        ...item,
                        dish_name: dishDetails.name,  // Название блюда
                        price: dishDetails.price,     // Цена блюда
                    };
                })
            );
            setCart(updatedCart);
            calculateTotal(updatedCart); // Расчёт общей стоимости
        } catch (error) {
            setError('Failed to fetch cart');
            console.error(error);
        } finally {
            setLoading(false);
        }
    };

    // Функция для расчета общей стоимости
    const calculateTotal = (dishes) => {
        const total = dishes.reduce((sum, dish) => sum + dish.price * dish.quantity, 0);
        setTotalPrice(total);
    };

    // Функция для оформления заказа
    const handleCreateOrder = async () => {
        setLoading(true);
        try {
            const response = await fetch('http://127.0.0.1:8000/api/cart/create-order', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`,
                },
                body: JSON.stringify({ dishes: cart }),
            });

            if (response.ok) {
                const orderData = await response.json();
                navigate(`/`); // Переход на страницу подтверждения заказа
            } else {
                throw new Error('Failed to create order');
            }
        } catch (error) {
            setError('Failed to create order');
            console.error(error);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen flex items-center justify-center bg-gray-100">
            <div className="max-w-4xl w-full p-6">
                <h1 className="text-3xl font-bold text-center mb-8">Ваш заказ</h1>
                {loading ? (
                    <div className="text-center">
                        <Spin size="large" />
                        <p>Загрузка...</p>
                    </div>
                ) : (
                    <div>
                        {cart.length === 0 ? (
                            <p className="text-center text-gray-500">Ваш заказ пуст</p>
                        ) : (
                            <div>
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
                                    {cart.map((item) => (
                                        <Card key={item.dish_id} className="shadow-md">
                                            <p className="text-lg font-semibold">{item.dish_name}</p>
                                            <p>Количество: {item.quantity}</p>
                                            <p>Цена за штуку: {item.price} Р</p>
                                            <p>Сумма: {item.quantity * item.price} Р</p>
                                        </Card>
                                    ))}
                                </div>
                                <p>Общая стоимость: {totalPrice} Р</p>
                            </div>
                        )}
                        <div className="mt-8 text-center">
                            <Button
                                type="primary"
                                onClick={handleCreateOrder}
                                disabled={cart.length === 0 || loading}
                            >
                                Оформить заказ
                            </Button>
                        </div>
                    </div>
                )}
                {error && (
                    <div className="text-red-500 text-center mt-4">
                        <p>{error}</p>
                    </div>
                )}
            </div>
        </div>
    );
}

export default OrderPage;

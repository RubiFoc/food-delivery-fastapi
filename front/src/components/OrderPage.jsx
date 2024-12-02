import { useEffect, useState } from 'react';
import { Button, Card, message, Spin } from 'antd';
import { useNavigate } from 'react-router-dom';
import './styles/Order.css'; // Подключаем стили

function OrderPage() {
    const [token, setToken] = useState(localStorage.getItem('token'));
    const [cart, setCart] = useState([]);  // Убедитесь, что cart всегда массив
    const [totalPrice, setTotalPrice] = useState(0);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const navigate = useNavigate();
    const [balance, setBalance] = useState(0);

    // Проверка аутентификации
    useEffect(() => {
        const checkAuth = async () => {
            const storedToken = localStorage.getItem('token');
            if (storedToken) {
                setToken(storedToken);
                fetchCart(storedToken);  // Получаем данные корзины
                fetchBalance(storedToken);  // Получаем баланс
            } else {
                setError('Token not found');
            }
        };
        checkAuth();
    }, []);

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
    const fetchCart = async (token) => {
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

    // Функция для получения баланса
    const fetchBalance = async (token) => {
        try {
            const response = await fetch('http://127.0.0.1:8000/auth/user/balance', {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${token}`,
                },
            });

            if (response.ok) {
                const data = await response.json();
                setBalance(data.balance);
            } else {
                setBalance(0);
            }
        } catch (error) {
            console.error('Ошибка при получении баланса:', error);
            setError('Не удалось получить баланс');
        }
    };

    const handleLogout = async () => {
        try {
            await fetch('http://127.0.0.1:8000/auth/jwt/logout', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`,
                },
            });
            localStorage.removeItem('token');
            setToken(null);
            setCart([]);
            setBalance(0);
        } catch (error) {
            console.error('Ошибка при выходе:', error);
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
                body: JSON.stringify({dishes: cart}),
            });

            if (response.ok) {
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
        <div className="main-container">
            <header className="header">
                <div className="logo-and-balance">
                    <a href="/" className="logo">
                        <img src="src/components/images/logo.png" alt="Logo"/>
                        <span>My Food App</span>
                    </a>
                    {token && (
                        <div className="balance-section">
                            <span className="balance">Баланс: {balance} ₽</span>
                        </div>
                    )}
                </div>
                <button className="back-to-home" onClick={() => navigate('/')}>
                    На главную
                </button>
            </header>

            <div className="main-content">
                <h1 className="title">Ваш заказ</h1>
                {loading ? (
                    <div className="text-center">
                        <Spin size="large"/>
                        <p>Загрузка...</p>
                    </div>
                ) : (
                    <div>
                        {cart.length === 0 ? (
                            <p className="text-center text-gray-500">Ваш заказ пуст</p>
                        ) : (
                            <div>
                                <div className="dishes-grid">
                                    {cart.map((item) => (
                                        <Card key={item.dish_id} className="dish-card">
                                            <p className="dish-title">{item.dish_name}</p>
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
                {error && <p className="text-center text-red-500">{error}</p>}
            </div>
        </div>
    );
}

export default OrderPage;

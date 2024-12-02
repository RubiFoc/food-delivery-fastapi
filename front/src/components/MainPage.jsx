import { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Button, Select, Spin, message } from 'antd';
import { LogoutOutlined, ShoppingCartOutlined, PlusCircleOutlined } from '@ant-design/icons';
import './styles/style.css';  // Импорт CSS-файла

function MainPage() {
    const [token, setToken] = useState(localStorage.getItem('token'));
    const [isAuthenticated, setIsAuthenticated] = useState(false);
    const [error, setError] = useState('');
    const [dishes, setDishes] = useState([]);
    const [categories, setCategories] = useState([]);
    const [selectedCategory, setSelectedCategory] = useState('');
    const [loading, setLoading] = useState(true);
    const [cart, setCart] = useState([]);
    const [customerId, setCustomerId] = useState(null);
    const [balance, setBalance] = useState(0);
    const navigate = useNavigate();

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
                    const userData = await response.json();
                    setCustomerId(userData.id);
                    setIsAuthenticated(true);
                    fetchCategories();
                    fetchDishes();
                    fetchBalance();
                } else {
                    setIsAuthenticated(false);
                }
            } catch (error) {
                console.error('Ошибка при проверке аутентификации:', error);
                setIsAuthenticated(false);
            }
        };
        checkAuth();
    }, [token]);

    useEffect(() => {
        fetchDishes();
    }, [selectedCategory]);

    const fetchCategories = async () => {
        try {
            const response = await fetch('http://127.0.0.1:8000/api/dish-categories', {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${token}`,
                },
            });

            if (!response.ok) throw new Error('Не удалось загрузить категории');
            const data = await response.json();
            setCategories(data);
        } catch (error) {
            console.error(error);
            setError('Не удалось загрузить категории, попробуйте снова');
        }
    };

    const fetchDishes = async () => {
        setLoading(true);
        setError('');
        try {
            const url = selectedCategory
                ? `http://127.0.0.1:8000/api/dishes/category/${selectedCategory}`
                : 'http://127.0.0.1:8000/api/dishes';

            const response = await fetch(url, {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${token}`,
                },
            });

            if (!response.ok) throw new Error('Не удалось загрузить блюда');
            const data = await response.json();
            setDishes(data);
        } catch (error) {
            console.error(error);
            setError('Не удалось загрузить блюда, попробуйте снова');
        } finally {
            setLoading(false);
        }
    };

    const fetchBalance = async () => {
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
            setIsAuthenticated(false);
            setDishes([]);
            setCart([]);
            setBalance(0);
        } catch (error) {
            console.error('Ошибка при выходе:', error);
        }
    };

    const handleCategoryChange = (value) => {
        setSelectedCategory(value);
    };

    const addToCart = async (dish) => {
        try {
            const response = await fetch('http://127.0.0.1:8000/api/cart/add-dish', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`,
                },
                body: JSON.stringify({
                    dish_id: dish.id,
                    quantity: 1,
                }),
            });

            if (!response.ok) throw new Error('Не удалось добавить блюдо в корзину');
            const updatedCart = await response.json();
            setCart(updatedCart.dishes);
            message.success(`${dish.name} добавлено в корзину!`); // Уведомление об успешном добавлении
        } catch (error) {
            console.error('Ошибка при добавлении блюда в корзину:', error);
            setError(`Не удалось добавить блюдо в корзину: ${error.message}`);
        }
    };

    return (
        <div className="main-container">
            <header className="header">
                <div className="logo-and-balance">
                    <Link to="/" className="logo">
                        <img src="src/components/images/logo.png" alt="Logo"/>
                        <span>FoodExpress</span>
                    </Link>
                    {isAuthenticated && (
                        <div className="balance-section">
                            <span className="balance">Баланс: {balance} ₽</span>
                            <Link to="/add_balance">
                                <Button icon={<PlusCircleOutlined />} className="button-recharge">
                                    Пополнить
                                </Button>
                            </Link>
                        </div>
                    )}
                </div>
                {isAuthenticated && (
                    <div className="navigation-section">
                        <Select
                            placeholder="Выберите категорию"
                            value={selectedCategory}
                            onChange={handleCategoryChange}
                            className="nav-select"
                        >
                            <Select.Option value="">Все</Select.Option>
                            {categories.map(c => (
                                <Select.Option key={c.name} value={c.name}>
                                    {c.name}
                                </Select.Option>
                            ))}
                        </Select>
                        <Button type="text" icon={<ShoppingCartOutlined />} className="button-cart" onClick={() => navigate('/create_order')}>
                            Корзина
                        </Button>
                        <Button type="text" icon={<LogoutOutlined />} className="button-logout" onClick={handleLogout}>
                            Выйти
                        </Button>
                    </div>
                )}
            </header>

            <main className="main-content">
                {isAuthenticated ? (
                    <>
                        <h2 className="title">Наши лучшие блюда</h2>
                        <div className="dishes-grid">
                            {loading ? (
                                <div className="col-span-full flex justify-center">
                                    <Spin size="large"/>
                                </div>
                            ) : error ? (
                                <p className="col-span-full text-red-500 text-center">{error}</p>
                            ) : (
                                dishes.map(dish => (
                                    <div key={dish.id} className="dish-card">
                                        <img src={dish.image || '/default-dish.jpg'} alt={dish.name}
                                             className="dish-image"/>
                                        <h3 className="dish-title">{dish.name}</h3>
                                        <p>{dish.description}</p>
                                        <p className="dish-price">{dish.price} ₽</p>
                                        <Button
                                            type="primary"
                                            icon={<ShoppingCartOutlined />}
                                            className="mt-4 w-full bg-green-500"
                                            onClick={() => addToCart(dish)}
                                        >
                                            В корзину
                                        </Button>
                                    </div>
                                ))
                            )}
                        </div>
                    </>
                ) : (
                    <div className="text-center">
                        <h2 className="text-2xl font-bold text-gray-800 mb-4">Войдите, чтобы продолжить</h2>
                        <Link to="/login">
                            <Button className="bg-blue-500 text-white">Перейти к входу</Button>
                        </Link>
                    </div>
                )}
            </main>
        </div>
    );
}

export default MainPage;

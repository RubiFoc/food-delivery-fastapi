import {useState, useEffect} from 'react';
import {Link, useNavigate} from 'react-router-dom';
import {Button, Select, Spin, message} from 'antd';
import {LogoutOutlined, ShoppingCartOutlined, PlusCircleOutlined} from '@ant-design/icons';
import Header from './Header';
import './styles/MainPage.css';

function MainPage() {
    const [token, setToken] = useState(localStorage.getItem('token'));
    const [role, setRole] = useState(localStorage.getItem('role')); // Храним роль
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
                // Проверка аутентификации
                const response = await fetch('http://127.0.0.1:8000/auth/me', {
                    method: 'GET',
                    headers: {
                        'Authorization': `Bearer ${token}`,
                    },
                });

                if (response.ok) {
                    const userData = await response.json();
                    setIsAuthenticated(true);

                    // Получаем роль пользователя
                    const roleResponse = await fetch('http://127.0.0.1:8000/auth/my_role', {
                        method: 'GET',
                        headers: {
                            'Authorization': `Bearer ${token}`,
                        },
                    });

                    if (roleResponse.ok) {
                        const roleData = await roleResponse.json();
                        setRole(roleData.role); // Сохраняем роль
                        localStorage.setItem('role', roleData.role); // Сохраняем роль в localStorage
                    }
                    fetchBalance()
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
        fetchCategories();
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
            <Header
                isAuthenticated={isAuthenticated}
                balance={balance}
                categories={categories}
                selectedCategory={selectedCategory}
                onCategoryChange={setSelectedCategory}
                handleLogout={handleLogout}
                role_id={role}
            />

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
                                dishes.length > 0 ? (
                                    dishes.map(dish => (
                                        <div key={dish.id} className="dish-card">
                                            <img
                                                // src={dish.image || '/default-dish.jpg'}
                                                src={"src/components/images/logo.png"}
                                                alt={dish.name}
                                                className="dish-image"
                                            />
                                            <h3 className="dish-title">{dish.name}</h3>
                                            <p>{dish.description}</p>
                                            <p className="dish-price">{dish.price} ₽</p>
                                            <Button
                                                type="primary"
                                                icon={<ShoppingCartOutlined/>}
                                                className="mt-4 w-full bg-green-500"
                                                onClick={() => addToCart(dish)}
                                            >
                                                В корзину
                                            </Button>
                                        </div>
                                    ))
                                ) : (
                                    <p className="col-span-full text-center text-gray-500">Нет доступных блюд.</p>
                                )
                            )}
                        </div>
                    </>
                ) : (
                    <div className="auth-container">
                        <div className="auth-card">
                            <h1 className="auth-title">Добро пожаловать!</h1>
                            <p>Выберите действие, чтобы начать работу с нашей системой.</p>
                            <div className="auth-buttons">
                                <Link to="/login">
                                    <button>Вход</button>
                                </Link>
                                <Link to="/register">
                                    <button className="secondary">Регистрация</button>
                                </Link>
                                <Link to="/register/courier_or_worker">
                                    <button>Регистрация курьера/работника кухни</button>
                                </Link>
                            </div>
                        </div>
                    </div>
                )}
            </main>
        </div>
    );
}

export default MainPage;
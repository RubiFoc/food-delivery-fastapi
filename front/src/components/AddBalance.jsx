import { useState, useEffect } from 'react';
import { useLocation, useNavigate, Link } from 'react-router-dom';
import { Button, Select, Spin, message } from 'antd';
import { LogoutOutlined, ShoppingCartOutlined, PlusCircleOutlined } from '@ant-design/icons';
import './styles/AddBalance.css';  // Импорт CSS-файла

function AddBalance() {
    const location = useLocation();
    const navigate = useNavigate();
    const [token, setToken] = useState('');
    const [amount, setAmount] = useState('');
    const [error, setError] = useState('');
    const [newBalance, setNewBalance] = useState(null);
    const [isAuthenticated, setIsAuthenticated] = useState(false);
    const [balance, setBalance] = useState(0);
    const [categories, setCategories] = useState([]);
    const [selectedCategory, setSelectedCategory] = useState('');

    useEffect(() => {
        // Проверка наличия токена в localStorage
        const storedToken = localStorage.getItem('token');
        if (storedToken) {
            setToken(storedToken);
            setIsAuthenticated(true);
            fetchBalance();
            fetchCategories();
        } else {
            // Если токен не найден в localStorage, проверяем параметры URL
            const params = new URLSearchParams(location.search);
            const tokenFromUrl = params.get('token');
            if (tokenFromUrl) {
                setToken(tokenFromUrl);
                // Сохраняем токен в localStorage для последующих перезагрузок
                localStorage.setItem('token', tokenFromUrl);
                setIsAuthenticated(true);
                fetchBalance();
                fetchCategories();
            } else {
                setError('Token not found');
            }
        }
    }, [location]);

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

    const handleBalanceUpdate = async (e) => {
        e.preventDefault(); // Останавливаем отправку формы

        // Проверка, что введенная сумма — это число больше нуля
        const parsedAmount = parseFloat(amount);
        if (isNaN(parsedAmount) || parsedAmount <= 0) {
            alert('Please enter a valid balance amount');
            return;
        }

        try {
            const response = await fetch('http://127.0.0.1:8000/auth/user/balance', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ amount: parsedAmount }), // Отправляем parsedAmount
            });

            if (response.ok) {
                const data = await response.json();
                setNewBalance(data.new_balance);
                alert('Balance updated successfully!');
            } else {
                const errorData = await response.json();
                console.error('Error:', errorData);
                alert('Failed to update balance.');
            }
        } catch (error) {
            console.error('Error:', error);
            alert('An error occurred while updating the balance.');
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
            setBalance(0);
        } catch (error) {
            console.error('Ошибка при выходе:', error);
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
                            onChange={setSelectedCategory}
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
                <div className="bg-white p-8 rounded-lg shadow-lg w-96">
                    <h2 className="text-2xl font-bold text-center mb-6">Add Balance</h2>
                    {error && <p className="text-red-500 text-center mb-4">{error}</p>}
                    {newBalance !== null ? (
                        <p className="text-green-500 text-center mb-4">
                            Balance updated successfully! New Balance: {newBalance} Руб
                        </p>
                    ) : (
                        <form onSubmit={handleBalanceUpdate}>
                            <div className="mb-4">
                                <label htmlFor="amount" className="block text-sm font-semibold text-gray-700">
                                    Amount
                                </label>
                                <input
                                    type="number"
                                    id="amount"
                                    name="amount"
                                    className="w-full p-2 border border-gray-300 rounded-md"
                                    value={amount}
                                    onChange={(e) => setAmount(e.target.value)}
                                    required
                                />
                            </div>
                            <button
                                type="submit"
                                className="w-full bg-yellow-500 text-white py-2 rounded-md"
                            >
                                Add Balance
                            </button>
                        </form>
                    )}
                </div>
            </main>
        </div>
    );
}

export default AddBalance;

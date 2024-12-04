import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button, Spin, message, Input } from 'antd';
import Header from './Header'; // Подключение Header
import './styles/UpdateLocation.css'; // Импорт CSS-файла

function UpdateLocation() {
    const [token, setToken] = useState(localStorage.getItem('token'));
    const [isAuthenticated, setIsAuthenticated] = useState(false);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [categories, setCategories] = useState([]);
    const [selectedCategory, setSelectedCategory] = useState('');
    const [balance, setBalance] = useState(0);
    const [address, setAddress] = useState('');  // Added state for address
    const navigate = useNavigate();

    useEffect(() => {
        const checkAuth = async () => {
            if (!token) {
                setIsAuthenticated(false);
                navigate('/login');
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
                    fetchCategories();
                    fetchBalance();
                } else {
                    setIsAuthenticated(false);
                    navigate('/login');
                }
            } catch (error) {
                console.error('Ошибка при проверке аутентификации:', error);
                setIsAuthenticated(false);
                navigate('/login');
            } finally {
                setLoading(false);
            }
        };

        checkAuth();
    }, [token, navigate]);

    const fetchCategories = async () => {
        try {
            const response = await fetch('http://127.0.0.1:8000/api/dish-categories', {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${token}`,
                },
            });

            if (response.ok) {
                const data = await response.json();
                setCategories(data);
            } else {
                throw new Error('Не удалось загрузить категории');
            }
        } catch (error) {
            console.error(error);
            setError('Не удалось загрузить категории');
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
            setBalance(0);
        } catch (error) {
            console.error('Ошибка при выходе:', error);
        }
    };

    const handleUpdateLocation = async () => {
        if (!address) {
            message.error('Пожалуйста, введите адрес');
            return;
        }

        try {
            const response = await fetch(`http://127.0.0.1:8000/api/customer/update_location?address=${encodeURIComponent(address)}`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json',
                },
            });

            if (response.ok) {
                const data = await response.json();
                message.success(`Местоположение обновлено: ${data.location}`);
            } else {
                message.error('Не удалось обновить местоположение');
            }
        } catch (error) {
            console.error('Ошибка при обновлении местоположения:', error);
            message.error('Ошибка при обновлении местоположения');
        }
    };

    if (loading) {
        return (
            <div className="loading-container">
                <Spin size="large" />
            </div>
        );
    }

    return (
        <div className="update-location-container">
            <Header
                isAuthenticated={isAuthenticated}
                balance={balance}
                categories={categories}
                selectedCategory={selectedCategory}
                onCategoryChange={setSelectedCategory}
                handleLogout={handleLogout}
            />
            {isAuthenticated ? (
                <div className="content">
                    <h2>Обновите свой адрес</h2>
                    <Input
                        placeholder="Введите ваш адрес"
                        value={address}
                        onChange={(e) => setAddress(e.target.value)}
                        style={{ marginBottom: 20 }}
                    />
                    <Button type="primary" onClick={handleUpdateLocation}>
                        Сохранить
                    </Button>
                </div>
            ) : (
                <div className="text-center">
                    <h2 className="text-2xl font-bold text-gray-800 mb-4">Войдите, чтобы продолжить</h2>
                    <Button type="primary" onClick={() => navigate('/login')}>
                        Перейти к входу
                    </Button>
                </div>
            )}
        </div>
    );
}

export default UpdateLocation;

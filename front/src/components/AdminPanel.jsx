import React, { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import './styles/AdminPanel.css';
import Header from './Header';
import DishCategories from './DishCategories';
import Dishes from './Dishes';
import Orders from './Orders';
import Customers from './Customers';
import Couriers from './Couriers';

function AdminPanel() {
    const location = useLocation();
    const [token, setToken] = useState('');
    const [role, setRole] = useState(localStorage.getItem('role'));
    const [isAuthenticated, setIsAuthenticated] = useState(false);
    const [users, setUsers] = useState([]);
    const [error, setError] = useState('');
    const [activePage, setActivePage] = useState('users');

    useEffect(() => {
        const storedToken = localStorage.getItem('token');
        if (storedToken) {
            setToken(storedToken);
            setIsAuthenticated(true);
            fetchUsers(storedToken);
        } else {
            const params = new URLSearchParams(location.search);
            const tokenFromUrl = params.get('token');
            if (tokenFromUrl) {
                setToken(tokenFromUrl);
                localStorage.setItem('token', tokenFromUrl);
                setIsAuthenticated(true);
                fetchUsers(tokenFromUrl);
            } else {
                setError('Token не найден');
            }
        }
    }, [location]);

    const fetchUsers = async (token) => {
        try {
            const response = await fetch('http://127.0.0.1:8000/admins/users', {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${token}`,
                },
            });

            if (response.ok) {
                const data = await response.json();
                setUsers(data);
            } else {
                setError('Не удалось загрузить пользователей');
            }
        } catch (error) {
            console.error('Ошибка при загрузке пользователей:', error);
            setError('Ошибка при загрузке пользователей');
        }
    };

    const handleDeleteUser = async (id) => {
        try {
            const response = await fetch(`http://127.0.0.1:8000/admins/user/${id}`, {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${token}`,
                },
            });

            if (response.ok) {
                setUsers(users.filter(user => user.id !== id));
            } else {
                setError('Не удалось удалить пользователя');
            }
        } catch (error) {
            console.error('Ошибка при удалении пользователя:', error);
            setError('Ошибка при удалении пользователя');
        }
    };

    const handleUpdateUser = async (id, updatedData) => {
        try {
            const response = await fetch(`http://127.0.0.1:8000/admins/user/${id}`, {
                method: 'PUT',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(updatedData),
            });

            if (response.ok) {
                fetchUsers(token);
            } else {
                setError('Не удалось обновить пользователя');
            }
        } catch (error) {
            console.error('Ошибка при обновлении пользователя:', error);
            setError('Ошибка при обновлении пользователя');
        }
    };

    return (
        <div className="admin-panel-container">
            <aside className="sidebar">
                <h2 className="sidebar-title">Панель администратора</h2>
                <ul className="sidebar-menu">
                    <li>
                        <a href="#" onClick={() => setActivePage('users')}
                           className={activePage === 'users' ? 'active' : ''}>
                            Пользователи
                        </a>
                    </li>
                    <li>
                        <a href="#" onClick={() => setActivePage('dish-categories')}
                           className={activePage === 'dish-categories' ? 'active' : ''}>
                            Категории блюд
                        </a>
                    </li>
                    <li>
                        <a href="#" onClick={() => setActivePage('dishes')}
                           className={activePage === 'dishes' ? 'active' : ''}>
                            Блюда
                        </a>
                    </li>
                    <li>
                        <a href="#" onClick={() => setActivePage('orders')}
                           className={activePage === 'orders' ? 'active' : ''}>
                            Заказы
                        </a>
                    </li>
                    <li>
                        <a href="#" onClick={() => setActivePage('customers')}
                           className={activePage === 'customers' ? 'active' : ''}>
                            Клиенты
                        </a>
                    </li>
                    <li>
                        <a href="#" onClick={() => setActivePage('couriers')}
                           className={activePage === 'couriers' ? 'active' : ''}>
                            Курьеры
                        </a>
                    </li>
                </ul>
            </aside>

            <main className="main-content">
                <Header isAuthenticated={isAuthenticated} role={role}/>
                {activePage === 'users' && (
                    <>
                        <h1>Пользователи</h1>
                        <table className="users-table">
                            <thead>
                            <tr>
                                <th>ID</th>
                                <th>Email</th>
                                <th>Имя пользователя</th>
                                <th>Роль</th>
                                <th>Действия</th>
                            </tr>
                            </thead>
                            <tbody>
                            {users.map(user => (
                                <tr key={user.id}>
                                    <td>{user.id}</td>
                                    <td>{user.email}</td>
                                    <td>{user.username}</td>
                                    <td>{user.role.name}</td>
                                    <td>
                                        <button onClick={() => handleUpdateUser(user.id, {is_active: !user.is_active})}>
                                            {user.is_active ? 'Деактивировать' : 'Активировать'}
                                        </button>
                                        <button onClick={() => handleDeleteUser(user.id)}>Удалить</button>
                                    </td>
                                </tr>
                            ))}
                            </tbody>
                        </table>
                    </>
                )}
                {activePage === 'dish-categories' && <DishCategories token={token}/>}
                {activePage === 'dishes' && <Dishes token={token}/>}
                {activePage === 'orders' && <Orders token={token}/>}
                {activePage === 'customers' && <Customers token={token}/>} {/* Вкладка "Клиенты" */}
                {activePage === 'couriers' && <Couriers token={token}/>} {/* Вкладка "Курьеры" */}
            </main>
        </div>
    );
}

export default AdminPanel;

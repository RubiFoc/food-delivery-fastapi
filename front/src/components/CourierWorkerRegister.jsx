import { useState } from 'react';
import './styles/RegisterAdmin.css'; // Подключение общего CSS-файла для регистрации

function CourierWorkerRegister() {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [role, setRole] = useState('2'); // 2 - Курьер по умолчанию
    const [error, setError] = useState('');

    const handleRegister = async (e) => {
        e.preventDefault();
        if (password !== confirmPassword) {
            setError("Пароли не совпадают");
            return;
        }

        try {
            const response = await fetch('http://127.0.0.1:8000/auth/register', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    email: email,
                    username: email.split('@')[0], // Генерация имени пользователя из email
                    password: password,
                    is_active: true,
                    is_superuser: false,
                    is_verified: false,
                    role_id: parseInt(role), // Роль курьера или работника кухни
                }),
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Регистрация не удалась');
            }

            // Обработка успешной регистрации
            window.location.href = '/login';
        } catch (error) {
            console.error(error);
            setError(error.message || 'Регистрация не удалась, повторите попытку');
        }
    };

    return (
        <div className="auth-container">
            <div className="auth-card">
                <h2 className="auth-title">Регистрация курьера или работника кухни</h2>
                {error && <p className="text-red-500 text-center mb-4">{error}</p>}
                <form className="auth-form" onSubmit={handleRegister}>
                    <label htmlFor="email">Электронная почта</label>
                    <input
                        type="email"
                        id="email"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        required
                    />
                    <label htmlFor="password">Пароль</label>
                    <input
                        type="password"
                        id="password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        required
                    />
                    <label htmlFor="confirmPassword">Подтвердите пароль</label>
                    <input
                        type="password"
                        id="confirmPassword"
                        value={confirmPassword}
                        onChange={(e) => setConfirmPassword(e.target.value)}
                        required
                    />
                    <label htmlFor="role">Роль</label>
                    <select
                        id="role"
                        value={role}
                        onChange={(e) => setRole(e.target.value)}
                        required
                    >
                        <option value="2">Курьер</option>
                        <option value="3">Работник кухни</option>
                    </select>
                    <button type="submit">Зарегистрироваться</button>
                </form>
            </div>
        </div>
    );
}

export default CourierWorkerRegister;

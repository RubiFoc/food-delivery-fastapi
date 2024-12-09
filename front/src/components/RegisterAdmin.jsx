import {useEffect, useState} from 'react';
import Header from './Header'; // Импортируем компонент Header
import './styles/RegisterAdmin.css'; // Подключение CSS-файла

function RegisterAdmin() {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');
    const [token, setToken] = useState('');

    useEffect(() => {
        const storedToken = localStorage.getItem('token');
        if (storedToken) {
            setToken(storedToken);
            handleRegister(storedToken);
        } else {
            setError('Токен не найден');
        }
    }, []);

    const handleRegister = async (e) => {
        e.preventDefault();
        setError('');
        setSuccess('');

        if (password !== confirmPassword) {
            setError("Пароли не совпадают");
            return;
        }

        try {
            const response = await fetch('http://127.0.0.1:8000/admins/register', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`,
                },
                body: JSON.stringify({
                    email: email,
                    username: email.split('@')[0],
                    password: password,
                    is_active: true,
                    is_superuser: true,
                    is_verified: true,
                    role_id: 4,
                }),
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Ошибка регистрации');
            }

            setSuccess('Администратор успешно зарегистрирован!');
            setEmail('');
            setPassword('');
            setConfirmPassword('');
        } catch (error) {
            setError(error.message || 'Ошибка регистрации, пожалуйста, попробуйте снова');
        }
    };

    return (
        <div className="auth-container">
            <Header
                isAuthenticated={true}
                role_id={4}
                handleLogout={() => console.log("Выход из системы")}
            />

            <div className="auth-card">
                <h2 className="auth-title">Регистрация администратора</h2>
                {error && <p className="text-red-500 text-center mb-4">{error}</p>}
                {success && <p className="text-green-500 text-center mb-4">{success}</p>}
                <form className="auth-form" onSubmit={handleRegister}>
                    <label htmlFor="email">Email</label>
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
                    <button type="submit">Зарегистрировать</button>
                </form>
            </div>
        </div>
    );
}

export default RegisterAdmin;

import { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';

function AddBalance() {
    const location = useLocation();
    const navigate = useNavigate();
    const [token, setToken] = useState('');
    const [amount, setAmount] = useState('');
    const [error, setError] = useState('');
    const [newBalance, setNewBalance] = useState(null);

    useEffect(() => {
        // Проверка наличия токена в localStorage
        const storedToken = localStorage.getItem('token');
        if (storedToken) {
            setToken(storedToken);
        } else {
            // Если токен не найден в localStorage, проверяем параметры URL
            const params = new URLSearchParams(location.search);
            const tokenFromUrl = params.get('token');
            if (tokenFromUrl) {
                setToken(tokenFromUrl);
                // Сохраняем токен в localStorage для последующих перезагрузок
                localStorage.setItem('token', tokenFromUrl);
            } else {
                setError('Token not found');
            }
        }
    }, [location]);

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

    return (
        <div className="min-h-screen flex items-center justify-center bg-gray-100">
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
        </div>
    );
}

export default AddBalance;

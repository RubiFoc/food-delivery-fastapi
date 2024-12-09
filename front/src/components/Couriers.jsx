import React, { useState, useEffect } from 'react';
import './styles/AdminPanel.css';

function Couriers({ token }) {
    const [couriers, setCouriers] = useState([]);
    const [editingCourierId, setEditingCourierId] = useState(null);
    const [editedCourier, setEditedCourier] = useState({
        rating: '',
        rate: '',
        location: '',
        number_of_marks: '',
        user_email: '',
        user_username: '',
        user_registration_date: '',
        user_is_active: false,
        role_name: ''
    });
    const [error, setError] = useState('');

    useEffect(() => {
        fetchCouriers();
    }, []);

    const fetchCouriers = async () => {
        try {
            const response = await fetch('http://127.0.0.1:8000/admins/couriers', {
                headers: { 'Authorization': `Bearer ${token}` },
            });

            if (response.ok) {
                const data = await response.json();
                setCouriers(data);
            } else {
                setError('Не удалось загрузить курьеров');
            }
        } catch (error) {
            console.error('Error fetching couriers:', error);
            setError('Ошибка при загрузке курьеров');
        }
    };

    const handleUpdateCourier = async () => {
        try {
            const response = await fetch(`http://127.0.0.1:8000/admins/courier/${editingCourierId}`, {
                method: 'PUT',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    rating: editedCourier.rating,
                    rate: editedCourier.rate,
                    location: editedCourier.location,
                    number_of_marks: editedCourier.number_of_marks,
                }),
            });

            if (response.ok) {
                setEditingCourierId(null);
                setEditedCourier({
                    rating: '',
                    rate: '',
                    location: '',
                    number_of_marks: '',
                    user_email: '',
                    user_username: '',
                    user_registration_date: '',
                    user_is_active: false,
                    role_name: ''
                });
                fetchCouriers();
            } else {
                setError('Не удалось обновить данные курьера');
            }
        } catch (error) {
            console.error('Error updating courier:', error);
            setError('Ошибка обновления курьера');
        }
    };

    const handleDeleteCourier = async (id) => {
        try {
            const response = await fetch(`http://127.0.0.1:8000/admins/courier/${id}`, {
                method: 'DELETE',
                headers: { 'Authorization': `Bearer ${token}` },
            });

            if (response.ok) {
                setCouriers(couriers.filter(courier => courier.id !== id));
            } else {
                setError('Не удалось удалить курьера');
            }
        } catch (error) {
            console.error('Error deleting courier:', error);
            setError('Ошибка удаления курьера');
        }
    };

    return (
        <div>
            <h1>Курьеры</h1>
            {error && <p className="error">{error}</p>}
            <table className="couriers-table">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Рейтинг</th>
                        <th>Ставка</th>
                        <th>Локация</th>
                        <th>Количество оценок</th>
                        <th>Электронная почта</th>
                        <th>Имя пользователя</th>
                        <th>Дата регистрации</th>
                        <th>Активность</th>
                        <th>Роль</th>
                        <th>Действия</th>
                    </tr>
                </thead>
                <tbody>
                    {couriers.map(courier => (
                        <tr key={courier.id}>
                            <td>{courier.id}</td>
                            <td>
                                {editingCourierId === courier.id ? (
                                    <input
                                        type="number"
                                        value={editedCourier.rating}
                                        onChange={(e) => setEditedCourier({ ...editedCourier, rating: e.target.value })}
                                    />
                                ) : (
                                    courier.rating
                                )}
                            </td>
                            <td>
                                {editingCourierId === courier.id ? (
                                    <input
                                        type="number"
                                        value={editedCourier.rate}
                                        onChange={(e) => setEditedCourier({ ...editedCourier, rate: e.target.value })}
                                    />
                                ) : (
                                    courier.rate
                                )}
                            </td>
                            <td>
                                {editingCourierId === courier.id ? (
                                    <input
                                        type="text"
                                        value={editedCourier.location}
                                        onChange={(e) => setEditedCourier({ ...editedCourier, location: e.target.value })}
                                    />
                                ) : (
                                    courier.location
                                )}
                            </td>
                            <td>
                                {editingCourierId === courier.id ? (
                                    <input
                                        type="number"
                                        value={editedCourier.number_of_marks}
                                        onChange={(e) => setEditedCourier({ ...editedCourier, number_of_marks: e.target.value })}
                                    />
                                ) : (
                                    courier.number_of_marks
                                )}
                            </td>
                            <td>{editingCourierId === courier.id ? (
                                <input
                                    type="text"
                                    value={editedCourier.user_email}
                                    onChange={(e) => setEditedCourier({ ...editedCourier, user_email: e.target.value })}
                                />
                            ) : (
                                courier.user.email
                            )}
                            </td>
                            <td>{editingCourierId === courier.id ? (
                                <input
                                    type="text"
                                    value={editedCourier.user_username}
                                    onChange={(e) => setEditedCourier({ ...editedCourier, user_username: e.target.value })}
                                />
                            ) : (
                                courier.user.username
                            )}
                            </td>
                            <td>{editingCourierId === courier.id ? (
                                <input
                                    type="date"
                                    value={editedCourier.user_registration_date}
                                    onChange={(e) => setEditedCourier({ ...editedCourier, user_registration_date: e.target.value })}
                                />
                            ) : (
                                new Date(courier.user.registration_date).toLocaleDateString()
                            )}
                            </td>
                            <td>{editingCourierId === courier.id ? (
                                <input
                                    type="checkbox"
                                    checked={editedCourier.user_is_active}
                                    onChange={(e) => setEditedCourier({ ...editedCourier, user_is_active: e.target.checked })}
                                />
                            ) : (
                                courier.user.is_active ? 'Активен' : 'Неактивен'
                            )}
                            </td>
                            <td>{editingCourierId === courier.id ? (
                                <input
                                    type="text"
                                    value={editedCourier.role_name}
                                    onChange={(e) => setEditedCourier({ ...editedCourier, role_name: e.target.value })}
                                />
                            ) : (
                                courier.role.name
                            )}
                            </td>
                            <td>
                                {editingCourierId === courier.id ? (
                                    <>
                                        <button onClick={handleUpdateCourier}>Сохранить</button>
                                        <button onClick={() => setEditingCourierId(null)}>Отмена</button>
                                    </>
                                ) : (
                                    <>
                                        <button onClick={() => {
                                            setEditingCourierId(courier.id);
                                            setEditedCourier({
                                                rating: courier.rating,
                                                rate: courier.rate,
                                                location: courier.location,
                                                number_of_marks: courier.number_of_marks,
                                                user_email: courier.user.email,
                                                user_username: courier.user.username,
                                                user_registration_date: new Date(courier.user.registration_date).toLocaleDateString(),
                                                user_is_active: courier.user.is_active,
                                                role_name: courier.role.name
                                            });
                                        }}>Редактировать</button>
                                        <button onClick={() => handleDeleteCourier(courier.id)}>Удалить</button>
                                    </>
                                )}
                            </td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
}

export default Couriers;

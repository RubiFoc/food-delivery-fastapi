import React, { useState, useEffect } from 'react';
import './styles/Dishes.css';

function Dishes({ token }) {
    const [dishes, setDishes] = useState([]);
    const [newDish, setNewDish] = useState({
        name: '',
        price: '',
        weight: '',
        category_id: '',
        profit: '',
        time_of_preparing: '',
        image: null
    });
    const [error, setError] = useState('');

    useEffect(() => {
        fetchDishes();
    }, []);

    const fetchDishes = async () => {
        try {
            const response = await fetch('http://127.0.0.1:8000/admins/dishes', {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${token}`,
                },
            });

            if (response.ok) {
                const data = await response.json();
                setDishes(data);
            } else {
                setError('Не удалось загрузить блюда');
            }
        } catch (error) {
            console.error('Ошибка при загрузке блюд:', error);
            setError('Ошибка при загрузке блюд');
        }
    };

    const handleAddDish = async () => {
        const formData = new FormData();
        formData.append('name', newDish.name);
        formData.append('price', newDish.price);
        formData.append('weight', newDish.weight);
        formData.append('category_id', newDish.category_id);
        formData.append('profit', newDish.profit);
        formData.append('time_of_preparing', newDish.time_of_preparing);
        if (newDish.image) {
            formData.append('image', newDish.image);
        }

        try {
            const response = await fetch('http://127.0.0.1:8000/admins/dishes', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`,
                },
                body: formData,
            });

            if (response.ok) {
                fetchDishes(); // Обновить список блюд после добавления
                setNewDish({
                    name: '',
                    price: '',
                    weight: '',
                    category_id: '',
                    profit: '',
                    time_of_preparing: '',
                    image: null
                });
            } else {
                setError('Не удалось добавить блюдо');
            }
        } catch (error) {
            console.error('Ошибка при добавлении блюда:', error);
            setError('Ошибка при добавлении блюда');
        }
    };

    const handleDeleteDish = async (id) => {
        try {
            const response = await fetch(`http://127.0.0.1:8000/admins/dishes?id=${id}`, {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${token}`,
                },
            });

            if (response.ok) {
                setDishes(dishes.filter(dish => dish.id !== id));
            } else {
                setError('Не удалось удалить блюдо');
            }
        } catch (error) {
            console.error('Ошибка при удалении блюда:', error);
            setError('Ошибка при удалении блюда');
        }
    };

    const handleUpdateDish = async (id, updatedData) => {
        const formData = new FormData();
        formData.append('name', updatedData.name || '');
        formData.append('price', updatedData.price || '');
        formData.append('weight', updatedData.weight || '');
        formData.append('category_id', updatedData.category_id || '');
        formData.append('profit', updatedData.profit || '');
        formData.append('time_of_preparing', updatedData.time_of_preparing || '');
        if (updatedData.image) {
            formData.append('image', updatedData.image);
        }

        try {
            const response = await fetch(`http://127.0.0.1:8000/admins/dishes/${id}`, {
                method: 'PATCH',
                headers: {
                    'Authorization': `Bearer ${token}`,
                },
                body: formData,
            });

            if (response.ok) {
                fetchDishes(); // Обновить список блюд после изменения
            } else {
                setError('Не удалось обновить блюдо');
            }
        } catch (error) {
            console.error('Ошибка при обновлении блюда:', error);
            setError('Ошибка при обновлении блюда');
        }
    };

    return (
        <div className="main-content">
            <h1 className="page-title">Блюда</h1>
            <h2 className="page-title">Добавить новое блюдо</h2>
            <div className="input-group">
                <input
                    className="input"
                    type="text"
                    placeholder="Название"
                    value={newDish.name}
                    onChange={e => setNewDish({ ...newDish, name: e.target.value })}
                />
                <input
                    className="input"
                    type="number"
                    placeholder="Цена"
                    value={newDish.price}
                    onChange={e => setNewDish({ ...newDish, price: e.target.value })}
                />
                <input
                    className="input"
                    type="number"
                    placeholder="Вес"
                    value={newDish.weight}
                    onChange={e => setNewDish({ ...newDish, weight: e.target.value })}
                />
                <input
                    className="input"
                    type="number"
                    placeholder="Категория ID"
                    value={newDish.category_id}
                    onChange={e => setNewDish({ ...newDish, category_id: e.target.value })}
                />
                <input
                    className="input"
                    type="number"
                    placeholder="Прибыль"
                    value={newDish.profit}
                    onChange={e => setNewDish({ ...newDish, profit: e.target.value })}
                />
                <input
                    className="input"
                    type="number"
                    placeholder="Время приготовления"
                    value={newDish.time_of_preparing}
                    onChange={e => setNewDish({ ...newDish, time_of_preparing: e.target.value })}
                />
                <input
                    className="input"
                    type="file"
                    onChange={e => setNewDish({ ...newDish, image: e.target.files[0] })}
                />
                <button className="btn" onClick={handleAddDish}>Добавить блюдо</button>
            </div>
            {error && <p className="error">{error}</p>}
            <div className="table-container">
                <table className="dishes-table">
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Название</th>
                            <th>Цена</th>
                            <th>Вес</th>
                            <th>Категория</th>
                            <th>Прибыль</th>
                            <th>Время приготовления</th>
                            <th>Действия</th>
                        </tr>
                    </thead>
                    <tbody>
                        {dishes.map(dish => (
                            <tr key={dish.id}>
                                <td>{dish.id}</td>
                                <td>{dish.name}</td>
                                <td>{dish.price}</td>
                                <td>{dish.weight}</td>
                                <td>{dish.category_id}</td>
                                <td>{dish.profit}</td>
                                <td>{dish.time_of_preparing}</td>
                                <td>
                                    <button className="btn" onClick={() => handleUpdateDish(dish.id, { name: 'Updated Name' })}>Обновить</button>
                                    <button className="btn" onClick={() => handleDeleteDish(dish.id)}>Удалить</button>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
}

export default Dishes;

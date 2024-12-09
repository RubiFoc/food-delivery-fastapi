import React, { useState, useEffect } from 'react';
import './styles/AdminPanel.css';

function DishCategories({ token }) {
    const [categories, setCategories] = useState([]);
    const [newCategory, setNewCategory] = useState('');
    const [editingCategoryId, setEditingCategoryId] = useState(null);
    const [editedCategoryName, setEditedCategoryName] = useState('');
    const [error, setError] = useState('');

    useEffect(() => {
        fetchCategories();
    }, []);

    const fetchCategories = async () => {
        try {
            const response = await fetch('http://127.0.0.1:8000/api/dish-categories', {
                headers: { 'Authorization': `Bearer ${token}` },
            });

            if (response.ok) {
                const data = await response.json();
                setCategories(data);
            } else {
                setError('Не удалось загрузить категории блюд');
            }
        } catch (err) {
            console.error('Error fetching categories:', err);
            setError('Ошибка загрузки категорий');
        }
    };

    const handleAddCategory = async () => {
        try {
            const response = await fetch(`http://127.0.0.1:8000/admins/dish-categories?name=${encodeURIComponent(newCategory)}`, {
                method: 'POST',
                headers: { 'Authorization': `Bearer ${token}` },
            });

            if (response.ok) {
                fetchCategories();
                setNewCategory('');
            } else {
                setError('Не удалось добавить категорию');
            }
        } catch (err) {
            console.error('Error adding category:', err);
            setError('Ошибка добавления категории');
        }
    };

    const handleDeleteCategory = async (name) => {
        try {
            const response = await fetch(`http://127.0.0.1:8000/admins/dish-categories?name=${encodeURIComponent(name)}`, {
                method: 'DELETE',
                headers: { 'Authorization': `Bearer ${token}` },
            });

            if (response.ok) {
                fetchCategories();
            } else {
                setError('Не удалось удалить категорию');
            }
        } catch (err) {
            console.error('Error deleting category:', err);
            setError('Ошибка удаления категории');
        }
    };

    const handleUpdateCategory = async () => {
        if (!editedCategoryName) return;

        try {
            const response = await fetch(`http://127.0.0.1:8000/admins/dish-categories?old_name=${encodeURIComponent(categories.find(category => category.id === editingCategoryId).name)}&new_name=${encodeURIComponent(editedCategoryName)}`, {
                method: 'PATCH',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'accept': 'application/json',
                },
            });

            if (response.ok) {
                setEditingCategoryId(null);
                setEditedCategoryName('');
                fetchCategories();
            } else {
                setError('Не удалось изменить категорию');
            }
        } catch (err) {
            console.error('Error updating category:', err);
            setError('Ошибка изменения категории');
        }
    };

    return (
        <div>
            <h1>Категории блюд</h1>
            <div className="input-group">
                <input
                    type="text"
                    value={newCategory}
                    onChange={(e) => setNewCategory(e.target.value)}
                    placeholder="Название новой категории"
                />
                <button onClick={handleAddCategory}>Добавить категорию</button>
            </div>
            {error && <p className="error">{error}</p>}

            <table className="categories-table">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Название</th>
                        <th>Действия</th>
                    </tr>
                </thead>
                <tbody>
                    {categories.map(category => (
                        <tr key={category.id}>
                            <td>{category.id}</td>
                            <td>
                                {editingCategoryId === category.id ? (
                                    <input
                                        type="text"
                                        value={editedCategoryName}
                                        onChange={(e) => setEditedCategoryName(e.target.value)}
                                    />
                                ) : (
                                    category.name
                                )}
                            </td>
                            <td>
                                {editingCategoryId === category.id ? (
                                    <>
                                        <button onClick={handleUpdateCategory}>Сохранить</button>
                                        <button onClick={() => setEditingCategoryId(null)}>Отмена</button>
                                    </>
                                ) : (
                                    <>
                                        <button onClick={() => {
                                            setEditingCategoryId(category.id);
                                            setEditedCategoryName(category.name);
                                        }}>Редактировать</button>
                                        <button onClick={() => handleDeleteCategory(category.name)}>Удалить</button>
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

export default DishCategories;

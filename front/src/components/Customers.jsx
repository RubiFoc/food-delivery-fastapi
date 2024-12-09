import React, { useState, useEffect } from 'react';
import './styles/AdminPanel.css';

function Customers({ token }) {
    const [customers, setCustomers] = useState([]);
    const [editingCustomerId, setEditingCustomerId] = useState(null);
    const [editedCustomer, setEditedCustomer] = useState({ balance: '', location: '' });
    const [error, setError] = useState('');

    useEffect(() => {
        fetchCustomers();
    }, []);

    const fetchCustomers = async () => {
        try {
            const response = await fetch('http://127.0.0.1:8000/admins/customers', {
                headers: { 'Authorization': `Bearer ${token}` },
            });

            if (response.ok) {
                const data = await response.json();
                setCustomers(data);
            } else {
                setError('Не удалось загрузить клиентов');
            }
        } catch (error) {
            console.error('Error fetching customers:', error);
            setError('Ошибка при загрузке клиентов');
        }
    };

    const handleUpdateCustomer = async () => {
        try {
            const response = await fetch(`http://127.0.0.1:8000/admins/customer/${editingCustomerId}`, {
                method: 'PUT',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(editedCustomer),
            });

            if (response.ok) {
                setEditingCustomerId(null);
                setEditedCustomer({ balance: '', location: '' });
                fetchCustomers();
            } else {
                setError('Не удалось обновить данные клиента');
            }
        } catch (error) {
            console.error('Error updating customer:', error);
            setError('Ошибка обновления клиента');
        }
    };

    const handleDeleteCustomer = async (id) => {
        try {
            const response = await fetch(`http://127.0.0.1:8000/admins/user/${id}`, {
                method: 'DELETE',
                headers: { 'Authorization': `Bearer ${token}` },
            });

            if (response.ok) {
                setCustomers(customers.filter(customer => customer.id !== id));
            } else {
                setError('Не удалось удалить клиента');
            }
        } catch (error) {
            console.error('Error deleting customer:', error);
            setError('Ошибка удаления клиента');
        }
    };

    return (
        <div>
            <h1>Клиенты</h1>
            {error && <p className="error">{error}</p>}
            <table className="customers-table">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Баланс</th>
                        <th>Локация</th>
                        <th>Действия</th>
                    </tr>
                </thead>
                <tbody>
                    {customers.map(customer => (
                        <tr key={customer.id}>
                            <td>{customer.id}</td>
                            <td>
                                {editingCustomerId === customer.id ? (
                                    <input
                                        type="number"
                                        value={editedCustomer.balance}
                                        onChange={(e) => setEditedCustomer({ ...editedCustomer, balance: e.target.value })}
                                    />
                                ) : (
                                    customer.balance
                                )}
                            </td>
                            <td>
                                {editingCustomerId === customer.id ? (
                                    <input
                                        type="text"
                                        value={editedCustomer.location}
                                        onChange={(e) => setEditedCustomer({ ...editedCustomer, location: e.target.value })}
                                    />
                                ) : (
                                    customer.location
                                )}
                            </td>
                            <td>
                                {editingCustomerId === customer.id ? (
                                    <>
                                        <button onClick={handleUpdateCustomer}>Сохранить</button>
                                        <button onClick={() => setEditingCustomerId(null)}>Отмена</button>
                                    </>
                                ) : (
                                    <>
                                        <button onClick={() => {
                                            setEditingCustomerId(customer.id);
                                            setEditedCustomer({ balance: customer.balance, location: customer.location });
                                        }}>Редактировать</button>
                                        <button onClick={() => handleDeleteCustomer(customer.id)}>Удалить</button>
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

export default Customers;

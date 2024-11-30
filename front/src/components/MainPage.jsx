import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';

function MainPage() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [error, setError] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [dishes, setDishes] = useState([]);
  const [categories, setCategories] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState('');
  const [loading, setLoading] = useState(true);
  const [cart, setCart] = useState([]);
  const [customerId, setCustomerId] = useState(null);

  // Проверка аутентификации при загрузке страницы
  useEffect(() => {
    const checkAuth = async () => {
      try {
        const response = await fetch('http://127.0.0.1:8000/auth/me', {
          method: 'GET',
          credentials: 'include',
        });

        if (response.ok) {
          const userData = await response.json();
          setCustomerId(userData.id); // Получение ID пользователя
          setIsAuthenticated(true);
          fetchCategories();
          fetchDishes();
        } else {
          setIsAuthenticated(false);
        }
      } catch (error) {
        console.error('Authentication check failed:', error);
        setIsAuthenticated(false);
      }
    };
    checkAuth();
  }, []);

  // Функция для получения категорий
  const fetchCategories = async () => {
    try {
      const response = await fetch('http://127.0.0.1:8000/api/dish-categories', {
        method: 'GET',
        credentials: 'include',
      });

      if (!response.ok) throw new Error('Failed to fetch categories');
      const data = await response.json();
      setCategories(data);
    } catch (error) {
      console.error(error);
      setError('Failed to fetch categories, please try again');
    }
  };

  // Функция для получения блюд
  const fetchDishes = async () => {
    try {
      const url = selectedCategory
        ? `http://127.0.0.1:8000/api/dishes/category/${selectedCategory}`
        : 'http://127.0.0.1:8000/api/dishes';

      const response = await fetch(url, {
        method: 'GET',
        credentials: 'include',
      });

      if (!response.ok) throw new Error('Failed to fetch dishes');
      const data = await response.json();
      setDishes(data);
    } catch (error) {
      console.error(error);
      setError('Failed to fetch dishes, please try again');
    } finally {
      setLoading(false);
    }
  };

  // Логин
  const handleLogin = async (e) => {
    e.preventDefault();
    const formData = new URLSearchParams();
    formData.append('username', email);
    formData.append('password', password);

    try {
      const response = await fetch('http://127.0.0.1:8000/auth/jwt/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        credentials: 'include',
        body: formData.toString(),
      });

      if (!response.ok) throw new Error('Failed to login');
      setIsAuthenticated(true);
      const userData = await response.json();
      setCustomerId(userData.id); // Сохраняем customerId после входа
      fetchCategories();
      fetchDishes();
    } catch (error) {
      console.error('Login error:', error);
      setError('Invalid credentials, please try again');
    }
  };

  // Логаут
  const handleLogout = async () => {
    try {
      await fetch('http://127.0.0.1:8000/auth/jwt/logout', {
        method: 'POST',
        credentials: 'include',
      });
      setIsAuthenticated(false);
      setDishes([]);
      setCart([]);
    } catch (error) {
      console.error('Logout failed:', error);
    }
  };

  const handleCategoryChange = (e) => {
    setSelectedCategory(e.target.value);
    setLoading(true);
    fetchDishes();
  };

  // Добавление блюда в корзину
  const addToCart = async (dish) => {
    try {
      // Приводим dish.id и quantity к целым числам
      const dishId = parseInt(dish.id, 10);  // Преобразуем dish.id в число
      const quantity = 1;  // Здесь quantity всегда будет целым числом 1, но можно изменить по необходимости

      // Проверяем, что dishId и quantity действительно целые числа
      if (!Number.isInteger(dishId) || !Number.isInteger(quantity)) {
        throw new Error('Invalid dish_id or quantity');
      }

      const response = await fetch('http://127.0.0.1:8000/api/cart/add-dish', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({
          dish_id: dishId,  // dishId приведен к целому числу
          quantity: quantity,  // quantity уже является целым числом
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(`Failed to add dish to cart: ${errorData.detail || 'Unknown error'}`);
      }

      const updatedCart = await response.json();
      setCart(updatedCart.dishes);  // Обновляем корзину
    } catch (error) {
      console.error('Error adding dish to cart:', error);
      setError(`Failed to add dish to cart: ${error.message}`);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100">
      <div className="bg-white p-8 rounded-lg shadow-lg w-96">
        {isAuthenticated ? (
          <>
            <h2 className="text-2xl font-bold text-center mb-6">Welcome!</h2>
            <button onClick={handleLogout} className="w-full bg-red-500 text-white py-2 rounded-md">
              Logout
            </button>

            {/* Фильтр по категориям */}
            <div className="mt-6 mb-4">
              <label htmlFor="category" className="block text-sm font-semibold text-gray-700">
                Select Category
              </label>
              <select
                id="category"
                className="w-full p-2 border border-gray-300 rounded-md"
                value={selectedCategory}
                onChange={handleCategoryChange}
              >
                <option value="">All</option>
                {categories.map((category) => (
                  <option key={category.id} value={category.name}>
                    {category.name}
                  </option>
                ))}
              </select>
            </div>

            {/* Секция с блюдами */}
            <h3 className="text-xl font-semibold text-center mt-6 mb-4">Dishes</h3>
            {loading ? (
              <p className="text-center text-gray-500">Loading dishes...</p>
            ) : error ? (
              <p className="text-center text-red-500">{error}</p>
            ) : (
              <ul className="space-y-4">
                {dishes.map((dish) => (
                  <li key={dish.id} className="border-b py-2">
                    <h4 className="font-semibold">{dish.name}</h4>
                    <p>{dish.description}</p>
                    <p className="text-gray-500">{dish.price} Руб</p>
                    <button
                      onClick={() => addToCart(dish)}
                      className="mt-2 w-full bg-green-500 text-white py-2 rounded-md"
                    >
                      Add to Cart
                    </button>
                  </li>
                ))}
              </ul>
            )}

            {/* Кнопка для перехода на страницу заказов кухни */}
            <Link to="/kitchen_orders">
              <button className="w-full bg-blue-500 text-white py-2 rounded-md mt-6">
                View Kitchen Orders
              </button>
            </Link>

            {/* Кнопка для перехода на создание заказа */}
            <Link to="/create_order">
              <button className="w-full bg-purple-500 text-white py-2 rounded-md mt-6">
                Create Order
              </button>
            </Link>
          </>
        ) : (
          <>
            <h2 className="text-2xl font-bold text-center mb-6">Login</h2>
            {error && <p className="text-red-500 text-center mb-4">{error}</p>}
            <form onSubmit={handleLogin}>
              <div className="mb-4">
                <label htmlFor="email" className="block text-sm font-semibold text-gray-700">
                  Email
                </label>
                <input
                  type="email"
                  id="email"
                  name="email"
                  className="w-full p-2 border border-gray-300 rounded-md"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                />
              </div>
              <div className="mb-6">
                <label htmlFor="password" className="block text-sm font-semibold text-gray-700">
                  Password
                </label>
                <input
                  type="password"
                  id="password"
                  name="password"
                  className="w-full p-2 border border-gray-300 rounded-md"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                />
              </div>
              <button
                type="submit"
                className="w-full bg-blue-500 text-white py-2 rounded-md"
              >
                Login
              </button>
            </form>
          </>
        )}
      </div>
    </div>
  );
}

export default MainPage;

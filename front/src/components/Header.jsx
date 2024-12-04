import { Link, useNavigate } from 'react-router-dom';
import { Button, Select } from 'antd';
import { LogoutOutlined, ShoppingCartOutlined, PlusCircleOutlined, EnvironmentOutlined } from '@ant-design/icons';
import PropTypes from 'prop-types';
import './styles/header.css';
import logo from './images/logo.png'; // Импорт логотипа

const Header = ({ isAuthenticated, balance, categories, selectedCategory, onCategoryChange, handleLogout }) => {
    const navigate = useNavigate();
    return (
        <header className="header">
            <div className="logo-and-balance">
                <Link to="/" className="logo">
                    <img src={logo} alt="Logo" /> {/* Используем импортированный логотип */}
                    <span>FoodExpress</span>
                </Link>
                {isAuthenticated && (
                    <div className="balance-section">
                        <span className="balance">Баланс: {balance} ₽</span>
                        <Link to="/add_balance">
                            <Button icon={<PlusCircleOutlined />} className="button-recharge">
                                Пополнить
                            </Button>
                        </Link>
                    </div>
                )}
            </div>
            {isAuthenticated && (
                <div className="navigation-section">
                    <Select
                        placeholder="Выберите категорию"
                        value={selectedCategory}
                        onChange={onCategoryChange}
                        className="nav-select"
                    >
                        <Select.Option value="">Все</Select.Option>
                        {categories.map(c => (
                            <Select.Option key={c.name} value={c.name}>
                                {c.name}
                            </Select.Option>
                        ))}
                    </Select>
                    <Button type="text" icon={<ShoppingCartOutlined />} className="button-cart" onClick={() => navigate('/create_order')}>
                        Корзина
                    </Button>

                    {/* Ссылка на обновление локации */}
                    <Link to="/customer/location">
                        <Button type="text" icon={<EnvironmentOutlined />} className="button-location">
                            Обновить локацию
                        </Button>
                    </Link>

                    <Button type="text" icon={<LogoutOutlined />} className="button-logout" onClick={handleLogout}>
                        Выйти
                    </Button>
                </div>
            )}
        </header>
    );
};

Header.propTypes = {
    isAuthenticated: PropTypes.bool.isRequired,
    balance: PropTypes.number.isRequired,
    categories: PropTypes.array.isRequired,
    selectedCategory: PropTypes.string.isRequired,
    onCategoryChange: PropTypes.func.isRequired,
    handleLogout: PropTypes.func.isRequired,
};

export default Header;

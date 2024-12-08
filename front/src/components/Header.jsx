import { Link, useNavigate } from 'react-router-dom';
import { Button, Select } from 'antd';
import { LogoutOutlined, ShoppingCartOutlined, PlusCircleOutlined, FileDoneOutlined, DashboardOutlined, AppstoreAddOutlined, EnvironmentOutlined  } from '@ant-design/icons';
import PropTypes from 'prop-types';
import './styles/header.css';
import logo from './images/logo.png';

const Header = ({
    isAuthenticated,
    balance,
    categories,
    selectedCategory,
    onCategoryChange,
    handleLogout,
    role_id
}) => {
    const navigate = useNavigate();

    return (
        <header className="header">
            <div className="logo-and-balance">
                <Link to="/" className="logo">
                    <img src={logo} alt="Logo" /> <span>FoodExpress</span>
                </Link>
                {isAuthenticated && role_id === 1 && (
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

            <div className="navigation-section">
                {/* Для роли клиента */}
                {isAuthenticated && role_id === 1 && (
                    <>
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
                        <Button
                            type="text"
                            icon={<ShoppingCartOutlined />}
                            className="button-cart"
                            onClick={() => navigate('/create_order')}
                        >
                            Корзина
                        </Button>
                        <Link to="/customer/location">
                            <Button type="text" icon={<EnvironmentOutlined />} className="button-location">
                                Обновить локацию
                            </Button>
                        </Link>
                    </>
                )}

                {/* Для курьера */}
                {isAuthenticated && role_id === 2 && (
                    <>
                        <Link to="/courier/take_order">
                            <Button type="text" icon={<FileDoneOutlined />} className="button-location">
                                Управление заказами
                            </Button>
                        </Link>
                    </>
                )}

                {/* Для работника кухни */}
                {isAuthenticated && role_id === 3 && (
                    <>
                        <Link to="/kitchen_orders">
                            <Button type="text" icon={<FileDoneOutlined />} className="button-location">
                                Управление заказами
                            </Button>
                        </Link>
                    </>
                )}

                {/* Для администратора */}
                {isAuthenticated && role_id === 4 && (
                    <>
                        <Link to="/admin/register">
                            <Button type="text" icon={<AppstoreAddOutlined />} className="button-location">
                                Регистрация админа
                            </Button>
                        </Link>
                        <Link to="/admin">
                            <Button type="text" icon={<DashboardOutlined />} className="button-location">
                                Панель администратора
                            </Button>
                        </Link>
                        <Link to="http://localhost:8080/reports" target="_blank">
                            <Button type="text" icon={<FileDoneOutlined />} className="button-location">
                                Отчет
                            </Button>
                        </Link>
                    </>
                )}

                {/* Кнопка выхода */}
                {isAuthenticated && (
                    <Button type="text" icon={<LogoutOutlined />} className="button-logout" onClick={handleLogout}>
                        Выйти
                    </Button>
                )}
            </div>
        </header>
    );
};

Header.propTypes = {
    isAuthenticated: PropTypes.bool,
    balance: PropTypes.number,
    categories: PropTypes.array,
    selectedCategory: PropTypes.string,
    onCategoryChange: PropTypes.func,
    handleLogout: PropTypes.func,
    role_id: PropTypes.number,
};

export default Header;

import React from 'react';

const DishList = ({ dishes, categories, addToCart }) => {
  return (
    <div>
      <h2>Меню</h2>
      {categories.map(category => (
        <div key={category.id}>
          <h3>{category.name}</h3>
          <ul>
            {dishes
              .filter(dish => dish.category_id === category.id)
              .map(dish => (
                <li key={dish.id}>
                  {dish.name} - {dish.price} ₽
                  <button onClick={() => addToCart(dish)}>Добавить в корзину</button>
                </li>
              ))}
          </ul>
        </div>
      ))}
    </div>
  );
};

export default DishList;

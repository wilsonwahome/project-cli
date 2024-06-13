from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import User, Product, CartItem, Order, OrderItem, UserRole, OrderStatus
from datetime import datetime
import logging

# Set up logging
logging.basicConfig(filename='ecommerce.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Database setup
engine = create_engine('sqlite:///database.db')  # Adjust as per your database setup
Session = sessionmaker(bind=engine)

# Function to get current user from session
def get_current_user():
    try:
        with open('session.txt', 'r') as file:
            data = file.read().strip().split(',')
        if not data or len(data) != 2:
            return None
        username, role = data
        with Session() as session:
            return session.query(User).filter_by(username=username, role=UserRole(role)).first()
    except Exception as e:
        logging.error(f"Error getting current user: {e}")
        return None

# Restrict certain actions to admins
def admin_required(func):
    def wrapper(*args, **kwargs):
        user = get_current_user()
        if not user or user.role != UserRole.ADMIN:
            print("Admin access required.")
            return
        return func(*args, **kwargs)
    return wrapper

# Register user
def register(username, password, role=UserRole.USER):
    try:
        with Session() as session:
            if session.query(User).filter_by(username=username).first():
                print("Username already exists.")
                return
            user = User(username=username, password=password, role=role)
            session.add(user)
            session.commit()
            print("User registered successfully.")
            logging.info(f"User registered: {username} as {role.value}")
    except Exception as e:
        print("An error occurred while registering the user.")
        logging.error(f"Error registering user: {e}")

# Login user
def login(username, password):
    try:
        with Session() as session:
            user = session.query(User).filter_by(username=username, password=password).first()
            if user:
                with open('session.txt', 'w') as file:
                    file.write(f"{username},{user.role.value}")
                print("Logged in successfully.")
                logging.info(f"User logged in: {username}")
                if user.role == UserRole.ADMIN:
                    print("Welcome Admin!")
                else:
                    print("Welcome User!")
            else:
                print("Invalid username or password.")
    except Exception as e:
        print("An error occurred while logging in.")
        logging.error(f"Error logging in user: {e}")

# Logout user
def logout():
    try:
        with open('session.txt', 'w') as file:
            file.write('')
        print("Logged out successfully.")
        logging.info("User logged out.")
    except Exception as e:
        print("An error occurred while logging out.")
        logging.error(f"Error logging out user: {e}")

# Place order
def place_order():
    user = get_current_user()
    if not user:
        print("Please login first.")
        return

    try:
        with Session() as session:
            cart_items = session.query(CartItem).filter_by(user_id=user.id).all()
            if not cart_items:
                print("Your cart is empty. Please add items to your cart before placing an order.")
                return

            total = 0
            order_items = []
            for item in cart_items:
                product = session.query(Product).filter_by(id=item.product_id).first()
                total += product.price
                order_items.append(OrderItem(product_id=product.id, quantity=1, unit_price=product.price))

            order = Order(user_id=user.id, total=total, status=OrderStatus.PENDING)
            order.order_items = order_items
            session.add(order)
            session.commit()

            # Remove items from the cart after placing the order
            session.query(CartItem).filter_by(user_id=user.id).delete()
            
            print("Order placed successfully.")
            logging.info(f"Order placed: {order.id}, User: {user.username}")

    except Exception as e:
        print("An error occurred while placing the order.")
        logging.error(f"Error placing order: {e}")

# View orders
def view_orders():
    user = get_current_user()
    if not user:
        print("Please login first.")
        return
    try:
        with Session() as session:
            orders = session.query(Order).filter_by(user_id=user.id).all()
            if not orders:
                print("You have no orders.")
                return
            for order in orders:
                print(f"Order ID: {order.id}, Status: {order.status.value}")
                order_items = session.query(OrderItem).filter_by(order_id=order.id).all()
                for item in order_items:
                    product = session.query(Product).filter_by(id=item.product_id).first()
                    print(f"  Product ID: {product.id}, Name: {product.name}, Price: ${product.price}, Quantity: {item.quantity}")
    except Exception as e:
        print("An error occurred while viewing orders.")
        logging.error(f"Error viewing orders: {e}")

# Cancel order
def cancel_order(order_id):
    user = get_current_user()
    if not user:
        print("Please login first.")
        return
    try:
        with Session() as session:
            order = session.query(Order).filter_by(id=order_id, user_id=user.id).first()
            if not order:
                print("Order not found.")
                return
            if order.status != OrderStatus.PENDING:
                print("Only pending orders can be canceled.")
                return
            order.status = OrderStatus.CANCELED
            session.commit()
            print("Order canceled successfully.")
            logging.info(f"Order canceled: {order_id}, User: {user.username}")
    except Exception as e:
        print("An error occurred while canceling the order.")
        logging.error(f"Error canceling order: {e}")

# Update order status (admin only)
@admin_required
def update_order_status(order_id, status):
    try:
        with Session() as session:
            order = session.query(Order).filter_by(id=order_id).first()
            if not order:
                print("Order not found.")
                return
            order.status = status
            session.commit()
            print(f"Order status updated to {status.value}.")
            logging.info(f"Order status updated: {order_id}, Status: {status.value}")
    except Exception as e:
        print("An error occurred while updating the order status.")
        logging.error(f"Error updating order status: {e}")


def empty_cart():
    user = get_current_user()
    if not user:
        print("Please login first.")
        return

    try:
        with Session() as session:
            session.query(CartItem).filter_by(user_id=user.id).delete()
            session.commit()
            print("Cart emptied successfully.")
            logging.info(f"Cart emptied for user: {user.username}")
    except Exception as e:
        print("An error occurred while emptying the cart.")
        logging.error(f"Error emptying cart: {e}")

def list_users():
    try:
        with Session() as session:
            users = session.query(User).all()
            if not users:
                print("No users found.")
                return
            print("List of Users:")
            for user in users:
                print(f"ID: {user.id}, Username: {user.username}, Role: {user.role.value}")
    except Exception as e:
        print("An error occurred while listing users.")
        logging.error(f"Error listing users: {e}")

@admin_required
def add_product(name, price):
    try:
        with Session() as session:
            product = Product(name=name, price=price)
            session.add(product)
            session.commit()
            print("Product added successfully.")
            logging.info(f"Product added: {product.name}, Price: ${product.price}")
    except Exception as e:
        print("An error occurred while adding the product.")
        logging.error(f"Error adding product: {e}")

def list_products():
    try:
        with Session() as session:
            products = session.query(Product).all()
            if not products:
                print("No products found.")
                return
            print("List of Products:")
            for product in products:
                print(f"ID: {product.id}, Name: {product.name}, Price: ${product.price}")
    except Exception as e:
        print("An error occurred while listing products.")
        logging.error(f"Error listing products: {e}")

def add_to_cart(product_id):
    user = get_current_user()
    if not user:
        print("Please login first.")
        return

    try:
        with Session() as session:
            product = session.query(Product).filter_by(id=product_id).first()
            if not product:
                print("Product not found.")
                return

            cart_item = CartItem(user_id=user.id, product_id=product_id)
            session.add(cart_item)
            session.commit()
            print(f"Product '{product.name}' added to cart.")
            logging.info(f"Product added to cart: {product.name}, User: {user.username}")
    except Exception as e:
        print("An error occurred while adding to cart.")
        logging.error(f"Error adding to cart: {e}")

def view_cart():
    user = get_current_user()
    if not user:
        print("Please login first.")
        return

    try:
        with Session() as session:
            cart_items = session.query(CartItem).filter_by(user_id=user.id).all()
            if not cart_items:
                print("Your cart is empty.")
                return
            print("Cart Items:")
            for cart_item in cart_items:
                product = session.query(Product).filter_by(id=cart_item.product_id).first()
                print(f"Product ID: {product.id}, Name: {product.name}, Price: ${product.price}")
    except Exception as e:
        print("An error occurred while viewing cart.")
        logging.error(f"Error viewing cart: {e}")

@admin_required
def delete_user(username):
    try:
        with Session() as session:
            user = session.query(User).filter_by(username=username).first()
            if not user:
                print("User not found.")
                return

            # Delete the user's orders
            session.query(Order).filter_by(user_id=user.id).delete()

            # Delete the user
            session.delete(user)
            session.commit()
            print(f"User '{username}' deleted successfully.")
            logging.info(f"User deleted: {username}")
    except Exception as e:
        print("An error occurred while deleting the user.")
        logging.error(f"Error deleting user: {e}")
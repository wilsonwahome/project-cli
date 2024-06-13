from utils import *

# Main program
def main():
    while True:
        user = get_current_user()

        if not user:
            print("\nChoose an action:")
            print("1. Register")
            print("2. Login")
            print("3. Exit")
            choice = input("Enter your choice: ")

            if choice == '1':
                username = input("Enter username: ")
                password = input("Enter password: ")
                role_input = input("Enter role (user/admin): ").strip().lower()
                role = UserRole.ADMIN if role_input == "admin" else UserRole.USER
                register(username, password, role)
            elif choice == '2':
                username = input("Enter username: ")
                password = input("Enter password: ")
                login(username, password)
            elif choice == '3':
                print("Exiting program. Goodbye!")
                break
            else:
                print("Invalid choice. Please choose again.")
        else:
            print("\nChoose an action:")
            print("1. Logout")
            print("2. List Users (Admin Only)")
            print("3. Add Product (Admin Only)")
            print("4. List Products")
            print("5. Add to Cart")
            print("6. Empty Cart")
            print("7. View Cart")
            print("8. Place Order")
            print("9. View Orders")
            print("10. Cancel Order")
            print("11. Update Order Status (Admin Only)")
            print("12. Delete User (Admin Only)")
            print("13. Exit")
            
            choice = input("Enter your choice: ")

            if choice == '1':
                logout()
            elif choice == '2':
                if user.role == UserRole.ADMIN:
                    list_users()
                else:
                    print("Admin access required.")
            elif choice == '3':
                if user.role == UserRole.ADMIN:
                    name = input("Enter product name: ")
                    price = float(input("Enter product price: "))
                    add_product(name, price)
                else:
                    print("Admin access required.")
            elif choice == '4':
                list_products()
            elif choice == '5':
                product_id = int(input("Enter product ID to add to cart: "))
                add_to_cart(product_id)
            elif choice == '6':
                empty_cart()
            elif choice == '7':
                view_cart()
            elif choice == '8':
                place_order()
            elif choice == '9':
                view_orders()
            elif choice == '10':
                order_id = int(input("Enter order ID to cancel: "))
                cancel_order(order_id)
            elif choice == '11':
                if user.role == UserRole.ADMIN:
                    order_id = int(input("Enter order ID to update status: "))
                    status_input = input("Enter new status (pending/processed/delivered/canceled): ").strip().lower()
                    status = {
                        'pending': OrderStatus.PENDING,
                        'processed': OrderStatus.PROCESSED,
                        'delivered': OrderStatus.DELIVERED,
                        'canceled': OrderStatus.CANCELED
                    }.get(status_input)

                    if status:
                        update_order_status(order_id, status)
                    else:
                        print("Invalid status input.")
                else:
                    print("Admin access required.")
            elif choice == '12':
                if user.role == UserRole.ADMIN:
                    username = input("Enter username to delete: ")
                    delete_user(username)
                else:
                    print("Admin access required.")
            elif choice == '13':
                print("Exiting program. Goodbye!")
                break
            else:
                print("Invalid choice. Please choose again.")



if __name__ == "__main__":
    main()

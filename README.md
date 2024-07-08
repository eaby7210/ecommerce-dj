# E-Commerce Platform

An e-commerce platform built using Django, designed to provide a seamless shopping experience for users and efficient management tools for administrators.

## Index

- [Description](#description)
- [Installation](#installation)
- [Features](#features)
  - [Admin Side](#admin-side)
  - [User Side](#user-side)
- [Dependencies](#dependencies)
- [Frontend Technologies](#frontend-technologies)
- [License](#license)
- [Contributing](#contributing)
- [Contact](#contact)
- [References](#references)

## Description

This Django-based e-commerce platform specializes in selling electronics products and leverages modern web development tools to create a dynamic and responsive user experience. The backend is powered by Django and Django REST Framework (DRF), providing robust APIs for various functionalities. DRF's template renderer is used extensively to generate HTML templates dynamically, ensuring that the frontend can swiftly adapt to changing data without requiring full page reloads.

For the frontend, the platform utilizes HTMX and Alpine.js to enable seamless, interactive user experiences. HTMX is employed to handle AJAX requests and server responses, allowing for efficient data fetching and dynamic content updates directly within HTML. This setup reduces the need for traditional JavaScript, streamlining the codebase and improving maintainability.

The combination of DRF for backend APIs and template rendering, along with HTMX for frontend interactivity, results in a highly performant and user-friendly e-commerce platform. Users can enjoy features like real-time product filtering, dynamic cart updates, and smooth navigation across different sections of the site. Additionally, the integration with Razorpay ensures secure and efficient payment processing, enhancing the overall shopping experience.


## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/eaby7210/ecommerce-dj
    ```
2. Navigate to the project directory:
    ```sh
    cd ecommerce-dj
    ```
3. Install dependencies using Pipenv:
    ```sh
    pipenv install
    ```
4. Activate the virtual environment:
    ```sh
    pipenv shell
    ```
5. Apply migrations:
    ```sh
    python manage.py migrate
    ```
6. Create a superuser:
    ```sh
    python manage.py createsuperuser
    ```
7. Run the development server:
    ```sh
    python manage.py runserver
    ```

## Features

### Admin Side
- **User Management**
  - List users
  - Block/unblock users
- **Category Management**
  - Add, edit, and delete (soft delete) categories
- **Product Management**
  - Add, edit, and delete (soft delete) products
  - Multiple images per product (minimum 3), cropped and resized before upload
- **Order Management**
  - List orders
  - Change order status
  - Cancel orders
- **Stock Management**
  - Show stock levels in product listing and details pages
- **Coupon Management**
  - Create and delete coupons
- **Offer Management**
  - Product, category, and referral offers
- **Sales Reporting**
  - Daily, weekly, yearly, and custom date reports
  - Include discounts and coupon deductions
  - Filter by custom date range
  - Download reports as PDF or Excel
- **Dashboard**
  - Charts with yearly, monthly, etc. filters
  - Best selling products, categories, and brands (top 10)

### User Side
- **Home Page**
- **Authentication**
  - User sign up and login with validation
  - OTP sign up with timer and resend OTP
  - Single sign-on with Google
- **Product Browsing**
  - List products
  - Product details view with image zoom
  - Breadcrumbs, ratings, price, stock, highlights/specs, related products
- **User Profile**
  - Show user details, address, orders
  - Edit profile, cancel orders, change password
  - Address management (add, edit, delete multiple addresses)
- **Cart Management**
  - Add to cart, list products, remove products
  - Control quantity based on stock
  - Maximum quantity per person
  - Filter out of stock products
- **Advanced Search**
  - Sort by price (low to high, high to low), featured, new arrivals, A-Z, Z-A
- **Checkout**
  - Multiple addresses, edit and save addresses
  - Place order with Cash on Delivery (COD)
  - Handle orders above Rs 1000 (COD not allowed)
- **Order Management**
  - Order history and status
  - Invoice download (PDF)
  - Continue payment from order page for failed payments
  - Transaction history section
- **Payment Integration**
  - Online payment with Razorpay
- **Coupon Management**
  - Apply and remove coupons
- **Wishlist**
  - Add and remove items
- **Wallet**
  - Manage wallet for canceled orders

## Dependencies

- Django
- Django Debug Toolbar
- psycopg2
- Django REST Framework
- Django Filter
- Pillow
- Django CORS Headers
- DRF Nested Routers
- Razorpay
- Setuptools
- Django HTMX
- ReportLab
- WhiteNoise
- Gunicorn
- Django AllAuth
- Cryptography
- Python Dotenv

## Frontend Technologies

- HTMX
- Alpine.js
- Bootstrap


## Future Plans

- **Improvement in UI**
  - Enhance the user interface for a more modern and intuitive user experience.
- **Replacing Remaining JS with HTMX**
  - Replace the remaining JavaScript code with HTMX to simplify frontend interactions and improve performance.
- **Wallet Amount for Orders**
  - Implement functionality to allow users to use their wallet balance for placing orders.
- **User Membership Tiers**
  - Introduce membership tiers (gold, silver, bronze) with different benefits and features.
- **Product Variants**
  - Add support for product variants, such as different sizes or colors.
- **User-Friendly Enhancements**
  - Continuously work on making the application more user-friendly based on user feedback and testing.
- **JWT Authentication**
  - Implement JWT authentication to enhance security and scalability of user authentication.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.

## Contact

For any inquiries, please contact [eabythomascu@gmail.com](mailto:eabythomascu@gmail.com).

## References

- [Django Documentation](https://docs.djangoproject.com/en/stable/)
- [Django REST Framework Documentation](https://www.django-rest-framework.org/)
- [Razorpay Documentation](https://razorpay.com/docs/)
- [Pillow Documentation](https://pillow.readthedocs.io/en/stable/)
- [HTMX Documentation](https://htmx.org/docs/)
- [Alpine.js Documentation](https://alpinejs.dev/start)
- [Bootstrap Documentation](https://getbootstrap.com/docs/5.0/get)

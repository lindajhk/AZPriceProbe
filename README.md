![Logo](https://drive.google.com/uc?id=1Rs--Cubkkmtscz73qN0xQezYoLLcv8-p)

"AZPriceProbe" is a Flask-based web app written with Python that allows registered users to monitor Amazon product prices. If a product's current price is below their desired price, an email notification gets sent to their email. The app utilizes Bootstrap for UI, WTForms for form handling, SQLAlchemy for database management, Beautiful Soup for web scraping, and smtplib for email notifications. User authentication is incorporated for security. 

## Demo

![image](https://github.com/lindajhk/AZPriceProbe/assets/106854298/c14eb61f-14d2-4ff0-8a8a-3c7a98517bf2)

To register as a new user, click the register button and complete the information (username, email, password, confirm password).
![image](https://github.com/lindajhk/AZPriceProbe/assets/106854298/324f4e19-0dbd-466a-aa54-bc414cccc555)

If you already have an account, press the login and login with your information.
![image](https://github.com/lindajhk/AZPriceProbe/assets/106854298/947bb8fe-999b-4961-bd89-fa2cf70dc1ce)

To demo the app, press demo login and you will log into the demo login.

Once logged in, you can see all the products that you are tracking. To add a product, click the Add Product button and fill out the product information.
![image](https://github.com/lindajhk/AZPriceProbe/assets/106854298/9df8fd55-76c1-42c1-822b-5c7957c1baaf)
![image](https://github.com/lindajhk/AZPriceProbe/assets/106854298/e8502343-927f-46b5-babd-602a53ccaecb)

Once a product is added, you will see that the product page is updated with the new product. You can delete any products on your list and check the price. 
If you have multiple products on your list, then you can press the Check All button on top to check the prices on all your products.
When the price is checked, if any of the products have a price that is below your buy price, you will receive an email notification to your email.
![image](https://github.com/lindajhk/AZPriceProbe/assets/106854298/fdd69ef6-3075-4f33-a672-a2726daacd62)


## Environment Variables

To run this project, you will need to add the following environment variables to your .env file

`my_email` This is the email you want to use to send the email alerts

`password` This is the password for your email (`my_email`)

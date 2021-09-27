# Fruit-Seller-Chatbot-with-Recommendation-System 🤖

Fruits/Vegetable Seller Bot With Recommendation System Integrated (Using Apriori Algorithm) And MySql Database to record all the transactions and products/stock details.


## Install dependencies

```bash
pip install rasa
```
Installation docs: https://rasa.com/docs/rasa/installation/

Create a new python environment
```bash
conda create --name rasa python==3.6
```

Install all the requirements
```bash
pip install -r requirements.txt
```

Import SQL database "fruit_rasa" to your local server (Xampp)

Optional Installation
```bash
pip install rasa-x
```

**Import and setup the Mysql database**

## Run the bot

Use `rasa train` to train a model.

Then, to run, first set up your action server in one terminal window:
```bash
rasa run actions
```

In another window, run the following command to talk to the bot:
```
rasa shell --debug
```

Note that `--debug` mode will produce a lot of output meant to help you understand how the bot is working
under the hood. To simply talk to the bot, you can remove this flag.


You can also try out your bot locally using Rasa X by running
```
rasa x
```


## Integrated Features

* Sign In and Sign Up functionality with DB support
* User can check if the company sells a particular fruit or not
* Check the price of fruits
* Fruit menu which display fruit and price per kg
* User can verify the product detail which he want to purchase before checkout
* User can place order, which will then be stored in DB
* User can get details of his last purchase as well as all purchases
* Product Recommendation using Apriori Algorithm integrated


## Admin Features

* Questions
    * Who are my best customers
    * Area from, where i get max profit
    * Best selling product
    * What is my current stock of apples in mumbai
    * What is my total revenue
    * Montly revenue 
    * Profit earn from selling apples in nagpur
    * Which products are not selling
    * Which fruits are giving me loss
    * What is the most asked fruit and i don't have it

## Future Improvements

* Question => Price of 2 kg of apple
* Subsription feature for a particular or variety of fruits
* Give out to actual user, to make the model learn and handle extreme cases
* Check if the user already exists during sign up
* Use encryption to save password
* Check for user valid input (Sql injection)

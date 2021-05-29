# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

from typing import Any, Text, Dict, List , Union

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict
from rasa_sdk.events import EventType
from rasa_sdk.forms import FormAction
from rasa_sdk.events import SlotSet

from datetime import date
import mysql.connector
import pandas as pd

recommendation_df = pd.read_csv("./recommendations.csv")
def recommend(product, items=3):
    try:
        top_recommended_products = recommendation_df[recommendation_df["antecedents"] == product].sort_values(
            "confidence", ascending=False)["consequents"].head(items).tolist()
        return top_recommended_products
    except:
        return None

db = mysql.connector.connect(
  host="localhost",
  user="root",
  password="",
  database="fruit_rasa"
)

today = date.today()
mycursor = db.cursor()

# def get_fruit_name_from_id(fruit_id):
#     sql = "SELECT * FROM fruits WHERE id=2" 
#     mycursor = db.cursor()
#     mycursor.execute(sql)
#     row = mycursor.fetchone()
#     print("************8" + str(row))
#     return row[0]

def insert_product(customer_id,fruit_id,qty,total_amt):
    sql = "INSERT INTO orders (customer_id,fruit_id,qty,total_amt, date) VALUES (%s,%s,%s,%s,%s)"
    val = (customer_id,fruit_id,qty,total_amt,today)
    mycursor.execute(sql, val)
    db.commit()

    print(f"Record inserted for Customer ID {customer_id} in database")

def retrieve_all_previous_order(customer_id):
    sql = "SELECT qty,f.name,total_amt,date FROM orders,fruits as f WHERE customer_id = '" + customer_id + "' and fruit_id = f.id"
    mycursor.execute(sql)
    rows = mycursor.fetchall()

    records = ["Your purchase details are ass follow : "]
    for row in rows:
        records.append(row)
        print(row)
    print("All Record Retreived successfully for Customer ID " + str(customer_id))
    print(records)
    return records

def retrieve_previous_order(customer_id):
    # sql = "SELECT qty,f.name,total_amt,date FROM orders,fruits as f WHERE customer_id = '" + customer_id + "' and fruit_id = f.id"
    # sql = "SELECT * FROM orders WHERE customer_id = '" + customer_id + "'"

    sql = "SELECT qty,f.name,total_amt,date FROM orders,fruits as f WHERE customer_id = '" + customer_id + "' and date = (SELECT MAX( date ) FROM orders b WHERE b.customer_id = '" + customer_id + "')"

    mycursor.execute(sql)
    row = list(mycursor.fetchone())
    output_msg = f"Bought {str(row[0])} kg of {row[1]} for {str(row[2])} rs on {row[3]}"
    # row[0] = get_fruit_name_from_id(row[0])
    print("Last Purchase Record Retreived successfully for Customer ID " + str(customer_id))
    return output_msg

def get_customer_id(name,password):
    name = name.title()
    sql = "SELECT id FROM customers WHERE name = '" + name + "' and password = '" + password + "'"
    mycursor.execute(sql)
    row = mycursor.fetchone()
    # print("Customer ID :" + str(row[0]))
    return row[0]


def get_location(id):
    sql = "SELECT location FROM customers WHERE id = '" + str(id) + "'"
    mycursor.execute(sql)
    row = mycursor.fetchone()
    # print("User Location :" + str(row[0]))
    return row[0]
    
def sign_in(name,password):
    name = name.title()
    sql = "SELECT * FROM customers WHERE name = '" + name + "' and password = '" + password + "'"
    mycursor.execute(sql)
    row = mycursor.fetchone()
    try:
        if len(row) != 0:
            print(f"{name} just logged in ")
            customer_id = get_customer_id(name,password)
            return customer_id,"Success"
    except TypeError:
        return -1,"Failed"

def sign_up(name,location,password):
    name,location = name.title(), location.title()
    sql = "INSERT INTO customers (name,location,password) VALUES (%s,%s,%s)"
    val = (name,location,password)
    mycursor.execute(sql, val)
    db.commit()
    print(f"New User registered with name : {name} and location : {location}")

    customer_id = get_customer_id(name,password)
    return customer_id

def clean_input_for_fruit(fruit):
    # cleaning input to match db value
    fruit = fruit.title()
    if fruit == "Mangoes":
        fruit = "Mango"
    elif fruit.endswith("s"):
        fruit = fruit[:-1]
    return fruit

def get_price(fruit):
    
    fruit = clean_input_for_fruit(fruit)
    sql = "SELECT id,price FROM fruits WHERE name = '" + fruit + "'"
    mycursor.execute(sql)
    row = mycursor.fetchone()
    try: 
        if len(row) != 0:
            print("Price fetched for " + fruit)
            return row[0],row[1],"Success"
    except TypeError:
        return -1,-1,"Failed"

def get_fruit_id(fruit):
    fruit = clean_input_for_fruit(fruit)
    sql = "SELECT id FROM fruits WHERE name = '" + fruit + "'"
    mycursor.execute(sql)
    row = mycursor.fetchone()
    try: 
        if len(row) != 0:
            return row[0]
    except TypeError:
        return -1

def check_fruit(fruit):
    fruit = clean_input_for_fruit(fruit)
    sql = "SELECT id,price FROM fruits WHERE name = '" + fruit + "'"
    mycursor.execute(sql)
    row = mycursor.fetchone()
    try: 
        if len(row) != 0:
            return row[0],row[1],"Success"
    except TypeError:
        return -1,-1,"Failed"

class ActionRecommend(Action):
    
    def name(self) -> Text:
        return "action_recommend"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        user_entered_product = tracker.get_slot('product')

        recommended_products = recommend(user_entered_product)
        print(user_entered_product," : ",recommended_products)
        
        if recommended_products:        
            dispatcher.utter_message(text=f"Recommended Products are:\n")
            dispatcher.utter_message(text=str(recommended_products))
        else:
            dispatcher.utter_message(text=f"Please type some other product")
        return [SlotSet("product", None)]


class ActionSignIn(Action):

    def name(self) -> Text:
        return "action_sign_in"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        name = tracker.get_slot('name')
        password = tracker.get_slot('password')

        customer_id, status = sign_in(name,password)
        
        if status == "Failed":        
            dispatcher.utter_message(text="Please provide valid information or Sign up")
            dispatcher.utter_message(template="utter_sign_in_or_sign_up")
            return [SlotSet("name", None),SlotSet("password", None)]
        else:
            location = get_location(customer_id)
            dispatcher.utter_message(text=f"Logged in successfully as {name} and location : " + location)
        return [SlotSet("customer_id", str(customer_id)),SlotSet("location", location)]


class ActionSignUp(Action):
    
    def name(self) -> Text:
        return "action_sign_up"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        name = tracker.get_slot('name')
        location = tracker.get_slot('location')
        password = tracker.get_slot('password')

        customer_id = sign_up(name,location,password)

        return [SlotSet("customer_id", str(customer_id))]


class ActionAskPrice(Action):
    
    def name(self) -> Text:
        return "action_ask_price"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        fruit = tracker.get_slot('fruit')
        fruit_id,price,status = get_price(fruit)

        if status == "Failed":        
            dispatcher.utter_message(text="Sorry, But we don't have that product, please choose another fruit")
            return
        else:
            dispatcher.utter_message(text=f"Price of {fruit} is {price} rupees per kg")
            dispatcher.utter_message(text=f"If you like to buy {fruit}, please type 'place my order'")

        return [SlotSet("fruit_id", str(fruit_id)),SlotSet("price", str(price))]

class ActionFruitCheck(Action):

    def name(self) -> Text:
        return "action_do_you_have_fruit"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        fruit = tracker.get_slot('fruit')
        id,price, status = check_fruit(fruit)

        if status == "Failed":        
            dispatcher.utter_message(text="Sorry, But we don't have that product, please choose another fruit")
        else:
            dispatcher.utter_message(text=f"Yes we do for {price} per kg")
            dispatcher.utter_message(text=f"If you like to buy {fruit}, please type 'place my order'")

            return [SlotSet("price", str(price)),SlotSet("fruit_id", str(id))]
        return 
        
class ActionInsertProduct(Action):

    def name(self) -> Text:
        return "action_insert_product"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        customer_id = tracker.get_slot('customer_id')
        fruit_id = tracker.get_slot('fruit_id')
        fruit = tracker.get_slot('fruit')
        price = tracker.get_slot('price')
        qty = tracker.get_slot('qty')
        total_amt = int(price)*int(qty)

        if fruit_id == None:
            fruit_id = get_fruit_id(fruit)

        insert_product(customer_id,fruit_id,qty,total_amt)
        return [SlotSet("qty", None)]

class ActionAllPreviousOrder(Action):
    
    def name(self) -> Text:
        return "action_all_previous_order"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        customer_id = tracker.get_slot('customer_id')
        try:
            records = retrieve_all_previous_order(customer_id)
            if records:
                print(records)
                dispatcher.utter_message(text=str(records))
            else:
                dispatcher.utter_message(text="No previous transactions found")
        except:
            dispatcher.utter_message(text="Can you please say that again")
        return []

class ActionPreviousOrder(Action):

    def name(self) -> Text:
        return "action_previous_order"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        customer_id = tracker.get_slot('customer_id')
        records = retrieve_previous_order(customer_id)
        if records:
            print(records)
            dispatcher.utter_message(text=str(records))
        else:
            dispatcher.utter_message(text="No previous transactions found")
            
        return []


# class ActionHelloWorld(Action):
#
#     def name(self) -> Text:
#         return "action_hello_world"
#
#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
#
#         dispatcher.utter_message(text="Hello World!")
#
#         return []

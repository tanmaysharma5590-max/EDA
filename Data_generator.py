#EDA Project

#Step1:- Importing Libraries
import numpy as np
import pandas as pd
import random
from faker import Faker


#Instantiating the Faker library(to generate fake data)
fake = Faker()

#Step2:- Define base lists
categories={
    "Furniture":["Office Chair","Study Table","Sofa","Book Shelf","Dining Table"],
    "Office Supplies":["Pen","Note Book","Stapler","File Folder","Calculator"],
    "Electronics":["Laptop","Keybord","Mouse","Headphones","Monitor"],
    "Grocery":["Rice Bag","Cooking Oil","Sugar","Snacks","Juice Pack"]}
regions=["North","South","East","West"]
payment_Methods=["Cash","Credit Card","UPI","Net Banking"]
delivery_status=["Consumer","Corporate","Home Office"]
customer_segments=["Consumer","Corporate","Home Office"]


#Step3:- Generate Dataset
records=[] #Empty List to store all rows


for i in range(1000): #1000 fake orders
    order_id=f"ORD{1000+i}"
    order_date=fake.date_between(start_date='-2y', end_date='today')
    ship_date=order_date + pd.Timedelta(days=random.randint(1,7))


    customer_name=fake.name()
    customer_id=f"CUST{random.randint(100,999)}"
    customer_segment=random.choice(customer_segments)


    category=random.choice(list(categories.keys()))
    prodect_name=random.choice(categories[category])
    product_id=f"PROD{random.randint(1000,9999)}"

    region=random.choice(regions)
    state=fake.state()
    city=fake.city()

    quantity=random.randint(1,10)
    unit_price=random.randint(100,5000)
    discount=random.choice([0,5,10,15,20])


    sales_amount=quantity*unit_price*(1-discount/100)
    cost_price=sales_amount*random.uniform(0.6,0.9)
    profit=sales_amount - cost_price

    stock_left=random.randint(0,50)

    #Auto orders
    if stock_left<10:
        auto_reorder="Yes"
        reorder_quantity=random.randint(20,50)
    else:
        auto_reorder="No"
        reorder_quantity=0

    supplier_name=fake.company()   
    supplier_email=fake.company_email()
    payment_mode=random.choice(payment_Methods)
    delivery=random.choice(delivery_status)


    #Append row as a dictionary
    records.append({
        "Order ID":order_id,
        "Order Date":order_date,
        "Ship Date":ship_date,
        "Customer ID":customer_id,
        "Customer Name":customer_name,
        "Customer Segment":customer_segment,
        "Product ID":product_id,
        "Product Name":prodect_name,
        "Category":category,
        "Region":region,
        "State":state,
        "City":city,
        "Quantity":quantity,
        "Unit Price":unit_price,
        "Discount (%)":discount,
        "Sales Amount":round(sales_amount,2),
        "Cost Price":round(cost_price,2),
        "Profit":round(profit,2),
        "Payment Mode":payment_mode,
        "Delivery Status":delivery,
        "Supplier Name":supplier_name,
        "Supplier Email": supplier_email,
        "Stock Left":stock_left,
        "Auto Reorder":auto_reorder,
        "Reorder Quantity":reorder_quantity
    })


#step4:- Create DataFrame and Save to CSV
df=pd.DataFrame(records)

try:
     df.to_csv(r"C:\Users\ACER\Desktop\DataScience_Project\EDA_Project\synthetic_sales_data.csv",index=False)
     print("Dataset generated successfully! File saved as 'Superstore_Management_System.csv'")
except PermissionError:
    print("Please close the file 'superstore_management_system.csv' if it's open in Excel or Power BI and try again.")
import os
print(os.getcwd())


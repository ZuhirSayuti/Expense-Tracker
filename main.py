from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker
from sqlalchemy import create_engine,Integer, String, Float,Date
import matplotlib.pyplot as plt
import pandas as pd
import datetime


class Base(DeclarativeBase):
    pass

engine = create_engine("sqlite:///instance/expensetracker.db")

class Expense(Base):
    __tablename__ = "expenses"
    id:Mapped[int] = mapped_column(Integer, primary_key=True)
    product_name:Mapped[str] = mapped_column(String(250),nullable=False)
    amount:Mapped[float] = mapped_column(Float,nullable=False)
    category:Mapped[str] = mapped_column(String(250),nullable=False)
    date:Mapped[date] = mapped_column(Date,nullable=False)

Base.metadata.create_all(engine)


Session = sessionmaker(bind=engine)
session = Session()


def main():
    user_input = input("Hi do you want to check your expenses or add new expense or delete expense? Type 'Check' or 'New' or 'Delete' ")
    while user_input.lower() != "check" and user_input.lower() != "new" and user_input.lower() !="delete":
        user_input = input("Hi do you want to check your expenses or add new expense or delete expense? Type 'Check' or 'New' or 'Delete' ")
    if user_input.lower() == "check":
        expenses = get_all_expenses()
        total = 0
        expenses_product_name = []
        expenses_product_cost = []
        for num in range(len(expenses["Product"])):
            print(f"Product: {expenses['Product'][num]} Amount: {expenses['Amount'][num]} Category: {expenses['Category'][num]} Date: {expenses['Date'][num]}")
            total += expenses['Amount'][num]
            expenses_product_name.append(expenses['Product'][num])
            expenses_product_cost.append(expenses['Amount'][num])
        print(f"Total Expenses: {total}")
        graph_maker(expenses_product_name,expenses_product_cost)
        get_total_by_category()
        csv_ask = input("Do you want to download the file? Type 'Yes' or 'No' ")
        if csv_ask == "Yes".lower():
            export_to_csv()
            print("Done")
    elif user_input.lower() == "new":
        add_expense()
    elif user_input.lower() == "delete":
        expenses = get_all_expenses()
        for num in range(len(expenses["Product"])):
            print(f"Product: {expenses['Product'][num]} Amount: {expenses['Amount'][num]} Category: {expenses['Category'][num]} Date: {expenses['Date'][num]}")
        item_to_delete = input("What item do you want to delete? ")
        delete_expense(item_to_delete)

def get_all_expenses():
    result = session.query(Expense).all()
    session.commit()
    data = {
        "Product": [expense.product_name for expense in result],
        "Amount" : [expense.amount for expense in result],
        "Category": [expense.category for expense in result],
        "Date": [expense.date.strftime('%Y-%m-%d') for expense in result]
    }
    df = pd.DataFrame(data)
    return df

def add_expense():
    df = get_all_expenses()
    product_input = input("What is the name of the product? ").lower()
    while product_input in df["Product"].values:
        product_input = input("The item already exists please rename the item")
    cost_input = input("What is the cost of the product? ")
    category_input = input("What is the category of the product? Ex. Food, Groceries, Tech, others ").lower()
    date_input = input("What is the date of the product purchase? Enter in this format YY/MM/DD ")
    date_list = date_input.split("/")
    date= datetime.date(int(date_list[0]),int(date_list[1]),int(date_list[2]))
    new_expense = Expense(product_name=product_input,amount=cost_input,category=category_input,date=date)
    session.add(new_expense)
    session.commit()
    print("Expense added successfully!")

def get_total_by_category():
    df = get_all_expenses()
    total = df.groupby("Category")["Amount"].sum()
    print(f"Total By {total.to_string(index=True)}")

def graph_maker(x,y):
    plt.figure(figsize=(5,6))
    plt.bar(x,y, color="blue", width=0.3)
    max_value = max(y)
    buffer = max_value * 0.1
    plt.ylim(0,max_value + buffer)
    for i, value in enumerate(y):
        plt.text(i, value + buffer * 0.05, str(value), ha='center',fontsize=10)
    plt.xlabel("Product_name")
    plt.ylabel("Cost")
    plt.title("Expense Tracker")
    plt.tight_layout()
    plt.show()

def export_to_csv():
    df = get_all_expenses()
    df.to_csv("ExpensesFile.csv", index=False)

def delete_expense(item):
    expense_to_delete = session.query(Expense).filter_by(product_name=item).first()
    if expense_to_delete:
        session.delete(expense_to_delete)
        session.commit()
        print("Done")
        return True
    else:
        print("Item not Found")
        return False
while True:
    main()
    continue_check = input("Do you want to continue? type 'Yes' or 'No' ")
    if continue_check.lower() == "no":
        break

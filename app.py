import sqlite3
import random
import pandas as pd
from flask import Flask, render_template, request

app = Flask(__name__)

# ================= LOAD DATA =================
df = pd.read_excel(r"C:\Users\DELL\Downloads\buses.xlsx")
hotel_df = pd.read_excel(r"C:\Users\DELL\Downloads\hotels.xlsx")
flight_df  = pd.read_excel(r"C:\Users\DELL\Downloads\flights.xlsx")

# -------- CLEAN BUS DATA --------
df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d')
df['source'] = df['source'].astype(str).str.strip()
df['destination'] = df['destination'].astype(str).str.strip()
df['type'] = df['type'].astype(str).str.strip()

# -------- CLEAN HOTEL DATA --------
hotel_df['city'] = hotel_df['city'].astype(str).str.strip()
hotel_df['room_type'] = hotel_df['room_type'].astype(str).str.strip()

# -------- CLEAN FLIGHT DATA --------
flight_df['date'] = pd.to_datetime(flight_df['date']).dt.strftime('%Y-%m-%d')
flight_df['from_city'] = flight_df['from_city'].astype(str).str.strip()
flight_df['to_city'] = flight_df['to_city'].astype(str).str.strip()


# ================= DATABASE INIT =================
def init_db():
    conn = sqlite3.connect("travel.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS bus_booking (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        booking_id TEXT,
        name TEXT,
        email TEXT,
        bus_number TEXT,
        seat_number TEXT,
        source TEXT,
        destination TEXT,
        date TEXT,
        price INTEGER,
        status TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS hotel_booking (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        booking_id TEXT,
        name TEXT,
        email TEXT,
        hotel_name TEXT,
        city TEXT,
        price INTEGER,
        status TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS flight_booking (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        booking_id TEXT,
        name TEXT,
        email TEXT,
        flight_number TEXT,
        from_city TEXT,
        to_city TEXT,
        date TEXT,
        price INTEGER,
        status TEXT
    )
    """)
    cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    email TEXT UNIQUE,
    phone TEXT,
    city TEXT
)
""")

    conn.commit()
    conn.close()

init_db()


# ================= HOME =================
@app.route('/')
def home():
    return render_template('index.html')


# ================= BUS SEARCH =================
@app.route('/bus', methods=['GET', 'POST'])
def bus():
    if request.method == 'POST':
        source = request.form['source']
        destination = request.form['destination']
        date = request.form['date']

        filtered = df[
            (df['source'].str.lower() == source.lower()) &
            (df['destination'].str.lower() == destination.lower()) &
            (df['date'] == date)
        ]

        buses = filtered.to_dict(orient='records')

        return render_template("bus.html",
                               buses=buses,
                               searched=True,
                               source=source,
                               destination=destination,
                               date=date)

    return render_template("bus.html", searched=False)


# ================= SELECT SEAT =================
@app.route('/select-seat', methods=['POST'])
def select_seat():
    return render_template(
        "select_seat.html",
        booking_type="bus",
        bus_number=request.form['bus_number'],
        price=request.form['price'],
        name=request.form['name'],
        email=request.form['email'],
        source=request.form['source'],
        destination=request.form['destination'],
        date=request.form['date']
    )


# ================= GO TO PAYMENT =================
@app.route('/bus/book', methods=['POST'])
def bus_book():
    return render_template(
        "payment.html",
        booking_type="bus",
        data=request.form
    )


# ================= HOTEL =================
@app.route('/hotel/book', methods=['POST'])
def hotel_book():
    return render_template("payment.html",
                           booking_type="hotel",
                           data=request.form)
@app.route('/hotel', methods=['GET', 'POST'])
def hotel():
    if request.method == 'POST':

        city = request.form['city']
        checkin = request.form['checkin']
        checkout = request.form['checkout']

        filtered = hotel_df[
            hotel_df['city'].str.lower() == city.lower()
        ]

        hotels = filtered.to_dict(orient='records')

        return render_template(
            "hotel.html",
            hotels=hotels,
            searched=True,
            city=city,
            checkin=checkin,
            checkout=checkout
        )

    return render_template("hotel.html", searched=False)

# ================= FLIGHT =================
@app.route('/flight', methods=['GET', 'POST'])
def flight():
    if request.method == 'POST':
        from_city = request.form['from_city']
        to_city = request.form['to_city']
        date = request.form['date']

        filtered = flight_df[
            (flight_df['from_city'].str.lower() == from_city.lower()) &
            (flight_df['to_city'].str.lower() == to_city.lower()) &
            (flight_df['date'] == date)
        ]

        flights = filtered.to_dict(orient='records')

        return render_template(
            "flight.html",
            flights=flights,
            searched=True,
            from_city=from_city,
            to_city=to_city,
            date=date
        )

    return render_template("flight.html", searched=False)


# -------- FLIGHT SEAT SELECTION --------
@app.route('/flight/select-seat', methods=['POST'])
def flight_select_seat():
    return render_template(
        "flight_select_seat.html",
        flight_number=request.form['flight_number'],
        price=request.form['price'],
        name=request.form['name'],
        email=request.form['email'],
        from_city=request.form['from_city'],
        to_city=request.form['to_city'],
        date=request.form['date']
    )


# -------- FLIGHT PAYMENT --------
@app.route('/flight/book', methods=['POST'])
def flight_book():
    return render_template(
        "payment.html",
        booking_type="flight",
        data=request.form
    )

# ================= PAYMENT PROCESS =================
@app.route('/payment/process', methods=['POST'])
def process_payment():

    booking_type = request.form['booking_type']
    name = request.form['name']
    email = request.form['email']
    price = request.form['price']
    seat_number = request.form.get("seat_number")

    booking_id = booking_type[:1].upper() + "B" + str(random.randint(1000, 9999))

    conn = sqlite3.connect("travel.db")
    cursor = conn.cursor()

    if booking_type == "bus":
        cursor.execute("""
        INSERT INTO bus_booking
        (booking_id, name, email, bus_number, seat_number, source, destination, date, price, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (booking_id, name, email,
         request.form['bus_number'],
         seat_number,
         request.form['source'],
         request.form['destination'],
         request.form['date'],
         price, "CONFIRMED"))

        template = "bus_confirmation.html"

    elif booking_type == "hotel":
        cursor.execute("""
        INSERT INTO hotel_booking
        (booking_id, name, email, hotel_name, city, price, status)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (booking_id, name, email,
         request.form['hotel_name'],
         request.form['city'],
         price, "CONFIRMED"))

        template = "hotel_confirmation.html"

    elif booking_type == "flight":
        cursor.execute("""
        INSERT INTO flight_booking
        (booking_id, name, email, flight_number, from_city, to_city, date, price, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (booking_id, name, email,
         request.form['flight_number'],
         request.form['from_city'],
         request.form['to_city'],
         request.form['date'],
         price, "CONFIRMED"))

        template = "flight_confirmation.html"

    conn.commit()
    conn.close()

    return render_template(template,
                           booking_id=booking_id,
                           name=name,
                           price=price,
                           seat_number=seat_number)
# ================= MY BOOKINGS =================
@app.route('/my-bookings')
def my_bookings():
    conn = sqlite3.connect("travel.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM bus_booking ORDER BY id DESC")
    bus_bookings = cursor.fetchall()

    cursor.execute("SELECT * FROM flight_booking ORDER BY id DESC")
    flight_bookings = cursor.fetchall()

    cursor.execute("SELECT * FROM hotel_booking ORDER BY id DESC")
    hotel_bookings = cursor.fetchall()

    conn.close()

    return render_template(
        "my_bookings.html",
        bus_bookings=bus_bookings,
        flight_bookings=flight_bookings,
        hotel_bookings=hotel_bookings
    )


# ================= HELP =================
@app.route('/help')
def help_page():
    return render_template("help.html")


# ================= ACCOUNT =================
# ================= ACCOUNT =================
@app.route('/account', methods=['GET', 'POST'])
def account():
    conn = sqlite3.connect("travel.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        city = request.form['city']

        cursor.execute("""
        INSERT OR REPLACE INTO users (name, email, phone, city)
        VALUES (?, ?, ?, ?)
        """, (name, email, phone, city))

        conn.commit()

    cursor.execute("SELECT * FROM users ORDER BY id DESC LIMIT 1")
    user = cursor.fetchone()

    conn.close()

    return render_template("account.html", user=user)

if __name__ == '__main__':
    app.run(debug=True)
from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
from mysql.connector import Error
import hashlib

app = Flask(__name__)
CORS(app)

def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="agri_management"
        )
        return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

@app.route("/")
def home():
    return "Backend server is running!"

@app.route("/test-db")
def test_db():
    connection = get_db_connection()
    if connection and connection.is_connected():
        connection.close()
        return "Database connection successful!"
    return "Database connection failed!"

@app.route("/api/users/register", methods=["POST"])
def register_user():
    data = request.json
    connection = get_db_connection()
    
    if connection:
        try:
            cursor = connection.cursor()
            hashed_password = hashlib.sha256(data['password'].encode()).hexdigest()
            
            query = """INSERT INTO users (username, email, password, role, phone) 
                      VALUES (%s, %s, %s, %s, %s)"""
            values = (
                data['username'],
                data['email'],
                hashed_password,
                data['role'],
                data['phone']
            )
            
            cursor.execute(query, values)
            connection.commit()
            return jsonify({"success": True, "message": "Registration successful!"})
            
        except Error as e:
            return jsonify({"success": False, "message": str(e)})
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
    
    return jsonify({"success": False, "message": "Database connection failed"})

@app.route("/api/users/login", methods=["POST"])
def login_user():
    data = request.json
    connection = get_db_connection()
    
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            hashed_password = hashlib.sha256(data['password'].encode()).hexdigest()
            
            query = """SELECT id, username, email, role FROM users 
                      WHERE username = %s AND password = %s AND role = %s"""
            values = (data['username'], hashed_password, data['role'])
            
            cursor.execute(query, values)
            user = cursor.fetchone()
            
            if user:
                return jsonify({
                    "success": True,
                    "message": "Login successful!",
                    "user": user
                })
            else:
                return jsonify({
                    "success": False,
                    "message": "Invalid credentials"
                })
                
        except Error as e:
            return jsonify({"success": False, "message": str(e)})
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
    
    return jsonify({"success": False, "message": "Database connection failed"})

@app.route("/api/products", methods=["POST"])
def add_product():
    data = request.json
    connection = get_db_connection()
    
    if connection:
        try:
            cursor = connection.cursor()
            query = """INSERT INTO products (name, description, category, farmer_id, 
                      quantity, unit, price, location) 
                      VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""
            values = (
                data['name'],
                data['description'],
                data['category'],
                data['farmer_id'],
                data['quantity'],
                data['unit'],
                data['price'],
                data['location']
            )
            
            cursor.execute(query, values)
            connection.commit()
            return jsonify({"success": True, "message": "Product added successfully"})
        except Error as e:
            return jsonify({"success": False, "message": str(e)})
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
    return jsonify({"success": False, "message": "Database connection failed"})

@app.route("/api/products/farmer/<int:farmer_id>", methods=["GET"])
def get_farmer_products(farmer_id):
    connection = get_db_connection()
    
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            query = "SELECT * FROM products WHERE farmer_id = %s"
            cursor.execute(query, (farmer_id,))
            products = cursor.fetchall()
            return jsonify({"success": True, "products": products})
        except Error as e:
            return jsonify({"success": False, "message": str(e)})
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
    return jsonify({"success": False, "message": "Database connection failed"})

@app.route("/api/products", methods=["GET"])
def get_all_products():
    connection = get_db_connection()
    
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            query = """
                SELECT p.*, u.username as farmer_name 
                FROM products p 
                JOIN users u ON p.farmer_id = u.id
            """
            cursor.execute(query)
            products = cursor.fetchall()
            return jsonify({"success": True, "products": products})
        except Error as e:
            return jsonify({"success": False, "message": str(e)})
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
    return jsonify({"success": False, "message": "Database connection failed"})

@app.route("/api/products/search", methods=["GET"])
def search_products():
    category = request.args.get('category')
    location = request.args.get('location')
    min_price = request.args.get('min_price')
    max_price = request.args.get('max_price')
    
    connection = get_db_connection()
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            query = """
                SELECT p.*, u.username as farmer_name, u.phone as farmer_phone 
                FROM products p 
                JOIN users u ON p.farmer_id = u.id 
                WHERE 1=1
            """
            params = []
            
            if category:
                query += " AND category = %s"
                params.append(category)
            if location:
                query += " AND location LIKE %s"
                params.append(f"%{location}%")
            if min_price:
                query += " AND price >= %s"
                params.append(float(min_price))
            if max_price:
                query += " AND price <= %s"
                params.append(float(max_price))
                
            cursor.execute(query, params)
            products = cursor.fetchall()
            return jsonify({"success": True, "products": products})
        except Error as e:
            return jsonify({"success": False, "message": str(e)})
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
    return jsonify({"success": False, "message": "Database connection failed"})

@app.route("/api/markets", methods=["GET"])
def get_markets():
    connection = get_db_connection()
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT DISTINCT location FROM products")
            markets = cursor.fetchall()
            return jsonify({"success": True, "markets": markets})
        except Error as e:
            return jsonify({"success": False, "message": str(e)})
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
    return jsonify({"success": False, "message": "Database connection failed"})

if __name__ == "__main__":
    app.run(debug=True, port=5000)
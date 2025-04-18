from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
import mysql.connector
from mysql.connector import Error
import hashlib
import datetime

app = Flask(__name__, template_folder="templates", static_folder="static")
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

# Admin Authentication Check
def is_admin(user_id):
    connection = get_db_connection()
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT role FROM users WHERE id = %s", (user_id,))
            user = cursor.fetchone()
            return user and user['role'] == 'admin'
        except Error as e:
            print(f"Error checking admin status: {e}")
            return False
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
    return False

# Frontend routes - make sure these match your HTML templates
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/login")
def login_page():
    try:
        return render_template("login.html")
    except Exception as e:
        return f"Error loading login page: {str(e)}", 500

@app.route("/register")
def register_page():
    return render_template("register.html")

@app.route("/farmer-dashboard")
def farmer_dashboard():
    return render_template("farmer_dashboard.html")

@app.route("/trader-dashboard")
def trader_dashboard():
    return render_template("trader_dashboard.html")

@app.route("/admin-dashboard")
def admin_dashboard():
    return render_template("admin_dashboard.html")

# Update a product
@app.route("/api/products/<int:product_id>", methods=["PUT"])
def update_product(product_id):
    data = request.json
    connection = get_db_connection()
    
    if connection:
        try:
            cursor = connection.cursor()
            # Check if product exists and belongs to farmer
            check_query = "SELECT farmer_id FROM products WHERE id = %s"
            cursor.execute(check_query, (product_id,))
            result = cursor.fetchone()
            
            if not result:
                return jsonify({"success": False, "message": "Product not found"})
                
            farmer_id = result[0]
            if int(farmer_id) != int(data['farmer_id']):
                return jsonify({"success": False, "message": "Unauthorized access"})
            
            # Update product
            query = """UPDATE products 
                      SET name = %s, description = %s, category = %s, 
                      quantity = %s, unit = %s, price = %s, location = %s
                      WHERE id = %s"""
            values = (
                data['name'],
                data['description'],
                data['category'],
                data['quantity'],
                data['unit'],
                data['price'],
                data['location'],
                product_id
            )
            cursor.execute(query, values)
            connection.commit()             
            return jsonify({"success": True, "message": "Product updated successfully"})
        except Error as e:
           return jsonify({"success": False, "message": str(e)})
        finally:
           if connection.is_connected():
               cursor.close()
               connection.close()
    return jsonify({"success": False, "message": "Database connection failed"})

# Delete a product
@app.route("/api/products/<int:product_id>", methods=["DELETE"])
def delete_product(product_id):
   data = request.json
   connection = get_db_connection()
   
   if connection:
       try:
           cursor = connection.cursor()
           # Check if product exists and belongs to farmer
           check_query = "SELECT farmer_id FROM products WHERE id = %s"
           cursor.execute(check_query, (product_id,))
           result = cursor.fetchone()
           
           if not result:
               return jsonify({"success": False, "message": "Product not found"})
               
           farmer_id = result[0]
           if int(farmer_id) != int(data['farmer_id']):
               return jsonify({"success": False, "message": "Unauthorized access"})
           
           # Delete product
           query = "DELETE FROM products WHERE id = %s"
           cursor.execute(query, (product_id,))
           connection.commit()
           return jsonify({"success": True, "message": "Product deleted successfully"})
       except Error as e:
           return jsonify({"success": False, "message": str(e)})
       finally:
           if connection.is_connected():
               cursor.close()
               connection.close()
   return jsonify({"success": False, "message": "Database connection failed"})

@app.route("/test-template")
def test_template():
   import os
   template_path = os.path.join(app.template_folder, "login.html")
   if os.path.exists(template_path):
       return f"Template exists at {template_path}"
   else:
       return f"Template does not exist at {template_path}" 

@app.route("/test")
def test_page():
   return render_template("test.html")              

# API routes
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

@app.route("/api/products/advanced-search", methods=["GET"])
def advanced_search_products():
   # Get filter parameters
   category = request.args.get('category')
   location = request.args.get('location')
   min_price = request.args.get('min_price')
   max_price = request.args.get('max_price')
   search_term = request.args.get('search_term')
   sort_by = request.args.get('sort_by', 'price_asc')  # Default sort by price ascending
   
   connection = get_db_connection()
   if connection:
       try:
           cursor = connection.cursor(dictionary=True)
           
           # Base query
           query = """
               SELECT p.*, u.username as farmer_name, u.phone as farmer_phone 
               FROM products p 
               JOIN users u ON p.farmer_id = u.id 
               WHERE 1=1
           """
           params = []
           
           # Add filters
           if category and category != "All":
               query += " AND p.category = %s"
               params.append(category)
           
           if location and location != "All":
               query += " AND p.location LIKE %s"
               params.append(f"%{location}%")
           
           if search_term:
               query += " AND (p.name LIKE %s OR p.description LIKE %s OR p.category LIKE %s)"
               term = f"%{search_term}%"
               params.extend([term, term, term])
           
           if min_price:
               query += " AND p.price >= %s"
               params.append(float(min_price))
           
           if max_price:
               query += " AND p.price <= %s"
               params.append(float(max_price))
           
           # Add sorting
           if sort_by == 'price_asc':
               query += " ORDER BY p.price ASC"
           elif sort_by == 'price_desc':
               query += " ORDER BY p.price DESC"
           elif sort_by == 'newest':
               query += " ORDER BY p.created_at DESC"
           elif sort_by == 'quantity_desc':
               query += " ORDER BY p.quantity DESC"
           
           cursor.execute(query, params)
           products = cursor.fetchall()
           
           # Get all available locations for the filter dropdown
           cursor.execute("SELECT DISTINCT location FROM products")
           locations = cursor.fetchall()
           
           return jsonify({
               "success": True, 
               "products": products,
               "locations": [loc['location'] for loc in locations]
           })
           
       except Error as e:
           return jsonify({"success": False, "message": str(e)})
       finally:
           if connection.is_connected():
               cursor.close()
               connection.close()
   
   return jsonify({"success": False, "message": "Database connection failed"})

@app.route("/api/simple-trends", methods=["GET"])
def get_simple_trends():
    connection = get_db_connection()
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            
            # Get all products
            cursor.execute("SELECT DISTINCT product_name FROM price_trends")
            products = cursor.fetchall()
            product_list = [p['product_name'] for p in products]
            
            # Get all trends
            cursor.execute("SELECT * FROM price_trends ORDER BY product_name, date")
            all_trends = cursor.fetchall()
            
            # Format dates
            for trend in all_trends:
                if isinstance(trend['date'], (datetime.date, datetime.datetime)):
                    trend['date'] = trend['date'].strftime('%Y-%m-%d')
            
            return jsonify({
                "success": True,
                "products": product_list,
                "trends": all_trends
            })
            
        except Exception as e:
            print(f"Error in simple-trends: {e}")
            return jsonify({"success": False, "message": str(e)})
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
    
    return jsonify({"success": False, "message": "Database connection failed"})

@app.route("/api/price-trends", methods=["POST"])
def add_price_trend():
    data = request.json
    connection = get_db_connection()
    if connection:
        try:
            cursor = connection.cursor()
            
            query = """
                INSERT INTO price_trends (product_name, price, market, date, added_by)
                VALUES (%s, %s, %s, %s, %s)
            """
            
            values = (
                data['product_name'],
                data['price'],
                data.get('market', None),  # Handle potentially missing market
                data['date'],
                data.get('added_by', None)  # Handle potentially missing added_by
            )
            
            cursor.execute(query, values)
            connection.commit()
            
            return jsonify({"success": True, "message": "Price trend added successfully"})
            
        except Error as e:
            return jsonify({"success": False, "message": str(e)})
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
    
    return jsonify({"success": False, "message": "Database connection failed"})

@app.route("/api/price-trends", methods=["GET"])
def get_price_trends():
    product = request.args.get('product')
    days = request.args.get('days', '30')
    
    connection = get_db_connection()
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            
            # Get all available products
            cursor.execute("SELECT DISTINCT product_name FROM price_trends")
            products = cursor.fetchall()
            product_list = [p['product_name'] for p in products]
            
            # If no specific product requested, use the first one
            selected_product = product if product and product in product_list else (product_list[0] if product_list else None)
            
            # Get trends for the selected product and time period
            if selected_product:
                # Calculate date filter based on days
                query = """
                    SELECT pt.*, u.username as added_by_name 
                    FROM price_trends pt
                    LEFT JOIN users u ON pt.added_by = u.id
                    WHERE pt.product_name = %s 
                    AND pt.date >= DATE_SUB(CURRENT_DATE, INTERVAL %s DAY)
                    ORDER BY pt.date ASC, pt.market ASC
                """
                cursor.execute(query, (selected_product, int(days)))
                trends = cursor.fetchall()
                
                # Format dates for JSON response
                for trend in trends:
                    if isinstance(trend['date'], (datetime.date, datetime.datetime)):
                        trend['date'] = trend['date'].strftime('%Y-%m-%d')
                    # Handle null market
                    if trend['market'] is None:
                        trend['market'] = 'Unknown'
                
                return jsonify({
                    "success": True,
                    "products": product_list,
                    "selected_product": selected_product,
                    "trends": trends
                })
            else:
                return jsonify({
                    "success": True,
                    "products": [],
                    "trends": []
                })
                
        except Error as e:
            return jsonify({"success": False, "message": str(e)})
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
    
    return jsonify({"success": False, "message": "Database connection failed"})

@app.route("/test-trends")
def test_trends_page():
    return render_template("test_trends.html")

# =================================================================
# ADMIN DASHBOARD API ENDPOINTS
# =================================================================

# Get stats for admin dashboard
@app.route("/api/admin/stats", methods=["GET"])
def get_admin_stats():
    connection = get_db_connection()
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            
            # Get user counts
            cursor.execute("SELECT COUNT(*) as total FROM users")
            total_users = cursor.fetchone()['total']
            
            cursor.execute("SELECT COUNT(*) as count FROM users WHERE role = 'farmer'")
            farmers_count = cursor.fetchone()['count']
            
            cursor.execute("SELECT COUNT(*) as count FROM users WHERE role = 'trader'")
            traders_count = cursor.fetchone()['count']
            
            # Get product counts
            cursor.execute("SELECT COUNT(*) as total FROM products")
            total_products = cursor.fetchone()['total']
            
            cursor.execute("SELECT COUNT(DISTINCT category) as count FROM products")
            categories_count = cursor.fetchone()['count']
            
            # Get price trends counts
            cursor.execute("SELECT COUNT(*) as total FROM price_trends")
            total_trends = cursor.fetchone()['total']
            
            cursor.execute("SELECT COUNT(DISTINCT product_name) as count FROM price_trends")
            tracked_products = cursor.fetchone()['count']
            
            # Get recent users
            cursor.execute("SELECT id, username, email, role, created_at FROM users ORDER BY id DESC LIMIT 5")
            recent_users = cursor.fetchall()
            
            # Get recent products
            cursor.execute("""
                SELECT p.id, p.name, p.category, p.price, p.created_at, u.username as farmer_name
                FROM products p
                JOIN users u ON p.farmer_id = u.id
                ORDER BY p.id DESC LIMIT 5
            """)
            recent_products = cursor.fetchall()
            
            # Format dates for JSON
            for user in recent_users:
                if isinstance(user['created_at'], (datetime.date, datetime.datetime)):
                    user['created_at'] = user['created_at'].strftime('%Y-%m-%d %H:%M:%S')
            
            for product in recent_products:
                if isinstance(product['created_at'], (datetime.date, datetime.datetime)):
                    product['created_at'] = product['created_at'].strftime('%Y-%m-%d %H:%M:%S')
            
            return jsonify({
                "success": True,
                "stats": {
                    "users": {
                        "total": total_users,
                        "farmers": farmers_count,
                        "traders": traders_count
                    },
                    "products": {
                        "total": total_products,
                        "categories": categories_count
                    },
                    "price_trends": {
                        "total": total_trends,
                        "tracked_products": tracked_products
                    }
                },
                "recent_users": recent_users,
                "recent_products": recent_products
            })
        except Error as e:
            return jsonify({"success": False, "message": str(e)})
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
    
    return jsonify({"success": False, "message": "Database connection failed"})

# Get all users for admin
@app.route("/api/admin/users", methods=["GET"])
def get_admin_users():
    admin_id = request.args.get('admin_id')
    if not admin_id or not is_admin(admin_id):
        return jsonify({"success": False, "message": "Unauthorized access"})
    
    connection = get_db_connection()
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            
            cursor.execute("SELECT id, username, email, role, phone FROM users ORDER BY id DESC")
            users = cursor.fetchall()
            
            return jsonify({
                "success": True,
                "users": users
            })
        except Error as e:
            return jsonify({"success": False, "message": str(e)})
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
    
    return jsonify({"success": False, "message": "Database connection failed"})

# Get all products for admin
@app.route("/api/admin/products", methods=["GET"])
def get_admin_products():
    admin_id = request.args.get('admin_id')
    if not admin_id or not is_admin(admin_id):
        return jsonify({"success": False, "message": "Unauthorized access"})
    
    connection = get_db_connection()
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            
            query = """
                SELECT p.*, u.username as farmer_name 
                FROM products p 
                JOIN users u ON p.farmer_id = u.id
                ORDER BY p.id DESC
            """
            cursor.execute(query)
            products = cursor.fetchall()
            
            return jsonify({
                "success": True,
                "products": products
            })
        except Error as e:
            return jsonify({"success": False, "message": str(e)})
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
    
    return jsonify({"success": False, "message": "Database connection failed"})

# Admin delete product
@app.route("/api/admin/products/<int:product_id>", methods=["DELETE"])
def admin_delete_product(product_id):
    data = request.json
    admin_id = data.get('admin_id')
    
    if not admin_id or not is_admin(admin_id):
        return jsonify({"success": False, "message": "Unauthorized access"})
    
    connection = get_db_connection()
    if connection:
        try:
            cursor = connection.cursor()
            
            # Delete product
            cursor.execute("DELETE FROM products WHERE id = %s", (product_id,))
            connection.commit()
            
            return jsonify({
                "success": True,
                "message": "Product deleted successfully"
            })
        except Error as e:
            return jsonify({"success": False, "message": str(e)})
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
    
    return jsonify({"success": False, "message": "Database connection failed"})

# Get all price trends for admin
@app.route("/api/admin/price-trends", methods=["GET"])
def get_admin_price_trends():
    admin_id = request.args.get('admin_id')
    if not admin_id or not is_admin(admin_id):
        return jsonify({"success": False, "message": "Unauthorized access"})
    
    connection = get_db_connection()
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            
            query = """
                SELECT pt.*, u.username as added_by_name 
                FROM price_trends pt
                LEFT JOIN users u ON pt.added_by = u.id
                ORDER BY pt.id DESC
            """
            cursor.execute(query)
            trends = cursor.fetchall()
            
            # Format dates for JSON
            for trend in trends:
                if isinstance(trend['date'], (datetime.date, datetime.datetime)):
                    trend['date'] = trend['date'].strftime('%Y-%m-%d')
            
            # Get all product names for the dropdown
            cursor.execute("SELECT DISTINCT product_name FROM price_trends ORDER BY product_name")
            products = [row['product_name'] for row in cursor.fetchall()]
            
            # Get all markets for the dropdown
            cursor.execute("SELECT DISTINCT market FROM price_trends WHERE market IS NOT NULL ORDER BY market")
            markets = [row['market'] for row in cursor.fetchall()]
            
            return jsonify({
                "success": True,
                "trends": trends,
                "products": products,
                "markets": markets
            })
        except Error as e:
            return jsonify({"success": False, "message": str(e)})
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
    
    return jsonify({"success": False, "message": "Database connection failed"})

# Admin delete price trend
@app.route("/api/admin/price-trends/<int:trend_id>", methods=["DELETE"])
def admin_delete_price_trend(trend_id):
    data = request.json
    admin_id = data.get('admin_id')
    
    if not admin_id or not is_admin(admin_id):
        return jsonify({"success": False, "message": "Unauthorized access"})
    
    connection = get_db_connection()
    if connection:
        try:
            cursor = connection.cursor()
            
            # Delete price trend
            cursor.execute("DELETE FROM price_trends WHERE id = %s", (trend_id,))
            connection.commit()
            
            return jsonify({
                "success": True,
                "message": "Price trend deleted successfully"
            })
        except Error as e:
            return jsonify({"success": False, "message": str(e)})
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
    
    return jsonify({"success": False, "message": "Database connection failed"})

# Get all products and markets for price trend form
@app.route("/api/admin/products/names", methods=["GET"])
def get_admin_product_names():
    admin_id = request.args.get('admin_id')
    if not admin_id or not is_admin(admin_id):
        return jsonify({"success": False, "message": "Unauthorized access"})
    
    connection = get_db_connection()
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            
            # Get product names from both tables
            query = """
                SELECT DISTINCT name FROM (
                    SELECT name FROM products
                    UNION
                    SELECT product_name as name FROM price_trends
                ) AS combined_products
                ORDER BY name
            """
            cursor.execute(query)
            products = [row['name'] for row in cursor.fetchall()]
            
            # Get markets from the location field in products
            cursor.execute("SELECT DISTINCT location FROM products WHERE location IS NOT NULL ORDER BY location")
            markets = [row['location'] for row in cursor.fetchall()]
            
            return jsonify({
                "success": True,
                "products": products,
                "markets": markets
            })
        except Error as e:
            return jsonify({"success": False, "message": str(e)})
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
    
    return jsonify({"success": False, "message": "Database connection failed"})

# Add a handler for 404 errors
@app.errorhandler(404)
def page_not_found(e):
   return f"Page not found. Available routes: /, /login, /register, /farmer-dashboard, /trader-dashboard, /admin-dashboard", 404

if __name__ == "__main__":
   app.run(debug=True, port=5000)
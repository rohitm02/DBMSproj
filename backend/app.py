from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)

# Enable CORS for the React frontend
CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}})

# Database configuration
db_config = {
    'user': 'root',
    'password': 'rinzler',
    'host': 'localhost',
    'database': 'oem'
}

def get_db_connection():
    """Create and return a database connection"""
    try:
        connection = mysql.connector.connect(**db_config)
        return connection
    except Error as e:
        print(f"Error connecting to database: {e}")
        return None

# Supplier Routes
@app.route('/api/suppliers', methods=['GET'])
def get_suppliers():
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': 'Database connection failed'}), 500

        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM supplier ORDER BY supplier_id DESC")
        suppliers = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(suppliers)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/suppliers', methods=['POST'])
def add_supplier():
    try:
        data = request.json
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': 'Database connection failed'}), 500

        cursor = conn.cursor()
        query = """
        INSERT INTO supplier (company_name, contact_person, email, phone_number) 
        VALUES (%s, %s, %s, %s)
        """
        values = (
            data['company_name'],
            data['contact_person'],
            data['email'],
            data['phone_number']
        )
        cursor.execute(query, values)
        conn.commit()
        
        new_supplier_id = cursor.lastrowid
        cursor.close()
        conn.close()
        
        return jsonify({
            'supplier_id': new_supplier_id,
            **data
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Material Routes
@app.route('/api/materials', methods=['GET'])
def get_materials():
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': 'Database connection failed'}), 500

        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT * FROM raw_material 
            ORDER BY material_id DESC
        """)
        materials = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(materials)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/materials', methods=['POST'])
def add_material():
    try:
        data = request.json
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': 'Database connection failed'}), 500

        cursor = conn.cursor()
        query = """
        INSERT INTO raw_material 
        (material_name, description, current_stock_level, reorder_level) 
        VALUES (%s, %s, %s, %s)
        """
        values = (
            data['material_name'],
            data['description'],
            data['current_stock_level'],
            data['reorder_level']
        )
        cursor.execute(query, values)
        conn.commit()
        
        new_material_id = cursor.lastrowid
        cursor.close()
        conn.close()
        
        return jsonify({
            'material_id': new_material_id,
            **data
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/supplier_materials', methods=['POST'])
def add_supplier_material():
    try:
        data = request.json
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': 'Database connection failed'}), 500

        cursor = conn.cursor()
        query = """
        INSERT INTO supplier_material 
        (supplier_id, material_id, unit_price) 
        VALUES (%s, %s, %s)
        """
        values = (
            data['supplier_id'],
            data['material_id'],
            data['unit_price']
        )
        cursor.execute(query, values)
        conn.commit()
        
        new_id = cursor.lastrowid
        cursor.close()
        conn.close()
        
        return jsonify({
            'supplier_material_id': new_id,
            **data
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Purchase Order Routes
@app.route('/api/orders', methods=['GET'])
def get_orders():
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': 'Database connection failed'}), 500

        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT po.*, s.company_name as supplier_name 
            FROM purchase_order po 
            JOIN supplier s ON po.supplier_id = s.supplier_id 
            ORDER BY po.po_id DESC
        """)
        orders = cursor.fetchall()
        
        # Convert datetime objects to string format
        for order in orders:
            if 'order_date' in order and order['order_date']:
                order['order_date'] = order['order_date'].strftime('%Y-%m-%d %H:%M:%S')
        
        cursor.close()
        conn.close()
        return jsonify(orders)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/orders', methods=['POST'])
def add_order():
    try:
        data = request.json
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': 'Database connection failed'}), 500

        cursor = conn.cursor()
        query = """
        INSERT INTO purchase_order 
        (supplier_id, order_date, status, total_amount) 
        VALUES (%s, %s, %s, %s)
        """
        values = (
            data['supplier_id'],
            datetime.now(),
            data['status'],
            data['total_amount']
        )
        cursor.execute(query, values)
        conn.commit()
        
        new_order_id = cursor.lastrowid
        cursor.close()
        conn.close()
        
        return jsonify({
            'po_id': new_order_id,
            **data,
            'order_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Supplier Performance Routes
@app.route('/api/supplier_performance', methods=['GET'])
def get_supplier_performance():
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': 'Database connection failed'}), 500

        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT sp.*, s.company_name 
            FROM supplier_performance sp
            JOIN supplier s ON sp.supplier_id = s.supplier_id
            ORDER BY sp.performance_id DESC
        """)
        performance = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(performance)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/supplier_performance', methods=['POST'])
def add_supplier_performance():
    try:
        data = request.json
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': 'Database connection failed'}), 500

        cursor = conn.cursor()
        query = """
        INSERT INTO supplier_performance 
        (supplier_id, quality_rating, on_time_delivery_rate, average_response_time) 
        VALUES (%s, %s, %s, %s)
        """
        values = (
            data['supplier_id'],
            data['quality_rating'],
            data['on_time_delivery_rate'],
            data['average_response_time']
        )
        cursor.execute(query, values)
        conn.commit()
        
        new_performance_id = cursor.lastrowid
        cursor.close()
        conn.close()
        
        return jsonify({
            'performance_id': new_performance_id,
            **data
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Error Handlers
@app.errorhandler(404)
def not_found_error(error):
    return jsonify({'error': 'Resource not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(debug=True)
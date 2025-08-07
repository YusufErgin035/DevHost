from flask import Flask, request, jsonify , render_template , redirect , url_for , flash
import psycopg2 
import os
import subprocess
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
app.secret_key = "12098as45d6a5s"

list = []

def get_connection():
    return psycopg2.connect(
        host=os.getenv('DB_HOST'),
        port=os.getenv('DB_PORT'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        dbname=os.getenv('DB_NAME')
    )

@app.route('/', methods=["GET"])
def start():
    create_table()
    list = get_all_devices()
    return render_template("index.html", list=list)

@app.route("/", methods=["POST"])
def add():
    name = request.form["name"]
    ip = request.form["ip_address"]
    desc = request.form["description"]
    print("{name},{ip},{desc}")
    add_device(name,ip,desc)
    flash(f"{name} added succesfully!", "primary")
    return redirect(url_for("start"))

@app.route("/", methods=["DELETE"])
def rmv():
    id_data = int(request.get_json())
    name = remove_device(id_data)
    return name

@app.route("/", methods=["PATCH"])
def check():
    ip_address = request.get_json()
    deviceos = ""
    health = False
    comm = f"ping -n 1 {ip_address}"
    result = subprocess.run(comm, shell=True, capture_output=True, text=True).stdout
    if "Request timed out." in result or "Destination host unreachable" in result or "Ping request could not find host " in result:
        health = False
    else:
        health = True
        for line in result.splitlines():
            if "TTL=" in line:
                try:
                    ttl = int(line.split("TTL=")[1].split()[0])
                    if 64 < ttl <= 128:
                        deviceos = "Win"
                    elif ttl <= 64:
                        deviceos = "Linux"
                except Exception:
                    deviceos = ""
    return jsonify({"health": health, "deviceos": deviceos})

def create_table():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS devices (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            ip_address TEXT NOT NULL,
            description TEXT
        );
    """)
    conn.commit()
    cur.close()
    conn.close()

def get_all_devices():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, name, ip_address, description FROM devices;")
    rows = cur.fetchall()
    notes = []
    for row in rows:
        notes.append({
            "id": row[0],
            "name": row[1],
            "ip_address": row[2],
            "description": row[3]
        })
    cur.close()
    conn.close()
    return notes

def add_device(name, ip_address, description):
    try:
        conn = get_connection()
        print("Database connection established.")
        cur = conn.cursor()
        try:
            cur.execute(
                "INSERT INTO devices (name, ip_address, description) VALUES (%s, %s, %s);",
                (name, ip_address, description)
            )
            print("Device added successfully:", name, ip_address, description)
            conn.commit()
        except Exception as e:
            print("Error while executing SQL:", e)
            conn.rollback()
        finally:
            cur.close()
            print("Cursor closed.")
    except Exception as e:
        print("Error connecting to the database:", e)
    finally:
        try:
            conn.close()
            print("Database connection closed.")
        except Exception as e:
            print("Error closing the connection:", e)

def remove_device(id):
    name = None
    try:
        conn = get_connection()
        print("Database connection established.")
        cur = conn.cursor()
        try:

            cur.execute("SELECT name FROM devices WHERE id = %s", (id,))
            row = cur.fetchone()
            if row:
                name = row[0]
                cur.execute("DELETE FROM devices WHERE id = %s", (id,))
                if cur.rowcount > 0:
                    print(f"Device with id {id} removed successfully.")
                else:
                    print(f"No device found with id {id}.")
                conn.commit()
            else:
                print(f"No device found with id {id}.")
        except Exception as e:
            print("Error while executing SQL:", e)
            conn.rollback()
        finally:
            cur.close()
            print("Cursor closed.")
    except Exception as e:
        print("Error connecting to the database:", e)
    finally:
        try:
            conn.close()
            print("Database connection closed.")
        except Exception as e:
            print("Error closing the connection:", e)
    return name

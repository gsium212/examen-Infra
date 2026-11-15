import os
import pymssql
from flask import Flask, request, jsonify
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

def get_conn():
    return pymssql.connect(
        server=os.getenv('DB_HOST', 'db'),
        user=os.getenv('DB_USER', 'sa'),
        password=os.getenv('DB_PASSWORD'),
        database=os.getenv('DB_NAME', 'VentasDB'),
    )

# ---------- HEALTH ----------
@app.route('/health')
def health():
    try:
        get_conn().close()
        return jsonify({"status": "ok"}), 200
    except Exception as e:
        return jsonify({"status": "error", "detail": str(e)}), 500

# ---------- ÓRDENES ----------
@app.route('/ordenes', methods=['GET'])
def listar_ordenes():
    conn = get_conn(); cur = conn.cursor(as_dict=True)
    cur.execute("SELECT id, cliente, fecha, total FROM orden")
    data = [{"id": r["id"], "cliente": r["cliente"],
             "fecha": str(r["fecha"]), "total": float(r["total"])} for r in cur.fetchall()]
    conn.close()
    return jsonify(data), 200

@app.route('/ordenes', methods=['POST'])
def crear_orden():
    d = request.get_json()
    if not d or 'cliente' not in d:
        return jsonify({"error": "cliente requerido"}), 400
    conn = get_conn(); cur = conn.cursor()
    cur.execute("INSERT INTO orden (cliente, total) VALUES (%s, 0)", (d['cliente'],))
    conn.commit()
    cur.execute("SELECT @@IDENTITY")
    new_id = int(cur.fetchone()[0])
    conn.close()
    return jsonify({"id": new_id, "cliente": d['cliente'], "total": 0}), 201

@app.route('/ordenes/<int:oid>', methods=['GET'])
def obtener_orden(oid):
    conn = get_conn(); cur = conn.cursor(as_dict=True)
    cur.execute("SELECT id, cliente, fecha, total FROM orden WHERE id=%s", (oid,))
    r = cur.fetchone(); conn.close()
    if not r: return jsonify({"error": "no encontrada"}), 404
    return jsonify({"id": r["id"], "cliente": r["cliente"],
                    "fecha": str(r["fecha"]), "total": float(r["total"])}), 200

@app.route('/ordenes/<int:oid>', methods=['PUT'])
def actualizar_orden(oid):
    d = request.get_json()
    conn = get_conn(); cur = conn.cursor()
    cur.execute("UPDATE orden SET cliente=%s WHERE id=%s", (d['cliente'], oid))
    conn.commit(); conn.close()
    return jsonify({"id": oid, "cliente": d['cliente']}), 200

@app.route('/ordenes/<int:oid>', methods=['DELETE'])
def eliminar_orden(oid):
    conn = get_conn(); cur = conn.cursor()
    cur.execute("DELETE FROM orden WHERE id=%s", (oid,))
    conn.commit(); conn.close()
    return '', 204

# ---------- DETALLES ----------
@app.route('/ordenes/<int:oid>/detalles', methods=['GET'])
def listar_detalles(oid):
    conn = get_conn(); cur = conn.cursor(as_dict=True)
    cur.execute("""SELECT id, orden_id, producto, cantidad, precio_unitario
                   FROM orden_detalle WHERE orden_id=%s""", (oid,))
    data = [{"id": r["id"], "orden_id": r["orden_id"], "producto": r["producto"],
             "cantidad": r["cantidad"], "precio_unitario": float(r["precio_unitario"])}
            for r in cur.fetchall()]
    conn.close()
    return jsonify(data), 200

@app.route('/ordenes/<int:oid>/detalles', methods=['POST'])
def crear_detalle(oid):
    d = request.get_json()
    conn = get_conn(); cur = conn.cursor()
    cur.execute("""INSERT INTO orden_detalle (orden_id, producto, cantidad, precio_unitario)
                   VALUES (%s,%s,%s,%s)""",
                (oid, d['producto'], d['cantidad'], d['precio_unitario']))
    conn.commit()
    _recalcular(cur, oid); conn.commit()
    cur.execute("SELECT @@IDENTITY"); new_id = int(cur.fetchone()[0])
    conn.close()
    return jsonify({"id": new_id, "orden_id": oid, **d}), 201

@app.route('/detalles/<int:did>', methods=['PUT'])
def actualizar_detalle(did):
    d = request.get_json()
    conn = get_conn(); cur = conn.cursor()
    cur.execute("SELECT orden_id FROM orden_detalle WHERE id=%s", (did,))
    row = cur.fetchone()
    if not row: conn.close(); return jsonify({"error": "no encontrado"}), 404
    oid = row[0]
    cur.execute("""UPDATE orden_detalle SET producto=%s, cantidad=%s, precio_unitario=%s
                   WHERE id=%s""", (d['producto'], d['cantidad'], d['precio_unitario'], did))
    _recalcular(cur, oid); conn.commit(); conn.close()
    return jsonify({"id": did, **d}), 200

@app.route('/detalles/<int:did>', methods=['DELETE'])
def eliminar_detalle(did):
    conn = get_conn(); cur = conn.cursor()
    cur.execute("SELECT orden_id FROM orden_detalle WHERE id=%s", (did,))
    row = cur.fetchone()
    if not row: conn.close(); return jsonify({"error": "no encontrado"}), 404
    oid = row[0]
    cur.execute("DELETE FROM orden_detalle WHERE id=%s", (did,))
    _recalcular(cur, oid); conn.commit(); conn.close()
    return '', 204

def _recalcular(cur, oid):
    cur.execute("""UPDATE orden SET total = ISNULL(
        (SELECT SUM(cantidad*precio_unitario) FROM orden_detalle WHERE orden_id=%s), 0)
        WHERE id=%s""", (oid, oid))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

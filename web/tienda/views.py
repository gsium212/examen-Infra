import os, requests
from django.shortcuts import render, redirect
from django.contrib import messages

API = os.getenv('API_URL', 'http://api:5000')

# ---------- ÓRDENES ----------
def lista_ordenes(request):
    try:
        r = requests.get(f"{API}/ordenes", timeout=5)
        ordenes = r.json() if r.ok else []
        if not r.ok: messages.error(request, f"Error API: {r.status_code}")
    except Exception as e:
        ordenes = []; messages.error(request, f"Sin conexión con la API: {e}")
    return render(request, 'tienda/lista.html', {'ordenes': ordenes})

def crear_orden(request):
    if request.method == 'POST':
        try:
            r = requests.post(f"{API}/ordenes", json={'cliente': request.POST['cliente']}, timeout=5)
            if r.ok:
                messages.success(request, "Orden creada")
                return redirect('lista_ordenes')
            messages.error(request, f"Error {r.status_code}: {r.text}")
        except Exception as e:
            messages.error(request, f"Error: {e}")
    return render(request, 'tienda/form_orden.html', {'accion': 'Crear'})

def editar_orden(request, oid):
    if request.method == 'POST':
        try:
            r = requests.put(f"{API}/ordenes/{oid}", json={'cliente': request.POST['cliente']}, timeout=5)
            if r.ok:
                messages.success(request, "Orden actualizada")
                return redirect('lista_ordenes')
            messages.error(request, f"Error {r.status_code}")
        except Exception as e:
            messages.error(request, f"Error: {e}")
    try:
        o = requests.get(f"{API}/ordenes/{oid}", timeout=5).json()
    except Exception:
        o = {'id': oid, 'cliente': ''}
    return render(request, 'tienda/form_orden.html', {'accion': 'Editar', 'orden': o})

def eliminar_orden(request, oid):
    if request.method == 'POST':
        try:
            requests.delete(f"{API}/ordenes/{oid}", timeout=5)
            messages.success(request, "Orden eliminada")
        except Exception as e:
            messages.error(request, f"Error: {e}")
        return redirect('lista_ordenes')
    return render(request, 'tienda/confirmar.html', {'tipo': 'orden', 'id': oid})

# ---------- DETALLES ----------
def lista_detalles(request, oid):
    try:
        d = requests.get(f"{API}/ordenes/{oid}/detalles", timeout=5).json()
        o = requests.get(f"{API}/ordenes/{oid}", timeout=5).json()
    except Exception as e:
        d, o = [], {}
        messages.error(request, f"Error: {e}")
    return render(request, 'tienda/lista_detalles.html', {'detalles': d, 'orden': o})

def crear_detalle(request, oid):
    if request.method == 'POST':
        payload = {
            'producto': request.POST['producto'],
            'cantidad': int(request.POST['cantidad']),
            'precio_unitario': float(request.POST['precio_unitario']),
        }
        try:
            r = requests.post(f"{API}/ordenes/{oid}/detalles", json=payload, timeout=5)
            if r.ok:
                messages.success(request, "Detalle agregado")
                return redirect('lista_detalles', oid=oid)
            messages.error(request, f"Error {r.status_code}")
        except Exception as e:
            messages.error(request, f"Error: {e}")
    return render(request, 'tienda/form_detalle.html', {'accion': 'Crear', 'oid': oid})

def editar_detalle(request, oid, did):
    if request.method == 'POST':
        payload = {
            'producto': request.POST['producto'],
            'cantidad': int(request.POST['cantidad']),
            'precio_unitario': float(request.POST['precio_unitario']),
        }
        try:
            r = requests.put(f"{API}/detalles/{did}", json=payload, timeout=5)
            if r.ok:
                messages.success(request, "Detalle actualizado")
                return redirect('lista_detalles', oid=oid)
            messages.error(request, f"Error {r.status_code}")
        except Exception as e:
            messages.error(request, f"Error: {e}")
    return render(request, 'tienda/form_detalle.html', {'accion': 'Editar', 'oid': oid, 'did': did})

def eliminar_detalle(request, oid, did):
    if request.method == 'POST':
        try:
            requests.delete(f"{API}/detalles/{did}", timeout=5)
            messages.success(request, "Detalle eliminado")
        except Exception as e:
            messages.error(request, f"Error: {e}")
        return redirect('lista_detalles', oid=oid)
    return render(request, 'tienda/confirmar.html', {'tipo': 'detalle', 'id': did, 'oid': oid})

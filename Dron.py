
# VEJARANO - SANDOVAL - BOSA - MURCIA - LOPEZ
import tkinter as tk
import random
import heapq


FILAS_TABLERO, COLUMNAS_TABLERO = 7, 7
TAMANO_CASILLA = 60
costo_total_recorrido = 0


ventana_principal = tk.Tk()
ventana_principal.title("Sistema de Drones con Inteligencia Artificial")
ventana_principal.geometry("1000x650")
ventana_principal.configure(bg="#0f0f0f")


COLORES_ELEMENTOS = {
    "fondo_celda": "#2c2c2c",
    "dron": "#00d4ff",
    "restaurante": "#ffb703",
    "comunidad": "#06d6a0",
    "inundacion": "#3a86ff",
    "camino": "#8338ec",
    "panel": "#181818"
}


# POSICIONES FIJAS
POSICION_INICIAL_DRON = (0,0)
posiciones_restaurantes_iniciales = [(0,6), (6,0)]
posiciones_comunidades = [(6,6), (3,5)]


posicion_actual_dron = list(POSICION_INICIAL_DRON)
lista_restaurantes = posiciones_restaurantes_iniciales.copy()
lista_inundaciones = []
camino_calculado = []
modo_algoritmo = tk.StringVar(value="A*")
comunidades_visitadas = set()


juego_terminado = False  #  CONTROL GLOBAL


# ---------------- INUNDACIONES ----------------
def generar_posiciones_inundaciones():
    global lista_inundaciones
    lista_inundaciones = []


    posiciones_posibles = [
        (fila, columna)
        for fila in range(FILAS_TABLERO)
        for columna in range(COLUMNAS_TABLERO)
        if (fila, columna) not in posiciones_comunidades
        and (fila, columna) != POSICION_INICIAL_DRON
        and (fila, columna) not in lista_restaurantes
    ]


    random.shuffle(posiciones_posibles)


    if modo_algoritmo.get() == "MINIMAX":
        cantidad_inundaciones = 3
    else:
        cantidad_inundaciones = random.randint(6,7)


    for posicion in posiciones_posibles:
        bloquea_comunidad = False


        for comunidad in posiciones_comunidades:
            vecinos = [(comunidad[0]+dx, comunidad[1]+dy) for dx,dy in [(1,0),(-1,0),(0,1),(0,-1)]]
            vecinos = [v for v in vecinos if 0<=v[0]<FILAS_TABLERO and 0<=v[1]<COLUMNAS_TABLERO]


            vecinos_bloqueados = sum(1 for v in vecinos if v in lista_inundaciones or v == posicion)


            if vecinos_bloqueados >= len(vecinos):
                bloquea_comunidad = True


        if not bloquea_comunidad:
            lista_inundaciones.append(posicion)


        if len(lista_inundaciones) >= cantidad_inundaciones:
            break


# ---------------- INTERFAZ ----------------
contenedor_principal = tk.Frame(ventana_principal, bg="#0f0f0f")
contenedor_principal.pack(expand=True)


contenedor_cuadricula = tk.Frame(contenedor_principal)
contenedor_cuadricula.grid(row=0, column=0, padx=30)


panel_lateral = tk.Frame(contenedor_principal, bg=COLORES_ELEMENTOS["panel"], width=300)
panel_lateral.grid(row=0, column=1, padx=20)


etiqueta_estado = tk.Label(panel_lateral, text="Modo actual: A*", bg=COLORES_ELEMENTOS["panel"], fg="white")
etiqueta_estado.pack(pady=10)


etiqueta_costo = tk.Label(panel_lateral, text="Costo total: 0", bg=COLORES_ELEMENTOS["panel"], fg="white")
etiqueta_costo.pack(pady=5)


# ---------------- DIBUJAR ----------------
def dibujar_tablero():
    for elemento in contenedor_cuadricula.winfo_children():
        elemento.destroy()


    for fila in range(FILAS_TABLERO):
        for columna in range(COLUMNAS_TABLERO):
            posicion = (fila, columna)


            if posicion == tuple(posicion_actual_dron):
                color, texto = COLORES_ELEMENTOS["dron"], "🚁"
            elif posicion in lista_restaurantes:
                color, texto = COLORES_ELEMENTOS["restaurante"], "🍽️"
            elif posicion in posiciones_comunidades:
                color, texto = COLORES_ELEMENTOS["comunidad"], "🏠"
            elif posicion in lista_inundaciones:
                color, texto = COLORES_ELEMENTOS["inundacion"], "🌊"
            elif posicion in camino_calculado:
                color, texto = COLORES_ELEMENTOS["camino"], "•"
            else:
                color, texto = COLORES_ELEMENTOS["fondo_celda"], ""


            celda = tk.Frame(contenedor_cuadricula, bg=color, width=TAMANO_CASILLA, height=TAMANO_CASILLA)
            celda.grid(row=fila, column=columna, padx=4, pady=4)


            tk.Label(celda, text=texto, bg=color, fg="white",
                     font=("Segoe UI Emoji", 14)).place(relx=0.5, rely=0.5, anchor="center")


# ---------------- A* ----------------
def calcular_distancia_manhattan(a, b):
    # Esta función calcula la distancia entre dos puntos en la grilla.
    # Se usa como heurística (h), es decir, una estimación de qué tan lejos estamos del objetivo.
    return abs(a[0]-b[0]) + abs(a[1]-b[1])


def algoritmo_a_estrella(inicio, objetivo):
     # Aquí se crea la lista abierta, que en este caso es una cola de prioridad.
    # Se inicia con el nodo inicial y un costo 0.

    cola_prioridad = [(0 + calcular_distancia_manhattan(inicio, objetivo), inicio)]

    # Este diccionario guarda el costo acumulado g(n) de cada nodo.
    costos = {inicio: 0}   # g(n)

    # Este diccionario permite reconstruir el camino final.
    padres = {}

    # mientras no ESTÁ-VACÍA(lista_abierta) hacer
    while cola_prioridad:

        # Extrae el nodo con menor f(n)
        _, actual = heapq.heappop(cola_prioridad)

        # Si llegamos al objetivo, reconstruimos el camino
        if actual == objetivo:
            camino = []
            while actual in padres:
                camino.append(actual)
                actual = padres[actual]
            return camino[::-1] # Se invierte porque se construyó al revés

        # Movimientos posibles (arriba, abajo, izquierda, derecha)
        for dx, dy in [(1,0),(-1,0),(0,1),(0,-1)]:
            vecino = (actual[0]+dx, actual[1]+dy)

            # Validar que esté en el tablero y no sea inundación
            if not (0 <= vecino[0] < FILAS_TABLERO and 0 <= vecino[1] < COLUMNAS_TABLERO):
                continue
            # Evitar obstáculos (inundaciones)
            if vecino in lista_inundaciones:
                continue

            #Calcular nuevo costo acumulado g(n)
            nuevo_costo = costos[actual] + 1  # g(hijo)

            # Solo agregar hijo a lista_abierta si mejora el costo conocido
            if vecino not in costos or nuevo_costo < costos[vecino]:
                costos[vecino] = nuevo_costo
                # f(n) = g(n) + h(n)
                f = nuevo_costo + calcular_distancia_manhattan(vecino, objetivo)  # f = g + h

                # agregar hijo a lista_abierta
                heapq.heappush(cola_prioridad, (f, vecino))
                # Guardamos el padre para reconstrucción
                padres[vecino] = actual

    # devuelve fallo
    return []

# ---------------- ANIMACIÓN ----------------
def animar_movimiento_automatico():
    global juego_terminado, costo_total_recorrido

    if juego_terminado:
        return

    if camino_calculado:
        siguiente = camino_calculado.pop(0)
        posicion_actual_dron[0], posicion_actual_dron[1] = siguiente

        costo_total_recorrido += 1  # SUMA COSTO

        etiqueta_costo.config(text=f"Costo total: {costo_total_recorrido}")

        if tuple(posicion_actual_dron) in lista_restaurantes:
            lista_restaurantes.remove(tuple(posicion_actual_dron))

        if tuple(posicion_actual_dron) in posiciones_comunidades:
            comunidades_visitadas.add(tuple(posicion_actual_dron))

        verificar_victoria()
        dibujar_tablero()
        ventana_principal.after(300, animar_movimiento_automatico)

# ===================== MINIMAX  =====================

def obtener_acciones_posibles(posicion):
    # Esta función devuelve todos los movimientos válidos desde una posición.
    # Es equivalente a "Acciones(estado)" en el pseudocódigo.
    movimientos = [(1,0),(-1,0),(0,1),(0,-1)]
    acciones_validas = []

    for dx, dy in movimientos:
        nueva_posicion = (posicion[0]+dx, posicion[1]+dy)

        # Se valida que la posición esté dentro del tablero
        if 0<=nueva_posicion[0]<FILAS_TABLERO and 0<=nueva_posicion[1]<COLUMNAS_TABLERO:
            # También se evita que el dron se mueva a una inundación
            if nueva_posicion not in lista_inundaciones:
                acciones_validas.append(nueva_posicion)

    return acciones_validas

def aplicar_accion(posicion, accion):
    # Esta función representa RESULTADO(estado, acción)
    # En este caso simplemente devuelve la nueva posición
    return accion

def evaluar_estado(posicion):
    # Esta es la función heurística.
    # Se utiliza cuando se alcanza la profundidad máxima.
    # Mientras más cerca esté de una comunidad, mejor será el valor.
    distancia = min(calcular_distancia_manhattan(posicion, c) for c in posiciones_comunidades)
    return -distancia

def max_valor(posicion, profundidad, profundidad_maxima):
    # Esta función representa MAX-VALOR del pseudocódigo

    # Si se alcanza la profundidad límite, se evalúa el estado
    if profundidad == profundidad_maxima:
        return evaluar_estado(posicion), None

    # Se inicializa el valor con el peor caso posible
    valor_maximo = -float("inf")
    mejor_movimiento = None

    # Se recorren todas las acciones posibles
    for accion in obtener_acciones_posibles(posicion):
        nuevo_estado = aplicar_accion(posicion, accion)

        # Se llama a MIN-VALOR para simular la respuesta del entorno
        valor, _ = min_valor(nuevo_estado, profundidad+1, profundidad_maxima)

        # Se escoge el mayor valor (MAX quiere maximizar)
        if valor > valor_maximo:
            valor_maximo = valor
            mejor_movimiento = accion

    return valor_maximo, mejor_movimiento

def min_valor(posicion, profundidad, profundidad_maxima):
    # Esta función representa MIN-VALOR del pseudocódigo

    # Si se alcanza la profundidad límite, se evalúa el estado
    if profundidad == profundidad_maxima:
        return evaluar_estado(posicion), None

    # Se inicializa el valor con el mejor caso posible (porque MIN quiere minimizar)
    valor_minimo = float("inf")

    # Se recorren todas las acciones posibles
    for accion in obtener_acciones_posibles(posicion):
        nuevo_estado = aplicar_accion(posicion, accion)

        # Se llama nuevamente a MAX-VALOR
        valor, _ = max_valor(nuevo_estado, profundidad+1, profundidad_maxima)

        # MIN escoge el valor más bajo
        if valor < valor_minimo:
            valor_minimo = valor

    return valor_minimo, None

def minimax_busqueda(posicion_inicial, profundidad_maxima=2):
    # Esta función corresponde a MINIMAX-BUSQUEDA del pseudocódigo

    # Se inicia el algoritmo desde MAX
    valor, movimiento = max_valor(posicion_inicial, 0, profundidad_maxima)

    # Se devuelve la mejor acción encontrada
    return movimiento

# ---------------- MINIMAX INUNDACIONES ----------------
def mover_inundaciones_aleatoriamente():
    global lista_inundaciones

    nuevas_posiciones = []

    for inundacion in lista_inundaciones:
        dx, dy = random.choice([(1,0),(-1,0),(0,1),(0,-1)])
        nueva_pos = (inundacion[0]+dx, inundacion[1]+dy)

        if (0<=nueva_pos[0]<FILAS_TABLERO and 0<=nueva_pos[1]<COLUMNAS_TABLERO
            and nueva_pos not in posiciones_comunidades):
            nuevas_posiciones.append(nueva_pos)
        else:
            nuevas_posiciones.append(inundacion)

    lista_inundaciones[:] = nuevas_posiciones

# ---------------- MOVIMIENTO TECLAS----------------
## ESTE APARTADO FUE AYUDADO POR IA ##
def mover_dron_con_teclado(dx, dy):
   
    global juego_terminado

    if modo_algoritmo.get() != "MINIMAX" or juego_terminado:
        return

    nueva_fila = posicion_actual_dron[0] + dx
    nueva_columna = posicion_actual_dron[1] + dy

    if 0<=nueva_fila<FILAS_TABLERO and 0<=nueva_columna<COLUMNAS_TABLERO:
        if (nueva_fila, nueva_columna) not in lista_inundaciones:

            posicion_actual_dron[0], posicion_actual_dron[1] = nueva_fila, nueva_columna

            if tuple(posicion_actual_dron) in lista_restaurantes:
                lista_restaurantes.remove(tuple(posicion_actual_dron))

            if tuple(posicion_actual_dron) in posiciones_comunidades:
                comunidades_visitadas.add(tuple(posicion_actual_dron))

            mover_inundaciones_aleatoriamente()

            if tuple(posicion_actual_dron) in lista_inundaciones:
                etiqueta_estado.config(text="💀 FIN DEL JUEGO")
                juego_terminado = True
                return

            verificar_victoria()
            dibujar_tablero()

# CONTROLES
ventana_principal.bind("<Up>", lambda e: mover_dron_con_teclado(-1,0))
ventana_principal.bind("<Down>", lambda e: mover_dron_con_teclado(1,0))
ventana_principal.bind("<Left>", lambda e: mover_dron_con_teclado(0,-1))
ventana_principal.bind("<Right>", lambda e: mover_dron_con_teclado(0,1))

# ---------------- CONTROL ----------------
def iniciar_simulacion():
    global camino_calculado

    if juego_terminado:
        return

    etiqueta_estado.config(text=f"Modo actual: {modo_algoritmo.get()}")

    if modo_algoritmo.get() == "A*":
        posicion_actual = tuple(posicion_actual_dron)
        recorrido_total = []

        for destino in lista_restaurantes + posiciones_comunidades:
            segmento = algoritmo_a_estrella(posicion_actual, destino)
            recorrido_total += segmento
            if segmento:
                posicion_actual = segmento[-1]

        camino_calculado[:] = recorrido_total
        animar_movimiento_automatico()

def reiniciar_simulacion():
    global posicion_actual_dron, camino_calculado, lista_restaurantes, comunidades_visitadas, juego_terminado, costo_total_recorrido

    posicion_actual_dron = list(POSICION_INICIAL_DRON)
    lista_restaurantes = posiciones_restaurantes_iniciales.copy()
    comunidades_visitadas.clear()
    camino_calculado = []
    juego_terminado = False
    costo_total_recorrido = 0

    etiqueta_costo.config(text="Costo total: 0")

    generar_posiciones_inundaciones()
    dibujar_tablero()
    etiqueta_estado.config(text="Juego reiniciado")

def verificar_victoria():
    global juego_terminado

    if not lista_restaurantes and len(comunidades_visitadas) == len(posiciones_comunidades):
        etiqueta_estado.config(text="🏆 HAS GANADO")
        juego_terminado = True

# ---------------- BOTONES ----------------
tk.Radiobutton(panel_lateral, text="Algoritmo A*", variable=modo_algoritmo, value="A*",
               bg=COLORES_ELEMENTOS["panel"], fg="white").pack(anchor="w", padx=20, pady=10)

tk.Radiobutton(panel_lateral, text="Modo MINIMAX (control manual)", variable=modo_algoritmo, value="MINIMAX",
               bg=COLORES_ELEMENTOS["panel"], fg="white").pack(anchor="w", padx=20)

tk.Button(panel_lateral, text="INICIAR", command=iniciar_simulacion).pack(padx=20, pady=10, fill="x")
tk.Button(panel_lateral, text="REINICIAR", command=reiniciar_simulacion).pack(padx=20, pady=10, fill="x")

# ---------------- INICIO ----------------
generar_posiciones_inundaciones()
dibujar_tablero()
ventana_principal.mainloop()

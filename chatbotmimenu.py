import random
import nltk
import re
import unicodedata
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
from spellchecker import SpellChecker
nltk.download("punkt")
stemmer = PorterStemmer()
spell = SpellChecker(language="es")
#-----------------instalaciones necesarias-----------------#




#BASE DE DATOS SIMULADA DEL MENU DEL RESTAURANTE
menu = {
    "hamburguesa": ["clásica", "con queso", "doble carne"],
    "pizza": ["pepperoni", "hawaiana", "vegetariana"],
    "bebida": ["coca-cola", "jugo de naranja", "agua"],
    "taco": ["al pastor", "de pollo", "de res"],
    "sándwich": ["de jamón", "de pollo", "vegetariano"],
    "ensalada": ["césar", "mixta", "de atún"],
    "pasta": ["lasagna"],
    "postre": ["cheesecake", "flan", "brownie"],
    "sopa": ["de tomate", "de pollo", "minestrone"],
    "mariscos": ["ceviche", "pulpo a la gallega"],
}
#SINONIMOS DE LOS ITEMS DEL MENU
sinonimos = {
    "soda": "coca-cola",
    "gaseosa": "coca-cola",
    "refresco": "coca-cola",
    "tortilla": "taco",
    "pasta italiana": "pasta",
    "dulce": "postre",
    "caldo": "sopa",
    "frutos del mar": "mariscos",
}

frases_confirmacion = [
    "¿Quieres algo mas?",
    "¿Te gustaria añadir algo mas a tu pedido?",
    "Si deseas algo mas dime.",
]
frases_pedido = [
    "Perfecto, he agregado {} a tu pedido.",
    "Listo, {} ha sido añadido.",
    "{} esta en tu pedido.",
]


#-----------------funcion para corregir los errores ortograficos que el usuario ponga-----------------#
def corregir_ortografia(texto):
    palabras=word_tokenize(texto.lower())
    palabras_corregidas =[spell.correction(palabra) if spell.correction(palabra) else palabra for palabra in palabras]
    return " ".join(palabras_corregidas)

#-----------------aplicacion del stemming-----------------#
def aplicar_stemming(texto):
    palabras=word_tokenize(texto.lower())
    return " ".join([stemmer.stem(palabra) for palabra in palabras])
menu_stemmed={aplicar_stemming(k): [aplicar_stemming(op) for op in v] for k, v in menu.items()}
sinonimos_stemmed={aplicar_stemming(k): aplicar_stemming(v) for k, v in sinonimos.items()}


#-----------------sustituimos las palabras que ponga el usuario por las del diccionario-----------------
def reemplazar_sinonimos(mensaje):
    mensaje_stemmed = aplicar_stemming(mensaje)
    for frase, reemplazo in sinonimos_stemmed.items():
        mensaje_stemmed = re.sub(rf"\b{re.escape(frase)}\b", reemplazo, mensaje_stemmed, flags=re.IGNORECASE)
    return mensaje_stemmed

def quitar_tildes(texto):
    return ''.join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn')

#funcion para procesar la entrada del usuario y extraer el pedido con cantidad
def procesar_mensaje(mensaje):
    mensaje= quitar_tildes(mensaje)
    mensaje=corregir_ortografia(mensaje)
    mensaje=reemplazar_sinonimos(mensaje)
    mensaje_stemmed=aplicar_stemming(mensaje)  
    tokens=word_tokenize(mensaje.lower())
    pedido = {}
    cantidad= 1
    palabras =mensaje.split()
    for palabra in palabras:
        if palabra.isdigit():
            cantidad=int(palabra)
            break
    for categoria, opciones in menu.items():
        categoria_normalizada=quitar_tildes(categoria)  #normaliza la categoria
        categoria_stemmed=aplicar_stemming(categoria_normalizada)
        opciones_normalizadas=[quitar_tildes(op) for op in opciones]  #normaliza als opciones
        opciones_stemmed=[aplicar_stemming(op) for op in opciones_normalizadas]

        #primero se buscan coincidencias en las opciones
        opciones_encontradas =[opcion for opcion, opcion_stem in zip(opciones, opciones_stemmed) if opcion_stem in mensaje_stemmed]
        if opciones_encontradas:
            for opcion in opciones_encontradas:
                pedido[(categoria, opcion)]=cantidad
            return pedido
        #si no hay opcion especifica pero se dice la categoria
        if categoria_stemmed in mensaje_stemmed:
            print(f"🤖 Chatbot: ¿Qué tipo de {categoria} te gustaría? Tenemos: {', '.join(opciones)}")
            eleccion=input("Tú: ").strip().lower()
            eleccion=quitar_tildes(eleccion)
            if eleccion in opciones_normalizadas:
                pedido[(categoria, opciones[opciones_normalizadas.index(eleccion)])]=cantidad
            else:
                print("🤖 Chatbot: No entendí bien, elige una de las opciones disponibles.")
            return pedido
    return pedido





#EDICION DEL PEDIDO
def editar_pedido(pedido_actual):
    while True:
        if not pedido_actual:
            print("🤖 Chatbot: No hay productos en tu pedido. No hay nada que editar.")
            return pedido_actual
        print("\n🤖 Chatbot: Aquí está tu pedido actual:")
        items = [
            f"{i+1}. {categoria} {opcion} (x{cantidad})"
            for i, ((categoria, opcion),cantidad) in enumerate(pedido_actual.items())
        ]
        for item in items:
            print(item)

        print("\n🤖 Chatbot: ¿Quieres eliminar, modificar cantidad o agregar más productos? (eliminar/modificar/agregar/listo)")
        eleccion = input("Tú: ").strip().lower()
        if eleccion == "listo":
            break
#ELIMINAR
        elif eleccion=="eliminar":
            print("🤖 Chatbot: Ingresa el número del producto que deseas eliminar o escribe 'cancelar' para volver.")
            eliminar = input("Tú: ").strip().lower()
            if eliminar=="cancelar":
                continue
            if eliminar.isdigit():
                indice=int(eliminar)-1
                if 0<=indice<len(items):
                    item_eliminado=list(pedido_actual.keys())[indice]
                    del pedido_actual[item_eliminado]
                    print(f"🤖 Chatbot: {item_eliminado[1]} ha sido eliminado de tu pedido.")
                else:
                    print("🤖 Chatbot: Número inválido. Intenta de nuevo.")
#EDITAR NUMERO PRODUCTOS
        elif eleccion == "modificar":
            print("🤖 Chatbot: Ingresa el número del producto cuya cantidad deseas cambiar o escribe 'cancelar' para volver.")
            modificar = input("Tú: ").strip().lower()
            if modificar == "cancelar":
                continue
            if modificar.isdigit():
                indice = int(modificar) - 1
                if 0 <= indice < len(items):
                    item_modificado = list(pedido_actual.keys())[indice]
                    print(f"🤖 Chatbot: Ingresa la nueva cantidad para {item_modificado[1]}:")
                    nueva_cantidad=input("Tú: ").strip()
                    if nueva_cantidad.isdigit():
                        pedido_actual[item_modificado]=int(nueva_cantidad)
                        print(f"🤖 Chatbot: Ahora tienes {nueva_cantidad} {item_modificado[1]}.")
                    else:
                        print("🤖 Chatbot: Cantidad no válida.")
                else:
                    print("🤖 Chatbot: Número inválido. Intenta de nuevo.")
#NUEVO PRODUCTO
        elif eleccion=="agregar":
            print("🤖 Chatbot: Dime qué producto deseas agregar.")
            nuevo_producto=input("Tú: ").strip().lower()
            pedido_nuevo=procesar_mensaje(nuevo_producto)
            if pedido_nuevo:
                for item, cantidad in pedido_nuevo.items():
                    if item in pedido_actual:
                        pedido_actual[item]+=cantidad  # Sumar cantidad en lugar de duplicar
                    else:
                        pedido_actual[item]=cantidad
                print("🤖 Chatbot: Producto agregado con éxito.")
            else:
                print("🤖 Chatbot: No entendí bien, intenta describirlo de otra manera.")
        else:
            print("🤖 Chatbot: No entendí, ingresa 'eliminar', 'modificar', 'agregar' o 'listo'.")


#funciones del bot
def chatbot():
    print("🍽️¡Bienvenido a MiMenú Chatbot! Escribe 'salir' para terminar.\n")
    pedido_actual={}
    while True:
        mensaje = input("Tú: ").lower()
        if mensaje== "salir":
            print("🤖 Chatbot: ¡Hasta luego! 👋")
            break
        pedido =procesar_mensaje(mensaje)
        if pedido:
            for item, cantidad in pedido.items():
                if item in pedido_actual:
                    pedido_actual[item]+=cantidad
                else:
                    pedido_actual[item]=cantidad
            pedido_str = ", ".join(
                [f"{categoria} {opcion} (x{cantidad})" for (categoria,opcion), cantidad in pedido_actual.items()]
            )
            print(f"🤖 Chatbot: {random.choice(frases_pedido).format(pedido_str)}")
        else:
            print("🤖 Chatbot: No entendí bien, ¿puedes repetirlo de otra manera?")
            continue
        print(f"🤖 Chatbot: {random.choice(frases_confirmacion)} (si/no)")#confirmacion
        mensaje = input("Tú: ").lower()
        if mensaje not in ["si", "claro", "por supuesto"]:
            break
    if pedido_actual:
        while True:
            pedido_str = ", ".join(
                [f"{categoria} {opcion} (x{cantidad})" for (categoria, opcion), cantidad in pedido_actual.items()]
            )
            print(f"\n🤖 Chatbot: Tu pedido es: {pedido_str}. ¿Confirmar? (si/no/editar)")
            confirmar = input("Tú: ").strip().lower()
            if confirmar == "si":
                print("🤖 Chatbot: ¡Pedido confirmado! 🍔🥤")
                break
            elif confirmar == "editar":
                editar_pedido(pedido_actual)
            elif confirmar =="no":
                print("🤖 Chatbot: Pedido cancelado")
                break
            else:
                print("🤖 Chatbot: Respuesta no válida. Responde 'si', 'no' o 'editar'.")


#ejecutar el bot
if __name__ == "__main__":
    chatbot()
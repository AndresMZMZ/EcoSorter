from dataclasses import dataclass
import random


@dataclass(frozen=True)
class CategoriaResiduo:
    color_caja: str
    categoria: str
    nombre_es: str


CATEGORIAS: dict[str, CategoriaResiduo] = {
    "blanca": CategoriaResiduo(
        color_caja="blanca",
        categoria="Residuos aprovechables",
        nombre_es="Caja blanca",
    ),
    "verde": CategoriaResiduo(
        color_caja="verde",
        categoria="Residuos orgánicos",
        nombre_es="Caja verde",
    ),
    "negra": CategoriaResiduo(
        color_caja="negra",
        categoria="Residuos no reciclables o contaminados",
        nombre_es="Caja negra",
    ),
    "amarilla": CategoriaResiduo(
        color_caja="amarilla",
        categoria="Baterías y pilas",
        nombre_es="Caja amarilla",
    ),
    "roja": CategoriaResiduo(
        color_caja="roja",
        categoria="Otros residuos no reciclables",
        nombre_es="Caja roja",
    ),
}

COLORES_BBOX_BGR: dict[str, tuple[int, int, int]] = {
    "blanca": (255, 255, 255),
    "verde": (0, 200, 0),
    "negra": (40, 40, 40),
    "amarilla": (0, 220, 255),
    "roja": (0, 0, 220),
}

NOMBRES_OBJETOS_ES: dict[str, str] = {
    "bottle": "Botella",
    "wine glass": "Copa de vidrio",
    "cup": "Vaso o taza",
    "book": "Libro o cartón",
    "vase": "Florero de vidrio",
    "bowl": "Tazón",
    "fork": "Tenedor",
    "knife": "Cuchillo",
    "spoon": "Cuchara",
    "scissors": "Tijeras",
    "banana": "Plátano",
    "apple": "Manzana",
    "orange": "Naranja",
    "broccoli": "Brócoli",
    "carrot": "Zanahoria",
    "hot dog": "Comida procesada",
    "pizza": "Pizza",
    "donut": "Donut",
    "cake": "Pastel",
    "sandwich": "Sándwich",
    "potted plant": "Restos vegetales",
    "toilet": "Papel higiénico o servilleta usada",
    "toothbrush": "Cepillo de dientes usado",
    "battery": "Batería o pila",
    "cell phone": "Celular con batería",
    "remote": "Control remoto con pilas",
    "laptop": "Computador portátil",
    "tv": "Televisor",
    "chair": "Silla",
    "couch": "Sofá",
    "person": "Persona",
}

CLASES_BLANCA = {
    "bottle",
    "wine glass",
    "cup",
    "book",
    "vase",
    "bowl",
    "fork",
    "knife",
    "spoon",
    "scissors",
    "frisbee",
}

CLASES_VERDE = {
    "banana",
    "apple",
    "orange",
    "broccoli",
    "carrot",
    "hot dog",
    "pizza",
    "donut",
    "cake",
    "sandwich",
    "potted plant",
}

CLASES_NEGRA = {
    "toilet",
    "toothbrush",
    "tie",
    "handbag",
}

CLASES_AMARILLA = {
    "battery",
    "cell phone",
    "remote",
}


def clasificar_objeto(class_name: str) -> CategoriaResiduo:
    nombre = class_name.lower().strip()

    if nombre in CLASES_AMARILLA or "battery" in nombre or "pila" in nombre:
        return CATEGORIAS["amarilla"]
    if nombre in CLASES_NEGRA:
        return CATEGORIAS["negra"]
    if nombre in CLASES_VERDE:
        return CATEGORIAS["verde"]
    if nombre in CLASES_BLANCA:
        return CATEGORIAS["blanca"]

    return CATEGORIAS["roja"]


def nombre_objeto_es(class_name: str) -> str:
    nombre = class_name.lower().strip()
    return NOMBRES_OBJETOS_ES.get(nombre, class_name.replace("_", " ").title())


RECOMENDACIONES_POR_OBJETO: dict[str, list[str]] = {
    "bottle": [
        "Enjuagar, quitar la tapa y aplastar antes de depositar en caja blanca.",
        "Si es de vidrio, separar de otros materiales y colocar en contenedor de vidrio.",
        "Verificar que esté vacía y sin residuos de líquido antes de reciclar.",
    ],
    "wine glass": [
        "El vidrio de copas no siempre es reciclable. Verificar el tipo de vidrio.",
        "Si se rompió, envolver en papel antes de desechar en caja negra por seguridad.",
        "Enjuagar y depositar en contenedor de vidrio si acepta este tipo.",
    ],
    "cup": [
        "Si es plástico o vidrio reutilizable, lavar y reutilizar.",
        "Si es desechable de un solo uso, depositar en caja blanca limpia.",
        "Los vasos de styrofoam van en caja negra, no son reciclables.",
    ],
    "book": [
        "Si está en buen estado, donar en lugar de desechar.",
        "El papel y cartón van en caja blanca, sin grasas ni residuos.",
        "Retirar cubiertas de plástico o tela antes de reciclar.",
    ],
    "vase": [
        "El vidrio de floreros se puede reciclar si no está roto.",
        "Si tiene grietas, envolver en papel y desechar en caja negra.",
        "Lavar y depositar en contenedor de vidrio.",
    ],
    "bowl": [
        "Si es de cerámica y está roto, envolver y desechar en caja negra.",
        "Si es de vidrio o plástico reciclable, lavar y depositar en caja blanca.",
        "Reutilizar si está en buen estado.",
    ],
    "fork": [
        " cubiertos de plástico van en caja blanca si están limpios.",
        "Los cubiertos metálicos se pueden reciclar en caja blanca.",
        "Si están sucios de grasa, desechar en caja negra.",
    ],
    "knife": [
        "Envolver la hoja en papel o cartón antes de desechar por seguridad.",
        "Los cuchillos de plástico van en caja blanca limpios.",
        "Los cuchillos metálicos van en caja blanca si no tienen restos de comida.",
    ],
    "spoon": [
        "Cucharas de plástico limpias van en caja blanca.",
        "Las de metal también son reciclables en caja blanca.",
        "Si tienen residuos de grasa, lavar antes de depositar.",
    ],
    "scissors": [
        "Las tijeras metálicas van en caja blanca para reciclaje de metal.",
        "Si son de plástico, verificar si son reciclables en tu localidad.",
        "Envolver las puntas antes de desechar.",
    ],
    "banana": [
        "Las cáscaras de plátano son compostables. Depósitalas en caja verde.",
        "Cortar en trozos pequeños acelera la descomposición en compost.",
        "Evitar mezclar con residuos no orgánicos.",
    ],
    "apple": [
        "Cascaras y restos de manzana van en caja verde para compostaje.",
        "Las semillas son compostables pero pueden tardar más en descomponerse.",
        "Si la manzana está podrida, toda la pieza va en caja verde.",
    ],
    "orange": [
        "Las cáscaras de naranja son excelentes para compostaje. Caja verde.",
        "Cortar en trozos pequeños para mejor descomposición.",
        "Las cáscaras de cítricos agregan nutrientes al compost.",
    ],
    "broccoli": [
        "Restos de brócoli van en caja verde para compostaje.",
        "Incluye tallos y hojas, son perfectos para el compost.",
        "Cortar en trozos pequeños acelera la descomposición.",
    ],
    "carrot": [
        "Cáscaras y restos de zanahoria van en caja verde.",
        "Las puntas verdes también son compostables.",
        "Lavar antes de consumir, el agua de lavado no contaminará el compost.",
    ],
    "hot dog": [
        "Restos de comida procesada van en caja verde si son orgánicos.",
        "El empaque plástico o de papel va en su contenedor correspondiente.",
        "Evitar dejar restos grandes de comida en caja blanca.",
    ],
    "pizza": [
        "Cajas de pizza con grasa van en caja negra, no son reciclables.",
        "Restos de pizza sin grasa van en caja verde.",
        "El cartón limpio de la caja puede ir en caja blanca.",
    ],
    "donut": [
        "Restos de donas van en caja verde si son orgánicos.",
        "El empaque de plástico o papel va en su contenedor correspondiente.",
        "Si tiene grasas, desechar en caja negra.",
    ],
    "cake": [
        "Restos de pastel van en caja verde para compostaje.",
        "Los empaques van en sus contenedores correspondientes.",
        "Evitar mezclar con residuos no orgánicos.",
    ],
    "sandwich": [
        "Restos de sándwich sin empaque van en caja verde.",
        "El empaque de plástico o papel va en su contenedor correspondiente.",
        "Si tiene mayonesa u otros lácteos, compostar con precaución.",
    ],
    "potted plant": [
        "Restos vegetales van en caja verde para compostaje.",
        "La tierra y maceta pueden reutilizarse.",
        "Las raíces y hojas secas también son compostables.",
    ],
    "toilet": [
        "El papel higiénico usado va en caja negra, no es reciclable.",
        "Los pañales van en caja negra por razones de higiene.",
        "No tirar productos de higiene por el inodoro.",
    ],
    "toothbrush": [
        "Cepillos de dientes usados van en caja negra.",
        "Algunas marcas ofrecen programas de reciclaje para cepillos.",
        "Los cepillos de plástico no son reciclables comúnmente.",
    ],
    "battery": [
        "Las baterías van en caja amarilla, jamás en la basura común.",
        "Acumular varias pilas usadas y llevar a un punto de recolección.",
        "Las baterías de litio pueden ser peligrosas si se dañan, manejar con cuidado.",
    ],
    "cell phone": [
        "Los celulares con batería van en caja amarilla para disposición especial.",
        "Retirar datos personales antes de desechar.",
        "Considerar donar si funciona, o llevar a centro de reciclaje electrónico.",
    ],
    "remote": [
        "Controles remotos van en caja amarilla por las pilas/batería interna.",
        "Si tiene pilas removibles, sacarlas y desecharlas por separado en caja amarilla.",
        "El plástico del control puede ser reciclable en algunos centros.",
    ],
}

RECOMENDACIONES_POR_COLOR: dict[str, list[str]] = {
    "blanca": [
        "Asegúrate de que el material esté limpio y seco antes de depositarlo.",
        "No mezcles residuos orgánicos con reciclables.",
        "Los materiales limpios se pueden aplastar para ahorrar espacio.",
    ],
    "verde": [
        "Corta los restos en trozos pequeños para mejor compostaje.",
        "No incluyas residuos de plástico o metal en la caja verde.",
        "Los residuos orgánicos separados generan mejor compost.",
    ],
    "negra": [
        "Estos residuos no son reciclables. Deposítalos en la caja negra.",
        "Envuelve material punzante o cortante antes de desechar.",
        "No deposites residuos peligrosos en la caja negra.",
    ],
    "amarilla": [
        "Las baterías y pilas nunca van en la basura común, son contaminantes.",
        "Acumula pilas usadas y llévalas a un punto de recolección especial.",
        "Los residuos electrónicos contienen materiales valiosos que se pueden recuperar.",
    ],
    "roja": [
        "Estos residuos no encajan en las categorías principales de reciclaje.",
        "Verifica si tu localidad tiene puntos de recolección especiales.",
        "Algunos materiales pueden tener opciones de reciclaje especializado.",
    ],
}


def obtener_recomendacion(class_name: str, color_caja: str) -> str:
    nombre = class_name.lower().strip()
    opciones = RECOMENDACIONES_POR_OBJETO.get(nombre)
    if opciones:
        return random.choice(opciones)
    opciones_color = RECOMENDACIONES_POR_COLOR.get(color_caja, [])
    if opciones_color:
        return random.choice(opciones_color)
    return ""

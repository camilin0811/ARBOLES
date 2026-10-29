# AutoParts BST — Árbol de componentes automotrices

Taller de **Árboles** · Estructuras de Datos · Cuarto semestre

Aplicación web en **Python + Flask** que gestiona las piezas de un vehículo con un
**Árbol Binario de Búsqueda (ABB / BST)** y las muestra también como un **árbol de
ensamblaje n-ario** (Vehículo → Sistemas → Piezas). En el dibujo del árbol la raíz es
amarilla, las ramas azules y las hojas verdes.

## Caso de estudio: industria automotriz

Un taller o ensambladora maneja cientos de referencias de repuestos. Si estuvieran en
una lista (estructura lineal), encontrar una pieza obligaría a revisar elemento por
elemento. En cambio, las piezas se guardan en un ABB ordenado por **código de parte**
(`ENG-401`, `BRK-202`, …): en cada nodo se decide ir a la izquierda (código menor) o
a la derecha (código mayor), así que una búsqueda solo recorre **un camino** desde la
raíz. Con las 15 piezas de ejemplo, cualquier pieza se encuentra en máximo 4
comparaciones.

Cada pieza (nodo) guarda: `code`, `name`, `system`, `stock`, `cost` y `supplier`.

Todo el código Python está en inglés (clases, métodos, variables, mensajes y datos de ejemplo) y sin comentarios. La interfaz web también está en inglés.

Además, la misma información se organiza como un árbol jerárquico de ensamblaje:

```
SC-2026 Sedan                (root)
├── Engine                   (branch: main system)
│   ├── ENG-401 1.6L engine block   (leaf: part)
│   └── ...
├── Transmission
├── Suspension
├── Brakes
├── Body
└── Electrical
```

## Requisitos

- Python 3.10 o superior
- Flask (`pip install -r requirements.txt`)

## Ejecutar localmente

```bash
cd "trabajo arboles"

# (opcional) entorno virtual
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # Linux / macOS

pip install -r requirements.txt
python app.py
```

Abrir **http://127.0.0.1:5000** en el navegador.

La primera vez se crea `inventory.json` con 15 piezas de ejemplo. Los cambios
(agregar, editar, eliminar) se guardan en ese archivo. El botón **Restore sample**
vuelve a los datos iniciales.

### Pruebas

```bash
python test_tree.py -v
```

## Funcionalidades

| Función | Dónde | Concepto de la clase |
|---|---|---|
| Insertar pieza (si el código existe, se actualiza) | Formulario "Add part" | `Phonebook.insert` de la agenda telefónica |
| Buscar por código, animando el camino desde la raíz | "Search part" | `Phonebook.search` |
| Buscar por nombre parcial, sin distinguir mayúsculas ("SPARK") | "Search part" | Recorrido completo (el ABB está ordenado por código, no por nombre) |
| Eliminar (hoja, un hijo, dos hijos con sucesor in-order) | Detalle del nodo / "Inventory" | Eliminación en ABB |
| Recorridos in-order ↑, in-order ↓, pre-order, post-order + animación | Pestaña "Traversals" | `in_order_asc` del ejemplo de ordenamiento |
| Peso, altura, hojas, raíz, valor del inventario, stock bajo | Tarjetas superiores (Weight, Height, Leaves, Root…) | Peso y altura de un árbol |
| Nivel, grado, padre, hijos y tipo (raíz/rama/hoja) de cada nodo | Clic en un nodo | Partes de un árbol, nivel y grado |
| Filtros por sistema, proveedor, rango de costo y stock bajo | "Filter" | Recorrido in-order con condición |
| Búsqueda por rango de códigos (poda ramas fuera del rango) | "Code range" | Aprovechar el orden del ABB |
| Árbol de ensamblaje n-ario con peso, altura y orden | Pestaña "Assembly" | Árbol n-ario, orden de un árbol |
| Balancear el árbol (altura mínima) | Botón "Balance tree" | Idea base de los árboles AVL |

**Altura:** se cuenta en niveles, igual que en la clase (la raíz está en el nivel 1).
Un árbol vacío tiene altura 0 y uno con solo la raíz tiene altura 1.

## Estructura del proyecto

Todo está en una sola carpeta:

```
trabajo arboles/
├── app.py            # Servidor Flask: página principal y API JSON
├── tree.py           # Node y BinaryTree (ABB): insertar, buscar, eliminar,
│                     # recorridos, peso, altura, hojas, filtros, rango, balancear
├── assembly.py       # AssemblyNode: árbol n-ario Vehículo → Sistema → Pieza
├── storage.py        # Datos de ejemplo y guardado en JSON (en pre-order)
├── index.html        # Interfaz (HTML, CSS y JavaScript en un solo archivo)
├── test_tree.py      # Pruebas unitarias del ABB y del árbol de ensamblaje
├── requirements.txt
└── README.md
```

Al ejecutar la aplicación se crea `inventory.json` en esta misma carpeta.

¿Por qué se guarda en **pre-order**? Porque al volver a insertar las piezas en ese
orden (raíz primero, luego sus subárboles) el ABB se reconstruye con exactamente la
misma forma.

## API

| Método | Ruta | Descripción |
|---|---|---|
| GET | `/api/tree` | Árbol completo, estadísticas y recorrido in-order |
| POST | `/api/parts` | Insertar/actualizar pieza (JSON: code, name, system, stock, cost, supplier) |
| GET | `/api/parts/<code>` | Detalle de una pieza: nivel, grado, padre, hijos y camino |
| DELETE | `/api/parts/<code>` | Eliminar pieza |
| GET | `/api/search?q=` | Búsqueda por código exacto o por nombre parcial |
| GET | `/api/traversal/<tipo>` | `inorder`, `inorder_desc`, `preorder`, `postorder` |
| GET | `/api/filter?system=&supplier=&min_cost=&max_cost=&max_stock=` | Filtrar piezas |
| GET | `/api/range?from=&to=` | Piezas en un rango de códigos |
| GET | `/api/assembly` | Árbol de ensamblaje n-ario |
| POST | `/api/balance` | Balancear el ABB |
| POST | `/api/reset` | Restaurar datos de ejemplo |

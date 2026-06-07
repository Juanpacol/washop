# WASHOPS — Documentación del Proyecto

> Sistema de gestión para lavaderos de autos. Construido con React 19 + Vite + Supabase.

---

## ¿Qué hace esta aplicación?

Washops es una app web que permite gestionar todo lo que pasa en un lavadero de autos:

- Registrar **clientes** y sus **vehículos**
- Crear y seguir el estado de los **servicios** (lavado express, básico, full, premium)
- Registrar **pagos** y ver los ingresos totales
- **Exportar datos** a CSV
- Todo con **actualizaciones en tiempo real** desde la base de datos

---

## Estructura del Proyecto

```
washops-app/src/
├── App.jsx                        ← Entrada principal + rutas protegidas
├── main.jsx                       ← Punto de arranque de React
├── context/
│   └── AuthContext.jsx            ← Estado global de autenticación
├── features/
│   └── auth/
│       └── LoginPage.jsx          ← Formulario de login
├── hooks/
│   ├── useServices.js             ← Lógica de servicios
│   ├── useCustomers.js            ← Lógica de clientes y vehículos
│   └── usePayments.js             ← Lógica de pagos
├── lib/
│   ├── supabase.js                ← Conexión a Supabase
│   └── db.js                      ← Todas las operaciones de base de datos
└── shared/
    ├── components/
    │   ├── AppShell.jsx           ← Layout principal (sidebar + contenido)
    │   └── Sidebar.jsx            ← Menú de navegación lateral
    └── utils/
        ├── constants.js           ← Precios, estados y transiciones válidas
        ├── formatters.js          ← Formato de moneda, fechas y duración
        └── exportCsv.js           ← Exportación a CSV
```

---

## Flujo de Datos

```
Componente React
     ↓
Custom Hook  (useServices / useCustomers / usePayments)
     ↓
db.js  (todas las operaciones a la BD)
     ↓
Supabase  (PostgreSQL + Auth + Tiempo Real)
```

---
---

# Patrones de Diseño Implementados

---

## 1. Factory Method — Patrón Creacional

**¿Qué problema resuelve?**
Cuando se crea un servicio, el precio depende del tipo (`EXPRESS`, `BASIC`, `FULL`, `PREMIUM`). En lugar de que quien llama la función tenga que saber cuánto cuesta cada tipo, la **fábrica** lo resuelve internamente: le pasas el tipo y ella construye el objeto completo con el precio correcto.

**¿Dónde están los precios definidos?**
[washops-app/src/shared/utils/constants.js](washops-app/src/shared/utils/constants.js) — líneas 1–6

```js
// Líneas 1-6 — El "catálogo" de la fábrica: cada tipo tiene su precio
export const SERVICE_PRICES = {
  EXPRESS: 35000,
  BASIC:   45000,
  FULL:    75000,
  PREMIUM: 120000,
};
```

**¿Dónde se aplica la fábrica?**
[washops-app/src/lib/db.js](washops-app/src/lib/db.js) — líneas 82–89

```js
// Líneas 82-89 — createService es el Factory Method
// Recibe el tipo y construye el servicio completo con el precio correcto
export async function createService({ vehicle_id, customer_id, type }) {
  const { data, error } = await supabase
    .from('services')
    .insert({
      vehicle_id,
      customer_id,
      type,
      price: SERVICE_PRICES[type],  // ← la fábrica asigna el precio según el tipo
      status: 'PENDING',            // ← siempre inicia en PENDING
    })
    .select()
    .single();
  if (error) throw error;
  return data;
}
```

**¿Por qué es un Factory Method?**
El que llama `createService` solo dice *qué tipo* de servicio quiere. La función decide internamente cómo construir el objeto completo (precio, estado inicial). Si mañana cambian los precios, solo se toca `SERVICE_PRICES`, no todos los componentes que crean servicios.

---

## 2. Decorator — Patrón Estructural

**¿Qué problema resuelve?**
Varias páginas de la app son privadas: solo se deben mostrar si el usuario está autenticado, y además deben tener el layout (sidebar + header). En lugar de escribir esa lógica en cada página, `ProtectedRoute` la **envuelve** (decora) añadiéndole autenticación y layout sin tocar el componente original.

**¿Dónde está?**
[washops-app/src/App.jsx](washops-app/src/App.jsx) — líneas 13–18

```jsx
// Líneas 13-18 — ProtectedRoute es el Decorator
// Toma cualquier componente hijo y le añade: verificación de sesión + AppShell
function ProtectedRoute({ children }) {
  const { session, loading } = useAuth();

  if (loading)  return null;                        // espera mientras carga la sesión
  if (!session) return <Navigate to="/login" />;    // redirige si no está autenticado

  return <AppShell>{children}</AppShell>;
  //      ↑ envuelve al hijo con el layout completo (sidebar + contenido)
}
```

**¿Cómo se usa?**
[washops-app/src/App.jsx](washops-app/src/App.jsx) — líneas 24–29

```jsx
// Líneas 24-29 — Cualquier página que se envuelva en ProtectedRoute
// queda protegida y con layout sin escribir nada extra en ella
<Route path="/*" element={
  <ProtectedRoute>
    <MiPagina />   {/* ← MiPagina no sabe nada de auth ni de layout */}
  </ProtectedRoute>
} />
```

**¿Por qué es un Decorator?**
`ProtectedRoute` no modifica `MiPagina`, solo la rodea con comportamiento extra. Es exactamente lo que hace el patrón Decorator: añadir responsabilidades a un objeto sin alterar su código.

---

## 3. State — Patrón Comportamental

**¿Qué problema resuelve?**
Un servicio no puede pasar a cualquier estado en cualquier momento. Por ejemplo, no puedes completar un servicio que fue cancelado. El patrón State define **qué transiciones son válidas** y **rechaza las que no lo son**, haciendo que el ciclo de vida del servicio sea seguro y predecible.

**Ciclo de vida del servicio:**

```
  PENDING ──→ IN_PROGRESS ──→ COMPLETED
     │               │
     └───────────────┴──→ CANCELLED
```

**¿Dónde están las transiciones definidas?**
[washops-app/src/shared/utils/constants.js](washops-app/src/shared/utils/constants.js) — líneas 8–11

```js
// Líneas 8-11 — Mapa de transiciones permitidas
export const VALID_TRANSITIONS = {
  PENDING:     ['IN_PROGRESS', 'CANCELLED'],  // desde PENDING puedes ir a dos estados
  IN_PROGRESS: ['COMPLETED',   'CANCELLED'],  // desde IN_PROGRESS también dos opciones
  // COMPLETED y CANCELLED no aparecen → son estados finales, sin salida
};
```

**¿Dónde se aplica la validación?**
[washops-app/src/lib/db.js](washops-app/src/lib/db.js) — líneas 92–109

```js
// Líneas 92-109 — updateServiceStatus aplica el patrón State
export async function updateServiceStatus(id, newStatus, currentStatus) {

  // Paso 1: verificar que la transición sea válida
  const allowed = VALID_TRANSITIONS[currentStatus] || [];
  if (!allowed.includes(newStatus)) {
    throw new Error(`Transición no permitida: ${currentStatus} → ${newStatus}`);
    // ↑ si intentas ir a un estado no permitido, lanza error inmediatamente
  }

  // Paso 2: registrar timestamps según el estado al que se llega
  const extra = {};
  if (newStatus === 'IN_PROGRESS') extra.started_at   = new Date().toISOString();
  if (newStatus === 'COMPLETED')   extra.completed_at = new Date().toISOString();

  // Paso 3: guardar el nuevo estado en la BD
  const { data, error } = await supabase
    .from('services')
    .update({ status: newStatus, ...extra })
    .eq('id', id)
    .select()
    .single();
  if (error) throw error;
  return data;
}
```

**¿Por qué es State?**
Cada estado del servicio define qué puede hacer a continuación. La lógica de transición está centralizada en un solo lugar (`VALID_TRANSITIONS` + `updateServiceStatus`), no dispersa en múltiples componentes.

---
---

## Resumen

| # | Patrón | Tipo | Archivo | Líneas clave |
|---|--------|------|---------|-------------|
| 1 | **Factory Method** | Creacional | [constants.js](washops-app/src/shared/utils/constants.js) | 1–6 |
| | | | [db.js](washops-app/src/lib/db.js) | 82–89 |
| 2 | **Decorator** | Estructural | [App.jsx](washops-app/src/App.jsx) | 13–18 |
| 3 | **State** | Comportamental | [constants.js](washops-app/src/shared/utils/constants.js) | 8–11 |
| | | | [db.js](washops-app/src/lib/db.js) | 92–109 |

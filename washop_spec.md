# WASHOPS - Especificación del Sistema

**Versión:** 1.0  
**Última actualización:** 2026-05-08  
**Propósito:** Demostración educativa de 3 patrones de diseño fundamentales

---

## 📋 Resumen Ejecutivo

**WASHOPS** es un sistema de gestión para un servicio de lavado de vehículos que demuestra de manera práctica e interactiva tres patrones de diseño:

1. **Factory Method** - Creación de diferentes tipos de servicios
2. **Decorator Pattern** - Adición dinámica de extras/opcionales
3. **State Pattern** - Gestión del ciclo de vida de servicios

El sistema consta de un backend Python limpio y un frontend web moderno con interfaz intuitiva.

---

## 🏗️ Arquitectura General

### Estructura de Carpetas

```
washop/
├── patterns/                      # 3 Patrones de Diseño
│   ├── factory.py                 # Factory Method Pattern
│   ├── decorator.py               # Decorator Pattern
│   ├── state.py                   # State Pattern
│   └── __init__.py
│
├── frontend/                       # Interfaz Web
│   ├── index.html                 # Dashboard + Services + Modals
│   ├── styles.css                 # Diseño limpio y moderno
│   └── app.js                     # Lógica de frontend
│
├── __init__.py                    # Root imports
├── requirements.txt               # Dependencias
└── washop_spec.md                 # Este archivo
```

---

## 🎨 PATRONES DE DISEÑO IMPLEMENTADOS

### 1. FACTORY METHOD PATTERN (patterns/factory.py)

**Propósito:** Crear diferentes tipos de servicios sin especificar sus clases exactas

**Clases:**
- `Service` - Clase base
- `BasicService` - $45,000 (Lavado simple)
- `FullService` - $75,000 (Lavado + Secado)
- `PremiumService` - $120,000 (Profesional completo)
- `ExpressService` - $35,000 (Rápido, 20 min)
- `ServiceFactory` - Factory que crea servicios

**Uso en Frontend:**
- Modal Paso 1: Seleccionar tipo de servicio
- Los 4 tipos se muestran como cards interactivas

---

### 2. DECORATOR PATTERN (patterns/decorator.py)

**Propósito:** Agregar funcionalidades dinámicamente sin modificar la clase base

**Extras disponibles:**
- `WaxingExtra` - Encerado (+$15,000)
- `VacuumExtra` - Vacío Interior (+$12,000)
- `TirePolishExtra` - Pulimiento Llantas (+$10,000)

**Características:**
- Los extras se agregan a una lista en el servicio
- El precio se calcula dinámicamente
- Se pueden combinar múltiples extras
- Cálculo en tiempo real en el frontend

**Uso en Frontend:**
- Modal Paso 2: Seleccionar extras con checkboxes
- Precio total se actualiza automáticamente

---

### 3. STATE PATTERN (patterns/state.py)

**Propósito:** Manejar diferentes comportamientos según el estado del servicio

**Estados:**
- `PENDING` (Pendiente) - Estado inicial
- `IN_PROGRESS` (En Progreso) - Servicio activo
- `COMPLETED` (Completado) - Servicio finalizado
- `CANCELLED` (Cancelado) - Servicio cancelado

**Transiciones válidas:**
- PENDING → IN_PROGRESS → COMPLETED
- PENDING → CANCELLED
- IN_PROGRESS → CANCELLED

**Uso en Frontend:**
- Dashboard: Kanban board con 3 columnas por estado
- Services: Filtros por estado
- Los servicios nuevos comienzan en PENDING

---

## 🎨 FRONTEND - UI/UX

### Estructura de Páginas

#### 1. DASHBOARD
- **Métricas:** 4 tarjetas (Services Today, Completed, In Progress, Today's Revenue)
- **Active Services:** Kanban board con servicios organizados por estado
- **Recent Activity:** Panel derecho con últimas operaciones
- **Emojis:** 🚿 en título, emojis en métrica cards

#### 2. SERVICES
- **Filtros:** All, Pending, In Progress, Completed, Cancelled
- **Búsqueda:** Buscar por placa o cliente
- **Acciones:** Today, Export, + New Service
- **Tabla:** ID, Plate, Customer/Vehicle, Type, Status, Price, Time, Actions
- **Action Buttons:** Editar (✎), Más opciones (⋯)

#### 3. CUSTOMERS
- **Filtros:** All, Frequent (35%), Corporate (15%), Occasional (50%)
- **Búsqueda:** Buscar por nombre o email
- **Layout:** Grid de cards (3 columnas)
- **Información por cliente:**
  - Avatar con iniciales (color según tipo)
  - Nombre y tipo de cliente
  - Teléfono y email (generado automáticamente)
  - Vehículos asociados (desde servicios)
  - Número de servicios realizados
  - Total gastado en servicios
  - Botones: "View History" y "New Service"
- **Generación automática:** Los clientes se crean desde los servicios registrados
- **Tipos de cliente:**
  - **FREQUENT (35%)** - Avatar azul cyan
  - **CORPORATE (15%)** - Avatar naranja
  - **OCCASIONAL (50%)** - Avatar rosa

#### 4. PAYMENTS
- **Tabs:** Transactions (activo), Monthly Summary, Outstanding
- **Búsqueda:** Buscar por transacción
- **Acciones:** Selector de mes (March 2026), Export
- **Tabla de transacciones:** #TRX, Date, Service/Customer, Method, Amount, Status, Action
- **Métodos de pago:**
  - 💵 Cash
  - 📱 Nequi (Billetera digital)
  - 🏧 Debit (Tarjeta débito)
  - 💳 Credit (Tarjeta crédito)
- **Estados de pago:**
  - ● Confirmed (Verde)
  - ● Pending (Naranja)
  - ● Failed (Rojo)
- **Panel derecho:**
  - Monthly Revenue total (Ej: $8.42M)
  - Gráfico de ingresos por tipo de servicio
  - Desglose de métodos de pago
- **Generación automática:** Los pagos se crean desde los servicios registrados

#### 5. REPORTS
- **Period Filters:** This Month, This Week, Today, Quarter, Custom Range
- **KPI Cards:** 4 tarjetas con métricas principales
  - Total Revenue (ingresos totales)
  - Total Services (servicios realizados)
  - New Customers (nuevos clientes)
  - Avg. Service Time (tiempo promedio)
- **Gráficos:**
  - Bar chart: Ingresos diarios (últimos 28 días)
  - Pie chart: Distribución de ingresos por tipo de servicio
- **Performance Table:** Ranking de servicios por ingresos
- **Generación automática:** Todos los datos se calculan desde servicios registrados

#### 6. MODAL - CREAR NUEVO SERVICIO
- **Paso 1:** Seleccionar tipo (Factory Method)
- **Paso 2:** Agregar extras (Decorator Pattern)
- **Paso 3:** Datos del cliente (State - PENDING)

### Diseño Visual

**Tema:** Claro y profesional
- **Fondo principal:** #f5f5f5 (gris claro)
- **Componentes:** #fff (blanco)
- **Primario:** #00bcd4 (cyan)
- **Secundario:** #51cf66 (verde para dinero)
- **Estados:**
  - Pending: #ffe066 (amarillo)
  - In Progress: #74c0fc (azul)
  - Completed: #51cf66 (verde)

**Sidebar:**
- Ancho: 220px
- Color: #2c3e50 (azul oscuro)
- Menú con secciones (MAIN, MANAGEMENT, SETTINGS)

**Panel derecho (Recent Activity):**
- Ancho: 280px
- Color: #fff (blanco)
- Muestra últimos 5 servicios creados

---

## 💾 DATOS Y PERSISTENCIA

### Almacenamiento
- **localStorage del navegador** - Persiste datos entre sesiones
- Clave `washops_services`: Array de servicios
- Clave `washops_customers`: Array de clientes
- Formato: JSON array

### Estructura de Servicio

```javascript
{
  id: "SV-xxxx",           // ID único generado
  type: "FULL",            // Tipo de servicio
  price: 90000,            // Precio total
  extras: ["Encerado"],    // Extras seleccionados
  customer: "Juan Pérez",  // Nombre del cliente
  plate: "ABC-123",        // Placa del vehículo
  state: "PENDING",        // Estado actual
  timestamp: "2026-05-08..." // Fecha/hora de creación
}
```

### Estructura de Cliente

```javascript
{
  name: "Ana Gómez",                      // Nombre del cliente
  plate: "ABC-123",                       // Primera placa asociada
  phone: "(604) 312-4578",                // Teléfono generado
  email: "ana.gomez@email.com",           // Email generado
  vehicles: ["ABC-123", "XYZ-789"],       // Todas las placas de servicios
  servicesCount: 28,                      // Número de servicios
  totalSpent: 1200000,                    // Total gastado en servicios
  type: "FREQUENT",                       // Tipo: FREQUENT, CORPORATE, OCCASIONAL
  timestamp: "2026-05-08..."              // Fecha de primer servicio
}
```

---

## 🎯 FUNCIONALIDADES IMPLEMENTADAS

### ✅ Completadas

1. **Backend Patterns**
   - [x] Factory Method implementado
   - [x] Decorator Pattern implementado
   - [x] State Pattern implementado
   - [x] Separación en carpeta patterns/

2. **Frontend - Dashboard**
   - [x] Layout 3 columnas (Sidebar | Contenido | Recent Activity)
   - [x] 4 Métricas con emojis
   - [x] Kanban board dinámico
   - [x] Actualización en tiempo real

3. **Frontend - Services**
   - [x] Tabla de servicios
   - [x] Filtros por estado
   - [x] Búsqueda
   - [x] Action buttons
   - [x] Contadores dinámicos

4. **Frontend - Customers**
   - [x] Grid de customer cards
   - [x] Filtros por tipo (Frequent, Corporate, Occasional)
   - [x] Búsqueda por nombre/email
   - [x] Generación automática de clientes
   - [x] Teléfono y email generado dinámicamente
   - [x] Estadísticas por cliente (servicios, total gastado)
   - [x] Avatar con color según tipo
   - [x] Contadores dinámicos

5. **Frontend - Payments**
   - [x] Tabla de transacciones
   - [x] Tabs (Transactions, Monthly Summary, Outstanding)
   - [x] Generación automática de pagos desde servicios
   - [x] Métodos de pago (Cash, Nequi, Debit, Credit)
   - [x] Estados de pago (Confirmed, Pending, Failed)
   - [x] Panel derecho con métricas
   - [x] Gráfico de ingresos por tipo de servicio
   - [x] Desglose de métodos de pago
   - [x] Total de ingresos mensuales
   - [x] Contador de transacciones

6. **Frontend - Reports**
   - [x] KPI metric cards (Total Revenue, Total Services, New Customers, Avg. Time)
   - [x] Period filters (This Month, This Week, Today, Quarter, Custom Range)
   - [x] Bar chart: Ingresos diarios (últimos 28 días)
   - [x] Pie chart: Distribución por tipo de servicio
   - [x] Performance table: Ranking de servicios
   - [x] Generación automática de datos desde servicios
   - [x] Canvas API para gráficos dinámicos

7. **Frontend - Modal Crear Servicio**
   - [x] Paso 1: Factory Method (seleccionar tipo)
   - [x] Paso 2: Decorator (agregar extras)
   - [x] Paso 3: Datos del cliente
   - [x] Cálculo dinámico de precios
   - [x] Validación de campos

8. **Persistencia**
   - [x] localStorage para servicios
   - [x] Datos persisten entre sesiones
   - [x] Sincronización Dashboard ↔ Services

9. **UI/UX**
   - [x] Diseño limpio y profesional
   - [x] Tema claro
   - [x] Colores consistentes
   - [x] Responsive layout
   - [x] Emojis descriptivos

---

## 📊 DATOS DE PRUEBA

### Precios de Servicios

| Tipo | Precio Base |
|------|------------|
| BASIC | $45,000 |
| FULL | $75,000 |
| PREMIUM | $120,000 |
| EXPRESS | $35,000 |

### Precios de Extras

| Extra | Precio |
|-------|--------|
| Encerado | +$15,000 |
| Vacío Interior | +$12,000 |
| Pulimiento Llantas | +$10,000 |

### Ejemplo de Servicio Creado

```
ID: SV-1234
Tipo: PREMIUM
Cliente: Ana Gómez
Placa: ABC-123
Extras: Encerado, Vacío Interior
Precio Base: $120,000
Precio Extras: $27,000
Precio Total: $147,000
Estado: PENDING
```

---

## 🔄 FLUJO DE USUARIO

### Crear un Nuevo Servicio

1. **Dashboard/Services** → Click "+ New Service"
2. **Modal abre - Paso 1:** Selecciona tipo de servicio (Factory)
3. **Modal - Paso 2:** Selecciona extras deseados (Decorator)
4. **Modal - Paso 3:** Ingresa nombre cliente y placa
5. **Confirmar:** Click "Crear Servicio"
6. **Resultado:**
   - Servicio guardado en localStorage
   - Aparece en tabla Services
   - Aparece en Kanban (columna PENDING)
   - Aparece en Recent Activity

### Ver Servicios

- **Dashboard:** Kanban board organizado por estado
- **Services:** Tabla detallada con filtros
- **Filtros:** Puede filtrar por estado (Pending, In Progress, etc.)
- **Búsqueda:** Buscar por placa o nombre del cliente

---

## 🚀 PRÓXIMAS SECCIONES A IMPLEMENTAR

### Fase 2: Extensión del Sistema

- [x] **Customers** - Gestión de clientes
  - [x] Cards de clientes con información
  - [x] Generación automática desde servicios
  - [x] Teléfono y email generados
  - [x] Filtros por tipo (Frequent, Corporate, Occasional)
  - [x] Estadísticas (servicios, total gastado)
  - [ ] Historial de servicios por cliente
  - [ ] Calificaciones/reseñas

- [x] **Payments** - Gestión de pagos
  - [x] Tabla de transacciones
  - [x] Métodos de pago visualizados
  - [x] Estados de pago (Confirmed, Pending, Failed)
  - [x] Ingresos mensuales
  - [x] Desglose por tipo de servicio
  - [ ] Historial detallado de pagos
  - [ ] Facturas generables
  - [ ] Reportes de ingresos por período

- [x] **Reports** - Reportes y Analytics
  - [x] Ingresos por período (bar chart de últimos 28 días)
  - [x] Servicios más solicitados (pie chart y tabla)
  - [x] KPIs principales (Total Revenue, Services, Customers, Avg Time)
  - [x] Estadísticas por tipo de servicio
  - [ ] Monthly Summary tab
  - [ ] Outstanding tab

---

## 🛠️ TECNOLOGÍAS UTILIZADAS

### Backend
- **Python 3.x** - Lenguaje
- **Patrones de Diseño** - Factory, Decorator, State

### Frontend
- **HTML5** - Estructura
- **CSS3** - Estilos (diseño limpio)
- **JavaScript Vanilla** - Lógica (sin frameworks)
- **localStorage API** - Persistencia
- **Canvas API** - Gráficos dinámicos (Reports)

### Datos
- **JSON** - Formato de datos
- **localStorage** - Almacenamiento local

---

## 📝 NOTAS DE DISEÑO

### Decisiones Tomadas

1. **Sin Backend HTTP:** Se usa localStorage para simplicidad educativa
2. **Frontend Vanilla JS:** Sin React/Vue para mostrar JavaScript puro
3. **Patrones Simples:** Código legible y fácil de entender
4. **UI Moderna:** Diseño limpio que representa un sistema real
5. **Emojis Descriptivos:** Iconografía clara sin necesidad de assets

### Convenciones

- **Formato ID:** SV-XXXX (SV = Service)
- **Precios:** En pesos colombianos ($)
- **Estados:** UPPERCASE (PENDING, IN_PROGRESS, etc.)
- **Clases Python:** PascalCase
- **Variables JS:** camelCase
- **CSS:** kebab-case

---

## 🔍 VALIDACIONES

### Crear Servicio

- ✓ Debe seleccionar un tipo de servicio
- ✓ Debe ingresar nombre del cliente
- ✓ Debe ingresar placa del vehículo
- ✓ Mínimo 3 caracteres en nombre
- ✓ Formato de placa: XXX-XXX

### Filtros

- ✓ Actualizan dinámicamente los contadores
- ✓ Muestran correctamente los servicios filtrados
- ✓ Destacan el filtro activo

---

## 📈 MÉTRICAS ACTUALES

- **Servicios en sistema:** Dinámico (según lo creado)
- **Clientes en sistema:** Dinámico (generado desde servicios)
- **Pagos en sistema:** Dinámico (generado desde servicios)
- **Tipos de servicio:** 4
- **Extras disponibles:** 3
- **Estados de servicio:** 4
- **Tipos de cliente:** 3 (Frequent, Corporate, Occasional)
- **Métodos de pago:** 4 (Cash, Nequi, Debit, Credit)
- **Estados de pago:** 3 (Confirmed, Pending, Failed)
- **Páginas principales:** 5 (Dashboard, Services, Customers, Payments, Reports)
- **Modales:** 1 (Crear servicio)
- **Información generada automáticamente:** Teléfono, email, vehículos por cliente, métodos de pago, transacciones

---

## 🎓 PROPÓSITO EDUCATIVO

Este proyecto demuestra:

1. **Factory Method** → Cómo desacoplar la creación de objetos
2. **Decorator Pattern** → Cómo agregar funcionalidades dinámicamente
3. **State Pattern** → Cómo encapsular comportamiento por estado
4. **Buenas prácticas** → Código limpio, separación de responsabilidades
5. **Frontend moderno** → UI/UX profesional sin frameworks

---

## 📞 INFORMACIÓN DEL PROYECTO

- **Creado:** 2026-05-08
- **Propósito:** Demostración educativa
- **Asignatura:** Diseño de Software
- **Duración:** Aprox. 8 horas de desarrollo
- **Estado:** En progreso (Fase 1 completa)

---

**Última revisión:** 2026-05-08  
**Estado:** Fase 1 y 2 completas (Dashboard, Services, Customers, Payments, Reports implementados)

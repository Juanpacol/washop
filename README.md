# 🚿 WASHOPS - Sistema de Gestión de Lavado de Vehículos

> **Demostración educativa de 3 patrones de diseño fundamentales: Factory Method, Decorator Pattern y State Pattern**

---

## 📋 Resumen

**WASHOPS** es un sistema completo de gestión para un servicio de lavado de vehículos que demuestra de manera práctica e interactiva tres patrones de diseño clave de la ingeniería de software.

El proyecto incluye:
- ✅ **Backend Python** con implementación de patrones de diseño
- ✅ **Frontend web** moderno y responsive con interfaz profesional
- ✅ **5 secciones principales** (Dashboard, Services, Customers, Payments, Reports)
- ✅ **Persistencia de datos** con localStorage
- ✅ **Gráficos dinámicos** con Canvas API

---

## 🎨 Patrones de Diseño Implementados

### 1. **Factory Method Pattern** 
Crea diferentes tipos de servicios sin especificar sus clases exactas.

```python
# Ejemplo de uso
service = ServiceFactory.create_service("premium")
print(service.name)    # "PREMIUM"
print(service.get_price())  # 120000
```

**Servicios disponibles:**
- BASIC - $45,000 (Lavado simple)
- FULL - $75,000 (Lavado + Secado)
- PREMIUM - $120,000 (Profesional)
- EXPRESS - $35,000 (Rápido, 20 min)

---

### 2. **Decorator Pattern**
Agrega funcionalidades dinámicamente sin modificar la clase base.

```python
# Agregar extras a un servicio
service = ServiceFactory.create_service("full")
service.extras.append(WaxingExtra())  # +$15,000
print(service.get_price())  # 90,000
```

**Extras disponibles:**
- 🔧 Encerado - +$15,000
- 🧹 Vacío Interior - +$12,000
- ✨ Pulimiento Llantas - +$10,000

---

### 3. **State Pattern**
Maneja diferentes comportamientos según el estado del servicio.

```python
# Gestionar ciclo de vida del servicio
service = ServiceFactory.create_service("basic")
stateful = ServiceWithState(service)

print(stateful.state.get_state_name())  # "PENDING"
stateful.start()                        # PENDING → IN_PROGRESS
stateful.complete()                     # IN_PROGRESS → COMPLETED
```

**Estados disponibles:**
- 🟡 PENDING (Pendiente)
- 🔵 IN_PROGRESS (En Progreso)
- 🟢 COMPLETED (Completado)
- 🔴 CANCELLED (Cancelado)

---

## 🏗️ Arquitectura del Proyecto

```
washop/
├── patterns/                    # Patrones de Diseño Python
│   ├── factory.py              # Factory Method Pattern
│   ├── decorator.py            # Decorator Pattern
│   ├── state.py                # State Pattern
│   └── __init__.py
│
├── frontend/                    # Aplicación Web
│   ├── index.html              # Estructura (5 páginas)
│   ├── app.js                  # Lógica JavaScript
│   └── styles.css              # Estilos CSS
│
├── README.md                   # Este archivo
├── washop_spec.md              # Especificación completa
└── requirements.txt            # Dependencias Python
```

---

## 🖥️ Frontend - Secciones Principales

### 📊 Dashboard
- 4 métricas principales (Servicios hoy, Completados, En progreso, Ingresos)
- Kanban board dinámico organizado por estados
- Panel de actividad reciente
- Actualización en tiempo real

### 📋 Services
- Tabla detallada de todos los servicios
- Filtros por estado (Pending, In Progress, Completed, Cancelled)
- Búsqueda por placa o cliente
- Acciones rápidas (editar, más opciones)

### 👥 Customers
- Grid de clientes con información completa
- Filtros por tipo (Frequent, Corporate, Occasional)
- Búsqueda por nombre o email
- Estadísticas: servicios realizados y total gastado
- Generación automática desde servicios registrados

### 💳 Payments
- Tabla de transacciones detallada
- Métodos de pago: Cash, Nequi, Debit, Credit
- Estados: Confirmed, Pending, Failed
- Métricas mensuales de ingresos
- Gráficos de distribución

### 📈 Reports
- KPIs principales (Total Revenue, Services, Customers, Avg Time)
- Filtros por período (This Month, This Week, Today, etc.)
- Gráfico de barras: Ingresos diarios (últimos 28 días)
- Gráfico pie: Distribución por tipo de servicio
- Tabla de desempeño

---

## 🚀 Cómo Usar

### Opción 1: Abrir directamente en el navegador
1. Descarga o clona el repositorio
2. Abre `frontend/index.html` en tu navegador
3. ¡Listo! El sistema está funcional

### Opción 2: Ejecutar backend Python
```bash
# Instalar dependencias
pip install -r requirements.txt

# Usar los patrones de diseño
python
>>> from patterns import ServiceFactory, ServiceWithState, WaxingExtra
>>> service = ServiceFactory.create_service("full")
>>> service.extras.append(WaxingExtra())
>>> print(service.get_price())  # 90000
```

### Opción 3: Desplegar en GitHub Pages
El frontend está listo para desplegarse en GitHub Pages sin cambios.

---

## 💾 Datos y Persistencia

**Almacenamiento:** localStorage del navegador
- Los servicios se guardan automáticamente
- Los datos persisten entre sesiones
- Customers y Payments se generan automáticamente

**Estructura de datos:**
```javascript
// Servicio
{
  id: "SV-1234",
  type: "PREMIUM",
  price: 147000,
  extras: ["Encerado", "Vacío Interior"],
  customer: "Ana Gómez",
  plate: "ABC-123",
  state: "PENDING",
  timestamp: "2026-05-08T10:30:00Z"
}
```

---

## 🛠️ Tecnologías Utilizadas

### Backend
- **Python 3.x** - Lenguaje de programación
- **Patrones de Diseño** - Factory, Decorator, State

### Frontend
- **HTML5** - Estructura
- **CSS3** - Estilos y diseño responsive
- **JavaScript Vanilla** - Lógica (sin frameworks)
- **Canvas API** - Gráficos dinámicos
- **localStorage API** - Persistencia local

---

## 📊 Características Principales

✅ **Completas:**
- Implementación de 3 patrones de diseño
- 5 páginas funcionales
- Persistencia de datos
- Generación automática de clientes y pagos
- Gráficos dinámicos (bar chart, pie chart)
- Búsqueda y filtros
- Modal para crear servicios
- Diseño responsive
- Emojis descriptivos

⚡ **Futuras mejoras:**
- Integración con base de datos real
- API REST backend
- Autenticación de usuarios
- Reportes más detallados
- Historial de servicios por cliente

---

## 💡 Propósito Educativo

Este proyecto demuestra:

1. **Factory Method** → Desacoplamiento en la creación de objetos
2. **Decorator Pattern** → Adición dinámica de funcionalidades
3. **State Pattern** → Encapsulación de comportamiento por estado
4. **Buenas prácticas** → Código limpio y separación de responsabilidades
5. **Frontend moderno** → UI/UX profesional sin frameworks

---

## 📸 Flujo de Usuario

1. **Crear Servicio**
   - Dashboard/Services → Click "+ New Service"
   - Modal Paso 1: Seleccionar tipo (Factory)
   - Modal Paso 2: Seleccionar extras (Decorator)
   - Modal Paso 3: Datos del cliente
   - ✅ Servicio guardado automáticamente

2. **Ver Servicios**
   - Dashboard: Kanban organizado por estado
   - Services: Tabla con filtros y búsqueda
   - Clientes y pagos se generan automáticamente

3. **Reportes**
   - Filtrar por período
   - Ver KPIs principales
   - Analizar gráficos de ingresos

---

## 📝 Notas Importantes

- **Sin Backend HTTP:** Se usa localStorage para simplicidad educativa
- **Frontend Vanilla JS:** Sin React/Vue para mostrar JavaScript puro
- **Datos de Prueba:** Generados automáticamente para demostración
- **Totalmente Funcional:** Sistema completo listo para usar

---

## 👨‍💻 Autor

**Juan Pablo Botero**
- Asignatura: Diseño de Software
- Propósito: Demostración educativa de patrones de diseño

---

## 📄 Documentación

Para más detalles técnicos, consulta:
- `washop_spec.md` - Especificación completa del sistema

---

## 🎯 Conclusión

**WASHOPS** es un sistema educativo completo que demuestra cómo aplicar patrones de diseño en una aplicación real, combinando backend Python con un frontend web moderno y profesional.

¡Listo para aprender patrones de diseño de forma práctica! 🚀

---

**Última actualización:** 2026-05-08  
**Versión:** 1.0  
**Estado:** ✅ Completo y funcional

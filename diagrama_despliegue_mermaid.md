# Diagrama de Despliegue UML - WASHOPS

```mermaid
graph TB
    subgraph "End User Device" ["👤 End User Device"]
        browser["🌐 Web Browser<br/>Chrome/Firefox/Safari"]
        storage["💾 localStorage<br/>Data Persistence"]
    end
    
    subgraph "Browser Runtime" ["⚙️ Browser Runtime<br/>Execution Environment"]
        html["📄 index.html<br/>Dashboard | Services<br/>Customers | Payments"]
        css["🎨 styles.css<br/>Responsive Design<br/>3-Column Layout"]
        js["⚡ app.js<br/>Vanilla JavaScript<br/>Canvas Charts"]
    end
    
    subgraph "GitHub Pages Server" ["🖥️ GitHub Pages<br/>Web Server"]
        files["📦 Web Files<br/>https://Juanpacol<br/>.github.io/wahop/"]
    end
    
    subgraph "Data" ["💾 Data Storage"]
        services["Services"]
        customers["Customers"]
        payments["Payments"]
    end
    
    browser -->|HTTP GET| html
    browser -->|HTTP GET| css
    browser -->|HTTP GET| js
    
    html -.->|stores| storage
    css -.->|stores| storage
    js -.->|stores| storage
    
    storage -->|read/write| services
    storage -->|read/write| customers
    storage -->|read/write| payments
    
    files -->|serves| html
    files -->|serves| css
    files -->|serves| js
    
    style browser fill:#a5d8ff,stroke:#4a9eed,stroke-width:2px
    style storage fill:#c3fae8,stroke:#22c55e,stroke-width:2px
    style html fill:#ffc9c9,stroke:#ef4444,stroke-width:2px
    style css fill:#ffc9c9,stroke:#ef4444,stroke-width:2px
    style js fill:#ffc9c9,stroke:#ef4444,stroke-width:2px
    style files fill:#fff3bf,stroke:#f59e0b,stroke-width:2px
    style services fill:#d0bfff,stroke:#8b5cf6,stroke-width:1px
    style customers fill:#d0bfff,stroke:#8b5cf6,stroke-width:1px
    style payments fill:#d0bfff,stroke:#8b5cf6,stroke-width:1px
```

## 📋 Componentes del Diagrama

### Nodos (Nodes)
- **End User Device** - Máquina física del usuario
- **Browser Runtime** - Ambiente de ejecución del navegador
- **GitHub Pages Server** - Servidor de hosting

### Artefactos (Artifacts)
- **index.html** - Estructura de 5 páginas
- **styles.css** - Estilos y diseño responsive
- **app.js** - Lógica de aplicación (Vanilla JS)
- **Web Files** - Archivos en el servidor

### Comunicaciones (Relationships)
- **→** Flujo principal (HTTP GET)
- **-.->** Flujos secundarios (store/read)

### Datos (Data)
- **Services** - Servicios creados
- **Customers** - Clientes generados
- **Payments** - Pagos registrados

## 🔄 Flujo del Sistema

1. **User abre navegador** → Accede a https://Juanpacol.github.io/wahop/
2. **GitHub Pages** → Sirve index.html, styles.css, app.js
3. **Browser renderiza** → Muestra la interfaz WASHOPS
4. **Usuario interactúa** → Crea servicios, ve reportes, etc.
5. **JavaScript** → Almacena datos en localStorage
6. **localStorage** → Persiste datos entre sesiones

## 🛠️ Tecnologías por Componente

| Componente | Tecnología | Propósito |
|-----------|-----------|----------|
| Browser | Chrome/Firefox/Safari | Renderizar la aplicación |
| HTML | HTML5 | Estructura de las 5 páginas |
| CSS | CSS3 | Diseño responsive y temas |
| JavaScript | Vanilla JS | Lógica y interactividad |
| Storage | localStorage API | Persistencia de datos |
| Server | GitHub Pages | Hosting gratuito con HTTPS |
| Protocol | HTTPS | Comunicación segura |

## 📊 Capacidades del Sistema

✅ **Estático** - No requiere servidor backend  
✅ **Offline** - Funciona con datos en localStorage  
✅ **Rápido** - Sin latencia de red para interacciones  
✅ **Escalable** - Se puede migrar a backend en el futuro  
✅ **Seguro** - HTTPS automático en GitHub Pages  
✅ **Gratuito** - Hosting sin costo  

---

**Diagrama Generado:** 2026-05-08  
**Herramienta:** Mermaid  
**Formato:** UML Deployment Diagram

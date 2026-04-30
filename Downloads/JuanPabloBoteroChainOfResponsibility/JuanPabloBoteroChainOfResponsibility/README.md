# Chain of Responsibility - Moderación de Comentarios

## Cómo ejecutar

```bash
python main.py
```

## Qué hace el código

Sistema de moderación de comentarios que pasa cada texto por una cadena de filtros.
Cada filtro puede **bloquear**, **modificar** o **marcar** el contenido.

## Tests incluidos

### MODERACIÓN SECUENCIAL
Los filtros se ejecutan uno tras otro en orden. Si uno bloquea, se detiene.

#### Test 1: Comentario normal
```
Entrada:  "Este producto es genial, me encantó!"
Resultado: ✅ Pasa sin problemas
```

#### Test 2: Spam (bloqueado)
```
Entrada:  "Oferta especial, click aqui para ganar dinero gratis"
Resultado: 🚫 BLOQUEADO
Razón:    Contiene palabra spam "oferta"
Nota:     Se detiene aquí, no pasa a los otros filtros
```

#### Test 3: Palabras ofensivas (modificadas)
```
Entrada:  "Eres un idiota y un inutil"
Resultado: ✏️ MODIFICADO
Salida:   "Eres un ****** y un ******"
Nota:     Pasa a los demás filtros después de modificar
```

#### Test 4: Enlace externo (marcado)
```
Entrada:  "Mira este enlace: https://ejemplo.com para más info"
Resultado: ⚠️ MARCADO para revisión
Razón:    Contiene 1 enlace externo
```

#### Test 5: Comentario muy largo (marcado)
```
Entrada:  "Comentario muy largo: " + 200 caracteres de "a"
Resultado: ⚠️ MARCADO para revisión
Razón:    Supera 100 caracteres máximos
```

### MODERACIÓN PARALELA
Todos los filtros se ejecutan al mismo tiempo (en hilos separados).
Se consolidan todos los resultados.

#### Test: Comentario problemático en todo
```
Entrada:  "idiota mira https://spam.com oferta gratis"
Resultado: 
  - BLOQUEADO: contiene spam "oferta"
  - MODIFICADO: "idiota" → "******"
  - MARCADO: contiene enlace externo
```

## Estructura de archivos

- `main.py` → Punto de entrada, define tests
- `comment.py` → Dataclass del comentario
- `filter.py` → Clase base para los filtros
- `filters.py` → Los 4 filtros concretos (Spam, Profanidad, Longitud, Enlaces)
- `moderation_chain.py` → Orquestador (cadena secuencial o paralela)

## Cómo explicarlo en la sustentación

1. **Patrón**: Chain of Responsibility encadena objetos
2. **Flujo**: Comentario → Filtro 1 → Filtro 2 → Filtro 3 → Filtro 4 → Resultado
3. **Ventaja**: Agregar/quitar/reordenar filtros sin tocar el código principal
4. **Modos**: 
   - Secuencial: rápido, se detiene si bloquea
   - Paralelo: más rápido, no se detiene (todos corren)

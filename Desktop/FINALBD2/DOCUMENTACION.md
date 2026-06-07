# Documentación del Proyecto — Red Social Académica con Persistencia Políglota

**Asignatura:** Base de Datos II  
**Institución:** Politécnico Colombiano Jaime Isaza Cadavid  
**Profesor:** Manolo Pajaro Borras  
**Evaluación:** Final · 12 de junio de 2026

---

LINK VIDEO SUSTENTACION : https://youtu.be/yLR4h6FWalg


## Tabla de Contenidos

1. [¿Qué es este proyecto?](#1-qué-es-este-proyecto)
2. [¿Por qué se usan cuatro bases de datos?](#2-por-qué-se-usan-cuatro-bases-de-datos)
3. [¿Cómo fluyen los datos a través del sistema?](#3-cómo-fluyen-los-datos-a-través-del-sistema)
4. [Fase 1 — Corrección e Integridad en PostgreSQL](#4-fase-1--corrección-e-integridad-en-postgresql)
5. [Fase 2 — Lógica de Negocio: el Procedimiento y las Vistas](#5-fase-2--lógica-de-negocio-el-procedimiento-y-las-vistas)
6. [Fase 3 — El Puente Políglota: migración con Python](#6-fase-3--el-puente-políglota-migración-con-python)
7. [Fase 4 — La Interfaz Gráfica](#7-fase-4--la-interfaz-gráfica)
8. [La Infraestructura con Docker](#8-la-infraestructura-con-docker)
9. [Los Datos de Prueba](#9-los-datos-de-prueba)
10. [Técnicas de Prompting Aplicadas](#10-técnicas-de-prompting-aplicadas)
11. [Guía de Ejecución](#11-guía-de-ejecución)
12. [Solución de Problemas Comunes](#12-solución-de-problemas-comunes)

---

## 1. ¿Qué es este proyecto?

Este proyecto simula el backend de una **red social enfocada en comunidades académicas**. Los usuarios pueden publicar contenido, dejar comentarios en las publicaciones de otros y enviar solicitudes de amistad.

El punto de partida era un sistema mal construido: las tablas de la base de datos existían, pero no tenían ningún tipo de restricción entre ellas. Esto significa que era posible registrar una publicación de un autor que no existía, o un comentario sobre una publicación que nunca se creó, sin que el sistema lo detectara. Ese tipo de dato roto se llama **registro huérfano**.

El proyecto corrige ese problema desde la raíz y luego construye encima de esa base sólida un sistema completo que incluye:

- Una base de datos relacional bien estructurada con todas sus restricciones de integridad aplicadas correctamente.
- Lógica de negocio automatizada que vive dentro de la misma base de datos.
- Un proceso que copia y adapta la información hacia tres sistemas de bases de datos NoSQL distintos, cada uno pensado para un caso de uso diferente.
- Una aplicación de escritorio con interfaz visual para que el usuario pueda ver y operar todo desde un solo lugar.

---

## 2. ¿Por qué se usan cuatro bases de datos?

Esta es la esencia de la **Persistencia Políglota**: en lugar de forzar a una sola base de datos a hacerlo todo, se asigna a cada una el trabajo que mejor sabe hacer.

### PostgreSQL — El núcleo confiable

Es la base de datos principal. Aquí vive la verdad oficial del sistema. Garantiza que los datos sean correctos, que las relaciones entre tablas sean válidas y que ninguna operación quede a medias. Es el punto de partida de toda la información y el lugar donde se ejecuta la lógica de negocio más crítica.

La razón de usar PostgreSQL como núcleo es su robustez: soporta transacciones completas, restricciones de integridad, procedimientos almacenados y vistas. Es la opción natural para guardar datos estructurados que no pueden permitirse inconsistencias.

### MongoDB — El lector rápido de contenido

MongoDB almacena las publicaciones de una manera muy diferente a PostgreSQL. En lugar de guardar la información en tablas separadas que luego hay que unir, MongoDB guarda una publicación como un documento completo que ya incluye dentro de sí mismo el nombre del autor y todos los comentarios que ha recibido.

Esto tiene una ventaja práctica enorme: cuando la aplicación quiere mostrar una publicación con sus comentarios, MongoDB responde con una sola consulta. En PostgreSQL, la misma operación requeriría unir tres tablas diferentes. Para un sistema de contenido con mucha lectura, MongoDB es considerablemente más eficiente.

### Cassandra — El especialista en timelines

Cassandra está diseñada para responder muy rápido a un tipo de consulta muy específico: "dame todas las publicaciones de este usuario ordenadas del más reciente al más antiguo". Este es el comportamiento típico de cualquier red social cuando un usuario ve su propio historial de publicaciones.

Cassandra logra esa velocidad porque organiza físicamente los datos en disco exactamente en el orden en que van a ser consultados. No necesita ordenar ni buscar en el momento de la consulta, porque ya está todo en el orden correcto desde que se guardó.

### Redis — La memoria de corto plazo

Redis es una base de datos que vive completamente en la memoria RAM del servidor, lo que la hace extremadamente rápida. Se usa como caché: guarda temporalmente los resultados de las consultas más frecuentes para que no haya que recalcularlas cada vez.

En este proyecto, Redis guarda el feed de noticias completo y los contadores de likes de cada publicación. Cuando alguien abre la aplicación, en lugar de consultar PostgreSQL y recalcular todo, el sistema lee directamente desde Redis en cuestión de milisegundos. Los datos en Redis tienen una vida útil de cinco minutos; después de ese tiempo desaparecen automáticamente y la próxima vez que se ejecute el proceso de migración se vuelven a guardar actualizados.

---

## 3. ¿Cómo fluyen los datos a través del sistema?

El ciclo de vida de la información sigue siempre el mismo camino:

**Primero**, cuando el sistema arranca por primera vez, PostgreSQL lee automáticamente los archivos de definición del proyecto y crea todas las tablas con sus restricciones, registra los datos de prueba e instala las vistas y el procedimiento almacenado. Esto sucede sin intervención manual.

**Segundo**, el usuario ejecuta el proceso de migración desde Python o desde el botón en la interfaz gráfica. Este proceso conecta a PostgreSQL, extrae toda la información, la transforma al formato que necesita cada base de datos NoSQL y la carga en MongoDB, Cassandra y Redis, en ese orden.

**Tercero**, la interfaz gráfica se conecta a las cuatro bases de datos y muestra los datos de cada una en su panel correspondiente. El usuario puede ver el feed de noticias desde PostgreSQL, los documentos enriquecidos desde MongoDB, el timeline de un usuario desde Cassandra, y las claves en caché desde Redis.

Si el usuario ejecuta el procedimiento de crear amistad desde la interfaz, ese cambio va directamente a PostgreSQL. Para que MongoDB, Cassandra y Redis reflejen ese cambio, habría que volver a ejecutar el proceso de migración.

---

## 4. Fase 1 — Corrección e Integridad en PostgreSQL

Esta fase responde la pregunta: ¿cómo le decimos a PostgreSQL que exija coherencia entre las tablas?

### El problema original

Las tablas del sistema original tenían columnas como "identificador del autor" en la tabla de publicaciones, pero PostgreSQL no sabía que ese número debía corresponder a un usuario real. Era posible registrar una publicación con un número de autor que no existía en la tabla de usuarios. Eso es exactamente lo que un **registro huérfano** es: un dato que apunta a nada.

### La solución: llaves foráneas

Una **llave foránea** es una instrucción que le dice a PostgreSQL "el valor de esta columna debe existir como identificador en esa otra tabla". Con ese cambio, si alguien intenta registrar una publicación con un autor que no existe, PostgreSQL rechaza la operación automáticamente.

Se añadieron llaves foráneas en cinco puntos del sistema:

- La columna del autor en publicaciones ahora exige que ese autor exista en la tabla de usuarios.
- Las dos columnas de la tabla de comentarios exigen que tanto el usuario que comenta como la publicación comentada existan en sus respectivas tablas.
- Las dos columnas de la tabla de amistades exigen que tanto el usuario que envía la solicitud como el que la recibe sean usuarios reales.

Todas estas llaves foráneas están configuradas en modo **cascada**: si se borra un usuario, todas sus publicaciones, comentarios y amistades se borran automáticamente también. Esto evita que queden restos de datos sin dueño.

### La restricción de auto-amistad

Se añadió una regla que impide que un usuario se envíe a sí mismo una solicitud de amistad. Si los dos identificadores en una fila de amistades son el mismo número, PostgreSQL rechaza la inserción automáticamente. Ninguna lógica adicional en Python ni en la interfaz necesita verificarlo.

### Los índices de rendimiento

Se crearon cuatro índices para acelerar las búsquedas más frecuentes del sistema. Un índice funciona como el índice al final de un libro: en lugar de revisar toda la tabla fila por fila para encontrar algo, la base de datos salta directamente a donde está la información. Esto hace que consultas como "todas las publicaciones de un autor" o "todos los comentarios de una publicación" sean mucho más rápidas.

---

## 5. Fase 2 — Lógica de Negocio: el Procedimiento y las Vistas

Esta fase traslada parte de la inteligencia del sistema hacia adentro de la base de datos, para que esa lógica funcione igual sin importar desde dónde se acceda.

### El procedimiento almacenado: crear una amistad

Un **procedimiento almacenado** es una secuencia de pasos guardada dentro de la base de datos que se puede ejecutar con una sola instrucción. Su ventaja es que la lógica es consistente: no importa si el usuario crea una amistad desde la interfaz gráfica, desde un script de Python o desde la consola de PostgreSQL, siempre va a pasar exactamente lo mismo.

El procedimiento para crear amistades hace tres cosas en orden:

**Primero**, verifica si ya existe alguna relación entre los dos usuarios indicados, buscando en ambas direcciones. Una solicitud de A hacia B es la misma relación que una de B hacia A; no deben existir las dos al mismo tiempo.

**Segundo**, si ya existe una relación, el procedimiento avisa con un mensaje y termina sin hacer nada. No falla con un error, simplemente informa y se detiene.

**Tercero**, si no existe ninguna relación previa, registra una nueva solicitud de amistad con estado "pendiente".

El caso en que alguien intente hacerse amigo de sí mismo ni siquiera llega al procedimiento: la restricción del esquema lo bloquea antes de que el procedimiento pueda ejecutarse.

### Las vistas analíticas

Una **vista** es una consulta guardada dentro de la base de datos que se puede usar como si fuera una tabla normal. Cada vez que se consulta, la base de datos ejecuta la consulta por dentro y devuelve los resultados actualizados. Las vistas no guardan datos propios; simplifican el acceso a consultas que de otro modo serían complejas de escribir.

Se crearon tres vistas:

**Solicitudes pendientes:** Muestra todas las solicitudes de amistad que todavía no han sido aceptadas. En lugar de mostrar solo números de identificación, la vista ya une la información y muestra los nombres reales del usuario que envió la solicitud y del que la recibió.

**Amistades consolidadas:** Similar a la anterior, pero muestra solo las amistades que ya están en estado aceptado. Permite ver rápidamente quiénes son amigos entre sí.

**Feed de noticias:** Es la vista más compleja. Une información de tres tablas: usuarios, publicaciones y comentarios. Para cada publicación muestra el nombre del autor, el texto del contenido, la fecha, el número de likes y, mediante un conteo automático, cuántos comentarios ha recibido esa publicación. Los resultados aparecen ordenados del más reciente al más antiguo. Esta es la vista que aparece en el panel de PostgreSQL de la interfaz gráfica.

---

## 6. Fase 3 — El Puente Políglota: migración con Python

Esta fase es el corazón técnico del proyecto. Python actúa como intermediario entre el mundo relacional y el mundo NoSQL, transformando los datos según lo que cada base de datos espera recibir.

### La configuración centralizada

Antes de hacer cualquier migración, existe un archivo que guarda las direcciones y contraseñas de las cuatro bases de datos en un solo lugar. Cualquier módulo del sistema que necesite conectarse a una base de datos importa sus datos de conexión desde ese archivo único. Si cambia un puerto o una contraseña, el cambio se hace una sola vez y se propaga automáticamente a todo el sistema.

### La extracción desde PostgreSQL

El primer paso del proceso de migración es conectarse a PostgreSQL y traer toda la información que se va a distribuir. Se extraen cuatro conjuntos de datos: la lista completa de usuarios, la lista de publicaciones, la lista de comentarios, y el resultado ya calculado de la vista del feed de noticias. Toda esta información llega a Python como listas de objetos simples, listos para ser transformados.

### La carga en MongoDB

Para MongoDB, la transformación más importante es el **enriquecimiento de documentos**. En lugar de guardar los datos en el mismo formato separado que tienen en PostgreSQL, Python los combina antes de guardarlos.

Cada publicación se convierte en un documento completo que ya incluye dentro de sí mismo toda la información del autor, no solo su número de identificación sino también su nombre y país, y la lista completa de los comentarios que ha recibido esa publicación. El resultado es un documento autosuficiente que no necesita consultar ninguna otra colección para mostrar toda la información relevante de una publicación.

### La carga en Cassandra

Para Cassandra, la transformación es de naturaleza diferente. No se trata de enriquecer documentos, sino de organizar los datos de la manera correcta para que las consultas sean eficientes.

Cassandra necesita que quien diseña el sistema piense primero en cómo se van a consultar los datos antes de definir cómo se van a guardar. En este caso, la pregunta clave es qué se quiere buscar. La respuesta es el historial de publicaciones de un usuario específico, ordenado del más nuevo al más antiguo.

Con esa consulta en mente, se diseña la estructura de Cassandra de manera que todos los datos de un mismo usuario queden físicamente juntos en el disco, y dentro de ese grupo, ordenados por fecha de más reciente a más antiguo. Cuando se hace la consulta, Cassandra no necesita buscar ni ordenar; simplemente lee los datos en el orden en que ya están guardados.

El módulo también está preparado para el hecho de que Cassandra puede tardar hasta 90 segundos en estar disponible después de arrancar. Si la conexión falla al principio, el sistema espera y vuelve a intentarlo varias veces antes de rendirse.

### La carga en Redis

Para Redis, la transformación es la más sencilla. Se toman tres tipos de datos y se guardan con nombres de clave descriptivos:

El primero es el resultado completo del feed de noticias, guardado como texto estructurado. La próxima vez que la interfaz necesite mostrar el feed, puede leerlo directamente desde Redis sin tocar PostgreSQL.

El segundo son los contadores de likes de cada publicación, guardados individualmente. Si se necesita saber cuántos likes tiene una publicación específica, Redis lo responde casi instantáneamente.

El tercero es el número total de usuarios en el sistema, útil para estadísticas rápidas.

Los tres tipos de datos tienen una vida útil de cinco minutos. Después de ese tiempo Redis los elimina automáticamente.

### El orquestador

Existe un módulo que coordina el proceso completo en orden: primero la extracción de PostgreSQL, luego la carga en MongoDB, luego en Cassandra, luego en Redis. Muestra en pantalla el progreso de cada paso con mensajes numerados. Este módulo es el que se ejecuta desde la terminal y también el que la interfaz gráfica llama cuando el usuario presiona el botón de migración.

---

## 7. Fase 4 — La Interfaz Gráfica

La interfaz gráfica está construida con la librería PyQt6 y tiene un diseño de tema oscuro moderno. Se organiza con una barra de navegación a la izquierda y el contenido principal a la derecha.

### Diseño general

Al lado izquierdo hay una barra fija con el nombre del proyecto y seis botones de navegación, uno por cada sección. Al pie de esa barra aparecen cuatro indicadores de colores que representan el estado de conexión de cada base de datos. En la parte inferior de la ventana hay una barra de estado que muestra mensajes de confirmación o error después de cada acción.

### Sección ETL — Migración políglota

Es la sección principal de la interfaz. Tiene un botón destacado con un diseño de degradado de colores para iniciar el proceso de migración completo. Cuando se presiona, ocurren varias cosas al mismo tiempo:

El proceso de migración corre en un hilo separado, lo que significa que la ventana no se congela ni se bloquea mientras trabaja. El usuario puede seguir usando la interfaz.

Aparece una barra de progreso animada mientras el proceso está en marcha.

Cuatro pequeñas etiquetas cambian de color gris a verde con una marca de verificación a medida que cada paso termina: primero PostgreSQL cuando termina la extracción, luego MongoDB, luego Cassandra y finalmente Redis.

El área de registro muestra los mensajes del proceso con colores diferentes según la base de datos que está trabajando en ese momento.

### Sección PostgreSQL

Muestra el resultado de la vista del feed de noticias en una tabla organizada con columnas, encabezados y filas alternadas de diferentes tonos para facilitar la lectura. La tabla es interactiva y las columnas se pueden ajustar.

### Sección MongoDB

Muestra los documentos de las publicaciones con colores para facilitar la lectura: las claves de cada documento aparecen en azul, los textos en verde y los números en lila. Cada documento está separado del siguiente por una línea divisoria.

### Sección Cassandra

Tiene un campo de texto donde el usuario escribe el número de identificación de un usuario y presiona un botón para ver su timeline. La tabla resultante muestra las publicaciones de ese usuario ordenadas de la más reciente a la más antigua. También es posible presionar Enter directamente en el campo de texto para ejecutar la consulta sin hacer clic en el botón.

### Sección Redis

Muestra todas las claves activas actualmente en el caché en una tabla de tres columnas: el nombre de la clave, su valor, y el tiempo de vida restante en segundos. Esto permite ver en tiempo real cuánto tiempo le queda a cada dato antes de que Redis lo elimine automáticamente.

### Sección Procedimientos Almacenados

Tiene un formulario con dos campos para ingresar los identificadores de dos usuarios y un botón para ejecutar el procedimiento de crear amistad. El resultado aparece de inmediato: si la amistad se creó correctamente el mensaje aparece en verde, y si ya existía aparece en amarillo como advertencia.

Debajo del formulario hay dos botones adicionales para consultar las vistas de amistades: uno para ver las solicitudes pendientes y otro para ver las amistades ya aceptadas. Ambos muestran los resultados en una tabla.

---

## 8. La Infraestructura con Docker

Docker es la tecnología que permite correr los cuatro sistemas de bases de datos sin tener que instalarlos directamente en el computador. Cada base de datos corre dentro de un contenedor, que es como una pequeña computadora virtual aislada con todo lo que ese servicio necesita para funcionar.

El archivo de configuración de Docker define los cuatro contenedores con todos sus parámetros: qué versión de software usar, qué puerto exponer hacia afuera, dónde guardar los datos para que no se pierdan al reiniciar, y cómo verificar que el contenedor está listo para recibir conexiones.

Esa última parte, la verificación de disponibilidad, se llama **healthcheck**. Cada contenedor tiene definido un comando de verificación que Docker ejecuta periódicamente. Cuando ese comando tiene éxito, Docker confirma que el servicio está operativo.

Cassandra tiene un tratamiento especial: a diferencia de los otros tres servicios que se inicializan en cuestión de segundos, Cassandra puede tardar entre 60 y 90 segundos en estar completamente lista. El archivo de configuración le da ese tiempo antes de empezar a verificar su estado, lo que evita que el sistema lo marque como fallido prematuramente.

PostgreSQL también tiene una configuración especial: está configurado para aceptar conexiones sin necesidad de contraseña desde fuera del contenedor. Esto es adecuado para un entorno de desarrollo académico y evita problemas de autenticación que son frecuentes en Windows cuando hay una instalación local de PostgreSQL en el mismo computador.

Cada contenedor tiene su propio espacio de almacenamiento persistente. Si se detiene y se vuelve a iniciar Docker, los datos siguen ahí tal como estaban.

---

## 9. Los Datos de Prueba

Los datos de prueba están diseñados estratégicamente para que cada componente del sistema tenga algo interesante que procesar y mostrar.

**Seis usuarios** registrados provenientes de cuatro países distintos. Esa variedad geográfica hace que los documentos de MongoDB sean más representativos, porque el campo del país tiene valores diferentes en cada uno.

**Ocho publicaciones** distribuidas entre cinco de los seis usuarios. Esa distribución crea múltiples grupos de datos en Cassandra, lo que hace la demostración más representativa de cómo funciona ese sistema cuando hay varios autores distintos.

**Doce comentarios** repartidos entre las publicaciones, con un máximo de tres por publicación. Esta distribución desigual hace que los grupos de comentarios en MongoDB tengan longitudes diferentes, lo que es más cercano a cómo se comporta un sistema real.

**Siete relaciones de amistad**: cuatro en estado aceptado y tres en estado pendiente. Esto garantiza que las dos vistas de amistades tengan filas para mostrar cuando se consultan desde la interfaz, y que el procedimiento de crear amistad tenga casos reales para verificar duplicados.

---

## 10. Técnicas de Prompting Aplicadas

El diseño de este proyecto incorpora tres técnicas de ingeniería de prompts. Estas son estrategias para estructurar el pensamiento y guiar el razonamiento al momento de diseñar cada componente, especialmente cuando se trabaja con inteligencia artificial como herramienta de apoyo al desarrollo.

### Zero-Shot — Para lo que es estándar y directo

La técnica Zero-Shot aplica cuando la tarea tiene una solución obvia que no necesita ejemplos previos para ser comprendida. Funciona dando la instrucción directamente y esperando el resultado correcto de inmediato, sin necesidad de mostrar ejemplos de cómo debe verse el resultado.

En este proyecto se usó para toda la parte de definición de tablas, restricciones e índices en PostgreSQL, y para las consultas de extracción de datos. Todas son operaciones bien definidas por estándares ampliamente conocidos que no generan ambigüedad en su interpretación.

### Few-Shot — Para patrones no obvios

La técnica Few-Shot aplica cuando el resultado esperado no es intuitivo para alguien sin experiencia en ese dominio específico. Antes de describir la solución general, se muestra primero un ejemplo concreto del resultado que se quiere obtener. Ese ejemplo sirve como referencia para que quien lea el diseño entienda hacia dónde apunta la solución.

En este proyecto se usó para el diseño de los documentos de MongoDB. Alguien que viene del mundo relacional tiende a pensar en colecciones separadas vinculadas por identificadores, exactamente como haría en PostgreSQL. Sin ver primero un ejemplo del documento completo con el autor y los comentarios ya incluidos dentro de la publicación, es difícil entender cuál es el modelo correcto para MongoDB. El ejemplo concreto previo evita ese error de diseño.

### CTD (Chain-Thought-Decomposition) — Para decisiones encadenadas

La técnica CTD aplica cuando hay que tomar múltiples decisiones en secuencia, donde cada decisión depende de la anterior y no se puede saltar ningún paso sin arriesgarse a llegar a una conclusión incorrecta. La técnica obliga a razonar en voz alta paso a paso antes de llegar a la solución final.

En este proyecto se usó para diseñar la estructura de Cassandra. No es posible definir correctamente cómo guardar los datos en Cassandra sin primero definir exactamente cómo se van a consultar. Si se empieza por el resultado final sin razonar los pasos intermedios, es muy probable que se elija la organización equivocada, lo que haría que las consultas fueran lentas o que los datos no llegaran en el orden esperado. La técnica obliga a razonar en orden: primero la pregunta que se quiere responder, luego qué datos se necesitan para responderla, luego cómo organizar esos datos para que la respuesta sea eficiente.

---

## 11. Guía de Ejecución

### Lo que se necesita antes de empezar

Es necesario tener instalado Docker Desktop en el computador y tenerlo abierto antes de ejecutar cualquier comando. También es necesario tener Python versión 3.11 o superior instalado.

### Orden de ejecución

**Paso 1:** Abrir Docker Desktop y esperar a que el ícono en la barra de tareas deje de animarse. Ese es el indicador de que Docker está listo para recibir instrucciones.

**Paso 2:** Desde la carpeta raíz del proyecto, ejecutar el comando para levantar todos los servicios. Docker descargará las imágenes necesarias si es la primera vez que se ejecuta, lo cual puede tomar varios minutos dependiendo de la velocidad de internet.

**Paso 3:** Esperar aproximadamente 90 segundos. Cassandra es el servicio que más tarda en inicializar. Se puede verificar el estado de todos los contenedores con el comando correspondiente y esperar a que todos muestren el estado "healthy".

**Paso 4:** Instalar las dependencias de Python. Solo es necesario hacerlo una vez.

**Paso 5:** Ejecutar el proceso de migración desde la carpeta del módulo ETL. Este proceso extrae los datos de PostgreSQL y los carga en MongoDB, Cassandra y Redis. Si Cassandra todavía no está lista, el proceso esperará y reintentará automáticamente.

**Paso 6:** Lanzar la interfaz gráfica desde la carpeta de la interfaz. Se abrirá una ventana con el sistema completo.

### Para detener el sistema

Se puede detener todos los contenedores conservando los datos para la próxima sesión, o detenerlos y borrar todos los datos para empezar desde cero la próxima vez. Esta segunda opción es útil si se quiere probar el proceso completo desde el principio.

---

## 12. Solución de Problemas Comunes

### Docker no responde

El síntoma es un mensaje de error que dice que no puede conectarse al motor de Docker. La causa es que Docker Desktop no está abierto. La solución es buscarlo en el menú inicio del sistema operativo, abrirlo y esperar a que el ícono de la ballena en la barra de tareas deje de animarse.

### El proceso de migración falla en Cassandra

El síntoma es un mensaje que dice que no pudo conectarse. La causa más común es que Cassandra todavía no terminó de inicializar. El módulo intenta la conexión varias veces automáticamente con pausas entre intentos. Si falla después de todos los intentos, se puede verificar el estado de los contenedores y esperar a que Cassandra muestre el estado "healthy" antes de volver a intentar.

### La interfaz muestra errores al cargar datos de las bases de datos NoSQL

La causa es que el proceso de migración todavía no se ha ejecutado. MongoDB, Cassandra y Redis no tienen datos hasta que el ETL los carga. La solución es ir a la sección ETL de la interfaz y ejecutar el proceso completo primero.

### PostgreSQL dice que la contraseña es incorrecta

Este problema ocurre en Windows cuando hay una instalación local de PostgreSQL en el mismo computador. El proyecto usa el puerto 5433 en lugar del puerto estándar 5432 precisamente para evitar ese conflicto. Si el error persiste, se puede verificar que el archivo de configuración del proyecto tenga el número de puerto correcto.

### Los datos no se ven actualizados en Redis

Redis almacena los datos por un máximo de cinco minutos. Después de ese tiempo los elimina automáticamente. Para ver datos en el panel de Redis, se debe ejecutar el proceso de migración recientemente. Si el caché está vacío, la sección de Redis mostrará que no hay claves activas, lo cual es el comportamiento esperado.

# Taller 01

## 1.  *Cree un repositorio de Github en donde van a alojar el contenido del taller. Las modificaciones a ese proyecto las realizaran aquí para no alterar la versión original.*
- Se clono el Proyecto sin alterar ningun archivo del Proyecto original, con esa base se haran las actividades que se requieran
## 2.  **Revisión autocrítica**:  *Mencionen aspectos de su proyecto, relacionados con los parámetros de calidad vistos en clase (Usabilidad, Compatibilidad, Rendimiento, Seguridad), resaltando aspectos que cumplan estos parámetros y aspectos a mejorar. Incluya aspectos donde pueda aplicar inversión*
####  **Usabilidad**

####  Aspectos Positivos
- **Sistema de administración de Django**: La base del proyecto utiliza Django, proporcionando un sistema de administración robusto y usable.

####  Aspectos a Mejorar
- **Estructura de aplicaciones**: Múltiples apps innecesarias que confunden la navegación del código
- **Vistas y rutas incompletas**: Varios archivos `views.py` y `urls.py` vacíos o incompletos
- **Falta de estructura de navegación**: No existe una plantilla unificada ni flujo claro de usuario

---

###  **Compatibilidad**

####  Aspectos Positivos
- **Framework multiplataforma**: Django puede ejecutarse en distintos sistemas operativos
- **Entorno virtual**: Uso de entorno virtual para aislamiento de dependencias

####  Aspectos a Mejorar
- **Gestión de dependencias**: Falta archivo `requirements.txt` o `Pipfile` documentado
- **Compatibilidad no probada**: No se ha verificado funcionamiento en diferentes versiones de Python/Django

---

###  **Rendimiento**

####  Aspectos Positivos
- **Arquitectura ligera**: Sistema pequeño que no requiere grandes recursos
- **Despliegue inicial**: Funciona adecuadamente en servidor local y producción básica

####  Aspectos a Mejorar
- **Duplicación de código**: Estructuras innecesarias que aumentan carga de mantenimiento
- **Consultas a base de datos**: No se utilizan `select_related` 
- **Normalización de datos**: Falta de normalización puede generar redundancia futura

---

###  **Seguridad**

####  Aspectos Positivos
- **Protecciones incorporadas**: Django ofrece protección contra:
  -  CSRF (Cross-Site Request Forgery)
  -  XSS (Cross-Site Scripting) 
  -  SQL Injection

####  Aspectos a Mejorar
- **Control de acceso**: No hay manejo de autenticación ni autorización por roles
- **Validación de formularios**: Falta validación estricta y contraseñas seguras


## 3.   **Inversión de Dependencias**: *Escoja alguna clase de su proyecto y realice una inversión de dependencia según lo visto en clase. Documente bien los cambios en el repositorio.*

#### El proyecto por defecto esta muy esparcidos no tiene definidos muchas cosas basicas y para el usuario es muy complicado lidear con el pero vimos internamente que el proyecto esta violando unos de los principios por ejemolo la vista SearchView en `search/views.py` depende directamente de la carga de datos desde el archivo `search_data.json` mediante funciones concretas de utils.py. 
#### Esto genera varios problemas:
- *Alto acoplamiento:* La vista no solo se encarga de mostrar resultados, sino que también depende unicamente del archivo JSON.
- *Difícil de escalar:* Si queremos cambiar la fuente de datos, tendríamos que modificar directamente la vista.
- *Mantenimiento complicado:* Cualquier cambio en la estructura de los datos rompe la vista, afectando la estabilidad del proyecto.
#### Se implementó una interfaz abstracta DataLoader que define un contrato para cargar datos. La vista ahora depende de esta abstracción, y no de la implementación concreta. Entonces el JSONDataLoader implementa DataLoader y se encarga de cargar los datos desde search_data.json y la vista recibe un objeto que cumple con la interfaz DataLoader, invocando solo el método load_data() esto da paso a:
- *Reducción de acoplamiento:* La vista no necesita saber de dónde vienen los datos.
- *Escalabilidad:*  Se puede agregar nuevos loaders sin modificar la vista.
- *Flexibilidad:* Permite **swapping loaders** que facilita las migraciones sin la intervencion innecesaria de vistas que no el sistema no necesite.



## 4.   **Aplicación de patrón de diseño Python**: *Escoja alguno de los patrones de diseño de Python vistos en clase (puede ser más de uno) y aplíquelo en alguna de las funcionalidades de su proyecto original. Indique claramente el proceso de decisión detrás de la elección del patrón y cómo mejora la implementación usando el patrón elegido. Documente bien los cambios en el repositorio.*

### 5.   **Aplicación de patrón de Diseño Django**: *Escoja alguno de los patrones de diseño de Django vistos en clase (puede ser más de uno) y aplíquelo en alguna de las funcionalidades de su proyecto original. Indique claramente el proceso de decisión detrás de la elección del patrón y cómo mejora la implementación usando el patrón elegido. Documente bien los cambios en el repositorio. Deben implementar por lo menos dos patrones, para dos partes diferentes de la arquitectura (ejemplo: Vistas CRUD para controladores y Normalización para Modelos).*

##   **BONO**: *Implementen una nueva funcionalidad desde cero, aplicando patrones de diseño de su elección y justificando sus decisiones a la hora de incluir la funcionalidad y de aplicar los patrones escogidos.*

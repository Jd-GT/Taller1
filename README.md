# Taller 01

## 1.  *Cree un repositorio de Github en donde van a alojar el contenido del taller. Las modificaciones a ese proyecto las realizaran aquí para no alterar la versión original.*
- Se clono el Proyecto sin alterar ningun archivo del Proyecto original, con esa base se haran las actividades que se requieran
## 2.  **Revisión autocrítica**:  *Mencionen aspectos de su proyecto, relacionados con los parámetros de calidad vistos en clase (Usabilidad, Compatibilidad, Rendimiento, Seguridad), resaltando aspectos que cumplan estos parámetros y aspectos a mejorar. Incluya aspectos donde pueda aplicar inversión*
####  **Usabilidad**

#### El proyecto se construyó sobre Django, lo que ya ofrece cierta facilidad para gestionar datos gracias al panel de administración. Sin embargo, la organización actual de las aplicaciones no ayuda: hay apps duplicadas, lo que confunde tanto al desarrollador como al usuario final. Además, varias vistas y rutas están vacías o incompletas, lo que genera la sensación de que la web no está terminada y, por lo tanto, no permite al usuario cumplir el objetivo principal del sistema. 

---

###  **Compatibilidad**

#### La base en Django asegura que el proyecto puede ejecutarse en diferentes entornos con solo contar con Python. Aun así, falta un archivo `requirements.txt` para garantizar que otros desarrolladores puedan levantar el sistema. Tampoco hay pruebas documentadas en distintas versiones de Python o Django, lo que abre la posibilidad de que surjan errores si se despliega en otro entorno.

---

###  **Rendimiento**

####  Al ser un proyecto pequeño, no tiene exigencias de hardware ni de servidores potentes. Sin embargo, el rendimiento podría verse afectado en el futuro porque el código presenta duplicaciones y estructuras innecesarias. También sería recomendable optimizar las consultas a la base de datos y revisar la normalización de los modelos, ya que de lo contrario podría haber problemas de escalabilidad más adelante.

####  Aspectos a Mejorar
- **Duplicación de código**: Estructuras innecesarias que aumentan carga de mantenimiento
- **Consultas a base de datos**: No se utilizan `select_related` 

---

###  **Seguridad**

####  Django ya trae protecciones por defecto contra ataques comunes, lo cual es un punto a favor. El problema es que el proyecto no implementa mecanismos de autenticación ni autorización que controlen lo que cada tipo de usuario puede hacer. Tampoco hay validaciones estrictas en formularios ni configuraciones básicas de seguridad para un entorno de producción. Esto lo convierte en un aspecto crítico a reforzar si se piensa desplegar el sistema en un escenario real.

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


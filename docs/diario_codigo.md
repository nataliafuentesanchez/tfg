# Diario de desarrollo del codigo

## Dia 1 - Implementacion de la demo web

**Fecha:** 24 de julio de 2026  
**Proyecto:** AnalisisImagenes  
**Objetivo de esta fase:** construir una primera version funcional de una aplicacion web capaz de recibir una imagen dermatologica y devolver un resultado orientativo de riesgo.

> Esta version tiene finalidad academica y de demostracion. No realiza un diagnostico medico y no sustituye la valoracion de un dermatologo.

## 1. Que problema resuelve el proyecto

El proyecto plantea una herramienta de apoyo para analizar imagenes dermatologicas. La aplicacion permite subir una imagen desde un navegador y obtener una respuesta estructurada con:

- una clasificacion primaria: `sano` o `enfermo`;
- un nivel de gravedad: `ninguno`, `bajo`, `medio` o `peligro`;
- una estimacion de lesion `benigno_probable` o `maligno_probable`;
- una puntuacion de riesgo entre `0.0` y `1.0`;
- una recomendacion de seguimiento o derivacion dermatologica;
- un informe escrito para una persona;
- una respuesta JSON para trazabilidad tecnica.

La finalidad de esta primera fase no es crear todavia un modelo de inteligencia artificial entrenado, sino construir y comprobar todo el flujo de la aplicacion. De esta forma, cuando se entrene el modelo en una fase posterior, se podra sustituir el metodo de inferencia sin tener que rehacer la interfaz ni la API.

## 2. Arquitectura general

La aplicacion se divide en dos capas principales:

```text
Navegador
    |
    | selecciona una imagen y envia una peticion HTTP
    v
API web FastAPI
    |
    | valida el archivo y llama al servicio de inferencia
    v
Servicio de analisis
    |
    | procesa la imagen y calcula el resultado
    v
Respuesta JSON + informe legible
```

Esta separacion permite que cada parte tenga una responsabilidad concreta:

- **La interfaz** se ocupa de la experiencia de la persona usuaria.
- **La API** recibe peticiones y devuelve respuestas.
- **El servicio de inferencia** contiene la logica de analisis.
- **Los esquemas** definen la forma de los datos.
- **Las pruebas** comprueban que las partes importantes funcionan.

## 3. Tecnologias utilizadas

### Python

Python es el lenguaje principal del proyecto. Se utiliza por su amplio ecosistema para desarrollo web, procesamiento de imagenes y aprendizaje automatico.

### FastAPI

FastAPI es el framework utilizado para crear la API web. Permite definir rutas HTTP, recibir archivos, validar respuestas y generar automaticamente documentacion tecnica de la API.

En este proyecto se utilizan tres rutas principales:

- `GET /`: devuelve la interfaz web.
- `GET /health`: comprueba que el servidor esta activo.
- `POST /analyze`: recibe una imagen y ejecuta el analisis.

### Uvicorn

Uvicorn es el servidor que ejecuta la aplicacion FastAPI y la hace accesible desde el navegador mediante `http://127.0.0.1:8000/`.

### OpenCV

OpenCV se utiliza para leer y procesar las imagenes. En la version actual permite:

- convertir los bytes recibidos en una imagen;
- redimensionar la imagen para trabajar con un tamano comun;
- convertir entre espacios de color;
- calcular contraste;
- detectar zonas de color intenso;
- detectar bordes.

### NumPy

NumPy permite trabajar con la imagen como una matriz numerica. Esto facilita calcular medias, desviaciones, proporciones y otros valores utilizados por el baseline de analisis.

### Pydantic

Pydantic se utiliza mediante FastAPI para definir y validar el formato de las respuestas. Asi se garantiza que la puntuacion de riesgo, por ejemplo, siempre este dentro del intervalo permitido entre `0.0` y `1.0`.

### Pytest

Pytest se utiliza para ejecutar las pruebas automaticas del proyecto.

## 4. Explicacion de los archivos principales

### `app/main.py`

Este archivo es el punto de entrada de la aplicacion.

La funcion `create_app()` crea una instancia de FastAPI y configura:

- el titulo de la API;
- la descripcion del proyecto;
- la version actual;
- la carpeta de archivos estaticos;
- las rutas definidas en `app/api/routes.py`.

La variable `app` contiene la aplicacion que Uvicorn ejecuta con el comando `app.main:app`.

En otras palabras, este archivo conecta las distintas partes del backend y prepara el servidor.

### `app/api/routes.py`

Este archivo define las rutas HTTP y actua como punto de comunicacion entre el navegador y el backend.

#### Ruta `GET /`

Devuelve el HTML de la interfaz web. La pagina incluye:

- el titulo y la descripcion del sistema;
- un selector para elegir una imagen;
- un boton para iniciar el analisis;
- una zona para mostrar el informe legible;
- una zona para mostrar el JSON tecnico;
- un aviso de que el resultado no es un diagnostico medico.

#### Ruta `GET /health`

Devuelve:

```json
{"status": "ok"}
```

Esta ruta se utiliza para saber rapidamente si el servidor esta funcionando. Tambien puede ser util en futuras fases para monitorizacion o despliegue.

#### Ruta `POST /analyze`

Esta ruta recibe el archivo enviado desde el navegador mediante un formulario multipart.

El proceso es el siguiente:

1. FastAPI recibe el archivo.
2. El servidor lee su contenido.
3. Se comprueba que el archivo no este vacio.
4. Se llama a `analyze_image()`.
5. Si la imagen no es valida, se devuelve un error HTTP `400`.
6. Si todo es correcto, se devuelve un objeto `AnalysisResponse`.

La ruta no contiene la logica matematica del analisis. Esa responsabilidad se delega al servicio de inferencia para mantener el codigo organizado.

### `app/services/inference_service.py`

Este es el nucleo de la version actual. Contiene un baseline heuristico, es decir, un metodo inicial basado en caracteristicas visuales de la imagen y no en una red neuronal entrenada.

#### Decodificacion de la imagen

La funcion `_decode_image()` convierte los bytes recibidos en una matriz de imagen utilizando OpenCV. Si OpenCV no puede interpretar el archivo, se lanza un error indicando que el formato no es valido o que el archivo esta corrupto.

#### Extraccion de caracteristicas

La funcion `_compute_risk_score()` redimensiona la imagen a `224 x 224` pixeles y calcula varias caracteristicas:

- `red_mean`: media del canal rojo;
- `contrast`: variacion de intensidad de los pixeles;
- `hotspot_ratio`: proporcion de pixeles con valores rojos elevados;
- `edge_density`: densidad de bordes detectados mediante Canny.

Estas caracteristicas no representan todavia un diagnostico clinico. Sirven para construir un prototipo reproducible que permita probar el flujo completo.

#### Que hace exactamente el algoritmo

El algoritmo actual no compara la imagen con una base de datos ni ha aprendido sus reglas a partir de ejemplos medicos. Es un sistema determinista de puntuacion: para una misma imagen y las mismas condiciones siempre produce el mismo resultado.

El procesamiento completo es el siguiente:

1. La API recibe la imagen como una secuencia de bytes.
2. OpenCV intenta decodificar esos bytes. Si no puede hacerlo, el archivo se considera invalido.
3. La imagen se redimensiona a `224 x 224` pixeles. Esto hace que todas las imagenes entren en el calculo con el mismo tamano, aunque originalmente tengan resoluciones diferentes.
4. La imagen se convierte de BGR, que es el formato utilizado internamente por OpenCV, a RGB para analizar correctamente el canal rojo.
5. Se calcula un conjunto pequeno de caracteristicas visuales.
6. Cada caracteristica se normaliza y se multiplica por un peso concreto.
7. Las contribuciones se suman y el resultado se limita entre `0.0` y `1.0`. Ese resultado es `risk_score`.
8. La puntuacion se transforma en etiquetas mediante umbrales fijos.
9. Se genera la recomendacion, el informe legible y la respuesta JSON.

Por tanto, el codigo no afirma que una imagen tenga cancer. Lo que hace es medir algunos patrones visuales simples y convertirlos en una señal de riesgo orientativa para demostrar el funcionamiento de la aplicacion.

#### En que se basa cada caracteristica

Las caracteristicas utilizadas por el baseline son las siguientes:

- **Media del canal rojo (`red_mean`):** se calcula el promedio de la intensidad roja de todos los pixeles y se divide entre `255`. Una imagen con mas componente roja obtiene un valor mayor. En un prototipo puede servir como indicador de zonas rojizas, pero por si solo no permite distinguir una lesion ni una enfermedad.
- **Contraste (`contrast`):** se convierte la imagen a escala de grises y se calcula su desviacion estandar. Una desviacion mayor indica que hay mas variacion entre zonas claras y oscuras. El valor se normaliza dividiendolo entre `128` y se limita posteriormente a `1.0`.
- **Proporcion de zonas intensamente rojas (`hotspot_ratio`):** se cuenta que porcentaje de pixeles tiene un valor del canal rojo superior a `200`. Este valor intenta representar la presencia de zonas con color rojo intenso. En el calculo final se multiplica por `3.0` para aumentar su contribucion, pero nunca puede superar el valor normalizado `1.0`.
- **Densidad de bordes (`edge_density`):** se aplica el detector de bordes Canny con umbrales `80` y `150`. Se calcula que proporcion de pixeles ha sido identificado como borde. Una densidad alta puede representar una imagen con mas cambios o irregularidades visuales, pero no equivale directamente a un borde clinicamente irregular.

Los valores utilizados son caracteristicas globales de toda la imagen. El baseline no localiza una lesion concreta, no segmenta la piel y no identifica estructuras dermatologicas. Esta es una diferencia fundamental respecto a un futuro modelo entrenado con imagenes medicas etiquetadas.

#### Como se obtiene `risk_score`

El codigo asigna los siguientes pesos:

| Caracteristica | Peso | Interpretacion dentro del prototipo |
|---|---:|---|
| Media del rojo | `0.34` | Es la contribucion mas grande. Favorece imagenes con mayor componente rojiza. |
| Contraste | `0.28` | Aumenta el riesgo estimado cuando existe mas variacion de intensidad. |
| Zonas rojas intensas | `0.26` | Aumenta el resultado cuando hay una proporcion importante de pixeles rojos. |
| Densidad de bordes | `0.12` | Tiene la contribucion menor y representa cambios de contorno o textura. |

La suma de los pesos es `1.0`. Por ello, si todas las caracteristicas normalizadas alcanzaran su valor maximo, la puntuacion teorica tambien seria `1.0`. La funcion `numpy.clip()` garantiza que nunca se devuelva un valor fuera de `[0.0, 1.0]`.

Estos pesos no han sido aprendidos mediante entrenamiento. Son parametros definidos manualmente para crear una primera regla reproducible. En la fase de IA, los pesos y las reglas seran sustituidos o aprendidos por un modelo a partir de un conjunto de imagenes etiquetadas.

#### Como se convierten las puntuaciones en resultados

El resultado se construye en cascada:

1. **Clasificacion primaria:** si `risk_score < 0.50`, se devuelve `sano`; si `risk_score >= 0.50`, se devuelve `enfermo`.
2. **Gravedad:** se aplica la tabla de umbrales de la funcion `_severity_from_score()`. Un valor inferior a `0.50` recibe `ninguno`; a partir de ahi se asignan `bajo`, `medio` o `peligro`.
3. **Estimacion benigno/maligno:** si el riesgo es inferior a `0.75`, se devuelve `benigno_probable`; a partir de `0.75`, se devuelve `maligno_probable`. Es una estimacion interna del prototipo y no un diagnostico.
4. **Derivacion:** se marca `referral = true` si el riesgo es mayor o igual que `0.80` o si la estimacion es `maligno_probable`.
5. **Recomendacion textual:** se genera un mensaje diferente para derivacion prioritaria, revision programada o seguimiento preventivo.

Es importante observar que los umbrales de la clasificacion primaria y de la gravedad estan coordinados: un caso con `risk_score` inferior a `0.50` es `sano` y tiene gravedad `ninguno`, mientras que un caso desde `0.50` ya se considera `enfermo` y como minimo tiene gravedad `bajo`.

#### Ejemplo numerico

Si una imagen produjera los valores normalizados siguientes:

```text
red_mean = 0.40
contrast = 0.50
hotspot_ratio_normalizado = 0.30
edge_density_normalizada = 0.20
```

La puntuacion seria:

```text
risk_score = (0.34 * 0.40) + (0.28 * 0.50)
           + (0.26 * 0.30) + (0.12 * 0.20)
           = 0.378
```

Con `risk_score = 0.378`, el sistema devolveria `sano`, gravedad `ninguno`, `benigno_probable` y no recomendaria una derivacion prioritaria. Este ejemplo muestra que la salida depende de las caracteristicas calculadas y de los umbrales, no de una decision aleatoria.

#### Que significa el resultado y que no significa

El resultado significa que el baseline ha encontrado una determinada combinacion de color, contraste, zonas rojas y bordes, y que esa combinacion ha superado o no unos umbrales definidos manualmente.

El resultado no significa que:

- la imagen haya sido diagnosticada por una IA entrenada;
- se haya demostrado que la lesion sea realmente sana, enferma, benigna o maligna;
- la puntuacion sea una probabilidad clinica validada;
- el sistema pueda sustituir la revision de un dermatologo.

En el TFG debe describirse como una **clasificacion orientativa basada en reglas visuales**, creada para validar la arquitectura y el flujo de la aplicacion. La validacion clinica y el aprendizaje de los parametros corresponden a la siguiente fase.

#### Calculo de la puntuacion

Las caracteristicas se combinan mediante una suma ponderada:

```text
risk_score =
    0.34 * red_mean_normalizado
  + 0.28 * contraste_normalizado
  + 0.26 * zonas_rojas_normalizadas
  + 0.12 * densidad_de_bordes_normalizada
```

El resultado se limita al intervalo `[0.0, 1.0]`. Cuanto mayor es el valor, mayor es el riesgo estimado por este baseline.

#### Asignacion de gravedad

La funcion `_severity_from_score()` transforma la puntuacion numerica en una categoria:

| Puntuacion | Gravedad |
|---|---|
| Menor que `0.50` | `ninguno` |
| Desde `0.50` hasta menor que `0.65` | `bajo` |
| Desde `0.65` hasta menor que `0.80` | `medio` |
| Desde `0.80` | `peligro` |

El umbral de derivacion prioritaria se define como `0.80` mediante la constante `URGENT_REFERRAL_THRESHOLD`.

#### Clasificacion y recomendacion

La aplicacion considera que el caso es `enfermo` cuando la puntuacion es igual o superior a `0.50`. En los casos con mayor puntuacion se marca `maligno_probable`; en los demas se marca `benigno_probable`.

Si el riesgo alcanza `0.80` o se considera maligno probable, se recomienda una derivacion prioritaria al dermatologo. Si el riesgo es intermedio, se recomienda una revision programada. En los casos de baja alarma se indica seguimiento preventivo.

Estas categorias son orientativas y forman parte del prototipo. No deben presentarse como una prediccion clinica validada.

#### Informe para la persona usuaria

La funcion `_build_user_report()` transforma los valores tecnicos en un texto que puede entender una persona no tecnica. Esto permite mostrar dos salidas simultaneas:

- una explicacion natural para la interfaz;
- un JSON completo para documentacion, auditoria y futuras evaluaciones.

### `app/schemas/prediction.py`

Este archivo define la clase `AnalysisResponse`, que representa la respuesta oficial del endpoint `/analyze`.

El esquema incluye:

- nombre del archivo;
- etiqueta primaria;
- gravedad;
- tipo probable de lesion;
- puntuacion de riesgo;
- indicador de derivacion;
- posible causa visual;
- recomendacion;
- informe legible;
- disclaimer medico.

El esquema es importante porque evita que cada respuesta tenga una estructura diferente. Tambien facilita que en el futuro el servicio heuristico sea sustituido por un modelo de IA manteniendo el mismo contrato de salida.

### `app/static/js/app.js`

Este archivo controla el comportamiento de la interfaz en el navegador.

Cuando la persona selecciona una imagen, el nombre del archivo aparece en pantalla. Al pulsar el boton de analisis:

1. Se comprueba que exista una imagen.
2. Se crea un objeto `FormData`.
3. La imagen se envia a `/analyze` mediante `fetch()`.
4. El boton cambia temporalmente a `Analizando...`.
5. La respuesta se muestra como informe legible y como JSON.
6. Si ocurre un error, se muestra un mensaje comprensible.
7. Al terminar, el boton vuelve a su estado inicial.

### `app/static/css/styles.css`

Este archivo contiene los estilos de la interfaz. Su objetivo es que la demo resulte clara y adecuada para una presentacion academica.

Incluye:

- colores asociados a un entorno clinico;
- distribucion adaptable a ordenador y movil;
- panel para cargar la imagen;
- tarjetas de resultado;
- bloque de salida tecnica;
- estados visuales para la carga y los resultados.

El CSS esta separado del HTML para que el diseno pueda evolucionar sin modificar la logica del backend.

## 5. Pruebas automaticas

Las pruebas se encuentran en la carpeta `tests/`.

### Pruebas unitarias

`tests/unit/test_inference_service.py` comprueba:

- que las puntuaciones se convierten en los niveles de gravedad esperados;
- que el umbral de derivacion urgente es `0.80`;
- que el analisis devuelve un informe legible.

### Prueba de integracion

`tests/integration/test_health_endpoint.py` crea un cliente de prueba de FastAPI y comprueba que `GET /health` devuelve el estado correcto.

Las pruebas se ejecutan con:

```bash
./venv/bin/python -m pytest -q
```

En la comprobacion realizada durante este dia se obtuvieron cuatro pruebas superadas.

## 6. Entorno virtual y dependencias

El proyecto utiliza un entorno virtual local llamado `venv`. Su finalidad es aislar las librerias del proyecto de las librerias instaladas globalmente en el ordenador.

La preparacion inicial se realiza con:

```bash
python3 -m venv venv
./venv/bin/python -m pip install -r requirements.txt
```

El fichero `requirements.txt` fija las versiones de FastAPI, Uvicorn, OpenCV, NumPy, pandas, python-multipart, Pydantic, Pytest y HTTPX. Fijar versiones ayuda a que la aplicacion se comporte de forma reproducible.

## 7. Ejecucion de la aplicacion

En macOS o Linux se puede utilizar:

```bash
./start.sh
```

Este script:

1. crea `venv` si no existe;
2. activa el entorno virtual;
3. instala las dependencias;
4. inicia Uvicorn en `127.0.0.1:8000`.

La aplicacion se abre en:

```text
http://127.0.0.1:8000/
```

Para detener el servidor se utiliza:

```bash
./stop.sh
```

Tambien se incluyen `start.cmd` y `stop.cmd` para Windows.

## 8. Flujo completo de una peticion

El recorrido de una imagen dentro del sistema es el siguiente:

```text
1. La persona selecciona una imagen en el navegador.
2. app.js crea una peticion POST /analyze.
3. routes.py recibe el archivo.
4. routes.py comprueba que el archivo no este vacio.
5. inference_service.py decodifica la imagen con OpenCV.
6. Se calculan caracteristicas visuales.
7. Se calcula risk_score.
8. Se asignan etiqueta, gravedad y recomendacion.
9. prediction.py valida la estructura de la respuesta.
10. FastAPI devuelve el JSON.
11. app.js muestra el informe y el JSON en pantalla.
```

Este flujo demuestra que existe una separacion clara entre presentacion, comunicacion, procesamiento y validacion de datos.

## 9. Por que se ha comenzado con un baseline

Comenzar con un baseline permite validar primero la infraestructura del sistema:

- se comprueba que la interfaz puede subir archivos;
- se comprueba que la API recibe y devuelve datos;
- se prueba el formato de la respuesta;
- se verifica el funcionamiento de la recomendacion;
- se prepara una base de pruebas;
- se puede presentar una demo sin esperar a terminar el entrenamiento.

Esta decision reduce el riesgo tecnico de intentar resolver a la vez la interfaz, la API, el procesamiento de imagenes y el entrenamiento de un modelo.

## 10. Limitaciones actuales

La implementacion actual tiene las siguientes limitaciones:

- no utiliza una red neuronal entrenada;
- no ha sido validada con un dataset clinico;
- las reglas visuales no equivalen a criterios medicos;
- no se puede utilizar para diagnosticar una enfermedad;
- no se almacenan resultados en una base de datos;
- no incluye autenticacion ni integracion hospitalaria;
- la termografia queda fuera de la primera version.

Estas limitaciones deben explicarse en el TFG para diferenciar claramente entre un prototipo de apoyo y una herramienta clinica validada.

## 11. Trabajo futuro

En una siguiente fase se podra incorporar un modelo de inteligencia artificial entrenado con imagenes dermatologicas anonimizadas, por ejemplo de ISIC, HAM10000 o PAD-UFES-20, siempre revisando sus licencias y caracteristicas.

El futuro flujo sera similar al actual:

```text
imagen -> preprocesamiento -> modelo entrenado -> probabilidades -> respuesta API
```

La principal sustitucion se realizara dentro de `inference_service.py`. La interfaz, las rutas y el esquema `AnalysisResponse` podran mantenerse si el nuevo modelo devuelve los mismos campos.

Antes de utilizar un modelo con finalidad academica avanzada sera necesario evaluar:

- sensibilidad o recall de la clase enfermo;
- capacidad para detectar casos peligrosos;
- F1 macro;
- AUC ROC para benigno y maligno;
- matriz de confusion por gravedad;
- tiempo de respuesta;
- reproducibilidad de los resultados.

## 12. Conclusiones del Dia 1

Durante esta fase se ha construido una primera version ejecutable de AnalisisImagenes. La aplicacion ya permite recorrer el flujo completo desde la carga de una imagen hasta la generacion de un resultado estructurado.

El valor principal de esta etapa es haber creado una base modular y comprobable. La aplicacion funciona como un prototipo de apoyo a la decision y queda preparada para incorporar posteriormente un modelo de inteligencia artificial entrenado con imagenes reales.

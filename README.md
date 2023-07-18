**Maracaibo, julio de 2023**

# Modelo de Análisis

Este proyecto presenta el proceso de creación de un bot de Telegram con
la capacidad de recibir una o varias imágenes, retocarlas para facilitar
su legibilidad, recortarlas y modificarlas para que sus dimensiones
concuerden con las de un documento, agrupar las imágenes y enviarlas
dentro de un solo archivo PDF, facilitando el escaneo de imágenes
impresas o escritas *siempre y cuando la hoja sea lo suficientemente
distinguible del fondo donde se tomó la foto*. Es una herramienta
esencial para un estudiante, sirviendo para digitalizar trabajos,
informes, libros o algún otro material de estudio que se necesite y no
se tenga el archivo original.

# Ingeniería de Requisitos

El programa fue hecho en el lenguaje de programación Python 3.11.3, y
utilizando además la ayuda del creador de bots de Telegram
(`@BotFather`). Las funcionalidades principales de este bot y su
interfaz de usuario pueden ser accedidas con solamente conocer el nombre
de usuario del bot, por medio de comandos en el chat,
siendo fácilmente utilizable hasta por aquellos que no estén
familiarizados con la tecnología. La edición de las imágenes como tal
sucede al momento de enviarse, pero es necesario que las imágenes se
encuentren en un fondo distinguible del color de la hoja para que el bot
las detecte bien, luego procederá a aplicar las mejoras en la imagen que
luego formarán a ser parte del PDF.

Los comandos principales que utiliza el bot son los siguientes:

-   `/start` - Inicia las funciones del bot. Este comando permite que
    las funciones del bot puedan ser accedidas por el usuario, además
    que crea el token único de usuario para guardar sus archivos y que
    no se mezclen con el de otros usuarios.

-   `/pdf` - Convierte las imágenes enviadas a formato pdf. Una vez se
    hayan enviado las imágenes por medio del chat, guardará todas las
    imágenes dentro de la carpeta con el ID del usuario recibido a la
    hora de introducir el comando /start, las juntará dentro de un
    archivo PDF con las mejoras previamente aplicadas y será enviado al
    usuario.

-   `/last` - A conveniencia del usuario, el comando /last sirve para
    eliminar la última imagen enviada, de manera que no se tenga que
    borrar todo el documento para corregir algún error en el orden o en
    la captura de la imagen.

-   `/reset` - Este comando eliminará todas las imágenes en el
    documento, permitiendo empezar otra vez. Puede utilizarse para crear
    un documento nuevo, o si hubo muchos errores en la creación del
    mismo.

-   `/help` - Muestra una ventana de ayuda similar a estas
    descripciones. Ayuda al usuario a familiarizarse con las funciones
    del bot y asi pueda ser utilizado fácilmente.

Una vez instaladas las librerías y dependencias del programa, debe
empezar a ejecutarse en la computadora que se utilizará de servidor,
guardando en la ruta especificada, en la carpeta del usuario, las
imágenes que serán convertidas a PDF para luego enviarse. Como forma de
prueba, se pueden aplicar funciones para que el bot muestre el proceso
de detección, alteración y funcionalidad en la computadora host para
tener un entendimiento mayor de su funcionamiento. Siempre y cuando el
programa se encuentre corriendo en una computadora que actúe como
servidor, el programa se puede utilizar desde cualquier dispositivo que
pueda conectarse a Telegram.

# Paquetes de terceros utilizados

A continuación se lista la gran mayoría de los módulos con sus
respectivas versiones utilizadas para el desarrollo así como para la
puesta en marcha del programa.
Obtenidos de *The Python Package Index*: `https://pypi.org/` con `pip`.

    anyio==3.6.2
    certifi==2023.5.7
    click==8.1.3
    h11==0.14.0
    httpcore==0.17.2
    httpx==0.24.1
    idna==3.4
    imageio==2.31.1
    imutils==0.5.4
    lazy_loader==0.2
    mypy-extensions==1.0.0
    networkx==3.1
    numpy==1.24.3
    opencv-python==4.7.0.72
    opencv-python-headless==4.7.0.72
    packaging==23.1
    pathspec==0.11.1
    Pillow==9.5.0
    platformdirs==3.5.1
    python-telegram-bot==20.3
    PyWavelets==1.4.1
    scikit-image==0.21.0
    scipy==1.10.1
    sniffio==1.3.0
    tifffile==2023.4.12

# Instrucciones para el despliegue

1.  Debe crear su propio bot con `@BotFather` en Telegram utilizando los
    siguientes comandos:
    `/start`,
    `/newbot`,
    Escribimos el usuario del bot.
    Si el usuario del bot no está en uso recibirá la notificación de
    creación exitosa y el token en el siguiente formato:
    ` 1234567890:XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX`

3.  Acceder con el Símbolo del Sistema (`CMD`) de Windows al directorio
    contenedor del código fuente ubicado en `DocumentScanner-es/`.

4.  Instalar las librerías de terceros necesarias, con el siguiente
    comando:
    `pip install -r requirements.txt`.

5.  Colocar el token de su bot de Telegram creado con `@BotFather` en el
    archivo sin extensión `token`, el cual se encuentra en el directorio
    mencionado anteriormente.

6.  Ejecutar el bot:
    `python documentscanner/main.py`

    El cual debería generar una salida similar a la siguiente:
    `telegram.ext.Application - INFO - Application started`

Luego de seguir estos pasos, el bot estará operativo hasta que el
usuario detenga la ejecución del servidor con `Ctrl-C`.

# Muestra de funcionamiento

![image](/readme/3.jpg)
![image](/readme/5.jpg)
![image](/readme/1.jpg)
![image](/readme/2.jpg)

# Referencias

El algoritmo de "CamScanner" fue implementado de los siguientes repositorios (que aunque no tienen licencia igual se les hace mención, ya que el objetivo de este proyecto era la elaboración del bot):
* https://github.com/AdityaPai2398/CamScanner-In-Python
* https://github.com/savannahar68/CamScanner-Python/

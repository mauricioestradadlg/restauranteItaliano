import json
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from django.conf import settings


class BrevoEmailError(Exception):
    """
    Error personalizado para identificar fallos
    durante el envío de correos mediante Brevo.
    """

    pass


def enviar_correo_brevo(
    *,
    asunto,
    destinatario,
    contenido,
    nombre_destinatario="",
    responder_a=None,
):
    """
    Envía un correo mediante la API HTTPS de Brevo
    utilizando únicamente librerías estándar de Python.

    Parámetros:
        asunto:
            Asunto del correo.

        destinatario:
            Dirección de correo que recibirá el mensaje.

        contenido:
            Contenido del correo en texto plano.

        nombre_destinatario:
            Nombre opcional del destinatario.

        responder_a:
            Correo que aparecerá cuando el receptor
            presione el botón Responder.

    Retorna:
        Un diccionario con la respuesta de Brevo.

    Lanza:
        BrevoEmailError:
            Si falta configuración, ocurre un error HTTP
            o no es posible conectarse con Brevo.
    """

    # =========================================
    # VALIDACIÓN DE CONFIGURACIÓN
    # =========================================

    if not settings.BREVO_API_KEY:
        raise BrevoEmailError(
            "No se encontró la variable BREVO_API_KEY."
        )

    if not settings.BREVO_SENDER_EMAIL:
        raise BrevoEmailError(
            "No se encontró la variable BREVO_SENDER_EMAIL."
        )

    if not destinatario:
        raise BrevoEmailError(
            "No se especificó un destinatario."
        )

    # =========================================
    # CONSTRUCCIÓN DEL MENSAJE
    # =========================================

    payload = {
        "sender": {
            "name": settings.BREVO_SENDER_NAME,
            "email": settings.BREVO_SENDER_EMAIL,
        },
        "to": [
            {
                "email": destinatario,
                "name": nombre_destinatario or destinatario,
            }
        ],
        "subject": asunto,
        "textContent": contenido,
    }

    # Hace que el botón "Responder" utilice
    # el correo del usuario que llenó el formulario.
    if responder_a:
        payload["replyTo"] = {
            "email": responder_a,
        }

    # Convierte el diccionario de Python a JSON
    # y posteriormente a bytes.
    datos_json = json.dumps(
        payload,
        ensure_ascii=False,
    ).encode("utf-8")

    # =========================================
    # ENCABEZADOS DE LA PETICIÓN
    # =========================================

    encabezados = {
        "accept": "application/json",
        "content-type": "application/json",
        "api-key": settings.BREVO_API_KEY,
    }

    peticion = Request(
        url=settings.BREVO_API_URL,
        data=datos_json,
        headers=encabezados,
        method="POST",
    )

    # =========================================
    # ENVÍO A LA API DE BREVO
    # =========================================

    try:
        with urlopen(
            peticion,
            timeout=settings.BREVO_TIMEOUT,
        ) as respuesta:

            codigo_estado = respuesta.getcode()

            cuerpo_respuesta = respuesta.read().decode(
                "utf-8"
            )

    except HTTPError as error:
        # Brevo respondió, pero rechazó la solicitud:
        # API key incorrecta, remitente no verificado,
        # contenido inválido, etc.

        try:
            detalle = error.read().decode("utf-8")
        except Exception:
            detalle = str(error)

        raise BrevoEmailError(
            f"Brevo respondió con el código "
            f"{error.code}: {detalle[:500]}"
        ) from error

    except URLError as error:
        # No fue posible establecer la conexión:
        # problemas de Internet, DNS o conexión HTTPS.

        razon = getattr(
            error,
            "reason",
            str(error),
        )

        raise BrevoEmailError(
            f"No fue posible conectarse con Brevo: {razon}"
        ) from error

    except TimeoutError as error:
        raise BrevoEmailError(
            "La conexión con Brevo excedió el tiempo límite."
        ) from error

    except Exception as error:
        raise BrevoEmailError(
            f"Ocurrió un error inesperado al enviar "
            f"el correo: {error}"
        ) from error

    # =========================================
    # VALIDACIÓN DE LA RESPUESTA
    # =========================================

    if codigo_estado not in (200, 201, 202):
        raise BrevoEmailError(
            f"Brevo respondió con un código inesperado: "
            f"{codigo_estado}"
        )

    if not cuerpo_respuesta:
        return {
            "status_code": codigo_estado,
        }

    try:
        respuesta_json = json.loads(
            cuerpo_respuesta
        )

    except json.JSONDecodeError:
        respuesta_json = {
            "status_code": codigo_estado,
            "respuesta": cuerpo_respuesta,
        }

    return respuesta_json
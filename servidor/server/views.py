import logging

from django.conf import settings
from django.contrib import messages
from django.shortcuts import redirect, render

from .email_service import (
    BrevoEmailError,
    enviar_correo_brevo,
)
from .forms import ContactoForm, TrabajoForm


logger = logging.getLogger(__name__)


# =========================================
# PÁGINAS GENERALES
# =========================================

def inicio(request):
    return render(
        request,
        "server/index.html",
    )


def menu(request):
    return render(
        request,
        "server/menu.html",
    )


def nosotros(request):
    return render(
        request,
        "server/nosotros.html",
    )


def sucursales(request):
    return render(
        request,
        "server/sucursales.html",
    )


# =========================================
# FORMULARIO DE CONTACTO
# =========================================

def contacto(request):
    form = ContactoForm(
        request.POST or None
    )

    if request.method == "POST":

        # Campo oculto utilizado como protección
        # básica contra bots.
        if request.POST.get("website"):
            logger.warning(
                "Se bloqueó un posible envío automático "
                "en el formulario de contacto."
            )

            return redirect("contacto")

        if form.is_valid():
            datos = form.cleaned_data

            # Comprueba que el correo interno
            # de la empresa esté configurado.
            if not settings.EMAIL_EMPRESA:
                logger.error(
                    "No se configuró la variable "
                    "EMAIL_EMPRESA."
                )

                messages.error(
                    request,
                    "No pudimos procesar tu mensaje "
                    "en este momento. Inténtalo nuevamente.",
                )

                return render(
                    request,
                    "server/contacto.html",
                    {
                        "form": form,
                    },
                )

            email_usuario = (
                datos["email"]
                .strip()
                .lower()
            )

            email_empresa = (
                settings.EMAIL_EMPRESA
                .strip()
                .lower()
            )

            # Esta advertencia ayuda durante las pruebas.
            # Si ambos correos son iguales, ambos mensajes
            # llegarán a la misma bandeja.
            if email_usuario == email_empresa:
                logger.warning(
                    "El correo escrito por el usuario "
                    "es el mismo configurado como "
                    "EMAIL_EMPRESA. Ambos mensajes "
                    "llegarán a la misma bandeja."
                )

            # -----------------------------------------
            # CORREO INTERNO PARA LA EMPRESA
            # -----------------------------------------

            contenido_empresa = (
                "Se recibió un nuevo mensaje desde "
                "la página de contacto.\n\n"
                f"Nombre: {datos['nombre']}\n"
                f"Email: {datos['email']}\n"
                f"Asunto: {datos['asunto']}\n\n"
                "Mensaje:\n"
                f"{datos['mensaje']}\n"
            )

            try:
                enviar_correo_brevo(
                    asunto=(
                        f"[Contacto web] "
                        f"{datos['asunto']}"
                    ),

                    # Este mensaje solamente se dirige
                    # al correo interno de la empresa.
                    destinatario=(
                        settings.EMAIL_EMPRESA
                    ),

                    nombre_destinatario=(
                        "Restaurante Italiano"
                    ),

                    contenido=contenido_empresa,

                    # Al presionar Responder, la empresa
                    # responderá al usuario.
                    responder_a=datos["email"],
                )

            except BrevoEmailError as error:
                logger.exception(
                    "No se pudo enviar el correo "
                    "interno del formulario de contacto. "
                    "Detalle: %s",
                    error,
                )

                messages.error(
                    request,
                    "No pudimos enviar tu mensaje "
                    "en este momento. Inténtalo nuevamente.",
                )

                return render(
                    request,
                    "server/contacto.html",
                    {
                        "form": form,
                    },
                )

            # -----------------------------------------
            # CONFIRMACIÓN PARA EL USUARIO
            # -----------------------------------------

            contenido_confirmacion = (
                f"Hola {datos['nombre']},\n\n"
                "Gracias por contactar a "
                "Restaurante Italiano.\n\n"
                "Recibimos tu mensaje y te "
                "responderemos lo antes posible.\n\n"
                "Atentamente,\n"
                "Restaurante Italiano S.A. de C.V."
            )

            try:
                enviar_correo_brevo(
                    asunto="Recibimos tu mensaje",

                    # Esta confirmación solamente se
                    # dirige al usuario.
                    destinatario=datos["email"],

                    nombre_destinatario=(
                        datos["nombre"]
                    ),

                    contenido=(
                        contenido_confirmacion
                    ),

                    # Si el usuario responde a la
                    # confirmación, su respuesta llegará
                    # al correo de la empresa.
                    responder_a=(
                        settings.EMAIL_EMPRESA
                    ),
                )

            except BrevoEmailError as error:
                # La empresa ya recibió el formulario.
                # Por eso no se muestra un error general
                # si únicamente falla la confirmación.
                logger.exception(
                    "La empresa recibió el formulario, "
                    "pero no se pudo enviar la "
                    "confirmación al usuario. "
                    "Detalle: %s",
                    error,
                )

            messages.success(
                request,
                "Tu mensaje fue enviado correctamente.",
            )

            return redirect("contacto")

        messages.error(
            request,
            "Revisa los datos del formulario.",
        )

    return render(
        request,
        "server/contacto.html",
        {
            "form": form,
        },
    )


# =========================================
# FORMULARIO DE TRABAJO
# =========================================

def trabajo(request):
    form = TrabajoForm(
        request.POST or None
    )

    if request.method == "POST":

        # Campo oculto utilizado como protección
        # básica contra bots.
        if request.POST.get("website"):
            logger.warning(
                "Se bloqueó un posible envío automático "
                "en el formulario de trabajo."
            )

            return redirect("trabajo")

        if form.is_valid():
            datos = form.cleaned_data

            # Comprueba que el correo interno
            # de la empresa esté configurado.
            if not settings.EMAIL_EMPRESA:
                logger.error(
                    "No se configuró la variable "
                    "EMAIL_EMPRESA."
                )

                messages.error(
                    request,
                    "No pudimos procesar tu solicitud "
                    "en este momento. Inténtalo nuevamente.",
                )

                return render(
                    request,
                    "server/trabajo.html",
                    {
                        "form": form,
                    },
                )

            sucursal = dict(
                TrabajoForm.SUCURSALES
            ).get(
                datos["sucursal"],
                datos["sucursal"],
            )

            email_usuario = (
                datos["email"]
                .strip()
                .lower()
            )

            email_empresa = (
                settings.EMAIL_EMPRESA
                .strip()
                .lower()
            )

            if email_usuario == email_empresa:
                logger.warning(
                    "El correo escrito por el candidato "
                    "es el mismo configurado como "
                    "EMAIL_EMPRESA. Ambos mensajes "
                    "llegarán a la misma bandeja."
                )

            # -----------------------------------------
            # CORREO INTERNO PARA LA EMPRESA
            # -----------------------------------------

            contenido_empresa = (
                "Se recibió una nueva solicitud "
                "desde la página Trabaja con Nosotros."
                "\n\n"
                f"Nombre: {datos['nombre']}\n"
                f"Email: {datos['email']}\n"
                f"Sucursal elegida: {sucursal}\n"
            )

            try:
                enviar_correo_brevo(
                    asunto=(
                        "[Solicitud de empleo] "
                        f"{datos['nombre']} - "
                        f"{sucursal}"
                    ),

                    # Este mensaje solamente se dirige
                    # al correo interno de la empresa.
                    destinatario=(
                        settings.EMAIL_EMPRESA
                    ),

                    nombre_destinatario=(
                        "Restaurante Italiano"
                    ),

                    contenido=contenido_empresa,

                    # La empresa podrá responderle
                    # directamente al candidato.
                    responder_a=datos["email"],
                )

            except BrevoEmailError as error:
                logger.exception(
                    "No se pudo enviar el correo "
                    "interno del formulario de trabajo. "
                    "Detalle: %s",
                    error,
                )

                messages.error(
                    request,
                    "No pudimos enviar tu solicitud "
                    "en este momento. Inténtalo nuevamente.",
                )

                return render(
                    request,
                    "server/trabajo.html",
                    {
                        "form": form,
                    },
                )

            # -----------------------------------------
            # CONFIRMACIÓN PARA EL CANDIDATO
            # -----------------------------------------

            contenido_confirmacion = (
                f"Hola {datos['nombre']},\n\n"
                f"Recibimos tu solicitud para "
                f"{sucursal}.\n\n"
                "Nuestro equipo revisará la información "
                "y se pondrá en contacto contigo si "
                "existe una vacante compatible.\n\n"
                "Atentamente,\n"
                "Restaurante Italiano S.A. de C.V."
            )

            try:
                enviar_correo_brevo(
                    asunto=(
                        "Recibimos tu solicitud"
                    ),

                    # Esta confirmación solamente se
                    # dirige al candidato.
                    destinatario=datos["email"],

                    nombre_destinatario=(
                        datos["nombre"]
                    ),

                    contenido=(
                        contenido_confirmacion
                    ),

                    # Si responde, llegará a la empresa.
                    responder_a=(
                        settings.EMAIL_EMPRESA
                    ),
                )

            except BrevoEmailError as error:
                logger.exception(
                    "La empresa recibió la solicitud, "
                    "pero no se pudo enviar la "
                    "confirmación al candidato. "
                    "Detalle: %s",
                    error,
                )

            messages.success(
                request,
                "Tu solicitud fue enviada correctamente.",
            )

            return redirect("trabajo")

        messages.error(
            request,
            "Revisa los datos del formulario.",
        )

    return render(
        request,
        "server/trabajo.html",
        {
            "form": form,
        },
    )
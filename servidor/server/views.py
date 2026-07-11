

import logging

from django.conf import settings
from django.contrib import messages
from django.core.mail import EmailMessage
from django.shortcuts import redirect, render

from .forms import ContactoForm, TrabajoForm

logger = logging.getLogger(__name__)


def inicio(request):
    return render(request, "server/index.html")


def menu(request):
    return render(request, "server/menu.html")


def nosotros(request):
    return render(request, "server/nosotros.html")


def sucursales(request):
    return render(request, "server/sucursales.html")


def contacto(request):
    form = ContactoForm(request.POST or None)

    if request.method == "POST":
        if request.POST.get("website"):
            return redirect("contacto")

        if form.is_valid():
            datos = form.cleaned_data

            cuerpo = (
                "Se recibió un nuevo mensaje desde la página de contacto.\n\n"
                f"Nombre: {datos['nombre']}\n"
                f"Email: {datos['email']}\n"
                f"Asunto: {datos['asunto']}\n\n"
                "Mensaje:\n"
                f"{datos['mensaje']}\n"
            )

            try:
                EmailMessage(
                    subject=f"[Contacto web] {datos['asunto']}",
                    body=cuerpo,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[settings.EMAIL_DESTINO],
                    reply_to=[datos["email"]],
                ).send(fail_silently=False)

                EmailMessage(
                    subject="Recibimos tu mensaje",
                    body=(
                        f"Hola {datos['nombre']},\n\n"
                        "Gracias por contactar a Restaurante Italiano. "
                        "Recibimos tu mensaje y te responderemos lo antes posible.\n\n"
                        "Atentamente,\n"
                        "Restaurante Italiano S.A. de C.V."
                    ),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[datos["email"]],
                ).send(fail_silently=True)

            except Exception:
                logger.exception("No se pudo enviar el correo del formulario de contacto.")
                messages.error(
                    request,
                    "No pudimos enviar tu mensaje en este momento. Inténtalo nuevamente.",
                )
            else:
                messages.success(
                    request,
                    "Tu mensaje fue enviado correctamente. Revisa tu correo para la confirmación.",
                )
                return redirect("contacto")
        else:
            messages.error(request, "Revisa los datos del formulario.")

    return render(request, "server/contacto.html", {"form": form})


def trabajo(request):
    form = TrabajoForm(request.POST or None)

    if request.method == "POST":
        if request.POST.get("website"):
            return redirect("trabajo")

        if form.is_valid():
            datos = form.cleaned_data
            sucursal = dict(TrabajoForm.SUCURSALES).get(
                datos["sucursal"],
                datos["sucursal"],
            )

            cuerpo = (
                "Se recibió una nueva solicitud desde la página Trabaja con Nosotros.\n\n"
                f"Nombre: {datos['nombre']}\n"
                f"Email: {datos['email']}\n"
                f"Sucursal elegida: {sucursal}\n"
            )

            try:
                EmailMessage(
                    subject=f"[Solicitud de empleo] {datos['nombre']} - {sucursal}",
                    body=cuerpo,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[settings.EMAIL_DESTINO],
                    reply_to=[datos["email"]],
                ).send(fail_silently=False)

                EmailMessage(
                    subject="Recibimos tu solicitud",
                    body=(
                        f"Hola {datos['nombre']},\n\n"
                        f"Recibimos tu solicitud para {sucursal}. "
                        "Nuestro equipo revisará la información y se pondrá en contacto contigo "
                        "si existe una vacante compatible.\n\n"
                        "Atentamente,\n"
                        "Restaurante Italiano S.A. de C.V."
                    ),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[datos["email"]],
                ).send(fail_silently=True)

            except Exception:
                logger.exception("No se pudo enviar el correo del formulario de trabajo.")
                messages.error(
                    request,
                    "No pudimos enviar tu solicitud en este momento. Inténtalo nuevamente.",
                )
            else:
                messages.success(
                    request,
                    "Tu solicitud fue enviada correctamente. Revisa tu correo para la confirmación.",
                )
                return redirect("trabajo")
        else:
            messages.error(request, "Revisa los datos del formulario.")

    return render(request, "server/trabajo.html", {"form": form})
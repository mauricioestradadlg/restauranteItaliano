
from django import forms


class ContactoForm(forms.Form):
    nombre = forms.CharField(label="Nombre", max_length=120, strip=True)
    email = forms.EmailField(label="Email", max_length=254)
    asunto = forms.CharField(label="Asunto", max_length=180, strip=True)
    mensaje = forms.CharField(
        label="Mensaje",
        max_length=3000,
        strip=True,
        widget=forms.Textarea,
    )


class TrabajoForm(forms.Form):
    SUCURSALES = [
        ("monterrey", "Sucursal Monterrey"),
        ("san_pedro", "Sucursal San Pedro"),
        ("santiago", "Sucursal Santiago"),
        ("santa_catarina", "Sucursal Santa Catarina"),
        ("cumbres", "Sucursal Cumbres"),
        ("apodaca", "Sucursal Apodaca"),
        ("guadalupe", "Sucursal Guadalupe"),
        ("san_nicolas", "Sucursal San Nicolás"),
        ("escobedo", "Sucursal Escobedo"),
        ("valle_alto", "Sucursal Valle Alto"),
        ("contry", "Sucursal Contry"),
        ("linda_vista", "Sucursal Linda Vista"),
        ("san_jeronimo", "Sucursal San Jerónimo"),
        ("mitras", "Sucursal Mitras"),
        ("pueblo_serena", "Sucursal Pueblo Serena"),
        ("centro", "Sucursal Centro"),
    ]

    nombre = forms.CharField(label="Nombre completo", max_length=120, strip=True)
    email = forms.EmailField(label="Email", max_length=254)
    sucursal = forms.ChoiceField(label="Sucursal", choices=SUCURSALES)

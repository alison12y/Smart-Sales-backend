from django.contrib.auth import get_user_model
from django.db.utils import OperationalError

def run():
    User = get_user_model()
    try:
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
            print(" Superusuario 'admin' creado automáticamente.")
        else:
            print("ℹ El superusuario 'admin' ya existe.")
    except OperationalError as e:
        print(" Error al intentar crear el superusuario:", e)
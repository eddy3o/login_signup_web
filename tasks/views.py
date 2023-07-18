from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import login, logout
import re 
from tasks.models import CustomUser, Empresa
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
# Create your views here.



def home(request):
    if not request.user.is_authenticated:
        return redirect('Login/Signup')
    else:
        return render (request, 'home.html')



def loginRegistro(request):
    if request.method == 'POST':
        if 'login--' in request.POST:
            #login
            username = request.POST['username']
            password = request.POST['password']
            try:
                user = CustomUser.objects.get(username=username)
                if user.check_password(password):
                    login(request, user)
                    return redirect('Home')
                else:
                    return render(request, 'index.html', {'user_not_found': True})
            except CustomUser.DoesNotExist:
                return render(request, 'index.html', {'user_not_found': True})
        elif 'registrarse--' in request.POST:
            #registro
            username = request.POST['username']
            rut_de_la_empresa = request.POST['rut_de_la_empresa']
            rut_del_empleado = request.POST['rut_del_empleado']
            if CustomUser.objects.filter(username=username).exists() or CustomUser.objects.filter(rut_del_empleado=rut_del_empleado).exists():
                return render(request, 'index.html', {'usuario_ya_existente': True})
            elif (not Empresa.objects.filter(rut=rut_de_la_empresa).exists()) or (not bool(re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', request.POST['email']))):
                return render(request, 'index.html', {'datos_invalidos': True})
            else:
                try:
                    #creo el mensaje
                    msg = MIMEMultipart()
                    msg['From'] = 'correo.confirmacion.pagina@gmail.com'
                    msg['To'] = request.POST['email']
                    msg['Subject'] = 'Confirmación de registro'
                    #creo el mensaje, el mensaje tiene que ser profesional y no muy largo, agrega el asunto y el cuerpo del mensaje 
                    message = 'Hola, ' + request.POST['first_name'] + ' ' + request.POST['last_name'] + ',\n\n' + 'Bienvenido a nuestra página web, tu usuario es: ' + username + ' y tu contraseña es: ' + request.POST['password'] + ', por favor, no compartas esta información con nadie. Cualquier duda o consulta, puedes contactarnos a través de este mismo correo.\n\n' + 'Saludos cordiales,\n' + 'Atte. Administración de la página web.'
                    #agrego el mensaje al correo
                    msg.attach(MIMEText(message, 'plain'))
                    #creo el servidor
                    server = smtplib.SMTP('smtp.gmail.com: 587')
                    server.starttls()
                    #iniciar sesión
                    server.login(msg['From'], 'eagmfrhitbkzwpzp')
                    #enviar el mensaje
                    server.sendmail(msg['From'], msg['To'], msg.as_string())
                    server.quit()
                    #creo el usuario
                    user = CustomUser.objects.create_user(username=username, 
                                                        password= request.POST['password'],
                                                        email=request.POST['email'],
                                                        first_name=request.POST['first_name'],           
                                                        last_name=request.POST['last_name'],
                                                        rut_de_la_empresa=Empresa.objects.get(rut=rut_de_la_empresa),
                                                        rut_del_empleado=rut_del_empleado)
                    login(request, user)
                except Exception:
                    return render(request, 'index.html', {'datos_invalidos': True})
                return redirect('Home')
        else:
            return HttpResponse('Error')
    return render(request, 'index.html')



def signout(request):
    try:
        logout(request)
        return redirect('Login/Signup')
    except:
        return HttpResponse('Error al cerrar sesión')

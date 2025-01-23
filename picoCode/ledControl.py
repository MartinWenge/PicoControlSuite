import network
import socket
from time import sleep
from picozero import pico_led
import machine
import rp2
import sys

ssid = 'MagentaWLAN-YDFM'
password = '81545519344995478823'

# define LED PINs (GPIO Numbers)
led_stellwerk = machine.Pin(1,  machine.Pin.OUT)
led_fachwerk1 = machine.Pin(5,  machine.Pin.OUT)
led_fachwerk2 = machine.Pin(9,  machine.Pin.OUT)
led_schuppen  = machine.Pin(13, machine.Pin.OUT)
led_muehle    = machine.Pin(14, machine.Pin.OUT)

def connect():
    #connect to WLAN
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
    while wlan.isconnected() == False:
        if rp2.bootsel_button() == 1:
            sys.exit()
        print('Waiting for connection...')
        pico_led.on()
        sleep(0.5)
        pico_led.off()
        sleep(0.5)
    ip = wlan.ifconfig()[0]
    print(f'Connected on {ip}')
    pico_led.on()
    sleep(1)
    return ip

def open_socket(ip):
    #open a socket
    address = (ip, 80)
    connection = socket.socket()
    connection.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    connection.bind(address)
    connection.listen(1)
    return connection

def webpage():
    #Template HTML
    pinState_stellwerk = "an" if led_stellwerk.value() == 1 else "aus"
    pinState_fachwerk1 = "an" if led_fachwerk1.value() == 1 else "aus"
    pinState_fachwerk2 = "an" if led_fachwerk2.value() == 1 else "aus"
    pinState_schuppen = "an" if led_schuppen.value() == 1 else "aus"
    pinState_muehle = "an" if led_muehle.value() == 1 else "aus"
    
    html = f"""
            <!DOCTYPE html>
            <html>
            <head>
            <meta charset="UTF-8" />
            <title>Pico control page</title>
            <style>
              input[type="submit"] {{
                  margin: 10px;
                  min-width: 160px;
                  max-width: 260px;
                  height: 40px;
                  background-color: burlywood;
                  border-radius: 6px;
                  font-size: 20px;
              }}
              .grid-container {{
                  display: grid;
                  grid-template-columns: 1fr 1fr 1fr 1fr 1fr;
                  grid-template-rows: 50px 50px 50px;
                  column-gap: 10px;
                  justify-items: center;
              }}
            </style>
            </head>
            <body>
            <h1>Hallo vom Raspberry</h1>
            
            <h2>Schalter für alle Lichter</h2>
            <form action="./lighton">
            <input type="submit" value="alle Lichter an" />
            </form>
            <form action="./lightoff">
            <input type="submit" value="alle Lichter aus" />
            </form>
            
            <h2>Schalter für einzelne Lichter</h2>
            <div class="grid-container">
                <form action="./lightonstellwerk">
                    <input type="submit" value="Licht Stellwerk an" />
                </form>
                <form action="./lightonfachwerk1">
                    <input type="submit" value="Licht Fachwerkhaus 1 an" />
                </form>
                <form action="./lightonfachwerk2">
                    <input type="submit" value="Licht Fachwerkhaus 2 an" />
                </form>
                    <form action="./lightonschuppen">
                <input type="submit" value="Licht Schuppen an" />
                </form>
                    <form action="./lightonmuehle">
                <input type="submit" value="Licht Mühle an" />
                </form>

                <form action="./lightoffstellwerk">
                    <input type="submit" value="Licht Stellwerk aus" />
                </form>
                <form action="./lightofffachwerk1">
                    <input type="submit" value="Licht Fachwerkhaus 1 aus" />
                </form>
                <form action="./lightofffachwerk2">
                    <input type="submit" value="Licht Fachwerkhaus 2 aus" />
                </form>
                <form action="./lightoffschuppen">
                    <input type="submit" value="Licht Schuppen aus" />
                </form>
                <form action="./lightoffmuehle">
                    <input type="submit" value="Licht Mühle aus" />
                </form>
                
                <p>LED Stellwerk ist {pinState_stellwerk}.</p>
                <p>LED Fachwerkhaus 1 ist {pinState_fachwerk1}.</p>
                <p>LED Fachwerkhaus 2 ist {pinState_fachwerk2}.</p>
                <p>LED Schuppen ist {pinState_schuppen}.</p>
                <p>LED Mühle ist {pinState_muehle}.</p>
            </div>
            
            <h2>Allgemeine Steuerung</h2>
            <form action="./close">
            <input type="submit" value="Server anhalten" />
            </form>
            </body>
            </html>
            """
    return str(html)

def serve(connection):
    #start a web server
    pico_led.off()
    temperature = 0
    print("serve html snippet")
    while True:
        client = connection.accept()[0]
        request = client.recv(1024)
        request = str(request)
        try:
            request = request.split()[1]
        except IndexError:
            pass
        if request == '/lighton?':
            pico_led.on()
            
            led_stellwerk.value(1)
            led_fachwerk1.value(1)
            led_fachwerk2.value(1)
            led_schuppen.value(1)
            led_muehle.value(1)
        elif request =='/lightoff?':
            pico_led.off()
            
            led_stellwerk.value(0)
            led_fachwerk1.value(0)
            led_fachwerk2.value(0)
            led_schuppen.value(0)
            led_muehle.value(0)
        elif request =='/lightonstellwerk?':
            led_stellwerk.value(1)
        elif request =='/lightoffstellwerk?':
            led_stellwerk.value(0)
        elif request =='/lightonfachwerk1?':
            led_fachwerk1.value(1)
        elif request =='/lightofffachwerk1?':
            led_fachwerk1.value(0)
        elif request =='/lightonfachwerk2?':
            led_fachwerk2.value(1)
        elif request =='/lightofffachwerk2?':
            led_fachwerk2.value(0)
        elif request =='/lightonschuppen?':
            led_schuppen.value(1)
        elif request =='/lightoffschuppen?':
            led_schuppen.value(0)
        elif request =='/lightonmuehle?':
            led_muehle.value(1)
        elif request =='/lightoffmuehle?':
            led_muehle.value(0)
        elif request == '/close?':
            sys.exit()
        html = webpage()
        client.send(html)
        client.close()


try:
    ip = connect()
    connection = open_socket(ip)
    serve(connection)
except KeyboardInterrupt:
    machine.reset()

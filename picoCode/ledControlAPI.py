import network
import socket
from time import sleep
import machine
import rp2
import sys

ssid = 'MagentaWLAN-YDFM'
password = '81545519344995478823'

# define LED PINs (GPIO Numbers)
led_onboard   = machine.Pin(25, machine.Pin.OUT)
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
        led_onboard.value(1)
        sleep(0.5)
        led_onboard.value(0)
        sleep(0.5)
    ip = wlan.ifconfig()[0]
    print(f'Connected on {ip}')
    led_onboard.value(1)
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

def responseJson():
    pinState_stellwerk = "true" if led_stellwerk.value() == 1 else "false"
    pinState_fachwerk1 = "true" if led_fachwerk1.value() == 1 else "false"
    pinState_fachwerk2 = "true" if led_fachwerk2.value() == 1 else "false"
    pinState_schuppen = "true" if led_schuppen.value() == 1 else "false"
    pinState_muehle = "true" if led_muehle.value() == 1 else "false"
    
    json = f"""
            {{
                "statusStellwerk": {pinState_stellwerk},
                "statusFachwerk1": {pinState_fachwerk1},
                "statusFachwerk2": {pinState_fachwerk2},
                "statusSchuppen": {pinState_schuppen},
                "statusMuehle": {pinState_muehle}
            }}
            """
    return str(json)

def serve(connection):
    #start a web server
    led_onboard.value(0)
    temperature = 0
    print("serve API")
    while True:
        client = connection.accept()[0]
        request = client.recv(1024)
        request = str(request)
        try:
            request = request.split()[1]
        except IndexError:
            pass
        if request == '/lighton?':
            led_onboard.value(1)
            
            led_stellwerk.value(1)
            led_fachwerk1.value(1)
            led_fachwerk2.value(1)
            led_schuppen.value(1)
            led_muehle.value(1)
        elif request =='/lightoff?':
            led_onboard.value(0)
            
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
            
        response_json = responseJson()
        
        client.send("HTTP/1.1 200 OK\nContent-Type: application/json\nConnection: close\n\n")
        client.sendall(response_json)
        client.close()


try:
    ip = connect()
    connection = open_socket(ip)
    serve(connection)
except KeyboardInterrupt:
    machine.reset()


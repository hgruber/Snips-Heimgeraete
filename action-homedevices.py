#!/usr/bin/env python3

from hermes_python.hermes import Hermes, MqttOptions
from zabbix_api import ZabbixAPI
import toml, json, re, datetime, random

USERNAME_INTENTS = "hgruber"
MQTT_BROKER_ADDRESS = "localhost:1883"
MQTT_USERNAME = None
MQTT_PASSWORD = None

def user_intent(intentname):
    return USERNAME_INTENTS + ":" + intentname

def zabbix_items():
    global zapi
    sensors = {
    }
    reg = re.compile('homegear\..*\.(.*)\[(.*)\]')
    a = zapi.item.get({'output':'extend','search':{'key_':'homegear'}})
    for i in a:
        sensor = reg.sub('\\1',i['key_'])
        location = reg.sub('\\2',i['key_'])
        if sensor not in sensors: sensors[sensor] = {}
        sensors[sensor][location] = i['itemid']
    return sensors

def zabbix_query(item):
    global zapi
    a = zapi.history.get({'itemids':item, 'output':'extend', 'history':0, 'sortfield': 'clock', 'sortorder': 'DESC', 'limit':1})
    print(a)
    return a[0]['value']

def subscribe_intent_callback(hermes, intent_message):
    global sensors
    intentname = intent_message.intent.intent_name
    current_session_id = intent_message.session_id
    result_sentence = "no intent found"
    unit = {
        'temperature': 'Celsius',
        'actual_temperature': 'Celsius',
        'humidity': '%',
        'level': '%'
    }

    slots = intent_message.slots
    if slots.device: print(slots.device.first().value)

    device = ''
    if 'location' in slots and slots.location.first():
        location = slots.location.first().value
    else: location = ''
    if intentname == user_intent("sensor_query"):
        if slots.device and slots.location:
            if slots.location.first().value == 'Wohnzimmer':
                location = 'Klima Wohnzimmer'
                if slots.device.first().value == 'Temperatur':
                    device = 'temperature'
                elif slots.device.first().value == 'Luftfeuchte':
                    device = 'humidity'
            elif slots.location.first().value == 'Aussen':
                location = 'Aussen'
                if slots.device.first().value == 'Temperatur':
                    device = 'temperature'
                elif slots.device.first().value == 'Luftfeuchte':
                    device = 'humidity'
            elif slots.device.first().value == 'Temperatur':
                device = 'actual_temperature'
            elif slots.device.first().value == 'Luftfeuchte':
                device = 'humidity'
            elif slots.device.first().value == 'Status':
                device = 'level'
            else:
               device = ''
            if device in sensors:
                print(sensors[device][location])
                a = float(zabbix_query(sensors[device][location]))
                result_sentence = "Die {0} {1} beträgt {2} {3}".format(slots.device.first().value, slots.location.first().value,str(a).replace('.',','),unit[device])
            else:
                result_sentence = "Abfrage {0} {1}".format(slots.device.first().value, slots.location.first().value)
        elif (slots.device and slots.device.first().value == 'Markise') or (slots.location and slots.location.first().value == 'Terasse'):
            result_sentence = "Abfrage Markise"
        else:
            result_sentence = "Es fehlen Angaben in der Anfrage"


    elif intentname == user_intent("set_thermostat"):
        result_sentence = "Thermostat setzen"

    elif intentname == user_intent("roll") or intentname == user_intent("set_actuator"):
        if (slots.action or slots.value) and slots.location:
            result_sentence = "Ja, sehrwohl"
        elif (slots.action or slots.value) and slots.device and slots.device.first().value == 'Markise':
            result_sentence = "Ja, sehrwohl"
        else:
            result_sentence = "Ich benötige mehr Informationen, um einen Aktor zu bewegen."

    elif intentname == user_intent("calendar_query"):
        if slots.date:
            result_sentence = "Familienkalender für den {0}.{1}.".format(slots.date.first().value.day, slots.date.first().value.month)
            for attr, value in slots.date.first().__dict__.items(): print(attr, value)
        else:
            result_sentence = "Ich benötige noch eine Zeitangabe."

    elif intentname == user_intent("time_query"):
        topic = intent_message.slots.topic.first().value
        hours = datetime.datetime.now().hour
        minutes = datetime.datetime.now().minute
        year = datetime.datetime.now().year
        month = datetime.datetime.now().month
        day = datetime.datetime.now().day
        weekday = datetime.datetime.now().isoweekday()
        weekday_list = ['Montag', 'Dienstag', 'Mittwoch', 'Donnerstag', 'Freitag', 'Samstag', 'Sonntag']
        if topic == 'Zeit':
            if minutes == 0:
                minutes = ""
            if hours == 1:
                result_sentence = "ein Uhr {0} .".format(minutes)
            else:
                result_sentence = "{0} Uhr {1} .".format(hours, minutes)
            first_part = ["Gerade ist es", "Es ist jetzt", "Es ist", "Die aktuelle Zeit ist"]
            result_sentence = random.choice(first_part) + " " + result_sentence
        elif topic == 'Datum':
            result_sentence = "Heute ist {0}, der {1}.{2}.{3} .".format(weekday_list[weekday - 1], day, month, year)
        else:
            result_sentence = "Diese Funktion ist noch nicht unterstützt"

    elif intentname == user_intent("switch"):
        if not slots.action: action = 'ein'
        else: action = slots.action.first().value
        if not slots.location: location = 'Wohnzimmer'
        else: location = slots.location.first().value
        result_sentence = "Ja, ich schalte das Gerät {0} für {1} {2}".format(slots.device.first().value, location, action)

    elif intentname == user_intent("zapp"):
        result_sentence = "ich schalte den Fernseher um auf {0}".format(slots.channel.first().value)

    hermes.publish_end_session(current_session_id, result_sentence)

if __name__ == "__main__":
    snips_config = toml.load('/etc/snips.toml')
    if 'mqtt' in snips_config['snips-common'].keys():
        MQTT_BROKER_ADDRESS = snips_config['snips-common']['mqtt']
    if 'mqtt_username' in snips_config['snips-common'].keys():
        MQTT_USERNAME = snips_config['snips-common']['mqtt_username']
    if 'mqtt_password' in snips_config['snips-common'].keys():
        MQTT_PASSWORD = snips_config['snips-common']['mqtt_password']

    config = read_configuration_file("config.ini")
    zabbix = config['secret']['zabbix_api']
    zapi = ZabbixAPI(server=zabbix['url'])
    zapi.login(zabbix['user'], zabbix['passwd'])
    sensors = zabbix_items()
    print(sensors)

    mqtt_opts = MqttOptions(username=MQTT_USERNAME, password=MQTT_PASSWORD, broker_address=MQTT_BROKER_ADDRESS)
    with Hermes(mqtt_options=mqtt_opts) as h:
        h.subscribe_intents(subscribe_intent_callback).start()


#!/usr/bin/env python3

from hermes_python.hermes import Hermes, MqttOptions
import toml

USERNAME_INTENTS = "hgruber"
MQTT_BROKER_ADDRESS = "localhost:1883"
MQTT_USERNAME = None
MQTT_PASSWORD = None


def user_intent(intentname):
    return USERNAME_INTENTS + ":" + intentname


def subscribe_intent_callback(hermes, intent_message):
    intentname = intent_message.intent.intent_name

    if intentname == user_intent("sensor_query"):
        result_sentence = "Sensorabfrage"
        current_session_id = intent_message.session_id
        hermes.publish_end_session(current_session_id, result_sentence)

    elif intentname == user_intent("set_thermostat"):
        result_sentence = "Thermostat setzen"
        current_session_id = intent_message.session_id
        hermes.publish_end_session(current_session_id, result_sentence)

    elif intentname == user_intent("roll"):
        result_sentence = "Ich soll jetzt irgenwas rollen"
        current_session_id = intent_message.session_id
        hermes.publish_end_session(current_session_id, result_sentence)

    elif intentname == user_intent("calendar_query"):
        result_sentence = "Im Familienkalender finde ich momentan gar nichts"
        current_session_id = intent_message.session_id
        hermes.publish_end_session(current_session_id, result_sentence)

    elif intentname == user_intent("switch"):
        result_sentence = "Ja, ich schalte den Fernseher ein"
        current_session_id = intent_message.session_id
        hermes.publish_end_session(current_session_id, result_sentence)

    elif intentname == user_intent("set_actuator"):
        device = intent_message.slots.device.first().value
        location = intent_message.slots.location.first().value
        value = intent_message.slots.value.first().value
        result_sentence = "Ok, ich stelle jetzt den {device} im Raum {location} auf {value}".format(device=device,location=location,value=value)
        current_session_id = intent_message.session_id
        hermes.publish_end_session(current_session_id, result_sentence)

    elif intentname == user_intent("zapp"):
        result_sentence = "ich schalte um auf Pro 7"
        current_session_id = intent_message.session_id
        hermes.publish_end_session(current_session_id, result_sentence)

if __name__ == "__main__":
    snips_config = toml.load('/etc/snips.toml')
    if 'mqtt' in snips_config['snips-common'].keys():
        MQTT_BROKER_ADDRESS = snips_config['snips-common']['mqtt']
    if 'mqtt_username' in snips_config['snips-common'].keys():
        MQTT_USERNAME = snips_config['snips-common']['mqtt_username']
    if 'mqtt_password' in snips_config['snips-common'].keys():
        MQTT_PASSWORD = snips_config['snips-common']['mqtt_password']

    mqtt_opts = MqttOptions(username=MQTT_USERNAME, password=MQTT_PASSWORD, broker_address=MQTT_BROKER_ADDRESS)
    with Hermes(mqtt_options=mqtt_opts) as h:
        h.subscribe_intents(subscribe_intent_callback).start()


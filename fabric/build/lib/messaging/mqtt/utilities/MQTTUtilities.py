import time
from configuration.appConfigProvider import AppConfigProvider
from paho.mqtt import client as mqtt_client


class NebulaMQTTUtilities:
    def __init__(self):
        data_Provider = AppConfigProvider()
        self.configs = data_Provider.get_config_by_category("NEBULASTREAMER")
        self.user_name = next(f for f in self.configs if f.key == "USER_NAME")
        self.password = next(f for f in self.configs if f.key == "PASS")
        self.host_val = next(f for f in self.configs if f.key == "HOST_VAL")

    def get_client(self):
        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                print("Connected to MQTT Broker")
            else:
                print("Failed to connect return code %d \n", rc)

        host_vals = self.host_val.value.split(":")
        port = int(str(host_vals[2]))
        host_val = str(host_vals[1]).replace("//", "")
        curr_time = round(time.time() * 1000)
        client = mqtt_client.Client("nebula.rivulet-{0}".format(curr_time))
        client.username_pw_set(self.user_name.value, self.password.value)
        client.on_connect = on_connect
        client.connect(host_val, port)
        return client

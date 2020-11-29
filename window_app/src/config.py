from configparser import ConfigParser

config = ConfigParser()

config['server'] = {
    'ip':'13.125.89.118',
    'port':8081,
    'local_ip':'127.0.0.1'
}

config['reserved'] = {
    'pw':'pw',
    'login':'login',
    'signup':'signup',
    'Connected':'Connected',
    'ok':'ok',
    'closed':'closed'
}


with open('./config.ini', 'w') as f:
      config.write(f)
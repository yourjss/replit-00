#!/usr/bin/python3
import os, sys, re, glob, json, zipfile, uuid, subprocess, time

UUID = "53e8a774-b753-4716-888e-c4ea37a5aee1"

port = 443  

vlport = 15645  
vlpath = f"/{UUID}-vl"

vmport = 45123  
vmpath = f"/{UUID}-vm"

trport = 17452  
trpath = f"/{UUID}-tr"

core_name = "_"
config_name = "_.json"

c1 = {
  'log': {
    'loglevel': 'none'
  },
  'inbounds': [{
    'port': port,
    'protocol': 'vless',
    'settings': {
      'clients': [{
        'id': UUID,
        'flow': 'xtls-rprx-direct'
      }],
      'decryption':
      'none',
      'fallbacks': [{
        'path': vlpath,
        'dest': vlport
      }, {
        'path': trpath,
        'dest': trport
      }, {
        'path': vmpath,
        'dest': vmport
      }]
    },
    'streamSettings': {
      'network': 'tcp'
    }
  }, {
    'port': vlport,
    'listen': '127.0.0.1',
    'protocol': 'vless',
    'settings': {
      'clients': [{
        'id': UUID
      }],
      'decryption': 'none'
    },
    'streamSettings': {
      'network': 'ws',
      'wsSettings': {
        'path': vlpath
      }
    }
  }, {
    'port': trport,
    'listen': '127.0.0.1',
    'protocol': 'trojan',
    'settings': {
      'clients': [{
        'password': UUID
      }]
    },
    'streamSettings': {
      'network': 'ws',
      'security': 'none',
      'wsSettings': {
        'path':trpath
      }
    }
  }, {
    'port': vmport,
    'listen': '127.0.0.1',
    'protocol': 'vmess',
    'settings': {
      'clients': [{
        'id': UUID
      }]
    },
    'streamSettings': {
      'network': 'ws',
      'security': 'none',
      'wsSettings': {
        'path':vmpath
      }
    }
  }],
  'outbounds': [{
    'protocol': 'freedom'
  }]
}

if __name__ == '__main__':
  with open(os.path.join(os.getcwd(), config_name), "w", encoding='utf8') as f:
    f.write(json.dumps(c1, separators=(',', ':'), indent=2))
  # os.remove(os.path.abspath(__file__))
  zfile = glob.glob(os.path.join(os.getcwd(), "*.zip"))[0]
  with zipfile.ZipFile(zfile) as z:
      for i in z.namelist():
          if re.search(r"xray$", i):
              with open(os.path.join(os.getcwd(), core_name), 'wb') as c:
                  c.write(z.read(i))
          elif re.search(r"\.dat$", i):
              with open(os.path.join(os.getcwd(), re.search("([^/]+)$", i).group(1)), 'wb') as c:
                  c.write(z.read(i))
  os.chmod(os.path.join(os.getcwd(), core_name), 0o777, )
  subprocess.run([
    os.path.join(os.getcwd(), core_name), "run", "-c",
    os.path.join(os.getcwd(), config_name)
  ])
  print("++++++++++++++++++++++++++++++++++++++++")
  sys.exit(0)

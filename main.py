#!/usr/bin/python3
import os, sys, re, glob, json, zipfile, uuid,subprocess,time

UUID = "38ae9a72-7bd1-4b44-bade-a8cea313f8c6"  # uuid.uuid4().__str__()
ProxySite = "www.bing.com"
Port = 8800
 
vlport = 12345  # {{...}}
vmport = 13579  # {{...}}

vlpath = f"/{UUID}-vl"
vmpath = f"/{UUID}-vm"

core_name = "nginxpy"
config_name = "nginxpy.json"
nginx_conf = "nginxpy.conf"
nginx_confdir = "/etc/nginx/conf.d/"

c1 = {'log': {'loglevel': 'info'},
      'routing': {'domainStrategy': 'AsIs', 'rules': [
          {'type': 'field', 'ip': ['geoip:private'], 'outboundTag': 'block'}]},
      'inbounds': [
          {'listen': '127.0.0.1', 'port': vlport, 'protocol': 'vless',
           'settings': {'clients': [{'id': UUID}], 'decryption': 'none'},
           'streamSettings': {'network': 'ws', 'security': 'none',
                              'wsSettings': {'acceptProxyProtocol': False, 'path': vlpath}}},
          {'listen': '127.0.0.1', 'port': vmport, 'protocol': 'vmess',
           'settings': {'clients': [{'id': UUID, 'alterId': 0}], 'disableInsecureEncryption': True},
           'streamSettings': {'network': 'ws', 'security': 'none',
                              'wsSettings': {'acceptProxyProtocol': False, 'path': vmpath}}}],
      'outbounds': [{'protocol': 'freedom', 'tag': 'direct'}, {'protocol': 'blackhole', 'tag': 'block'}]}


c2 = """server {
  listen       {{Port}} default_server;
  listen       [::]:{{Port}};

  resolver 8.8.8.8:53;
  location / {
    proxy_pass https://{{ProxySite}};
    proxy_ssl_server_name on;
    proxy_redirect off;
    sub_filter_once off;
    sub_filter {{ProxySite}} $server_name;
    proxy_http_version 1.1;
    proxy_set_header Host {{ProxySite}};
    proxy_set_header Connection "";
    proxy_set_header Referer $http_referer;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header User-Agent $http_user_agent;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto https;
  }
  
  location = {{vlpath}} {
    if ($http_upgrade != "websocket") { 
        return 404;
    }
    proxy_redirect off;
    proxy_pass http://127.0.0.1:{{vlport}};
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_set_header Host $http_host;
  }

  location = {{vmpath}} {
    if ($http_upgrade != "websocket") { 
        return 403;
    }
    proxy_redirect off;
    proxy_pass http://127.0.0.1:{{vmport}};
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_set_header Host $http_host;
  }
}
"""

if __name__ == '__main__':
    print(os.getcwd(), os.listdir("/"), sep='\n')
    with open(os.path.join(os.getcwd(), config_name), "w", encoding='utf8') as f:
        f.write(json.dumps(c1,  separators=(',', ':'), indent=2))
    try:
        os.makedirs(nginx_confdir)
    except:
        pass
    with open(os.path.join(nginx_confdir, nginx_conf), "w", encoding='utf8') as f:
        for k, v in {
            r"\{\{vlpath}}": str(vlpath),
            r"\{\{vmpath}}": str(vmpath),
            r"\{\{vlport}}": str(vlport),
            r"\{\{vmport}}": str(vmport),
            r"\{\{ProxySite}}": str(ProxySite),
            r"\{\{Port}}": str(Port),
        }.items():
            c2 = re.sub(k, v, c2)
        f.write(c2)
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
    os.system("ls -all")
    print(c1,c2,sep="\n")
    os.remove(zfile)
    # os.remove(os.path.abspath(__file__))
    subprocess.Popen(
          [os.path.join(os.getcwd(), core_name),"run","-c",os.path.join(os.getcwd(), config_name)]
    )
    time.sleep(10)
    subprocess.run(["nginx","-g","daemon off;"],)
    print("++++++++++++++++++++++++++++++++++++++++")
    sys.exit(0)

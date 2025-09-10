from traitlets.config import get_config

c = get_config()

# Network and security settings for development
c.ServerApp.ip = '0.0.0.0'
c.ServerApp.port = 8888
c.ServerApp.allow_root = True
c.ServerApp.open_browser = False

# Security settings (development only!)
c.ServerApp.token = ''
c.ServerApp.password = ''
c.ServerApp.allow_origin = '*'
c.ServerApp.disable_check_xsrf = True
c.ServerApp.allow_remote_access = True

# Optional: Set default directory
c.ServerApp.root_dir = '/app'

# Optional: Enable extensions
c.ServerApp.jpserver_extensions = {'jupyterlab': True}

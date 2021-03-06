import os
import subprocess
import shutil


folder_database = 'database'
folder_viewer = 'viewer'
folder_cache = 'cache'
folder_index = 'index'

path_project = '/var/www/python/corpus-viewer'

path_data = '/data'

path_file_settings = os.path.join('/', 'settings.py')

def find_owner(filename):
    return os.stat(filename).st_uid

def main():
    id_owner = find_owner('/data_corpus')
    subprocess.run('usermod -u {} www-data'.format(id_owner), shell=True)

    print(os.getenv('folder_setting_files'))

    id_corpus = get_id()

    path_data_corpus = os.path.join(path_data, id_corpus)

    if not os.path.exists(path_data_corpus):
        os.makedirs(path_data_corpus)

    config_django_settings(id_corpus, path_data_corpus)
    config_django_urls(id_corpus)

    change_directory_database(id_corpus, path_data_corpus)

    configure_apache(id_corpus)

    subprocess.run("./setup.sh", cwd=path_project)

    subprocess.run(["python3", "manage.py", "collectstatic"], cwd=path_project+'/viewer-framework')

    subprocess.run('chown -R  www-data:www-data {}'.format(path_project), shell=True)
    subprocess.run('chown -R  www-data:www-data {}'.format(os.path.join(path_data_corpus, folder_viewer)), shell=True)

    subprocess.run('service apache2 restart', shell=True)

    endless_loop()


def endless_loop():
    # stupid hack at the moment: keep the process alive for k8s/docker
    import time
    while True:
        try:
            time.sleep(60000)
        except:
            pass

def configure_apache(id_corpus):
    list_lines = []
    with open('/etc/apache2/sites-available/000-default.conf', 'r') as f:
        for index, line in enumerate(f):
            list_lines.append(line)
                            
            if index == 10:
                list_lines.append('ServerName corpus-viewer\n')

                list_lines.append('Alias /static/ {}/viewer-framework/static/\n'.format(path_project))

                list_lines.append('Alias /favicon.ico {}/viewer-framework/static/favicon.ico\n'.format(path_project))

                list_lines.append('<Directory {}/>\n'.format(path_project))
                list_lines.append('Require all granted\n')
                list_lines.append('</Directory>\n')

                list_lines.append('<Directory /data/viewer/{}/>\n'.format(id_corpus))
                list_lines.append('Require all granted\n')
                list_lines.append('</Directory>\n')

                list_lines.append('<Directory {}/viewer-framework/viewer-framework/>\n'.format(path_project))
                list_lines.append('<Files wsgi.py>\n')
                list_lines.append('Require all granted\n')
                list_lines.append('</Files>\n')
                list_lines.append('</Directory>\n')

                list_lines.append('WSGIDaemonProcess viewer-framework python-home=/var/www/python/corpus-viewer/viewer-framework/ python-path={}/viewer-framework/\n'.format(path_project))
                list_lines.append('WSGIProcessGroup viewer-framework\n')
                list_lines.append('WSGIScriptAlias / {}/viewer-framework/viewer-framework/wsgi.py\n'.format(path_project))

    with open('/etc/apache2/sites-available/000-default.conf', 'w') as f:
        for line in list_lines:
            f.write(line)

def get_id():
    dict_settings = load_corpus_from_file(path_file_settings)

    return dict_settings['id_corpus']

def config_django_settings(id_corpus, path_data_corpus):
    path_cache = os.path.join(path_data_corpus, folder_viewer, folder_cache)
    if not os.path.exists(path_cache):
        os.makedirs(path_cache)

    path_index = os.path.join(path_data_corpus, folder_viewer, folder_index)
    if not os.path.exists(path_index):
        os.makedirs(path_index)


    list_lines = []
    is_databases = False
    with open(path_project+'/viewer-framework/viewer-framework/settings.py', 'r') as f:
        for line in f:
            if is_databases:
                if line.startswith('}'):
                    is_databases = False
            else:
                if line.startswith('DATABASES'):
                    is_databases = True
                    continue

                if line.startswith('PATH_FILES_CACHE'):
                    line = 'PATH_FILES_CACHE = "{}"'.format(path_cache)

                if line.startswith('PATH_FILES_INDEX'):
                    line = 'PATH_FILES_INDEX = "{}"'.format(path_index)

                if line.startswith('DEBUG'):
                    line = 'DEBUG = False'

                if line.startswith('DASHBOARD_AVAILABLE'):
                    continue

                list_lines.append(line)


    dict_databases = {
            'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'HOST': 'localhost',
            'PASSWORD': 'safepassword',
            'NAME': id_corpus,
            'USER': id_corpus,
        }
    }

    with open(path_project+'/viewer-framework/viewer-framework/settings.py', 'w') as f:
        for line in list_lines:
            f.write(line)

        f.write('DATABASES = {}\n'.format(dict_databases))

        f.write('STATIC_ROOT = os.path.join(BASE_DIR, \'static/\')\n'.format())

    shutil.copyfile(path_file_settings, os.path.join(path_project+'/settings', '{}.py'.format(id_corpus)))

    return id_corpus

def config_django_urls(id_corpus):
    with open(path_project+'/viewer-framework/viewer-framework/urls.py', 'w') as f:
        f.write('''
from django.conf.urls import include, url
from django.contrib import admin

urlpatterns = [
    #url(r'^admin/', admin.site.urls),
    #url(r'^', include('dashboard.urls')),
    url(r'^', include('viewer.urls')),
    #url(r'^example_app/', include('example_app.urls')),
]
        ''')


def config_django_templates():

    content = ''
    with open(path_project+'/viewer-framework/viewer/templates/viewer/header_navbar.html', 'r') as f:
        content = f.read()
        content = content.replace('url \'viewer:index\' id_corpus', 'url \'viewer:index\'')
        content = content.replace('url \'viewer:view_item\' id_corpus', 'url \'viewer:view_item\'')
        content = content.replace('url \'viewer:get_page\' id_corpus', 'url \'viewer:get_page\'')
        content = content.replace('url \'viewer:tags_export\' id_corpus', 'url \'viewer:tags_export\'')
        content = content.replace('url \'viewer:tags\' id_corpus', 'url \'viewer:tags\'')
        content = content.replace('url \'viewer:add_token\' id_corpus', 'url \'viewer:add_token\'')
        content = content.replace('url \'viewer:edit\' id_corpus', 'url \'viewer:edit\'')
        
    with open(path_project+'/viewer-framework/viewer/templates/viewer/header_navbar.html', 'w') as f:
        f.write(content)

    content = ''
    with open(path_project+'/viewer-framework/viewer/templates/viewer/index.html', 'r') as f:
        content = f.read()
        content = content.replace('url \'viewer:index\' id_corpus', 'url \'viewer:index\'')
        content = content.replace('url \'viewer:view_item\' id_corpus', 'url \'viewer:view_item\'')
        content = content.replace('url \'viewer:get_page\' id_corpus', 'url \'viewer:get_page\'')
        content = content.replace('url \'viewer:tags_export\' id_corpus', 'url \'viewer:tags_export\'')
        content = content.replace('url \'viewer:tags\' id_corpus', 'url \'viewer:tags\'')
        content = content.replace('url \'viewer:add_token\' id_corpus', 'url \'viewer:add_token\'')
        content = content.replace('url \'viewer:edit\' id_corpus', 'url \'viewer:edit\'')
        
    with open(path_project+'/viewer-framework/viewer/templates/viewer/index.html', 'w') as f:
        f.write(content)

    content = ''
    with open(path_project+'/viewer-framework/viewer/templates/viewer/table.html', 'r') as f:
        content = f.read()
        content = content.replace('url \'viewer:index\' id_corpus', 'url \'viewer:index\'')
        content = content.replace('url \'viewer:view_item\' id_corpus', 'url \'viewer:view_item\'')
        content = content.replace('url \'viewer:get_page\' id_corpus', 'url \'viewer:get_page\'')
        content = content.replace('url \'viewer:tags_export\' id_corpus', 'url \'viewer:tags_export\'')
        content = content.replace('url \'viewer:tags\' id_corpus', 'url \'viewer:tags\'')
        content = content.replace('url \'viewer:add_token\' id_corpus', 'url \'viewer:add_token\'')
        content = content.replace('url \'viewer:edit\' id_corpus', 'url \'viewer:edit\'')
        
    with open(path_project+'/viewer-framework/viewer/templates/viewer/table.html', 'w') as f:
        f.write(content)

    content = ''
    with open(path_project+'/viewer-framework/viewer/templates/viewer/tags.html', 'r') as f:
        content = f.read()
        content = content.replace('url \'viewer:index\' id_corpus', 'url \'viewer:index\'')
        content = content.replace('url \'viewer:view_item\' id_corpus', 'url \'viewer:view_item\'')
        content = content.replace('url \'viewer:get_page\' id_corpus', 'url \'viewer:get_page\'')
        content = content.replace('url \'viewer:tags_export\' id_corpus', 'url \'viewer:tags_export\'')
        content = content.replace('url \'viewer:tags\' id_corpus', 'url \'viewer:tags\'')
        content = content.replace('url \'viewer:add_token\' id_corpus', 'url \'viewer:add_token\'')
        content = content.replace('url \'viewer:edit\' id_corpus', 'url \'viewer:edit\'')
        
    with open(path_project+'/viewer-framework/viewer/templates/viewer/tags.html', 'w') as f:
        f.write(content)

def init_database(id_corpus):
    subprocess.run("""su -- postgres -c "psql -c \\\"CREATE USER {} WITH PASSWORD 'safepassword';\\\"" """.format(id_corpus), shell=True)

    subprocess.run("""su -- postgres -c "psql -c \\\"CREATE DATABASE {};\\\"" """.format(id_corpus), shell=True)

    subprocess.run("""su -- postgres -c "psql -c \\\"GRANT ALL PRIVILEGES ON DATABASE {} TO {};\\\"" """.format(id_corpus, id_corpus), shell=True)

def change_directory_database(id_corpus, path_data_corpus):
    path_database_corpus = os.path.join(path_data_corpus, folder_database)

    subprocess.run('service postgresql stop', shell=True)
    # shutil.rmtree(path_database_corpus)

    init = False
    if not os.path.exists(path_database_corpus):
        os.mkdir(path_database_corpus)
        subprocess.run('chown -R postgres:postgres {}'.format(path_database_corpus), shell=True)
        subprocess.run('su -c \'/usr/lib/postgresql/9.5/bin/initdb -D {}\' postgres'.format(path_database_corpus), shell=True)
        init = True

    list_lines = []
    with open('/etc/postgresql/9.5/main/postgresql.conf', 'r') as f:
        for line in f:
            if line.startswith('data_directory'):
                line = 'data_directory = \'{}\'\n'.format(path_database_corpus)

            list_lines.append(line)

    with open('/etc/postgresql/9.5/main/postgresql.conf', 'w') as f:
        for line in list_lines:
            f.write(line)

    subprocess.run('service postgresql start', shell=True)

    if init:
        init_database(id_corpus)

def load_corpus_from_file(file):
    with open(file, 'r') as f:
        global_env = {}
        local_env = {}

        compiled = compile(f.read(), '<string>', 'exec')
        exec(compiled, global_env, local_env)

        print('parsed settings for \'{}\''.format(file))

    return local_env['DICT_SETTINGS_VIEWER']

main()

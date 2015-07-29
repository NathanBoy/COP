import web
import json
{% if auth %}
import base64
import re
{% endif %}

# BACKEND FUNCTIONS
{% for import_object in functions_import_list -%}
from {{import_object.file}} import {{import_object.name}}
{% endfor %}

# CALLABLE OBJECTS
{% for import_object in objects_import_list -%}
from {{import_object.file}} import {{import_object.name}}
{% endfor %}

urls = (
{% for url_object in url_object_list -%}
    "{{url_object.path}}" , "{{url_object.callback}}" ,
{% endfor -%}
)

{% if auth %}
users = {{users}}
{% endif %}

class NotFoundError(web.HTTPError):
    def __init__(self,message):
        status = '404 '+message
        headers = {'Content-Type': 'text/html'}
        data = '<h1>'+message+'</h1>'
        web.HTTPError.__init__(self, status, headers, data)

class BadRequestError(web.HTTPError):
    def __init__(self,message):
        status = '400 '+message
        headers = {'Content-Type': 'text/html'}
        data = '<h1>'+message+'</h1>'
        web.HTTPError.__init__(self, status, headers, data)

class Successful(web.HTTPError):
    def __init__(self,message,info=''):
        status = '200 '+message
        headers = {'Content-Type': 'application/json'}
        data = info
        web.HTTPError.__init__(self, status, headers, data)

{% if auth %}
class basicauth:

    @classmethod
    def check(self,auth):
        if auth is not None:
            auth2 = re.sub("^Basic ","", auth)
            user,pswd = base64.decodestring(auth2).split(':')
            if user in users.keys() and pswd == users[user]:
                return True
            else:
                return False
        else:
            return False
{% endif %}

{% for callback in callback_list %}

#{{callback.path}}
class {{callback.name}}:
    {% for method in callback.method_list %}
    
    def {% filter upper %}{{method.name}}{% endfilter %}({{callback.arguments|join(', ')}}):
        {% if auth %}
        if not basicauth.check(web.ctx.env.get("HTTP_AUTHORIZATION")):
            web.header('WWW-Authenticate','Basic realm="Auth example"')
            web.ctx.status = '401 Unauthorized'
            return 'Unauthorized'
        {% endif %}
        print "{{method.printstr}}"
        {% if cors %}
        web.header('Access-Control-Allow-Origin','{{url}}')
        {% endif %}
        {% if method.web_data_body %}
        json_string=web.data() #data in body
            {% if method.json_parser %}
        json_struct=json.loads(json_string) #json parser.
        input={{method.new_object}}(json_struct) #It creates an object instance from the json_struct data."
                {% if method.response %}
        response={{callback.name}}Impl.{{method.name}}({{method.impl_arguments}}, input)
                {% else %}
        response={{callback.name}}Impl.{{method.name}}(input)
                {% endif %}
            {% else %}
            {% endif %}
        {% else %}
        response={{callback.name}}Impl.{{method.name}}({{method.impl_arguments}})
        {% endif %}
        {% for resp in method.responses %}
            {% if resp.jotason %}
        #js={} #Uncomment to create json response
            {% endif %}
        #{{resp.handleResp}} #Uncomment to handle responses
        {% endfor %}
        raise Successful('Successful operation','{"description":"{{method.printstr}}"}')
    {% endfor %}
    {% if cors %}

    def OPTIONS({{callback.arguments|join(', ')}}):
        web.header('Access-Control-Allow-Origin','{{url}}')
        web.header('Access-Control-Allow-Headers','Origin, X-Requested-With, Content-Type, Accept, Authorization')
        raise Successful('Successful operation','{"description":"Options called CORS"}')
    {% endif %}

{% endfor %}
# Chris - cvaras@itsec.cl
# -*- coding: utf-8 -*-

import stuffs
import changeconfig
import logger
import subprocess
import network
import os
import urllib

# Define Paths Production
ProdNginxEnabled = '/opt/waf/nginx/etc/sites-enabled/'
ProdNginxAvail = '/opt/waf/nginx/etc/sites-available/'
ProdModsecConf = '/opt/waf/nginx/etc/modsecurity_conf/'
ProdModsecRules = '/opt/waf/nginx/etc/modsec_rules/'
BackendProd = '/opt/waf/nginx/etc/backend/'
LogsPATH = '/opt/waf/nginx/var/log/'
ListenPATH = '/opt/waf/nginx/etc/listen/'
SslPATH = "/opt/waf/nginx/etc/ssl/"
DenyPathsDir = '/opt/waf/nginx/etc/rewrite/paths/'

def humanbytes(B):
   #Return the given bytes as a human friendly KB, MB, GB, or TB string
   #https://stackoverflow.com/questions/12523586/python-format-size-application-converting-b-to-kb-mb-gb-tb/52379087
   B = float(B)
   KB = float(1024)
   MB = float(KB ** 2) # 1,048,576
   GB = float(KB ** 3) # 1,073,741,824
   TB = float(KB ** 4) # 1,099,511,627,776

   if B < KB:
      return '{0} {1}'.format(B,'Bytes' if 0 == B > 1 else 'Byte')
   elif KB <= B < MB:
      return '{0:.2f} KB'.format(B/KB)
   elif MB <= B < GB:
      return '{0:.2f} MB'.format(B/MB)
   elif GB <= B < TB:
      return '{0:.2f} GB'.format(B/GB)
   elif TB <= B:
      return '{0:.2f} TB'.format(B/TB)

#function to validate the email in smtp test config
def email_format(test_smtp):
    if IS_EMAIL()(test_smtp.vars.dummy_field)[1] != None:
        test_smtp.errors.dummy_field = 'Invalid email format'

#validator used to check public and private key for recaptcha2 in general configuration
def captcha_validator(form):
    if form.vars.captcha == 'enabled':
        if IS_NOT_EMPTY()(form.vars.captcha_public_key)[1] != None:
            form.errors.captcha_public_key = 'Public key is needed'
        if IS_NOT_EMPTY()(form.vars.captcha_private_key)[1] != None:
            form.errors.captcha_private_key = 'Private key is needed'

@auth.requires_login()
def Media():
    
    return dict(icon="fa fa-star", page="Media icons tribute", title="Media tributing")

@auth.requires_login()
def GeneralConfig():
    db.general_config.id.readable = False
    q = db(db.general_config.id == 1).select().first()
    record = db.general_config(1)
    if q:
        form = SQLFORM(db.general_config, record, formstyle='bootstrap4_stacked')
    else:
        form = SQLFORM(db.general_config, formstyle='bootstrap4_stacked')
    if form.process(keepvalues=True, onvalidation=captcha_validator).accepted:
        response.flash = 'Configuration saved'


    labels = {'dummy_field':'Email'}
    test_smtp = SQLFORM(db.dummy, dbio=False, labels=labels,formstyle='bootstrap4_stacked')
    if test_smtp.process(keepvalues=True, onvalidation=email_format).accepted:
        mail = auth.settings.mailer
        m = mail.send(to=[test_smtp.vars.dummy_field],
          subject='WAF2Py Test Email',
          # If reply_to is omitted, then mail.settings.sender is used
          #reply_to='us@example.com',
          message='Hi there! looks like the SMTP configuration is working :)'
          )
        if m:
            response.flash = 'Email sent'
        else:
            response.flash = 'There is a problem sending the email, please check the SMTP parameters'
    #else:
    #    response.

    return dict(form=form, icon="fa fa-pencil", page="General configuration", title="Waf2Py - general configuration",test_smtp=test_smtp)

@auth.requires_login()
def Users():
    form = SQLFORM.grid(db.auth_user, searchable=False, csv=False)
    try:
        form[1][0][0]['_class'] = 'table table-bordered'
        form[1][0]['_class'] = 'table'
    except:
        pass
    
    return dict(form=form,  icon="fa fa-user-group", page="User Managament", title="Waf2Py - User Managament")

@auth.requires_login()
def SaveCRSConf():
    a = stuffs.Filtro()
    b = a.CheckStr(request.args(0))

    if b != 'YES':
        response.flash = 'Incorrect format id'
        return 'Incorrect format id'

    elif len(request.args(0)) != 40:
        response.flash = 'Incorrect length id'
        return 'Incorrect length id'

    else:
        query = db(db.production.id_rand == request.args(0)).select().first()
        if query:
            crs_path = ProdModsecRules+query.app_name+'/'
            record = ((db.rules.id_rand == query.id_rand) & (db.rules.rule_name == 'crs-setup.conf'))
            unquoted_body = urllib.parse.unquote(request.vars.body)
            db.rules.update_or_insert(record, rule_name='crs-setup.conf', id_rand=query.id_rand,body=unquoted_body)
            UpdateFiles = stuffs.CreateFiles()
            UpdateFiles.CreateModsecRule(crs_path, 'crs-setup.conf', unquoted_body)
            response.flash = 'crs setup file updated'
            #reload nginx
            stuffs.Nginx().Reload()

        else:
            return "Incorrect id"
    

@auth.requires_login()
def CRSSetupEdit():
    a = stuffs.Filtro()
    b = a.CheckStr(request.args(0))
    if b != 'YES':
        response.flash = 'Incorrect format id'
        content = None
        rule_name = ''
    elif len(request.args(0)) != 40:
        response.flash = 'Incorrect length id'
        content = None
        rule_name = ''
    else:
        query = db(db.production.id_rand == request.args(0)).select().first()
        if query:
            crs_conf = ProdModsecRules+query.app_name+'/crs-setup.conf'
            query_rule = db((db.rules.id_rand == request.args(0)) & (db.rules.rule_name == 'crs-setup.conf')).select(db.rules.body).first()
            if not query_rule:
                f = open(crs_conf, 'r')
                content = f.read()
                f.close()
            else:
                content = query_rule.body
        else:
            response.flash = "Incorrect id"
            content = None

    return dict(icon="fa fa-pencil", page="Core Rule Set Configuration", title="Waf2Py - CRS Configuration Editor", content=content, rule_name='CRS-setup.conf')

@auth.requires_login()
def SaveRule():
    a = stuffs.Filtro()
    b = a.CheckStr(request.args(0))

    if b != 'YES':
        response.flash = 'Incorrect format id'
        return 'Incorrect format id'

    elif len(request.args(0)) != 40:
        response.flash = 'Incorrect length id'
        return 'Incorrect length id'

    else:
        query = db(db.production.id_rand == request.args(0)).select().first()
        if query:
            rule_name = request.args(1).upper()+'.conf'
            rules_path = ProdModsecRules+query.app_name+'/rules/'
            rules = os.listdir(rules_path)
            print(query.id_rand)
            if rule_name in rules:
                record = ((db.rules.id_rand == query.id_rand) & (db.rules.rule_name == request.args(1).upper()))
                unquoted_body = urllib.parse.unquote(request.vars.body)
                db.rules.update_or_insert(record, body=unquoted_body)
                UpdateFiles = stuffs.CreateFiles()
                UpdateFiles.CreateModsecRule(rules_path, rule_name, unquoted_body)
                response.flash = 'Rule updated'
                #reload nginx
                stuffs.Nginx().Reload()
            else:
                response.flash = "Rule doesn't exist"
                return "Rule doesn't exist"

        else:
            response.flash = 'Incorrect id' 
            return "Incorrect id"

@auth.requires_login()
def RuleEdit():
    a = stuffs.Filtro()
    b = a.CheckStr(request.args(0))
    if b != 'YES':
        response.flash = 'Incorrect format id'
        content = None
        rule_name = ''

    elif len(request.args(0)) != 40:
        response.flash = 'Incorrect length id'
        content = None
        rule_name = ''
    
    else:
        query = db(db.production.id_rand == request.args(0)).select().first()
        if query:
            rule_name = request.args(1).upper()+'.conf'
            rules_path = ProdModsecRules+query.app_name+'/rules/'
            rules = os.listdir(rules_path)
            if rule_name in rules:
                query_rule = db((db.rules.id_rand == request.args(0)) & (db.rules.rule_name == request.args(1).upper())).select(db.rules.body).first()
                #print('query rule')
                #print(query_rule)
                try:
                    #cause an error if query.body is None
                    query_rule.body.upper() #just forcing an error if is None and jump to the exception
                    content = query_rule.body
                    #print('rule come from db')
                    
                except:
                    f = open(rules_path+rule_name, 'r')
                    content = f.read()
                    f.close()
                    #print('rule come from file rule')
            else:
                session.flash = "Rule doesn't exist"
                content = None
                rule_name = ''
        else:
            session.flash = "Incorrect id"
            content = None
            rule_name = ''
            
    return dict(icon="fa fa-pencil", page="Rule editor", title="Waf2Py - Rule editor", content=content, rule_name=rule_name)

@auth.requires_login()
def GetActiveConnections():
    connections = {}
    data = []
    cmd="sudo lsof -a -i4 -i6 -itcp | grep 'ESTABLISHED' | awk '{print $9}'"
    direct_output = subprocess.check_output(cmd, shell=True)
    c = direct_output.splitlines()
    for cc in c:
         data.append([str(cc, 'utf-8').split('->')[0], str(cc, 'utf-8').split('->')[1]])

    return response.json({'total': len(c), 'connections':data})


@auth.requires_login()
def ActiveConnections():
    direct_output = subprocess.check_output('ls', shell=True)

    return dict(page="Active connections", icon="fa fa-arrows", title="",)

@auth.requires_login()
def ManageAllRules():
    import os
    import stuffs

    a = stuffs.Filtro()

    b = a.CheckStr(request.vars['id'])
    if b == 'NO':
        logger.Logger.NewLogError(db2, auth.user.username, "Manage all rules: Invalid characters in data received - Debug: %s" %(b))

    if b == 'YES':
        rules_enabled = 'ls /opt/waf/nginx/etc/modsec_rules/'+query[0]['app_name']+'/enabled_rules | grep  ".conf$" | sed "s/.conf//g"'
        r = subprocess.Popen(rules_enabled, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        rules_that_exist,rules_that_exist_err = r.communicate()
        rules_that_exist = rules_that_exist.replace("REQUEST-901-INITIALIZATION\n","")


    return dict()


@auth.requires_login()
def ManageRules():
    import stuffs
    
    a = stuffs.Filtro()
    reload_waf = stuffs.Nginx()
    b = ''
    c = ''
    try:
        b = a.CheckStr(request.vars['id'])
        c = a.CheckRuleName(request.vars['rule'])

    except:

        logger.Logger.NewLogError(db2, auth.user.username, "Manage rules: Invalid characters in data received - Debug: %s %s %s" %(b,c,d))

    if b == 'YES' and c == 'YES' and request.vars['action'] in ['On','Off']:
        query = db(db.production.id_rand == request.vars['id']).select(db.production.app_name)
        if query:
            rulest_that_exist = 'cat /opt/waf/nginx/etc/modsec_rules/'+query[0]['app_name']+'/rules.list'
            #Check if rule exist in rules.list
            f = open('/opt/waf/nginx/etc/modsec_rules/'+query[0]['app_name']+'/rules.list')
            for x in f:
                x = x.replace('\n','')
                if request.vars['rule'] == x:
                    q = db((db.rules.id_rand == request.vars['id']) & (db.rules.rule_name == request.vars['rule'])).select()
                    rule = request.vars['rule'] + ".conf"
                    if request.vars['action'] == 'On':

                        os.system('cp /opt/waf/nginx/etc/modsec_rules/%s/rules/%s /opt/waf/nginx/etc/modsec_rules/%s/enabled_rules/%s' %(query[0]['app_name'],rule,query[0]['app_name'],rule))
                        reload_waf.Reload()

                    else:
                        os.system('rm /opt/waf/nginx/etc/modsec_rules/%s/enabled_rules/%s' %(query[0]['app_name'],rule))
                        reload_waf.Reload()
                    if q:
                        db((db.rules.id_rand == request.vars['id']) & (db.rules.rule_name == request.vars['rule'])).update(status=request.vars['action'])
                    else:
                        db.rules.insert(id_rand=request.vars['id'],
                                        rule_name=request.vars['rule'],
                                        status=request.vars['action']
                                       )
                    logger.Logger.NewLogApp(db2, auth.user.username, "Manage rules: Rule: "+request.vars['rule'] + " "+ request.vars['action'])
                    msg = 'Done'
                    break

    else:
        msg = "Manage rules: Invalid characters in data received - Debug: %s %s %s" %(b,c,d)
        logger.Logger.NewLogError(db2, auth.user.username, "Manage rules: Invalid characters in data received - Debug: %s %s %s" %(b,c,d))

    return msg

@auth.requires_login()
def index():
    return dict(page="Welcome", icon="", title="")

def user():
    session.enabled = 'active'
    session.disabled = ''
    session.e_expanded = 'true'
    session.d_expanded = 'false'
    return dict(form=auth())

@auth.requires_login()
def Dashboard():
    import psutil

    #RAM usage
    ram_percent = psutil.virtual_memory().percent
    ram_used = humanbytes(psutil.virtual_memory().used)
    ram_total = humanbytes(psutil.virtual_memory().total)
    ram_free = humanbytes(psutil.virtual_memory().free)
    
    #SWAP Usage
    swap_total = humanbytes(psutil.swap_memory().total)
    swap_used = humanbytes(psutil.swap_memory().used)
    swap_free = humanbytes(psutil.swap_memory().free)
    swap_percent = psutil.swap_memory().percent
    
    #DISK Usage
    disk = psutil.disk_usage('/')
    disk_total = humanbytes(disk.total)
    disk_used = humanbytes(disk.used)
    disk_free = humanbytes(disk.free)
    disk_percent = disk.percent
    
    #CPU Usage
    cpu_percent = psutil.cpu_percent()
    
    #summary per app
    stats = []
    row = db(db.summary).select()
    for r in row:
        stats.append({'app_name':r.app_name, 'id_rand':r.id_rand,'critical':r.critical, 'warning':r.warning, 'notice':r.notice, 'error':r.error, 'total_requests':r.total_requests})

    
    
    return dict(page="Dashboard", icon="fa fa-bar-chart", title="", swap_percent=swap_percent, swap_free=swap_free, swap_total=swap_total, swap_used=swap_used,ram_percent=ram_percent, ram_free=ram_free, ram_total=ram_total, ram_used=ram_used, cpu_percent=cpu_percent, disk_total=disk_total, disk_used=disk_used, disk_free=disk_free, disk_percent=disk_percent, summary=stats,)



@auth.requires_login()
def reload():
    a = stuffs.Nginx()
    r = a.Reload()

    return r


@auth.requires_login()
def start():
    a = stuffs.Nginx()
    r = a.Start()
    return r

@auth.requires_login()
def stop():
    a = stuffs.Nginx()
    r = a.Stop()
    return r

@auth.requires_login()
def check():
    a = stuffs.Nginx()
    r = a.SyntaxCheck()
    return r

@auth.requires_login()
def Manage():
    return dict(icon="mdi mdi-engine", page="Manage the Engine", title="Start/Reload/Stop the Engine")

@auth.requires_login()
def ProdEdit():
    import os
    a = stuffs.Filtro()
    b = a.CheckStr(request.args[0])

    if b == 'YES':
        query = db(db.production.id_rand == request.args[0]).select(db.production.nginx_conf_data,
                                                                db.production.modsec_conf_data,
                                                                db.production.id_rand,
                                                                db.production.app_name,
                                                                db.production.backend_ip_http,
                                                                db.production.backend_ip_https,
                                                                db.production.listen_ip,
                                                                db.production.ports_http,
                                                                db.production.ports_https,
                                                                db.production.extra_headers,
                                                                db.production.paths_denied,
                                                                )
        query2 = db(db.system).select(db.system.iface_ip, db.system.used_by)
        certificate = None
        if db(db.certificate.id_rand == request.args[0]).isempty() == False:
            certificate = db(db.certificate.id_rand == request.args[0]).select(db.certificate.cert,
                                                                                db.certificate.chain,
                                                                                db.certificate.privkey,
                                                                                db.certificate.protocol,
                                                                                db.certificate.prefer_cipher,
                                                                                db.certificate.ciphers)


        if query[0]['app_name']:
            #Create a dict with the status of the rules
            rule_state=db(db.rules.id_rand == request.args[0]).select()
            r_states = {}
            for x in rule_state:
                r_states[x['rule_name'].lower()] = x['status']

            rule_list = []
            #here we create a list of the rules that exist in rules folder, this is made it to to avoid tamper in the name of the rule parameter when the rules is enabled or disabled.
            #rules_base = 'ls /opt/waf/nginx/etc/modsec_rules/'+query[0]['app_name']+'/rules | grep  ".conf$" | cut -d "-" -f3,4,5,6,7,8 | sed "s/-/ /g" | sed "s/.conf//g"'
            rules_base = 'ls /opt/waf/nginx/etc/modsec_rules/'+query[0]['app_name']+'/rules | grep  ".conf$" | sed "s/.conf//g"'
            r = subprocess.Popen(rules_base, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            rules_that_exist,rules_that_exist_err = r.communicate()

            #Remove list if exist
            os.system('rm /opt/waf/nginx/etc/modsec_rules/'+query[0]['app_name']+'/rules.list')

            #Create an empty file
            os.system('touch /opt/waf/nginx/etc/modsec_rules/'+query[0]['app_name']+'/rules.list')
            #print(rules_that_exist)
            f = open('/opt/waf/nginx/etc/modsec_rules/'+query[0]['app_name']+'/rules.list', 'w')

            for i in rules_that_exist.splitlines():
                    f.write(str(i).replace("b'","").replace("'",""))
                    f.write('\n')
                    rule_list.append(str(i).replace("b'","").replace("'",""))
            f.close()
            return dict(r_states=r_states, rule_list=rule_list, query=query, query2=query2, certificate=certificate, page="Editing "+query[0]['app_name'], icon="fa fa-pencil", title="Modify the configuration")

    else:
        response.flash = 'Error in data supplied'
        redirect(URL('Websites'))




@auth.requires_login()
def basic_conf():
    grid = SQLFORM.grid(db.basic_conf, csv=False)
    return dict(grid=grid)



@auth.requires_login()
def Websites():
    links = ((
            lambda row: TAG.a(' ', _href=URL('default', 'WafLogs/' + str(row.id_rand)), target="callback-command", _class='btn btn-link glyphicon glyphicon-search')),(
            lambda row: TAG.a(' ', _href=URL('default', 'CheckProd/' + str(row.id_rand)), target="callback-command", _class='btn btn-info glyphicon glyphicon-check')),
            (lambda row: TAG.a(' ', _href=URL('default', 'ProdEdit/' + str(row.id_rand)), target="callback-command", _class="btn btn-info glyphicon glyphicon-pencil")),
            (lambda row: TAG.a(' ', _href=URL('default', 'EnableApp/' + str(row.id_rand)), target="callback-command", _class="btn btn-success glyphicon glyphicon-play")),
            (lambda row: TAG.a(' ', _href=URL('default', 'DisableApp/' + str(row.id_rand)), target="callback-command", _class="btn btn-warning glyphicon glyphicon-stop")),
            (lambda row: TAG.a(' ', _href=URL('default', 'DeleteApp/' + str(row.id_rand)), target="callback-command", _class="btn btn-danger glyphicon glyphicon-trash")),
             )
    headers = {'production.app_name': 'Name'}
    fields = [db.production.app_name,db.production.listen_ip, db.production.autor, db.production.id_rand, db.production.enabled]
    # Disable some camps in grid
    db.production.id_rand.writable = False
    db.production.id_rand.readable = False
    db.production.id_rand.writable = False
    db.production.id_rand.readable = False
    grid = SQLFORM.grid(db.production, links=links, headers=headers, details=False,fields=fields,searchable=False, csv=False, create=False, editable=False, deletable=False)
    enabled_counter = db(db.production.enabled == 'Enabled').count()
    disabled_counter = db(db.production.enabled == 'Disabled').count()
    query = db(db.production).select(db.production.app_name, db.production.name, db.production.app_name, db.production.backend_ip_http,
                                     db.production.backend_ip_https, db.production.listen_ip, db.production.mode, db.production.enabled, db.production.listening, db.production.id_rand)



    if enabled_counter <= disabled_counter:
        disabled_tab = 'active'
        disabled_exp = 'true'
        enabled_tab = ''
        enabled_exp = 'false'
    else:
        disabled_tab = ''
        disabled_exp = 'false'
        enabled_tab = 'active'
        enabled_exp = 'true'


    return dict(query=query, page="Websites", icon="fa fa-cloud", title="", enabled=enabled_counter, disabled=disabled_counter,
                disabled_tab=disabled_tab,disabled_exp=disabled_exp,enabled_exp=enabled_exp,enabled_tab=enabled_tab)




@auth.requires_login()
def DeleteApp():
    import os
    import subprocess
    import stuffs

    a = stuffs.Filtro()
    try:
        b = a.CheckStr(request.args[0])
    except:
        b = 'NO'

    if b == 'YES':

        query = db(db.production.id_rand == request.args[0]).select(db.production.app_name, db.production.vhost_id, db.production.listen_ip)
        # Remove symbolic links in /opt/waf/nginx/etc/sites-enabled/
        subprocess.Popen(['rm', ProdNginxEnabled + query[0]['app_name'] + '_nginx.conf'],
                                           stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # Remove sites in /opt/waf/nginx/etc/sites-available/
        subprocess.Popen(['rm', ProdNginxAvail + query[0]['app_name'] + '_nginx.conf'],
                                           stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # Remove modsecurity conf in /opt/waf/nginx/etc/modsecurity_conf/
        subprocess.Popen(['rm',  ProdModsecConf + query[0]['app_name'] + '_modsec.conf'],
                                           stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # Remove modsecurity conf in /opt/waf/nginx/etc/modsec_rules/ **not working****
        os.system('rm -r %s%s' %(ProdModsecRules, query[0]['app_name']))

        #Remove Backend file
        subprocess.Popen(['rm', BackendProd + query[0]['app_name']+'.conf'],
                                           stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        #Remove Listen file
        subprocess.Popen(['rm', '-r', ListenPATH + query[0]['app_name']],
                                           stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        #Remove Logs associated
        subprocess.Popen(['rm', '-r', LogsPATH + query[0]['app_name']],
                                           stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        #Remove rewrite config associated
        subprocess.Popen(['rm', '-r', DenyPathsDir + query[0]['app_name']],
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        

        #remove logrotation conf
        subprocess.Popen(['sudo', 'chown', 'www-data.www-data', '/home/www-data/waf2py_community/applications/Waf2Py/logrotation.d/%s.conf' %(query[0]['app_name'])], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        subprocess.Popen(['rm', '/home/www-data/waf2py_community/applications/Waf2Py/logrotation.d/%s.conf' %(query[0]['app_name'])],
                                           stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        #Remove ssl folder associated
        subprocess.Popen(['rm', '-r', SslPATH + query[0]['app_name']],
                                           stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        #delete rules status of this app
        db(db.rules.id_rand == request.args[0]).delete()
        #delete certificates
        db(db.certificate.id_rand == request.args[0]).delete()
        #delete summary 
        db(db.summary.id_rand == request.args[0]).delete()
        db(db.log_size.id_rand == request.args[0]).delete()
        #delete entry in db
        db(db.production.id_rand == request.args[0]).delete()
        #update status of the virtual ips
        is_used = db(db.system.iface_ip == query[0]['listen_ip']).select(db.system.used_by)
        if is_used:
            if is_used[0]['used_by'] == query[0]['app_name']:
                db(db.system.iface_ip == query[0]['listen_ip']).update(available='Available', used_by=None)
            else:
                is_used_update = is_used[0]['used_by'].replace(", " + query[0]['app_name'], "")
                is_used_update = is_used_update.replace(query[0]['app_name'] + ", ", "")
                is_used_update = is_used_update.replace(query[0]['app_name'], "")
                db(db.system.iface_ip == query[0]['listen_ip']).update(used_by=is_used_update)


        #reload nginx
        a = stuffs.Nginx()
        r = a.Reload()
        if r == "Reload Succesfull":
            resp = 'Application was'+ query[0]['app_name']  +'deleted'
            logger.Logger.NewLogApp(db2, auth.user.username, 'Application was'+ query[0]['app_name']  +'deleted')
            logger.Logger.NewLogApp(db2, auth.user.username, r)
        else:
            resp = r
        logger.Logger.NewLogApp(db2, auth.user.username, "Delete app " + query[0]['app_name'])
        response.flash = resp
        session.disabled = ''
        session.d_expanded = 'false'
        session.enabled = 'active'
        session.e_expanded = 'true'
        redirect(URL('Websites'))

    else:
        redirect(URL('Websites'))

    return locals()


@auth.requires_login()
def CreateNewApp():
    try:
        if request.vars['app_url'] != '' and len(request.vars['app_url']) < 45 and  request.vars['name'] != '' and len(request.vars['name']) < 45:
            AppName = request.vars['app_url']
            # Check if url contains dangerous character
            if any(c in AppName for c in "\"/'\;,=%#$*()[]?¿¡{}:!|&<>¨~°^ "):
                logger.Logger.NewLogError(db2, auth.user.username, "Add new app: Invalid characters in application URL")
                session.flash = 'Invalid characters found'
            # Check if name contains dangerous character
            elif any(c in request.vars['name'] for c in "\"/'\;,=%#$*()[]?¿¡{}:!|&<>¨~°^ "):
                logger.Logger.NewLogError(db2, auth.user.username, "Add new app: Invalid characters in application Name")
                session.flash = 'Invalid characters found'


            elif AppName[-1] == '.':
                logger.Logger.NewLogError(db2, auth.user.username, "Application url cannot end with dot(.)")
                session.flash = 'Application url cannot end with dot(.)'


            elif AppName.startswith('https:'):
                logger.Logger.NewLogError(db2, auth.user.username, "Application url cannot start with https://")
                session.flash = 'Application url cannot start with https://'

            elif AppName.startswith('http:'):
                logger.Logger.NewLogError(db2, auth.user.username, "Application url cannot start with http://")
                session.flash = 'Application url cannot start with http://'


            else:
                #check if app already exist in production
                query = db(db.production.app_name == AppName).select(db.production.app_name)
                if query:
                    session.flash = 'This Application Already Exist'


                else:
                    # Get nginx and modsecurity default conf
                    query = db(db.basic_conf).select(db.basic_conf.nginx_data_conf,
                                                      db.basic_conf.modsec3_data_conf
                                                     ).first()
                    #DataNginx = query.nginx_data_conf
                    #DataModsec = query.modsec3_data_conf

                    # Get a ramdom string for id_rand parameter
                    a = stuffs.Stuffs()
                    id_rand = a.password()

                    ##Deploy
                    app_id = db.new_app.insert(name=request.vars.name, app_name=AppName, id_rand=id_rand,max_fails='1', fail_timeout='60', autor=session['auth']['user']['username'], checked=1, deployed=0)
                    print('new app: {}'.format(app_id)) 
                    print(request.vars.name)
                    #id_app = db(db.new_app.app_name == AppName).select(db.new_app.id).first()
                    
                    db(db.new_app.id==app_id).update(vhost_id=app_id)
                    #id_app = db(db.new_app.app_name == AppName).select(db.new_app.id).first()
                    #modify the configuration
                    lista_nginx = []
                    lista_modsec = []


                    #Modify nginx configuration with new parameters
                    for line in query.nginx_data_conf.splitlines():
                        lista_nginx.append(line)
                    for line in lista_nginx:
                        if "SrvName" in line:
                            index = lista_nginx.index(line)
                            x = AppName.replace("www.", "")
                            a = line.replace("SrvNameAlias", "%s" %(x))
                            b = a.replace("SrvName", "%s" %(AppName))
                            lista_nginx[index] = b
                        #if "vhost_id" in line:
                        #    index = lista_nginx.index(line)
                        #    l = line.replace("vhost_id", "%s" %(app_id))
                        #    lista_nginx[index] = l
                        if "ModSecStatus" in line:
                            index = lista_nginx.index(line)
                            l = line.replace("ModSecStatus", "on")
                            lista_nginx[index] = l
                        #if "plbsid_id" in line:
                        #    index = lista_nginx.index(line)
                        #    l = line.replace("plbsid_id", "%s" %(app_id))
                        #    lista_nginx[index] = l
                    
                    #db(db.new_app.app_name == AppName).update(nginx_conf_data = '\n'.join(lista_nginx))
                

                    #Modify modsecurity conf with new parameters
                    for line in query.modsec3_data_conf.splitlines():
                        lista_modsec.append(line)
                        for line in lista_modsec:

                            if "SrvName" in line:
                                index = lista_modsec.index(line)
                                a = line.replace("SrvName", "%s" %(AppName))
                                lista_modsec[index] = a
                            #if "vhost_id" in line:
                            #    x = line.replace("vhost_id", "%s" %(app_id))
                            #    lista_modsec[index] = x

                        #db(db.new_app.app_name == AppName).update(modsec_conf_data = '\n'.join(lista_modsec))


                    # Update configuration
                    db(db.new_app.id==app_id).update(
                                      nginx_conf_data='\n'.join(lista_nginx),
                                      modsec_conf_data='\n'.join(lista_modsec),
                                     )
                    db.commit()
                    session.flash = 'Application created'
               

        else:
            if len(request.vars['app_url']) > 45:
                session.flash = 'App Name too long'
                logger.Logger.NewLogError(db2, auth.user.username, "Create app: App Name too long ")
                


            elif request.vars['app_url'] == '':
                session.flash = 'You must enter a name'
                logger.Logger.NewLogError(db2, auth.user.username, "Create app: you must enter a name ")

    

    except Exception as e:
        logger.Logger.NewLogError(db2, auth.user.username, str(e))
        session.flash = str(e)

    return redirect(URL('new_app'))



@auth.requires_login()
def deploy():
    a = stuffs.Filtro()
    b = a.CheckStr(request.args[0])
    if b == 'YES':
        query = db(db.new_app.id_rand == request.args[0]).select().first()
        AppName = query.app_name
        #if query[0]['checked'] == 1 :

        app_id = db.production.insert(app_name=query.app_name,
                             description=query.description,
                             modsec_conf_data=query.modsec_conf_data,
                             id_rand=query.id_rand,
                             autor=query.autor,
                             max_fails=query.max_fails,
                             fail_timeout=query.fail_timeout,
                             backend_ip=query.backend_ip,
                             name=query.name,
                             enabled='Disabled',
                             )
        nginx_conf_data = query.nginx_conf_data.replace('vhost_id', str(app_id)).replace('plbsid_id', str(app_id))
        #modsec_conf_data = query.modsec_conf_data.replace('vhost_id', str(app_id))
        db(db.production.id == app_id).update(vhost_id=app_id, plbsid_id=app_id, nginx_conf_data=nginx_conf_data)
        
        #Create Nginx default conf for new App
        CreateNginx = stuffs.CreateFiles()
        
        response = CreateNginx.CreateNginxFiles(ProdNginxAvail, AppName, nginx_conf_data)

        #Create folders and rules for new app
        CreateModsec = stuffs.CreateFiles()
        response = CreateModsec.CreateModsecFiles(ProdModsecRules, AppName, ProdModsecConf, query.modsec_conf_data)


        # Create symlinks from base_rules to enabled rules
        CreateLinks = stuffs.CreateFiles()
        response = CreateLinks.CreateRules(ProdModsecRules, AppName)
        #Update rule status in bd
        rules_enabled = 'ls /opt/waf/nginx/etc/modsec_rules/'+AppName+'/enabled_rules | grep  ".conf$" | sed "s/.conf//g"'
        r = subprocess.Popen(rules_enabled, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        rules_that_exist,rules_that_exist_err = r.communicate()
        rules_that_exist = str(rules_that_exist)
        rules_that_exist = rules_that_exist.replace("REQUEST-901-INITIALIZATION\n","")

        for i in rules_that_exist.splitlines():
            db.rules.insert(id_rand=request.args[0], rule_name=i, status='On')

        #create backend to prod path
        #create listen folder
        subprocess.Popen(['mkdir', ListenPATH+'%s' %(AppName)])

        #Create log rotation configuration
        log_rotation = stuffs.Maintenance()
        log_rotation.LogRotationFile(AppName)

        #create logs folder
        subprocess.Popen(['mkdir', '-p', '/opt/waf/nginx/var/log/%s/' %(AppName)])

        #create deny paths and headers directory
        subprocess.Popen(['mkdir', '-p', '/opt/waf/nginx/etc/rewrite/paths/%s' % (AppName)])
        db(db.new_app.id_rand == request.args[0]).delete()
        db.summary.insert(id_rand=request.args[0],app_name=query.app_name)
        db.log_size.insert(id_rand=request.args[0],app_name=query.app_name)
        db.commit()
        logger.Logger.NewLogApp(db2, auth.user.username, "Deploye Application: " + query.app_name + 'deployed' )
        redirect(URL('Websites'))

    else:
        redirect(URL('new_app'))



@auth.requires_login()
def DeleteNewApp():
    #import os

    a = stuffs.Filtro()
    b = a.CheckStr(request.args[0])
    if b == 'YES':

        #Get App Name
        query = db(db.new_app.id_rand == request.args[0]).select(db.new_app.app_name)
        if query:
            AppName =  str(query[0]['app_name'])

            db(db.new_app.id_rand == request.args[0]).delete()
            logger.Logger.NewLogApp(db2, auth.user.username, "Deleted App: Deleted " + AppName)
            response.flash = 'App Deleted'
        else:
            response.flash = 'App does not exist'
    else:
        response.flash = 'Invalid ID'



@auth.requires_login()
def new_app():
    query = db(db.new_app).select(db.new_app.app_name, db.new_app.autor, db.new_app.name, db.new_app.id_rand, db.new_app.checked)


    return dict(query=query, page="Add a new application", icon="fa fa-plus", title="Create a new application")


@auth.requires_login()
def status():
    listening = subprocess.Popen(['sudo','netstat', '-tulpen'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out1,err1 = listening.communicate()
    p1 = subprocess.Popen(['ps', 'aux'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    p2 = subprocess.Popen(['grep', 'nginx'], stdin=p1.stdout, stdout=subprocess.PIPE)
    running = p2.communicate()[0]

    if 'nginx' in str(out1):
        status = "Nginx running and apps running"

    elif 'nginx: master' in str(running):
        status = "Nginx running but 0 apps running"
    else:
        status = "Nginx not running"
    return status

@auth.requires_login()
def EngxEdit():

    #hacer filtro en caso de que vengan los datos en blanco (si se llama la funcion directamente arrojará error)
    a = stuffs.Filtro()
    b = a.CheckStr(request.args[0])

    if b == 'YES':
            query = db(db.production.id_rand == request.args[0]).select(db.production.nginx_conf_data, db.production.app_name).first()
            if query:
                db(db.production.id_rand == request.args[0]).update(nginx_conf_data=request.vars.body)
                DataNginx = query.nginx_conf_data
                AppName = query.app_name
                UpdateFiles = stuffs.CreateFiles()
                UpdateFiles.CreateNginxFiles(ProdNginxAvail, AppName, request.vars.body)
                #UpdateFiles.CreateNginxSymlink(ProdNginxAvail, AppName, 'prod')
                response.flash = 'Configuration Saved'
                r = stuffs.Nginx()
                r.Reload()
                logger.Logger.NewLogApp(db2, auth.user.username, "EngxEdit: prod saved configuration app: " + AppName)
            else:
                response.flash = 'App does not exist'

    else:
        response.flash = "Error in data supplied"



@auth.requires_login()
def ModsEdit():

    # hacer filtro en caso de que vengan los datos en blanco (si se llama la funcion directamente arrojará error)
    a = stuffs.Filtro()
    b = a.CheckStr(request.args[0])

    if b == 'YES':

        query = db(db.production.id_rand == request.args[0]).select(db.production.modsec_conf_data, db.production.app_name).first()
        if query:
            db(db.production.id_rand == request.args[0]).update(modsec_conf_data=request.vars.body)
            DataModsec = query.modsec_conf_data
            AppName = query.app_name

            UpdateFiles = stuffs.CreateFiles()
            UpdateFiles.CreateModsecConf(AppName, request.vars.body)
            response.flash = 'Configuration Saved'
            a = stuffs.Nginx()
            b = a.Reload()
            logger.Logger.NewLogApp(db2, auth.user.username, "Modsec conf Editor: new configuration created" + AppName)


        else:
            response.flash = "Error in data supplied"
            logger.Logger.NewLogApp(db2, auth.user.username, "Modsec conf Editor: Error in id parameter suplied " + AppName)

    else:
        response.flash = "Error in data supplied"
        redirect(URL('new_app'))



@auth.requires_login()
def BackendIps():
    import os
    import urllib.parse
    HttpBckend = False
    HttpsBckend = False
    http_backend_hosts = ''
    https_backend_hosts = ''
    f = stuffs.Filtro()
    b = f.CheckStr(request.vars['id'])
    if b == 'YES' and request.vars['http'] or request.vars['https']:
        create_backend = stuffs.CreateFiles()
        query = db(db.production.id_rand == request.vars['id']).select(db.production.app_name, db.production.max_fails,
                                                                        db.production.fail_timeout, db.production.vhost_id,
                                                                        db.production.plbsid_id) or redirect(URL('ProdEdit'))
        os.system('echo "" > /opt/waf/nginx/etc/backend/%s.conf ' % (query[0]['app_name']))
        http_backend = urllib.parse.unquote(request.vars['http']).splitlines()
        https_backend = urllib.parse.unquote(request.vars['https']).splitlines()
        #print('http_backend: {}'.format(http_backend))
        for b in http_backend:
            #print('http_backend iter {}'.format(b))
            backend_ip = b.split("=>")
            if "=>" not in b:
                response.flash = XML("Use format: 10.10.10.10=>80", sanitize=False)
                return
            elif IS_INT_IN_RANGE(1,65535)(backend_ip[1])[1] == None:
                http_backend_hosts += '\n'
                #print(str((backend_ip[0]))+':'+str((backend_ip[1])))
                http_backend_hosts += str((backend_ip[0]))+':'+str((backend_ip[1]))

            else:
                response.flash = "Error in backend suplied"
                return
            HttpBckend = True

        for b in https_backend:
            backend_ip = b.split("=>")
            if "=>" not in b:
                response.flash = XML("Use format: 10.10.10.10=>80", sanitize=False)
                return
            elif IS_INT_IN_RANGE(1,65535)(backend_ip[1])[1] == None:
                https_backend_hosts += '\n'
                https_backend_hosts += str((backend_ip[0]))+':'+str((backend_ip[1]))

            else:
                response.flash = "Error in backend suplied"
                return

            HttpsBckend = True

        if not http_backend:
            db(db.production.id_rand == request.vars['id']).update(backend_ip_http="{}".format(''))

        if not https_backend:
            db(db.production.id_rand == request.vars['id']).update(backend_ip_https="{}".format(''))

        if HttpBckend:
            db(db.production.id_rand == request.vars['id']).update(backend_ip_http="{}".format(http_backend_hosts.replace(':','=>')))
            r = create_backend.CreateBackend(str(query[0]['app_name']), "{}".format(http_backend_hosts),
                                         str(query[0]['vhost_id']), query[0]['max_fails'],
                                         query[0]['fail_timeout'], query[0]['vhost_id'], 'http')

        if HttpsBckend:
            db(db.production.id_rand == request.vars['id']).update(backend_ip_https="{}".format(https_backend_hosts.replace(':','=>')))
            r = create_backend.CreateBackend(str(query[0]['app_name']), "{}".format(https_backend_hosts),
                                         str(query[0]['vhost_id']), query[0]['max_fails'],
                                         query[0]['fail_timeout'], query[0]['vhost_id'], 'https')
        # Reload Nginx
        a = stuffs.Nginx()
        b = a.Reload()
        response.flash = 'Backend updated'

    else:
        response.flash = "Error in data supplied"

    return dict()

@auth.requires_login()
def CheckProd():

    s = stuffs.Nginx()
    r = s.SyntaxCheck()
    if "Syntax OK" in r:
        session.flash = 'Syntax OK'
        redirect(URL('Websites'))
    else:
        redirect(URL('Websites'))
    return dict()

@auth.requires_login()
def EnableApp():
    c = stuffs.Filtro()
    d = c.CheckStr(request.args[0])
    if d == 'YES':
        query = db(db.production.id_rand == request.args[0]).select(db.production.app_name, db.production.listen_ip)
        AppName = str(query[0]['app_name'])

        if query[0]['listen_ip'] != None:

            # Reload Nginx
            a = stuffs.Nginx()
            b = a.Reload()

            if 'Bad Syntax' in b:
                session.flash = 'Error in configuration, Not Enabled. --> ' + b
                logger.Logger.NewLogError(db2, auth.user.username, "EnableApp: Error in configuration, Not Enabled. --> " + str(b))
                redirect(URL('Websites'))
            else:
                #Enable app
                subprocess.Popen(['ln', '-sf', ProdNginxAvail + AppName + '_nginx.conf',
                             ProdNginxEnabled], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                db(db.production.id_rand == request.args[0]).update(enabled='Enabled')
                #change ownership to audit logs, otherwise they will not appear in the view
                subprocess.Popen(['chown', '-R', 'www-data.www-data','/opt/waf/nginx/var/log/%s' %(AppName)])
                logger.Logger.NewLogApp(db2, auth.user.username, "EnableApp: Enabled " + AppName)
                session.flash = AppName + ' Enabled'
                a.Reload()
                redirect(URL('Websites'))
                session.enabled = 'active'
                session.e_expanded = 'true'
                session.d_expanded = 'false'
                session.disabled = ''

                subprocess.Popen(['sudo', 'chown', '-R', 'www-data.www-data', '/opt/waf/nginx/var/log/'],
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                subprocess.Popen(['sudo', 'chmod', '755', '-R', '/opt/waf/nginx/var/log/'], stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE)
        else:
            session.flash = AppName + " has no IP assigned, first assign an IP to listen"
            redirect(URL('Websites'))
    else:
        redirect(URL('Websites'))

    return dict(active='active')

@auth.requires_login()
def DisableApp():

    a = stuffs.Filtro()
    b = a.CheckStr(request.args[0])
    if b == 'YES':

        query = db(db.production.id_rand == request.args[0]).select(db.production.app_name)

        # Remove symbolic links in /opt/waf/nginx/etc/sites-enabled/
        subprocess.Popen(['rm', ProdNginxEnabled + query[0]['app_name'] + '_nginx.conf'],
                                           stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        db(db.production.id_rand == request.args[0]).update(enabled='Disabled')

        # Reload Nginx
        a = stuffs.Nginx()
        b = a.Reload()

        if 'Bad Syntax' in b:
            session.flash = B(SPAN('Disabled but I will not reload until you fix the error: ->  ')) + b
            logger.Logger.NewLogError(db2, auth.user.username, "DisableApp: Disabled but I will not reload until you fix the error: ->   " + str(b))
            redirect(URL('Websites'))
        else:
            logger.Logger.NewLogApp(db2, auth.user.username, 'DisableApp: ' + query[0]['app_name'] + ' Disabled' )
            session.flash = query[0]['app_name'] + ' Disabled'
            redirect(URL('Websites'))
            session.enabled = ''
            session.e_expanded = 'false'
            session.d_expanded = 'true'
            session.disabled = 'active'

    else:
        redirect(URL('Websites'))



@auth.requires_login()
def Listen():
    import stuffs
    import os
    import changeconfig
    from pathlib import Path

    a = stuffs.Filtro()
    b = a.CheckStr(request.vars['id'])
    c = 'YES' if IS_IPADDRESS()(request.vars['listen_ip'])[1] == None else 'NO'
    IpChanged = False
    #if multiples come they will be separated in a new line
    if '-' in request.vars['http_ports']:
        request.vars['http_ports'] = request.vars['http_ports'].replace('-','\n')
        for port in request.vars['http_ports'].splitlines():
             if IS_INT_IN_RANGE(1, 65535)(port)[1] != None:
                    response.flash = 'Invalid HTTP ports.'
                    return
             else:
                d = 'YES'
                #asign ports to variables
                multi_http_ports = True

    else:
        d = 'YES' if IS_INT_IN_RANGE(1, 65535)(request.vars['http_ports'])[1] == None else 'NO'
        multi_http_ports = False


    if '-' in request.vars['https_ports']:
        request.vars['https_ports'] = request.vars['https_ports'].replace('-','\n')
        for port in request.vars['https_ports'].splitlines():
             if IS_INT_IN_RANGE(1, 65535)(port)[1] != None:
                    response.flash = 'Invalid HTTPS ports'
                    return
             else:
                e = 'YES'
                multi_https_ports = True
    else:
        e = 'YES' if IS_INT_IN_RANGE(1, 65535, error_message='Invalid port')(request.vars['https_ports'])[1] == None else 'NO'
        multi_https_ports = False

    #if id, listen_ip and ports are valid
    if b == 'YES' and c == 'YES' and (d == 'YES' or e == 'YES') == True:
        UpdateFiles = stuffs.CreateFiles()
        #Get a list with the ips saved in "Add Interface" function
        ips = db(db.system).select(db.system.iface_ip)

        #Get actual ip
        actual_ip = db(db.production.id_rand == request.vars['id']).select(db.production.listen_ip)

        #Get data configuration for the app
        query = db(db.production.id_rand == request.vars['id']).select(db.production.nginx_conf_data, db.production.app_name)

        try:
            ips_list = []
            for i in ips:
                ips_list.append(i['iface_ip'])

            # if in the list, it's get processed
            if request.vars['listen_ip'] in ips_list:
                #remove listen old files
                os.system('rm %s%s/listenHTTP.conf' %(ListenPATH, query[0]['app_name']))
                os.system('rm %s%s/listenHTTPS.conf' %(ListenPATH, query[0]['app_name']))

                #if ip is different
                if actual_ip[0]['listen_ip'] != request.vars['listen_ip']:
                    #check if other app is using this ip and get the app_name
                    is_used_by = db(db.system.iface_ip == actual_ip[0]['listen_ip']).select(db.system.used_by)
                    if is_used_by:
                        is_used_by = is_used_by[0]['used_by'].replace(", "+query[0]['app_name'],"")
                        is_used_by = is_used_by.replace(query[0]['app_name']+", ","")
                        is_used_by = is_used_by.replace(query[0]['app_name'],"")
                        #update list of apps using this ip
                        if is_used_by == "":
                            is_used_by = None
                            db(db.system.iface_ip == actual_ip[0]['listen_ip']).update(used_by=is_used_by, available='Available')
                        else:
                            db(db.system.iface_ip == actual_ip[0]['listen_ip']).update(used_by=is_used_by)
                    else:
                        is_used_by = None
                        db(db.system.iface_ip == actual_ip[0]['listen_ip']).update(used_by=is_used_by, available='Available')

                    #check if new ip has other apps
                    new_ip_used_by = db(db.system.iface_ip == request.vars['listen_ip']).select(db.system.used_by)
                    #print "new_ip_used_by: ", new_ip_used_by[0]
                    if new_ip_used_by[0]['used_by'] != None:
                        new_ip_used_by = new_ip_used_by[0]['used_by']+", "+query[0]['app_name']
                        #update list of apps using this ip
                        db(db.system.iface_ip == request.vars['listen_ip']).update(used_by=new_ip_used_by, available='In use')

                    else:
                        #print 'Else'
                        db(db.system.iface_ip == request.vars['listen_ip']).update(used_by=query[0]['app_name'], available='In use')

                    #Update production ip with the new ip
                    db(db.production.id_rand == request.vars['id']).update(listen_ip=request.vars['listen_ip'])
                    IpChanged =True


                #If http ports are selected and valid, it will be created the listen file config
                if d == 'YES' and e == 'NO':
                    #update http ports
                    if multi_http_ports:
                        db(db.production.id_rand == request.vars['id']).update(ports_http=request.vars['http_ports'].replace("\n","-"))
                    db(db.production.id_rand == request.vars['id']).update(ports_https='')
                    f = open('%s%s/listenHTTP.conf' %(ListenPATH, query[0]['app_name']), 'a')
                    for port in request.vars['http_ports'].splitlines():
                        #print "Adding configuration"
                        f.write('listen %s:%s;' %(request.vars['listen_ip'], port))
                        f.write('\n')
                    f.close()
                    #Comment SSL certitificate line
                    if "#ssl_certificate" not in query[0]['nginx_conf_data']:
                        query[0]['nginx_conf_data'] = query[0]['nginx_conf_data'].replace(' ssl_certificate', '#ssl_certificate')

                    UpdateFiles.CreateNginxFiles(ProdNginxAvail, query[0]['app_name'], query[0]['nginx_conf_data'])

                    db(db.production.id_rand == request.vars['id']).update(nginx_conf_data=query[0]['nginx_conf_data'])
                    logger.Logger.NewLogApp(db2, auth.user.username, "Listening: {} -> {} - Ports: {}".format(query[0]['app_name'],  request.vars['listen_ip'], request.vars['http_ports']))
                    if IpChanged:
                        response.flash = 'IP and HTTP ports saved'
                    else:
                        response.flash = 'HTTP ports saved'

                #If https ports are selected and valid, it will be created the listen file config
                elif e == 'YES' and d == 'NO':
                    #update https ports
                    db(db.production.id_rand == request.vars['id']).update(ports_https=request.vars['https_ports'].replace("\n","-"))
                    db(db.production.id_rand == request.vars['id']).update(ports_http='')
                    f = open('%s%s/listenHTTPS.conf' %(ListenPATH, query[0]['app_name']), 'a')
                    for port in request.vars['https_ports'].splitlines():
                        f.write('listen %s:%s ssl;' %(request.vars['listen_ip'], port))
                        f.write('\n')
                    f.close()
                    #Create dir ssl if not exist
                    Path(SslPATH + query[0]['app_name']).mkdir(parents=True, exist_ok=True)

                    #process = subprocess.Popen(['mkdir', SslPATH + query[0]['app_name']], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

                    query[0]['nginx_conf_data'] = query[0]['nginx_conf_data'].replace('#ssl_certificate', 'ssl_certificate')

                    UpdateFiles.CreateNginxFiles(ProdNginxAvail, query[0]['app_name'], query[0]['nginx_conf_data'])

                    db(db.production.id_rand == request.vars['id']).update(nginx_conf_data=query[0]['nginx_conf_data'])
                    logger.Logger.NewLogApp(db2, auth.user.username, "Listening: {} -> {} - Ports: {}".format(query[0]['app_name'],  request.vars['listen_ip'], request.vars['https_ports']))
                    if IpChanged:
                        response.flash = 'IP and HTTPS ports saved'
                    else:
                        response.flash = 'HTTPS ports saved'


                elif e == 'YES' and d == 'YES':
                    #update https ports
                    db(db.production.id_rand == request.vars['id']).update(ports_https=request.vars['https_ports'].replace("\n","-"))
                    db(db.production.id_rand == request.vars['id']).update(ports_http=request.vars['http_ports'].replace("\n","-"))
                    #Https part
                    f = open('%s%s/listenHTTPS.conf' %(ListenPATH, query[0]['app_name']), 'a')
                    for port in request.vars['https_ports'].splitlines():
                        #print "Adding configuration"
                        f.write('listen %s:%s ssl;' %(request.vars['listen_ip'], port))
                        f.write('\n')
                    f.close()
                    #Create ssl dir if not exist
                    Path(SslPATH + query[0]['app_name']).mkdir(parents=True, exist_ok=True)
                    #HTTP part
                    f = open('%s%s/listenHTTP.conf' %(ListenPATH, query[0]['app_name']), 'a')
                    for port in request.vars['http_ports'].splitlines():
                        #print "Adding configuration"
                        f.write('listen %s:%s;' %(request.vars['listen_ip'], port))
                        f.write('\n')
                    f.close()

                    query[0]['nginx_conf_data'] = query[0]['nginx_conf_data'].replace('#ssl_certificate', 'ssl_certificate')
                    UpdateFiles = stuffs.CreateFiles()
                    UpdateFiles.CreateNginxFiles(ProdNginxAvail, query[0]['app_name'], query[0]['nginx_conf_data'])

                    db(db.production.id_rand == request.vars['id']).update(nginx_conf_data=query[0]['nginx_conf_data'])

                    logger.Logger.NewLogApp(db2, auth.user.username, "Listening: {} -> {} - Ports: HTTP -> {} HTTPS -> {}".format(query[0]['app_name'],  request.vars['listen_ip'], request.vars['http_ports'], request.vars['https_ports']))
                    if IpChanged:
                        response.flash = 'IP, HTTPS and HTTP ports saved'
                    else:
                        response.flash = 'HTTPS and HTTP ports saved'

                #Reload changes
                u = stuffs.Nginx()
                u.Reload()

            else:
                response.flash = 'Invalid Ip'

        except Exception as e:
            logger.Logger.NewLogError(db2, auth.user.username, "ERROR in Listen function for app {}: {}".format(query[0]['app_name'], str(e)))
            #logger.Logger.NewLogError(db2, auth.user.username, "Listen: " + query[0]['app_name'] )
            response.flash = str(e)
            #print 'Error:', e
    else:
        response.flash = 'b:{} - c:{} - d:{} - e:{}'.format(b,c,d,e)
    return dict()

@auth.requires_login()
def Mode():
    a = stuffs.Filtro()
    id_rand = a.CheckStr(request.vars['id'])
    alias_mode = request.vars['mode']
    modes = ['Bridge', 'Vigilant', 'Defend']
    modsec_list = []
    if id_rand == 'YES' and alias_mode in modes:

        if alias_mode == 'Bridge':
            mode = 'Off'
        elif alias_mode == 'Vigilant':
            mode = 'DetectionOnly'
        elif alias_mode == 'Defend':
            mode = 'On'
        else:
            mode = 'On'
            alias_mode = 'Defend'

        modsec = db(db.production.id_rand == request.vars['id']).select(db.production.modsec_conf_data, db.production.app_name,db.production.mode)
        modsec_data = modsec[0]['modsec_conf_data']
        #change configuration
        #Change return a dictionary with status message and the new list whith changed configuration ex: {'newconf_list': 'data', 'message':'success or error'}
        change = changeconfig.Change()
        r = change.Text(modsec_data, 'SecRuleEngine', "SecRuleEngine %s" %(mode))
        db(db.production.id_rand == request.vars['id']).update(modsec_conf_data='\n'.join(r['new_list']), mode=alias_mode)


        #get new conf
        new = db(db.production.id_rand == request.vars['id']).select(db.production.modsec_conf_data)

        UpdateFiles = stuffs.CreateFiles()
        try:
            UpdateFiles.CreateModsecConf('prod', modsec[0]['app_name'], new[0]['modsec_conf_data'])
            logger.Logger.NewLogApp(db2, auth.user.username, "Mode: prod " +  modsec[0]['app_name'])
        except Exception as e:
            logger.Logger.NewLogError(db2, auth.user.username, "Mode: " + str(e))
            session.flash = e
        #response.flash = 'Configuracion Guardada'
        a = stuffs.Nginx()
        b = a.Reload()

        msg = 'Mode %s enabled' %(request.vars['mode'])
        session.flash = 'Mode %s enabled' %(request.vars['mode'])
    else:
        msg = 'Error'
        logger.Logger.NewLogError(db2, auth.user.username, "Mode: Error")


    return response.json(msg)

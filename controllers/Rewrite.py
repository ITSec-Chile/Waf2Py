#!/usr/bin/env python
# Chris - cvaras@itsec.cl
# -*- coding: utf-8 -*-
import subprocess
import stuffs
import re

ProdNginxAvail = '/opt/waf/nginx/etc/sites-available/'
DenyPathsDir = '/opt/waf/nginx/etc/rewrite/paths/'

@auth.requires_login()
def AddHeaders():
    a = stuffs.Filtro()
    #print request.vars
    check_list = []

    try:
        b = a.CheckStr(request.vars['id'])



    except Exception as debug:
        d = debug
        r = debug
        b = 'NO'
        response.flash = 'Error in data supplied'

    #something strange happens below, is more slow when POST contains no data .......
    if b == 'YES':

        if len(request.vars) == 1 and request.vars.keys()[0] == 'id':
            db(db.production.id_rand == request.vars['id']).update(extra_headers="")
            nginx_conf = db(db.production.id_rand == request.vars['id']).select(db.production.app_name,
                                                                                db.production.nginx_conf_data)
            replace = re.sub(r'(^            ##startInsertHead\w+##\n).*(^            ##endInsertHead\w+##)',
                             r'\1%s\2' % (''), nginx_conf[0]['nginx_conf_data'],
                             flags=re.S | re.M)
            db(db.production.id_rand == request.vars['id']).update(nginx_conf_data=replace)  # '\n'.join(r))
            db.commit()
            UpdateFiles = stuffs.CreateFiles()
            # try:

            # get the new conf
            nginx_conf = db(db.production.id_rand == request.vars['id']).select(db.production.app_name,
                                                                                db.production.nginx_conf_data)
            UpdateFiles.CreateNginxFiles(ProdNginxAvail, nginx_conf[0]['app_name'], nginx_conf[0]['nginx_conf_data'])
            response.flash = 'Configuration was saved'
            r = stuffs.Nginx()
            r.Reload()
            r = 'Configuration was saved'
        else:
            for test in request.vars.keys():
                if test != 'id':
                    if len(request.vars[test]) == 2:
                        check_list.append('YES')
                    else:
                        check_list.append('NO')
                        response.flash = 'Error in data supplied'

                    if request.vars[test][1] == "":
                        check_list.append('NO')
                        response.flash = 'Header must have a value!'
                    else:
                        check_list.append('YES')

                    if len(request.vars[test][0]) != 0:
                        check_list.append('YES')
                    else:
                        response.flash = 'Header name can\'t be empty!'
                        check_list.append('NO')
            r = ''
        if 'NO' not in check_list and len(check_list) > 1:
            cookies = []
            cookies_list = ''
            for i in request.vars.keys():

                if 'cookie' in i:
                    cookies.append('            add_header '+'"'+request.vars[i][0]+ '" "'+ request.vars[i][1] +'";\n')
                    cookies_list = cookies_list + request.vars[i][0] + ' '+ request.vars[i][1] + '\n'

                else:
                    pass

            db(db.production.id_rand == request.vars['id']).update(extra_headers=cookies_list)
            nginx_conf = db(db.production.id_rand == request.vars['id']).select(db.production.app_name,
                                                                                      db.production.nginx_conf_data)
            replace = re.sub(r'(^            ##startInsertHead\w+##\n).*(^            ##endInsertHead\w+##)', r'\1%s\2' %(''.join(cookies)), nginx_conf[0]['nginx_conf_data'],
                   flags=re.S | re.M)
            db(db.production.id_rand == request.vars['id']).update(nginx_conf_data=replace)  # '\n'.join(r))
            db.commit()
            UpdateFiles = stuffs.CreateFiles()
            try:

                #get the new conf
                nginx_conf = db(db.production.id_rand == request.vars['id']).select(db.production.app_name,
                                                                                db.production.nginx_conf_data)
                UpdateFiles.CreateNginxFiles(ProdNginxAvail, nginx_conf[0]['app_name'], nginx_conf[0]['nginx_conf_data'])
                response.flash = 'Configuration was saved'
                r = stuffs.Nginx()
                r.Reload()
                r = 'Configuration was saved'
                # NewLogApp(db2, auth.user.username, "Mode: prod " +  data[0]['app_name'])
            except Exception as e:
                # NewLogError(db2, auth.user.username, "Mode: " + str(e))
                session.flash = e
                r = e
    else:
        #print 'not continue'

        r = 'Error in data supplied'

    return response.json(r)


@auth.requires_login()
def DenyPaths():
    #print request.vars

    a = stuffs.Filtro()
    r = ''
    try:
        b = a.CheckStr(request.vars['id'])
    except Exception as error:
        r = error
        b = 'NO'
        response.flash = 'Error in data supplied'
    path_list = []
    count_safe = 0
    go_ahead = ''
    if b == 'YES':
        for i in request.vars.keys():
            if len(request.vars[i]) == 0:
                response.flash = "Paths can't be empty"
                break
            elif 'path' in i:
                path_list.append(request.vars[i])
                count_safe += 1
        if count_safe <= 20: #increase here if you want more than 20 paths to deny...
            go_ahead = 'YES'
        else:
            go_ahead = 'NO'
    if b == 'YES' and go_ahead == 'YES':
        #falta hacer que se guarden en la db y se muestren en la vista
        paths = '\n'.join(path_list)
        db(db.production.id_rand == request.vars['id']).update(paths_denied=paths)
        total_deny = ''
        for path in path_list:
            #print 'path: ', path
            total_deny += "location %s {\nreturn 403;}\n" %(path)

        #print 'total: ', total_deny
        name = db(db.production.id_rand == request.vars['id']).select(db.production.app_name)
        f = open(DenyPathsDir+name[0]['app_name']+'/'+name[0]['app_name']+'_denyPaths.conf', 'w')
        f.write(total_deny)
        f.close()
        r = stuffs.Nginx()
        r.Reload()
        response.flash = 'Configuration was saved'
        r = 'Configuration was saved'

    else:
        response.flash = 'Error in data supplied'
        if r == '':
            r = 'Error in data supplied'

    return r

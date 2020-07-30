<script src="/Waf2Py/static/bower_components/chart.js/chart.bundle.js"></script>

<script>
   function logs() {
   $.ajax({
   type: "GET",
   url: "/Logs/WafLogs_frame/{{=id_rand}}",
   success: function(data){
            //var mystring = data
            var mainDiv = "";
            var parsedJSON = JSON.stringify(data);
            var jsonData = JSON.parse(parsedJSON);
            var total = 0;
            if (jsonData['data'] != '') {
                for (var i = 0; i < jsonData['data'].length; i++) {
                    var parsed = JSON.parse(jsonData['data'][i])
                    //console.log(parsed['transaction']);
                    if (mainDiv !== 'created') {
                        //Main div
                        var iDiv1 = document.createElement('div');
                        iDiv1.className = 'col-lg-12';
                        var mainDiv = 'created';
                        //panel group div
                        var PanelGroup = document.createElement('div');
                        PanelGroup.className = 'box-group';
                        PanelGroup.id = 'accordion-logs';
                        iDiv1.appendChild(PanelGroup);

                    }
                    var arrayLength = parsed['transaction']['messages'].length;
                    for (var ii = 0; ii < arrayLength; ii++) {
                        total +=1;
                        //Panel default
                        var PanelDefault = document.createElement('div');
                        PanelDefault.className = 'box box-default';
                        PanelGroup.appendChild(PanelDefault);

                        //Panel heading
                        var PanelHeading = document.createElement('div');
                        PanelHeading.className = 'box-header';
                        PanelDefault.appendChild(PanelHeading);

                        //title h4
                        var H4 = document.createElement('h4');
                        H4.className = 'box-title';
                        PanelHeading.appendChild(H4);

                        //a tag
                        var A = document.createElement('a');
                        A.className = 'collapsed';
                        A.setAttribute("data-toggle", "collapse");
                        A.setAttribute("data-parent", "#accordion-logs");
                        A.setAttribute("href", "#collapse" + String(total));
                        A.setAttribute("aria-expanded", "false");
                        H4.appendChild(A);


                        //console.log(parsed['transaction']);
                        response_code = parsed['transaction']['response']['http_code']
                        var arrayLength = parsed['transaction']['messages'].length;
                        var message_index;
                        var ii;
                        var message;
                        var modsec_info;
                        var attack_info;
                        attack_info = parsed['transaction']['messages'][ii]['details']['data'];
                       if (String(response_code).startsWith(5)) {
                            var severity_string = 'Server ERROR'
                            var title = 'Server Error - Code: '+ String(response_code)+' '
                            var attack_info = 'An error '+ String(response_code) + ' was produced in: '+parsed['transaction']['request']['uri'];
                            var modsec_info = {'Information':'This is not an attack, check the error log tab for more information'} ;
                            var addBtn = 'no';
                        }
                        else if(parsed['transaction']['messages'][ii]['message'] !== "") {
                            var severity_string = parsed['transaction']['messages'][ii]['details']['severity']
                            var title = parsed['transaction']['messages'][ii]['message'] + '  ';
                            attack_info = parsed['transaction']['messages'][ii]['details']['data'];
                            var modsec_info = parsed['transaction']['messages'][ii]['details'];
                            var ruleId = parsed['transaction']['messages'][ii]['details']['ruleId']
                            var uri = parsed['transaction']['request']['uri']
                            var addBtn = 'yes';
                        }
                        else {
                            var severity_string = parsed['transaction']['messages'][ii]['details']['severity']
                            var title = parsed['transaction']['messages'][ii]['details']['file'] + '  ';
                            attack_info = parsed['transaction']['messages'][ii]['details']['match'];
                            var modsec_info = parsed['transaction']['messages'][ii]['details'];
                            var ruleId = parsed['transaction']['messages'][ii]['details']['ruleId']
                            var uri = parsed['transaction']['request']['uri']
                            var addBtn = 'yes';
                        }
                           var attack_div = document.createElement('div');
                           var label_style = '';
                           var color = '#5cb45b';
                           attack_div.style = "overflow-x: auto; white-space: pre-wrap;"
                           if (severity_string === "2") {
                                severity_string = "CRITICAL"
                                attack_div.setAttribute('class', 'danger_light_bulma')
                                label_style = 'label danger_light_bulma';
                            }
                            else if (severity_string === "3") {
                                severity_string = "WARNING"
                                attack_div.setAttribute('class', 'warning_bulma')
                                label_style = 'label warning_bulma';
                            }
                            else if (severity_string === "4") {
                                severity_string = "NOTICE"
                                attack_div.setAttribute('class', 'success_light_bulma')
                                label_style = 'label success_light_bulma';
                            }
                            else if (severity_string === "0") {
                                    severity_string = "NOTICE"
                                    attack_div.setAttribute('class', 'success_light_bulma')
                                    label_style = 'label success_light_bulma';
                                }
                            else if (severity_string === "5") {
                                severity_string = "Uknown severity "+String(response_code)
                                attack_div.setAttribute('class', 'link_light_bulma')
                                label_style = 'label link_light_bulma';
                            }
                            
                            else if (severity_string === "No severity set in rules") {
                                severity_string = "No severity set in rules"
                                attack_div.setAttribute('class', 'link_light_bulma')
                                label_style = 'label link_light_bulma';
                            }

                            var s = document.createTextNode(severity_string);
                            var date = document.createElement('span')
                            date.setAttribute('class', 'label info_light_bulma')
                            date.appendChild(document.createTextNode('#' + String(total) + ' - ' + parsed['transaction']['time_stamp']))
                            var T = document.createElement('span')
                            var S = document.createElement('span');
                            S.className = label_style;
                            T.className = label_style;
                            A.appendChild(date);
                            A.appendChild(document.createTextNode(' - '));
                            T.appendChild(document.createTextNode(title));
                            A.appendChild(T);
                            A.appendChild(document.createTextNode(' - '));
                            A.appendChild(S);
                            S.appendChild(s);

                            //panel collapse
                            var PanelCollapse = document.createElement('div');
                            PanelCollapse.className = 'panel-collapse collapse'
                            PanelCollapse.id = 'collapse' + String(total)
                            PanelCollapse.setAttribute("aria-expanded", "false");
                            //panel body
                            var PanelBody = document.createElement('div');
                            PanelBody.className = 'box-body';
                            var attacker = parsed['transaction']['client_ip'];
                            attack_div.appendChild(document.createTextNode(attack_info))
                            // Exclusion button
                            if ( addBtn === 'yes') {
                                div_actions = document.createElement('div')
                                div_actions.setAttribute("class","btn-group pull-right")
                                acctionButtons = document.createElement('button');
                                acctionButtons.appendChild(document.createTextNode("Exclude this rule "))
                                acctionButtons.setAttribute("class", "btn link_light_bulma dropdown-toggle");
                                acctionButtons.setAttribute("type", "button");
                                acctionButtons.setAttribute("data-toggle", "dropdown");
                                spanActButton = document.createElement('span')
                                spanActButton.setAttribute("class", "caret");
                                acctionButtons.appendChild(spanActButton)
                                div_actions.appendChild(acctionButtons)
                                ulActButton = document.createElement('ul')
                                ulActButton.setAttribute("class", "dropdown-menu");
                                liActButton = document.createElement('li')
                                aActButton1 = document.createElement('a')
                                aActButton1.setAttribute("href", "#");
                                aActButton1.setAttribute("onclick", "GlobalExclusion('"+ruleId+"', "+"'"+title+"',)");
                                aActButton1.appendChild(document.createTextNode("Global exclusion"))
                                liActButton2 = document.createElement('li')
                                aActButton2 = document.createElement('a')
                                aActButton2.setAttribute("href", "#");
                                aActButton2.setAttribute("onclick", "LocalExclusion('"+ruleId+"', "+"'"+title+"', "+"'"+uri+"')");
                                aActButton2.appendChild(document.createTextNode("Local exclusion"))
                                liActButton.appendChild(aActButton1)
                                liActButton2.appendChild(aActButton2)
                                ulActButton.appendChild(liActButton)
                                ulActButton.appendChild(liActButton2)
                                div_actions.appendChild(ulActButton)
                                PanelBody.appendChild(div_actions)
                                PanelBody.appendChild(document.createElement('br'))
                            }
                            
                            //attacker ip
                            var attacker_div = document.createElement('div');
                            attacker_div.innerHTML = '<h4><span class="label success_light_bulma">Attacker IP: '+attacker+'</span></h4>'
                            //country flag
                            var country_flag = document.createElement('img')
                            country_flag.setAttribute("class","flag flag-"+parsed['transaction']['country_code'].toLowerCase())
                            country_flag.setAttribute("src", "blank.gif")
                            attacker_div.appendChild(country_flag);
                            
                            //get headers
                            var div_header = document.createElement('div');
                            div_header.setAttribute("id", "div_header_"+String(total))
                            //Create table inside headers div
                            var table_headers = document.createElement('table');
                            table_headers.setAttribute("class","table table-hover")
                            table_headers_tr = document.createElement('tr');
                            table_headers_th = document.createElement('th');
                            table_headers_th1 = document.createElement('th');
                            table_headers_th.appendChild(document.createTextNode(' '));
                            table_headers_th1.appendChild(document.createTextNode('\t'+' '));
                            table_headers_tr.appendChild(table_headers_th);
                            table_headers_tr.appendChild(table_headers_th1);
                            table_headers.appendChild(table_headers_tr)
                            table_headers_td = document.createElement('td');
                            var headers = parsed['transaction']['request']['headers'];
                            var headers_keys = Object.keys(headers);
                            td_method = document.createElement('td')
                            tr_method = document.createElement('tr')
                            td_method_data = document.createElement('td')
                            td_method.appendChild(document.createTextNode('Method:'))
                            td_method_data.appendChild(document.createTextNode('\t'+parsed['transaction']['request']['method']+ '\n'))
                            tr_method.appendChild(td_method)
                            tr_method.appendChild(td_method_data)

                            //GeoIP
                            //Contry name
                            td_country_name = document.createElement('td')
                            tr_country_name = document.createElement('tr')
                            td_country_name_data = document.createElement('td')
                            td_country_name.appendChild(document.createTextNode('Country:'))
                            td_country_name_data.appendChild(document.createTextNode('\t'+parsed['transaction']['country']+ '\n'))
                            tr_country_name.appendChild(td_country_name)
                            tr_country_name.appendChild(td_country_name_data)

                            //City
                            td_city = document.createElement('td')
                            tr_city = document.createElement('tr')
                            td_city_data = document.createElement('td')
                            td_city.appendChild(document.createTextNode('City:'))
                            td_city_data.appendChild(document.createTextNode('\t'+parsed['transaction']['city']+ '\n'))
                            tr_city.appendChild(td_city)
                            tr_city.appendChild(td_city_data)

                            //uri
                            tr_uri = document.createElement('tr')
                            td_uri = document.createElement('td')
                            td_uri_data = document.createElement('td')
                            td_uri.appendChild(document.createTextNode('Uri:'))
                            td_uri_data.appendChild(document.createTextNode('\t'+parsed['transaction']['request']['uri']+ '\n'))
                            tr_uri.appendChild(td_uri)
                            tr_uri.appendChild(td_uri_data)

                            //version
                            tr_version = document.createElement('tr')
                            td_version = document.createElement('td')
                            td_version_data = document.createElement('td')
                            td_version.appendChild(document.createTextNode('Version:'))
                            td_version_data.appendChild(document.createTextNode('\t'+parsed['transaction']['request']['http_version'] + '\n'))
                            tr_version.appendChild(td_version)
                            tr_version.appendChild(td_version_data)


                            table_headers.appendChild(tr_city)
                            table_headers.appendChild(tr_country_name)
                            table_headers.appendChild(tr_method)
                            table_headers.appendChild(tr_uri)
                            table_headers.appendChild(tr_version)
                            //iterate for headers values
                            for (var h = 0; h < headers_keys.length; h++) {
                                bold_header = document.createElement('b');
                                table_headers_tr = document.createElement('tr');
                                table_headers_td = document.createElement('td');
                                table_headers_td2 = document.createElement('td');
                                table_headers_td.appendChild(document.createTextNode(headers_keys[h]+':'));
                                table_headers_td2.appendChild(document.createTextNode('\t'+headers[headers_keys[h]] + '\n'))
                                table_headers_tr.appendChild(table_headers_td)
                                table_headers_tr.appendChild(table_headers_td2)
                                table_headers.appendChild(table_headers_tr)
                            }
                            div_header.appendChild(table_headers)
                            var table_pre = document.createElement('pre')
                            table_pre.appendChild(div_header)

                            //get modsec info
                            var modsec_info_keys = Object.keys(modsec_info);
                            var all_modsec_info = '';
                            //Create table for modsec info
                            table_modsec = document.createElement('table')
                            table_modsec.style = "border: 1px; width: 800px"
                            tr_modsec = document.createElement('tr')
                            th_modsec = document.createElement('th')
                            th_modsec.appendChild(document.createTextNode(' '))
                            th_modsec.appendChild(document.createTextNode('\t'+' '))
                            tr_modsec.appendChild(th_modsec)
                            table_modsec.appendChild(tr_modsec)

                            for (var m = 0; m < modsec_info_keys.length; m++) {
                                tr_modsec_info = document.createElement('tr')
                                td_modsec_info = document.createElement('td')
                                td_modsec_info.appendChild(document.createTextNode(modsec_info_keys[m]+':'))
                                td_modsec_info.appendChild(document.createTextNode('\t'+modsec_info[modsec_info_keys[m]] + '\n'))
                                tr_modsec_info.appendChild(td_modsec_info)
                                table_modsec.appendChild(tr_modsec_info)
                            }
                            div_modsec = document.createElement('div')
                            div_modsec.setAttribute("id","attack_div_"+String(total))
                            div_modsec.appendChild(table_modsec)
                            modsec_pre = document.createElement('pre')
                            modsec_pre.appendChild(div_modsec)

                            var response_container = document.createElement('div')
                            response_container.innerHTML = '<h4><span class="label success_light_bulma">Response returned</span></h4>'
                            var response_pre = document.createElement('pre')
                            response_pre.innerHTML = 'HTTP Response code: <strong>'+parsed['transaction']['response']['http_code']+'</strong>';
                            response_pre.appendChild(document.createElement('br'))
                            //console.log(parsed['transaction'])
                            if (typeof parsed['transaction']['response']['body'] === "undefined") {
                                
                                response_pre.appendChild(document.createTextNode('No response body returned'))
                            }
                            else {
                                response_pre.appendChild(document.createTextNode(parsed['transaction']['response']['body']))
                            } 
                            response_container.appendChild(response_pre)

                            
                            var divButton = document.createElement('div');
                            divButton.style = "float: right";
                            var body = document.createElement('div');
                            body.style = "overflow-x: auto; white-space: pre-wrap;"
                            body.innerHTML = '<h4><span class="label success_light_bulma">Request headers</span></h4>'
                            body.appendChild(table_pre)
                            body.appendChild(document.createElement('br'))
                            body.appendChild(document.createElement('hr'))
                            var r_h4_body = document.createElement('h4')
                            var r_h4_label = document.createElement('span')
                            r_h4_label.setAttribute('class', 'label success_light_bulma')
                            r_h4_label.appendChild(document.createTextNode('Body request'))
                            r_h4_body.appendChild(r_h4_label)
                            body.appendChild(r_h4_body)
                            var request_body = document.createElement('pre')
                            if (parsed['transaction']['request']['body'] > 0) {
                                request_body.appendChild(document.createTextNode(parsed['transaction']['request']['body']))
                            }
                            else {
                                request_body.appendChild(document.createTextNode('This request does not contain body'))
                            } 
                            var response_body = document.createElement('div')
                            

                            body.appendChild(r_h4_body)
                            body.appendChild(request_body)
                            
                            response_container.appendChild(response_pre)
                            
                            body.appendChild(document.createElement('br'))
                            body.appendChild(document.createElement('hr'))
                            body.appendChild(response_container);
                            body.appendChild(document.createElement('hr'))
                            body.appendChild(document.createElement('br'))
                            var modsec_h4 = document.createElement('h4')
                            var modsec_h4_label = document.createElement('span')
                            modsec_h4_label.setAttribute('class', 'label success_light_bulma')
                            modsec_h4_label.appendChild(document.createTextNode('Modsecurity details'))
                            modsec_h4.appendChild(modsec_h4_label)
                            body.appendChild(modsec_h4)
                            body.appendChild(modsec_pre)
                            //body.appendChild(document.createTextNode(all_modsec_info))
                            //attack_div.appenMLdChild(fontAttack);
                            
                            //fontAttack.appendChild(fontAttackBold);
                            //fontAttackBold.appendChild(attack);

                            //fontAttacker.appendChild(fontAttackerBold);
                            //fontAttackerBold.appendChild(attacker_ip);
                            //attacker_div.appendChild(fontAttacker);
                            
                            
                            //PanelBody.appendChild(document.createElement('br'));
                            PanelBody.appendChild(document.createElement('br'));
                            PanelBody.appendChild(attack_div);
                            PanelBody.appendChild(attacker_div);
                            PanelBody.appendChild(document.createElement('br'));
                            PanelBody.appendChild(document.createElement('br'));
                            PanelBody.appendChild(body);
                            //PanelBody.appendChild(ajax);
                            PanelCollapse.appendChild(PanelBody);
                            PanelDefault.appendChild(PanelCollapse);
                            //PanelHeading.appendChild(PanelCollapse);

                            //var textnode = document.createTextNode(jsonData['data'][i]['titulo']);         // Create a text node
                            //iDiv1.appendChild(textnode);
                };
            }
            }
           else {
                var iDiv1 = document.createElement('div');
                iDiv1.className = 'col-md-10';
                var NoDataDiv = document.createElement('div');
                NoDataDiv.setAttribute("align","center");
                NoDataDiv.appendChild(document.createTextNode("No logs found."));
                iDiv1.appendChild(NoDataDiv);
            }
           var item = document.getElementById("loading").childNodes[0];
           item.replaceWith(iDiv1);
           //console.log(total_critical);
   }
   });
          };
$(document).ready(function(){
    $('#loading').html('<div align="center"><img src="/static/images/pacman_200px.gif"></div>');
    logs()
});
$('#show').click(function () {
		// add loading image to div
		$('#loading').html('<div align="center"><img src="/static/images/pacman_200px.gif"></div>');
        logs()
});
</script>
<script>
function GlobalExclusion(ruleId, title) {
    swal({
    title: 'Global Exclusion',
    text: 'Exlude this rule?',
    type: 'question',
    showCancelButton: true,
    confirmButtonColor: '#37bf6d',
    cancelButtonColor: '#f33a5f',
    confirmButtonText: 'Confirm',
    cancelButtonText: 'Cancel',
    buttonsStyling: true,
}). then((result) => {
       if (result.value) {
            $.ajax({
                  type: 'POST',
                  url: '/Waf2Py/Logs/ExcludeGlobal',
                  contentType: 'application/x-www-form-urlencoded',
                  data:{id_rand:'{{=id_rand}}', type:0, ruleid:ruleId, attack_name:title},
                  success: function(result){
                      swal(
                        'Success !','' + result, 'success'
                      )
                  }
                  });
        }
    })
}
//var inputValue =''
async function LocalExclusion(ruleId, title, Localpath) {
                const {value: name} = await swal({
                title: 'Exclude this rule for the following path ?',
                titleAttributes: {
                  width: 500,
                },
                text: 'Adjust the path to your needs (need to be without url encoding)',
                input: 'text',
                type: 'question',
                width: 500,
                inputAttributes: {
                  width: 100,
                },
                inputValue:Localpath,
                inputPlaceholder: 'Enter path you want to exclude ex: /page/bla.php or /page/bla.php?param=',
                showCancelButton: true,
                confirmButtonText: 'Confirm',
                cancelButtonText: 'Cancel',
                confirmButtonColor: '#37bf6d',
                cancelButtonColor: '#f33a5f',
                //var value = function(inputValue){},
              });

                if (name) {
                  $.ajax({
                  type: 'POST',
                  url: '/Waf2Py/Logs/ExcludeLocal',
                  contentType: 'application/x-www-form-urlencoded',
                  data:{id_rand:'{{=id_rand}}', type:1, ruleid:ruleId, attack_name:title, path:name},
                  success: function(result){
                      swal(
                        'Success !','' + result, 'success'
                      )
                  }
                  });
                  
        }
    }


</script>
<script>
    function Toggle(id) {
        $( "#div_header_"+id ).toggle( "slow", "linear" );
    };
    function ToggleAttack(id) {
        $( "#attack_div_"+id ).toggle( "slow", "linear" );
    };
</script>

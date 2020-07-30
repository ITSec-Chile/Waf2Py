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
            if (jsonData['data'] != '') {

                for (var i = 0; i < jsonData['data'].length; i++) {
                    //	alert(parsedJSON[i].Id);


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
                    A.setAttribute("href", "#collapse" + i);
                    A.setAttribute("aria-expanded", "false");
                    H4.appendChild(A);

                    //add vuln title
                    var s = document.createTextNode(jsonData['data'][i]['severidad']);
                    var severity_string = jsonData['data'][i]['severidad']
                    if (severity_string === "WARNING") {
                        var color = '#f7b543';
                    }

                    else if (severity_string === "CRITICAL") {
                        var color = '#f03154';
                    }
                    //else if (severity_string === "ALERT") {
                      //  var color = '#5cb45b';
                    //}
                    else if (severity_string === "NOTICE") {
                        var color = '#5cb45b';
                    }
                    else if (severity_string === "ERROR") {
                        var color = '#2a323c';
                    }
                    else if (severity_string === "No severity set in rules") {
                        var color = '#5cb45b';
                    }

                    var date = document.createTextNode('#' + (i + 1) + ' - ' + jsonData['data'][i]['fecha'] + ' - ');
                    //var color = '#f7b543';
                    var T = document.createElement('font')
                    var F = document.createElement('font');
                    F.color = color;
                    T.color = "##038b9a";
                    var title = document.createTextNode(jsonData['data'][i]['titulo'] + '  ');
                    A.appendChild(date);
                    T.appendChild(title);
                    A.appendChild(T);
                    A.appendChild(F);

                    F.appendChild(s);

                    //panel collapse
                    var PanelCollapse = document.createElement('div');
                    PanelCollapse.className = 'panel-collapse collapse'
                    PanelCollapse.id = 'collapse' + i
                    PanelCollapse.setAttribute("aria-expanded", "false");
                    //panel body
                    var PanelBody = document.createElement('div');
                    PanelBody.className = 'box-body';
                    var audit_info = jsonData['data'][i]['body'];
                    var attack_info = jsonData['data'][i]['ataque'];
                    var attacker = jsonData['data'][i]['attacker'];
                    var headers = jsonData['data'][i]['headers'];
                    var modsec_info = jsonData['data'][i]['modsec_info'];
                    //var audit_info = audit_info.replace('\x0a','<br />');
                    //var audit_info = audit_info.replace('\n','<br />');


                    var textdata = document.createTextNode(audit_info);
                    //attack div
                    var attack_div = document.createElement('div');
                    attack_div.style = "white-space: pre-wrap; background: red; border-radius: 3px";
                    var fontAttack = document.createElement('font');
                    fontAttack.color = "#FFFFFF";
                    var attack = document.createTextNode(attack_info);
                    var fontAttackBold = document.createElement('b');


                    //attacker info
                    var attacker_div = document.createElement('div');
                    attacker_div.style = "white-space: pre-wrap; background: #038b9a; border-radius: 3px; border-color: white";
                    var fontAttacker = document.createElement('font');
                    fontAttacker.color = "#FFFFFF";
                    var fontAttackerBold = document.createElement('b');
                    var attacker_ip = document.createTextNode("Attacker IP: " + attacker);
                    var headers_btn = document.createTextNode("Headers");
                    var body_desc = document.createTextNode("Body");
                    var info = document.createTextNode("Attack info");


                    var divButton = document.createElement('div');
                    divButton.style = "float: right";

                    var body = document.createElement('div');
                    var btn1 = document.createElement('button')
                    var btn2 = document.createElement('button')
                    var btn3 = document.createElement('button')
                    btn1.appendChild(headers_btn)
                    btn2.appendChild(body_desc)
                    btn3.appendChild(info)
                    btn1.setAttribute("class", "btn btn-sm btn-success")
                    btn2.setAttribute("class", "btn btn-sm btn-success")
                    btn3.setAttribute("class", "btn btn-sm btn-danger")
                    body.style = "overflow-x: auto; white-space: pre-wrap;"
                    body.appendChild(btn1)
                    body.appendChild(document.createElement('br'))
                    body.appendChild(document.createTextNode(headers))
                    body.appendChild(document.createElement('hr'))
                    body.appendChild(btn2)
                    body.appendChild(document.createElement('br'))
                    //body.appendChild(document.createTextNode("Body:\n"))
                    body.appendChild(textdata);
                    body.appendChild(document.createElement('hr'))
                    body.appendChild(btn3)
                    body.appendChild(document.createElement('br'))
                    body.appendChild(document.createTextNode(modsec_info))
                    attack_div.appendChild(fontAttack);
                    fontAttack.appendChild(fontAttackBold);
                    fontAttackBold.appendChild(attack);


                    attacker_div.appendChild(fontAttacker);
                    fontAttacker.appendChild(fontAttackerBold);
                    fontAttackerBold.appendChild(attacker_ip);

                    //Global Exclusion
                    var globalButton = document.createElement('button');
                    globalButton.setAttribute("type", "button");
                    globalButton.className = "btn btn-info ";
                    globalButton.id = "sa-warning";

                    globalButton.setAttribute("onclick", "ExcludeGlobal" + i + "()");
                    var global_icon = document.createElement('i');
                    global_icon.className = "mdi mdi-satellite-variant";
                    globalButton.appendChild(global_icon);
                    globalButton.appendChild(document.createTextNode("Global Exclusion"));


                    //Local exclusion
                    var LocallButton = document.createElement('button');
                    LocallButton.setAttribute("type", "button");
                    LocallButton.className = "btn btn-primary ";
                    LocallButton.id = "sa-warning";

                    LocallButton.setAttribute("onclick", "ExcludeLocal" + i + "()");
                    LocallButton.appendChild(document.createTextNode("Local Exclusion"));

                    //add swal and ajax exlcusion button
                    var ajax = document.createElement('script');
                    var lp = jsonData['data'][i]['path'].replace(/'/g, '%27');
                    var local_path = lp.replace(/\"/g, '%22');
                    ajax.type = 'text/javascript';
                    var ruleGlobal = " function ExcludeGlobal" + i + "() {\
                                        swal({\
                                        title: 'Global Exclusion',\
                                        text: 'Exlude this rule?',\
                                        type: 'warning',\
                                        showCancelButton: true,\
                                        confirmButtonColor: '#3085d6',\
                                        cancelButtonColor: '#d33',\
                                        confirmButtonText: 'Yes',\
                                        cancelButtonText: 'No',\
                                        confirmButtonClass: 'btn btn-success',\
                                        cancelButtonClass: 'btn btn-danger',\
                                        buttonsStyling: true,\
                                    }). then((result) => {\
                                           if (result.value) {\
                                                swal('Global exclusion added!', '', 'success');\
                                                $.ajax({\
                                                      type: 'POST',\
                                                      url: '/Waf2Py/Logs/ExcludeGlobal',\
                                                      contentType: 'application/x-www-form-urlencoded',\
                                                      data:{id_rand:'" + jsonData['data'][i]['randid'] + "', type:0, ruleid:'" + jsonData['data'][i]['rule'] + "', attack_name:'" + jsonData['data'][i]['titulo'] + "'},\
                                                      success: function(result){\
                                                          swal(\
                                                            'Success !','' + result, 'success'\
                                                          )\
                                                      }\
                                                      });\
                                            }\
                                        })\
                                    }"

                    var ruleLocal = "async function ExcludeLocal" + i + "() {\
                                        const {value: name} = await swal({\
                                        title: 'Exclude this rule for the following path ?',\
                                        titleAttributes: {\
                                          width: 500,\
                                        },\
                                        text: 'Adjust the path to your needs (need to be without url encoding)',\
                                        input: 'text',\
                                        width: 500,\
                                        inputAttributes: {\
                                          width: 100,\
                                        },\
                                        inputValue:'" + local_path + "',\
                                        inputPlaceholder: 'Enter path you want to exclude ex: /page/bla.php or /page/bla.php?param=',\
                                        showCancelButton: true,\
                                      });\
                                        if (name) {\
                                          $.ajax({\
                                          type: 'POST',\
                                          url: '/Waf2Py/Logs/ExcludeLocal',\
                                          contentType: 'application/x-www-form-urlencoded',\
                                          data: {id_rand:'" + jsonData['data'][i]['randid'] + "', type:1, path:name, ruleid:'" + jsonData['data'][i]['rule'] + "', attack_name:'" + jsonData['data'][i]['titulo'] + "'},\
                                          success: function(result){\
                                            swal(\
                                              'Rule excluded for the local path !','' + result, 'success'\
                                            )\
                                          }\
                                          })};\
                                       }"


                    globalRule = document.createTextNode(ruleGlobal);
                    localRule = document.createTextNode(ruleLocal);
                    ajax.appendChild(globalRule);
                    ajax.appendChild(localRule);
                    divButton.appendChild(globalButton);
                    divButton.appendChild(LocallButton);

                    PanelBody.appendChild(divButton);
                    PanelBody.appendChild(document.createElement('br'));
                    PanelBody.appendChild(document.createElement('hr'));
                    PanelBody.appendChild(attack_div);
                    PanelBody.appendChild(attacker_div);
                    PanelBody.appendChild(document.createElement('br'));
                    PanelBody.appendChild(body);
                    PanelBody.appendChild(ajax);
                    PanelCollapse.appendChild(PanelBody);
                    PanelDefault.appendChild(PanelCollapse);
                    //PanelHeading.appendChild(PanelCollapse);

                    //var textnode = document.createTextNode(jsonData['data'][i]['titulo']);         // Create a text node
                    //iDiv1.appendChild(textnode);


                };
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

            //alert(parsedJSON);
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

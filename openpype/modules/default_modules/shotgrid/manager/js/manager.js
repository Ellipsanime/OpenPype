// Check Form validity before Submit
(function () {
  'use strict'

  // Fetch all the forms we want to apply custom Bootstrap validation styles to
  var forms = document.querySelectorAll('.needs-validation')

  // Loop over them and prevent submission
  Array.prototype.slice.call(forms)
    .forEach(function (form) {
      form.addEventListener('submit', function (event) {
        if (!form.checkValidity()) {
          event.preventDefault()
          event.stopPropagation()
        }
        onBatchSubmit(event);
        form.classList.add('was-validated')
      }, false)
    })
})()

window.addEventListener('pywebviewready', initializeInterface)

window.addEventListener('load', (event) => {
    batchSelector = document.getElementById('selectOpenPypeProject');
    batchSelector.addEventListener("change", onBatchSelectorChange);
});

/* Event functions */

function onBatchSelectorChange(event) {

    project = event.target.options[event.target.selectedIndex].value;
    $("#shotgridUrl, #shotgridScriptName, #shotgridApiKey, #shotgridProjectId, #shotgridFieldMapping").val("");

    if (project != "newproject") {
        batchWorking();
        window.pywebview.api.getProjectBatchInfos(project).then((infos) => {
            $("#shotgridUrl").val(infos.url);
            $("#shotgridScriptName").val(infos.script_name);
            $("#shotgridApiKey").val(infos.api_key);
            $("#shotgridProjectId").val(infos.project_id);
            $("#shotgridFieldMapping").val(JSON.stringify(infos.fields_mapping, null, 5));
        }).then(batchEndWorking);
    }
}

function onBatchSubmit(event) {
    batchWorking();
    checkBatchValues().then((project_name) => {
        console.log("check OK")
        SendBatch(project_name).then(() => {
            console.log("batch OK")
            printInfo("Batch sent successfully");
            batchEndWorking();
            event.stopPropagation()
        }).catch((error) => {
            printWarning(error);
            batchEndWorking();
            event.stopPropagation()
        });
    }).catch(error => {
        printWarning(error);
        batchEndWorking();
        event.stopPropagation()
    });
}

/* Functions */

function initializeInterface() {
    console.log('Initialize interface');
    window.pywebview.api.getProjectList().then(fillProjectsSelector);
    window.pywebview.api.checkServerStatus().then((result) => {
        if (!result) {
            printError("Shotgrid module API unreachable");
        }
    });
    window.removeEventListener('pywebviewready', initializeInterface);
}

function fillProjectsSelector(projectList) {
    batchSelector = document.getElementById('selectOpenPypeProject');
    ScheduleSelector = document.getElementById('selectOpenPypeProjectSchedule');
    batchSelector.innerHTML = "<option value=\"newproject\">new project</option>";
    projectList.forEach(function(project){
        var el = document.createElement("option");
        el.innerHTML = project;
        el.value = project;
        elCopy = el.cloneNode(true);
        batchSelector.appendChild(el);
        ScheduleSelector.appendChild(elCopy);
    });
}

function checkBatchValues() {
    infos = getBatchInfos();
    console.log("check batch")
    return new Promise((success, failure) => {
        window.pywebview.api.checkProjectSettings(
            infos['url'],
            infos['script_name'],
            infos['api_key'],
            infos['project_id'],
        ).then((result) => {
            console.log(result);
            if (result["status_code"] == "200"){
                success(result["payload"]["status"]);
            } else {
                failure("Could not run batch with those settings");
            }
        });
    })
}

function SendBatch(projectName) {
    infos = getBatchInfos();
    newProject = (infos['project'] == "newproject")
    if (!newProject) {
        projectName = infos['project']
    }
    console.log("send batch")
    return new Promise((success, failure) => {
        var fieldsMapping;
        try {
            fieldsMapping = JSON.parse(infos['fields_mapping']);
        } catch(e) {
            failure("fields_mapping field contained malformed json");
            return;
        }
        window.pywebview.api.sendBatch(
            newProject,
            projectName,
            infos['url'],
            infos['script_name'],
            infos['api_key'],
            infos['project_id'],
            fieldsMapping
        ).then((result) => {
            console.log(result);
            if (result['status_code'] == 200){
                success();
            } else {
                failure(result['payload']['detail']);
            }
        });
    })
}

/* util */

function getBatchInfos() {
    return {
        'project': $("#selectOpenPypeProject").val(),
        'url': $("#shotgridUrl").val(),
        'script_name': $("#shotgridScriptName").val(),
        'api_key': $("#shotgridApiKey").val(),
        'project_id': $("#shotgridProjectId").val(),
        'fields_mapping': $("#shotgridFieldMapping").val(),
    }
}

function batchWorking() {
    spinner = document.createElement("span");
    spinner.setAttribute('class', "spinner-border spinner-border-sm");
    spinner.setAttribute('role', "status");
    spinner.setAttribute('aria-hidden', "true");
    $("#batchBtn").addClass("disabled");
    $("#batchBtn").html(spinner);
}

function batchEndWorking() {
    $("#batchBtn").removeClass("disabled");
    $("#batchBtn").html("Batch");
}

function printWarning(msg) {
    printMsg('warning', msg)
}

function printError(msg) {
    printMsg('danger', msg)
}

function printInfo(msg) {
    printMsg('info', msg)
}

function printMsg(type, msg){

    span = document.createElement("span");
    span.setAttribute('aria-hidden', 'true');
    span.innerHTML = '&times;';

    button = document.createElement("button");
    button.setAttribute('class', 'close');
    button.setAttribute('type', 'button');
    button.setAttribute('data-dismiss', 'alert');
    button.setAttribute('aria-label', 'Close');
    button.appendChild(span)

    alert = document.createElement("div");
    alert.setAttribute('class', 'alert alert-' + type + ' alert-dismissible fade show');
    alert.setAttribute('role', 'alert')
    alert.innerHTML = msg;
    alert.appendChild(button)

    $("#infoPanel").html(alert);
}

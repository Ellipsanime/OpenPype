window.addEventListener('pywebviewready', () => {
    console.log('pywebview ready');
    window.pywebview.api.getProjectList().then(fillProjectsSelector);
})

window.addEventListener('load', (event) => {
    batchSelector = document.getElementById('selectOpenPypeProject');
    batchSelector.addEventListener("change", onBatchSelectorChange);

    $("#batchBtn").click(onBatchSubmit);
});

/* Event functions */

function onBatchSelectorChange(event) {
    batchWorking();
    project = event.target.options[event.target.selectedIndex].value;
    $("#shotgridUrl, #shotgridScriptName, #shotgridApiKey, #shotgridProjectId, #shotgridFieldMapping").val("");

    if (project != "#new") {
        window.pywebview.api.getProjectBatchInfos(project).then((infos) => {
            $("#shotgridUrl").val(infos.url);
            $("#shotgridScriptName").val(infos.script_name);
            $("#shotgridApiKey").val(infos.api_key);
            $("#shotgridProjectId").val(infos.project_id);
            $("#shotgridFieldMapping").val(JSON.stringify(infos.fields_mapping, null, 5));
        });
    }
    batchEndWorking();
}

function onBatchSubmit(event) {
    batchWorking();

    if (checkBatchValues()) {
        console.log('OK');
    } else {
        console.log('KO');
        printWarning("Could not run batch with those settings");

    }

    batchEndWorking();
}

/* Functions */

function fillProjectsSelector(projectList) {
    batchSelector = document.getElementById('selectOpenPypeProject');
    ScheduleSelector = document.getElementById('selectOpenPypeProjectSchedule');

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

    val = {
        'project': $("#selectOpenPypeProject").val(),
        'url': $("#shotgridUrl").val(),
        'script_name': $("#shotgridScriptName").val(),
        'api_key': $("#shotgridApiKey").val(),
        'project_id': $("#shotgridProjectId").val(),
    }
    window.pywebview.api.checkProjectSettings(val).then((result) => {
        return result
    });
}

/* util */

function batchWorking() {
    spinner = document.createElement("span");
    spinner.setAttribute('class', "spinner-border spinner-border-sm");
    spinner.setAttribute('role', "status");
    spinner.setAttribute('aria-hidden', "true");
    $("#batchBtn").attr("disabled");
    $("#batchBtn").html(spinner);
}

function batchEndWorking() {
    $("#batchBtn").attr("enabled");
    $("#batchBtn").html("Batch");
}

function printWarning(msg) {
    printMsg('warning', msg)
}

function printError(msg) {
    printMsg('critical', msg)
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

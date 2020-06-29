$(window).on("load", function(){
    $("table tr").each(function(){
        var checkbox = $(this).find("input[type=checkbox]");
        var status = $(this).find("td:eq(8)");
        if (status.text() == "队列") {
            checkbox.attr("disabled","disabled");
            // status.css("color", "#333333");
        } else if (status.text() == "执行") {
            checkbox.attr("disabled","disabled");
            // status.css("color", "#0099CC");
        } else if (status.text() == "完成") {
            checkbox.attr("checked", false);
            // status.css("color", "#4CCEAC");
        } else if (status.text() == "空闲") {
            checkbox.attr("checked", true);
            // status.css("color", "#CCCCFF")
        }
    });
    if (message == "None"){
        return;
    }
    else {
        alert(message);
    }
});
function refresh(){
    location.reload(true);
}
function loadMoreTasks(){
    // 每次加载数量为3
    var tasksNumberWanted = showNumber + 3;
    var url = this.location.href;
    var query = this.location.search;
    // 如果已经存在&n=, 则将其删除
    if (url.indexOf("&n=") > 0) {
        url = url.substring(0, url.indexOf("&n"));
    }
    // 祼地址需要补充?
    if (query.startsWith("?") == false){
        url += "?"
    }
    url += "&n=" + tasksNumberWanted;
    window.location.replace(url);
}
var halfWindowHeight = $(window).height() / 2;
/****** 设置modal setExecuteTime 显示的坐标 ******/
function setModalHeight(modal, height){
    modal.css("display", "block");
    modal.find(".modal-dialog").css({
    "margin-top": height,
    });
}
$("#setExecuteTime").on("show.bs.modal", function(e){
    setModalHeight($(this), halfWindowHeight);
});
$("#showActivityLog").on("show.bs.modal", function(e){
    setModalHeight($(this), 100);
});
$("#editTask").on("show.bs.modal", function(e){
    setModalHeight($(this), halfWindowHeight);
});
$("#uploadTestCasesButton").click(function(){
    var caseFile = $("#caseFile").val();
    if (caseFile == "") {
        alert("请选择测试用例文件!!!");
        return;
    } else if ((caseFile.slice(-4) == ".csv") != true) {
        alert("测试用例需以.csv结尾!!!");
        return;
    }
    var sentence = "  再次确认上传内容:\n  测试用例: " + caseFile;
    if (confirm(sentence)) {
        $("#uploadTestCasesForm").submit();
    }
});
$("#project").change(function(){
    $("#projects").submit();
});
function addTask(exectime){
    var server = $("#server").val()
    var project = $("#project").val();
    var platform = $("#platform").val();
    var app = $("#app").val();
    var file = $("#files").val();
    if (app == null) {
        alert("请选择测试包名!!!");
        return
    } else if (platform == null) {
        alert("请选择对应平台!!!");
        return;
    } else if (file == null) {
        alert("请选择对应测试用例!!!");
        return;
    }
    $.ajax({
        cache: false,
        url: "addtask/",
        dataType: "text",
        type: "POST",
        async: true,
        data: {
            "server": server,
            "project": project,
            "platform": platform,
            "package" : app,
            "casefile": file,
            "exectime": exectime,
        },
        success: function(data){
            if (confirm(JSON.parse(data))){
                location.reload(true);
            }
        }
    });
}
function resetTask(id){
    $.ajax({
        cache: false,
        url: "resettask/",
        dataType: "text",
        type: "POST",
        async: true,
        data: {
            "id": id
        },
        success: function(data){
            if (confirm(JSON.parse(data))) {
                location.reload(true);
            }
        }
    });
}
$("#addRealTimeTask").click(function(){
    addTask("early");
});
$("#addCrontab").click(function(){
    addTask($("#executeTime").val());
});
$("#removeTask").click(function(){
    var inputs = $("input[type=checkbox]")
    var ids = new Array();
    for (i=0; i<inputs.length; i++) {
        if (inputs[i].checked == true) {
            ids.push(inputs[i].id);
        }
    }
    if (ids.length == 0) {
        alert("至少选择1个任务!")
        return
    }
    $.ajax({
        cache: false,
        url: "removetask/",
        dataType: "text",
        type: "POST",
        async: true,
        data: {
            "ids": JSON.stringify(ids),
        },
        success: function(data){
            if (confirm(JSON.parse(data))){
                location.reload(true);
            }
        }
    })
});
$("#startTest").click(function(){
    var inputs = $("input[type=checkbox]")
    var ids = new Array();
    for (i=0; i<inputs.length; i++){
        if (inputs[i].checked == true){
            ids.push(inputs[i].id);
        }
    }
    $.ajax({
        cache: false,
        url: "execute/",
        dataType: 'text',
        type: 'POST',
        async: true,
        data: {
            "ids": JSON.stringify(ids),
        },
        success: function(data){
            if (confirm(JSON.parse(data))){
                location.reload(true);
            }
        }
    });
});
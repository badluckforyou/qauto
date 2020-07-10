function updateRequestBySize(requestDivSize) {
    if (requestDivSize > 500 && requestDivSize < 700) {
        $("#methods").css("width", "22%");
        $("#dataType").css("width", "22%");
        $("#targetUrl").css("width", "54%");
        $("#headerType").css("width", "33%");
        $("#headerBody").css("width", "65%");
        $("#startTest").html("Send");
        $("#setHeaders").html("Customize");
    } else if (requestDivSize <= 500) {
        $("#methods").css("width", "30%");
        $("#dataType").css("width", "30%");
        $("#targetUrl").css("width", "38%");
        $("#headerType").css("width", "40%");
        $("#headerBody").css("width", "58%");
        $("#startTest").html("Send");
        $("#setHeaders").html("Cust");
    } else {
        $("#methods").css("width", "15%");
        $("#dataType").css("width", "15%");
        $("#targetUrl").css("width", "69%");
        $("#headerType").css("width", "20%");
        $("#headerBody").css("width", "79%");
        $("#startTest").html("发送");
        $("#setHeaders").html("自定义");
    }
}
var result = "";
/****** 设置modal 显示的坐标 ******/
function setModalHeight(modal, height){
    modal.css("display", "block");
    modal.find(".modal-dialog").css({
      "margin-top": height,
    });
}
$("#requestHeaders").on("show.bs.modal", function(e){
    var modalHeight = $(this).height();
    var windowHeight = $(window).height();
    setModalHeight($(this), (modalHeight - windowHeight) / 2);
});
$("#details").on("show.bs.modal", function(e){
    var modalHeight = $(this).height();
    var windowHeight = $(window).height();
    setModalHeight($(this), (modalHeight - windowHeight) / 4);
});
$("#removeRandom").click(function(){
    $("#ramdomTimes").val("");
    $("#randomData").val("");
    $("#randomWrapper").css("display", "none");
    $("#randomTitle").css("display", "none");
});
$("#removeFull").click(function(){
    $("#fullTest").prop("checked", false);
    $("#fullData").val("");
    $("#fullWrapper").css("display", "none");
    $("#fullTitle").css("display", "none");
});
$("#clearHeaders").click(function(){
    $("#headers").val("");
});
$("#startTest").click(function(){
    var method = $("#methods").val();
    var dataType = $("#dataType").val();
    var targetUrl = $("#targetUrl").val();
    var requestData = $("#requestData").val();
    var sendType = "synchronous";
    if (targetUrl == "") {
        alert("请输入目标地址!")
        return
    }
    if ($("#headers").val() != "") {
        var headers = $("#headers").val();
    } else {
        var dict = {};
        dict[$("#headerType").val()] = $("#headerBody").val();
        var headers = JSON.stringify(dict);
    }
    if ($("#randomWrapper").css("display") == "none" || $("#randomTimes").val() == 0 || $("#randomTimes").val() == "") {
        var randomTimes = "";
        var randomData = "";
    } else {
        var randomTimes = $("#randomTimes").val();
        var randomData = $("#randomData").val();
        sendType = $("#sendType").val();
    }
    if ($("#fullTest").is(":checked")) {
        var fullData = $("#fullData").val();
        sendType = "asynchronous";
    } else {
        var fullData = "";
    }
    if (randomData != "" && fullData != "") {
        alert("两种测试互斥, 无法同时执行!");
        return
    }
    // 清空结果表
    $("#responseData").html("");
    // 清空跳转页签
    $("#tableSheet").html("");
    $.ajax({
        cache: false,
        url: "request/",
        dataType: 'text',
        type: 'POST',
        async: true,
        data: {
            "method": method,
            "url": targetUrl,
            "headers": headers,
            "data": requestData,
            "dataType": dataType,
            "sendType": sendType,
            "fullData": fullData,
            "randomData": randomData,
            "randomTimes": randomTimes,
        },
        success: function(data){
            if (data.substring(0, 1) != "[") {
                alert(JSON.parse(data));
                return
            }
            // 置为全局变量
            result = JSON.parse(data);
            // 默认显示第1页
            showRecv(result, 1);
        }
    });
});
/*** 根据后端返回的数据生成对应的结果表及跳转页签 ***/
function showRecv(data, thisPage){
    if ($("#fullWrapper").css("display") == "block" && $("#randomWrapper").css("display") == "block") {
        var splitIdent = 24;
    } else if ($("#fullWrapper").css("display") == "none" && $("#randomWrapper").css("display") == "none") {
        var splitIdent = 8;
    } else {
        var splitIdent = 16;
    }
    var totalPage = Math.floor(data.length / splitIdent);
    if (totalPage != (data.length / splitIdent)){
        totalPage += 1;
    }
    if (thisPage == 1 && thisPage == totalPage){
        var startIdent = 0;
        var endIdent = data.length;
        var tableSheet = `
            <span>First </span>&nbsp;|
            <span>Previous </span>&nbsp;|
            <span>Next </span>&nbsp;|
            <span>Last </span>&nbsp;|
            &nbsp;Page&nbsp;<span>` + thisPage + `</span>/<span>` + totalPage + `</span>`;
    } else if (thisPage == 1 && thisPage != totalPage){
        var startIdent = 0;
        var endIdent = splitIdent;
        var tableSheet = `
            <span>First </span>&nbsp;|
            <span>Previous </span>&nbsp;|
            <span><a href="javascript:void(0);" onclick="goPage(` + (thisPage + 1) + `)">Next </a></span>&nbsp;|
            <span><a href="javascript:void(0);" onclick="goPage(` + totalPage + `)">Last </a></span>&nbsp;|
            &nbsp;Page&nbsp;<span>` + thisPage + `</span>/<span>` + totalPage + `</span>`;
    } else if (thisPage != 1 && thisPage != totalPage){
        var startIdent = (thisPage - 1) * splitIdent;
        var endIdent = thisPage * splitIdent;
        var tableSheet = `
            <span><a href="javascript:void(0);" onclick="goPage(1)">First </a></span>&nbsp;|
            <span><a href="javascript:void(0);" onclick="goPage(` + (thisPage - 1) + `)">Previous </a></span>&nbsp;|
            <span><a href="javascript:void(0);" onclick="goPage(` + (thisPage + 1) + `)">Next </a></span>&nbsp;|
            <span><a href="javascript:void(0);" onclick="goPage(` + totalPage + `)">Last </a></span>&nbsp;|
            &nbsp;Page&nbsp;<span>` + thisPage + `</span>/<span>` + totalPage + `</span>`;
    } else if (thisPage != 1 && thisPage == totalPage){
        var startIdent = (thisPage - 1) * splitIdent;
        var endIdent = data.length;
        var tableSheet = `
            <span><a href="javascript:void(0);" onclick="goPage(1)">First </a></span>&nbsp;|
            <span><a href="javascript:void(0);" onclick="goPage(` + (thisPage - 1) + `)">Previous </a></span>&nbsp;|
            <span>Next </span>&nbsp;|
            <span>Last </span>&nbsp;|
            &nbsp;Page&nbsp;<span>` + thisPage + `</span>/<span>` + totalPage + `</span>`;
    }
    var htmlData = `
      <div class="table-responsive">
        <table class="table table-hover">
          <thead>
            <tr class="solid-header">
              <th style="width: 20%;">开始时间</th>
              <th style="width: 10%;">状态码</th>
              <th style="width: 10%;">耗时</th>
              <th style="width: 25%;">发送数据</th>
              <th style="width: 25%;">返回数据</th>
              <th style="width: 10%;"></th>
            </tr>
          </thead>
          <tbody>`;
    for (var i=startIdent; i<endIdent; i++){
        var sendData = data[i]["send_data"].toString().substring(0, 25)
        var recvDataFront = data[i]["recv_data"].substring(0, 1);
        if (recvDataFront != "[" && recvDataFront != "{") {
            var recvData = "一些string类型的数据";
        } else {
            var recvData = data[i]["recv_data"].toString().substring(0, 25);
        }
        htmlData += `
            <tr class="solid-header" id="` + i + `">
              <td>`+ data[i]["run_time"] + `</td>
              <td>`+ data[i]["status_code"] + `</td>
              <td>`+ data[i]["duration"] + `</td>
              <td>`+ sendData + ` ...</td>
              <td>`+ recvData + ` ...</td>
              <td><label class="badge badge-success" type="button" data-toggle="modal" data-target="#details" onclick="showMore(`+ i + `)">详细信息</label></td>
            </tr>`;
    }
    htmlData += `
          </tbody>
        </table>
      </div>`;
    // 生成结果表
    $("#responseData").html(htmlData);
    // 生成跳转页签
    $("#tableSheet").html(tableSheet);
    // staus code状态码颜色调整
    $("table tr").each(function(){
        var statusCode = $(this).find("td:eq(1)");
        if (statusCode.text() != 200){
            statusCode.css("color", "#f5003a");
        }
        else {
            statusCode.css("color", "#4CCEAC");
        }
    });
}
function showMore(i) {
    var sendData = JSON.stringify(JSON.parse(result[i]["send_data"]), null, 4);
    if (result[i]["recv_data"].substring(0, 1) == "{") {
        var recvData = JSON.stringify(JSON.parse(result[i]["recv_data"]), null, 4);
    } else {
        var recvData = result[i]["recv_data"];
    }
    $("#sendData").html(sendData);
    $("#recvData").val(recvData);
}
function goPage(page) {
    showRecv(result, page);
}
/****** 测试结果以csv文件形式下载 ******/
function downloadCsv(d) {
    var data = "开始时间,状态码,耗时,发送数据,返回数据\n";
    for (var i=0; i<result.length; i++){
        for (const k in result[i]) {
            data += result[i][k].toString().replace(/,/g, "&#44;") + ",";
        }
        data += "\n"
    }
    d.href = "data:text/csv;charset=utf-8," + encodeURIComponent(data);
}

$(function(){
    var requestDivSize = $("#request").width();
    updateRequestBySize(requestDivSize);
});
$(window).resize(function(){
    var requestDivSize = $("#request").width();
    updateRequestBySize(requestDivSize);
});
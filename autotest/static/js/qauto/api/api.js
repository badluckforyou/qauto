var halfWindowHeight = $(window).height() / 2;
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
$("#clearHeaders").click(function(){
    $("#headers").val("");
});
$("#startTest").click(function(){
    var method = $("#methods").val();
    var dataType = $("#dataType").val();
    var targetUrl = $("#targetUrl").val();
    var requestData = $("#requestData").val();
    if (targetUrl == ""){
        alert("请输入目标地址!")
        return
    }
    if ($("#headers").val() != ""){
        var headers = $("#headers").val();
    }
    else {
        var dict = {};
        dict[$("#headerType").val()] = $("#headerBody").val();
        var headers = JSON.stringify(dict);
    }
    if ($("#randomWrapper").css("display") == "block"){
        var randomTimes = $("#randomTimes").val();
        var randomData = $("#randomData").val();
    }
    else {
        var randomTimes = "";
        var randomData = "";
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
    var splitIdent = 18;
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
            &nbsp;Page&nbsp;<span>` + thisPage + `</span>/<span>` + totalPage + `</span>`
    }
    else if (thisPage == 1 && thisPage != totalPage){
        var startIdent = 0;
        var endIdent = splitIdent;
        var tableSheet = `
            <span>First </span>&nbsp;|
            <span>Previous </span>&nbsp;|
            <span><a href="javascript:void(0);" onclick="goPage(` + (thisPage + 1 ) + `)">Next </a></span>&nbsp;|
            <span><a href="javascript:void(0);" onclick="goPage(` + totalPage + `)">Last </a></span>&nbsp;|
            &nbsp;Page&nbsp;<span>` + thisPage + `</span>/<span>` + totalPage + `</span>`
    }
    else if (thisPage != 1 && thisPage != totalPage){
        var startIdent = (thisPage - 1) * splitIdent;
        var endIdent = thisPage * splitIdent;
        var tableSheet = `
            <span><a href="javascript:void(0);" onclick="goPage(1)">First </a></span>&nbsp;|
            <span><a href="javascript:void(0);" onclick="goPage(` + (thisPage - 1 ) + `)">Previous </a></span>&nbsp;|
            <span><a href="javascript:void(0);" onclick="goPage(` + (thisPage + 1 ) + `)">Next </a></span>&nbsp;|
            <span><a href="javascript:void(0);" onclick="goPage(` + totalPage + `)">Last </a></span>&nbsp;|
            &nbsp;Page&nbsp;<span>` + thisPage + `</span>/<span>` + totalPage + `</span>`
    }
    else if (thisPage != 1 && thisPage == totalPage){
        var startIdent = (thisPage - 1) * splitIdent;
        var endIdent = data.length;
        var tableSheet = `
            <span><a href="javascript:void(0);" onclick="goPage(1)">First </a></span>&nbsp;|
            <span><a href="javascript:void(0);" onclick="goPage(` + (thisPage - 1 ) + `)">Previous </a></span>&nbsp;|
            <span>Next </span>&nbsp;|
            <span>Last </span>&nbsp;|
            &nbsp;Page&nbsp;<span>` + thisPage + `</span>/<span>` + totalPage + `</span>`
    }
    var htmlData = `
        <table id="table" name="table" class="table table-hover table-sm">
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
        <tbody>`
    for (var i=startIdent; i<endIdent; i++){
        var sendData = data[i]["send_data"].toString().substring(0, 25)
        var recvDataFront = data[i]["recv_data"].substring(0, 1);
        if (recvDataFront != "[" && recvDataFront != "{") {
            var recvData = "似乎是一些string类型的数据";
        } else {
            var recvData = data[i]["recv_data"].toString().substring(0, 25);
        }
        htmlData += `
          <tr class="solid-header" id="` + i + `">
            <td style = "word-wrap:break-word;white-space:normal;">`+ data[i]["run_time"] + `</td>
            <td style = "word-wrap:break-word;white-space:normal;">`+ data[i]["status_code"] + `</td>
            <td style = "word-wrap:break-word;white-space:normal;">`+ data[i]["duration"] + `</td>
            <td style = "word-wrap:break-word;white-space:normal;">`+ sendData + ` ...</td>
            <td style = "word-wrap:break-word;white-space:normal;">`+ recvData + ` ...</td>
            <td><label class="badge badge-success" type="button" data-toggle="modal" data-target="#details" onclick="showMore(`+ i + `)">详细信息</label></td>
          </tr>`
    }
    htmlData += `
        </tbody>
        </table>`
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
function showMore(i){
    var sendData = JSON.stringify(JSON.parse(result[i]["send_data"]), null, 4);
    if (result[i]["recv_data"].substring(0, 1) == "{") {
        var recvData = JSON.stringify(JSON.parse(result[i]["recv_data"]), null, 4);
    } else {
        var recvData = result[i]["recv_data"];
    }
    $("#sendData").html(sendData);
    // $("#sendData").html(result[i]["send_data"]);
    $("#recvData").val(recvData);
}
function goPage(page){
    showRecv(result, page);
}
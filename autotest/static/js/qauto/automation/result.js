$(window).on("load", function(){
    $("table tr").each(function(){
        // 每列的测试结果都需要进行调色
        var fiveTd = $(this).find("td:eq(4)");
        if (fiveTd.text() == "失败"){
            fiveTd.css("color", "#f5003a");
        } else if (fiveTd.text() == "通过") {
            fiveTd.css("color", "#4CCEAC");
        }
        // 用例名的省略
        var caseName = $(this).find("td:eq(0)");
        caseName.attr("title", caseName.text());
        var length = caseName.text().length;
        if (length >= 30) {
            var front = caseName.text().substring(0, 25);
            var offside = caseName.text().substring(length - 5, length);
            var content = front + "&nbsp;&nbsp;...&nbsp;&nbsp;" + offside;
            caseName.html(content);
        }
        caseName.mouseover(function(){
            $(this).tooltip;
        });
    });
    $("#projects").change(function(){
        $("#projects").submit();
    });
    var total = success + failure;
    var percent = ((success / total) * 100).toFixed(1);
    // doughnut chart
    if ($("#doughnutChart").length) {
        var doughnutChartCanvas = $("#doughnutChart").get(0).getContext("2d");
        var doughnutData = {
            datasets: [{
                data: [success, failure],
                backgroundColor: ["#4CCEAC", "#f5003a"],
                borderColor: ["#4CCEAC", "#f5003a"],
                borderWidth: ["#4CCEAC", "#f5003a"]
            }],
            labels: [
                "通过",
                "失败",
            ],
        };
        var doughnutOptions = {
            responsive: true,
            showTooltips: false,
            cutoutPercentage: 40, //内部白色区域所占的百分比
            segmentShowStroke: false,
            animation: {
                animateScale: true, // doughnut chart动画从中心向外扩张
                animateRotate: true, // doughnut chart使用旋转动画
                onComplete: function(){
                    // console.log("😠 Please do not keep your mouse moving on the doughnut chart!!!");
                    // console.log("😊 If you don't, leave and let me alone ~~");
                }
            },
        };
        var doughnutChart = new Chart(doughnutChartCanvas, {
            type: "doughnut",
            data: doughnutData,
            options: doughnutOptions,
        });
        Chart.pluginService.register({
            beforeDraw: function(chart){
                var height = chart.chart.height;
                var width = chart.chart.width;
                var doughnut = chart.chart.ctx;
                doughnut.restore();
                // doughnutChartCanvas.font = fontsize + "em Verdana";
                doughnut.font = Chart.helpers.fontString(Chart.defaults.global.defaultFontSize, Chart.defaults.global.defaultFontStyle, Chart.defaults.global.defaultFontFamily)
                doughnut.textBaseline = "middle";

                var msg = "通过率";
                var msgWidth = doughnut.measureText(msg).width;
                var msgPosX = Math.round((width - msgWidth) / 2);
                var msgPosY = Math.round(height / 2 + 5);
                doughnut.fillText(msg, msgPosX, msgPosY);

                percent = percent + "%";
                if (total == 0){
                    percent = "0.00%";
                }
                var percentWidth = doughnut.measureText(percent).width;
                var percentPosX = Math.round((width - percentWidth) / 2);
                var percentPosY = Math.round(height / 2 + 25);
                doughnut.fillText(percent, percentPosX, percentPosY);
                doughnut.save();
            }
        });
    }
    if ($("#radial-chart").length) {
        data = {
            chart: {
                height: 360,
                type: "radialBar"
            },
            series: [percent],
            colors: ["#4CCEAC"],
            plotOptions: {
                radialBar: {
                    hollow: {
                        margin: 0,
                        size: "70%",
                        background: "rgba(255,255,255,0.1)"
                    },
                    track: {
                        dropShadow: {
                            enabled: !0,
                            top: 2,
                            left: 0,
                            blur: 4,
                            opacity: .02
                         }
                    },
                    dataLabels: {
                        name: {
                            offsetY: -10,
                            color: "#adb5bd",
                            fontSize: "15px"
                        },
                        value: {
                            offsetY: 5,
                            color: "#000000",
                            fontSize: "18px",
                            show: !0
                        }
                    }
                }
            },
            fill: {
                type: "gradient",
                gradient: {
                    shade: "dark",
                    type: "vertical",
                    gradientToColors: ["#87D4F9"],
                    stops: [0, 100]
                }
            },
            stroke: {
                lineCap: "round"
            },
            labels: ["Pass Rate"]
        };
        (r = new ApexCharts(document.querySelector("#radial-chart"), data)).render()
    }
    $("#totalNum").html(total);
    $("#successNum").html(success);
    $("#failNum").html(failure);
});
function getResultOfProject(project){
    location.replace("/automation/result/?project=" + project);
}
function getAllResult(){
    location.replace("/automation/result/");
}
function getResultOfDate(project, date){
    location.replace("/automation/result/?project=" + project + "&date=" + date);
}
/****** 跳转到新的页面 ******/
function goToNewHtml(game, report){
    window.open("/report/?game=" + game + "&report=" + report, "_blank");
}
function setModalHeight(modal, height){
    modal.css("display", "block");
    modal.find(".modal-dialog").css({
        "margin-top": height,
    });
}
var halfWindowHeight = $(window).height() / 2;
/****** 设置modal newUrl 显示的坐标 ******/
$("#newUrl").on("show.bs.modal", function(e){
    setModalHeight($(this), halfWindowHeight)
});
/****** 设置modal log 显示的坐标 ******/
$("#log").on("show.bs.modal", function(e){
    setModalHeight($(this), halfWindowHeight)
});
/****** 设置modal log 显示的内容 ******/
function showLog(log){
    $("#logMessage").html(log.replace(/"/g, ""));
    $("#log").on("show.bs.modal", function(e){
        var modalHeight = $(this).find(".modal-dialog").height();
        var windowHeight = $(window).height();
        if (modalHeight < windowHeight) {
            setModalHeight($(this), (windowHeight - modalHeight) / 2);
        } else {
            setModalHeight($(this), 100);
        }
    });
}
/****** 设置modal report 显示的坐标 ******/
$("#report").on("show.bs.modal", function(e){
    setModalHeight($(this), 150)
});
/****** 设置modal report 显示的内容 ******/
function showReport(report, image){
    $("#caseInfomation").html(report.replace(/"/g, ""));
    // image可能包含很多张图片, 因此需要进行切片检测
    var images = image.split(",");
    var imgsrc = "";
    for (const image of images) {
        imgsrc += '<img src="' + image +'" alt="图片无法显示" style="width: 100%; height: auto;">';
    }
    $("#screenshot").html(imgsrc);
    // $("#report").on("show.bs.modal", function(e){
    //   var modalHeight = $(this).find(".modal-dialog").height();
    //   var windowHeight = $(window).height();
    //   if (modalHeight < windowHeight) {
    //     setModalHeight($(this), (windowHeight - modalHeight) / 2)
    //   }
    // });
}
/****** 生成table的前后页等的跳转url ******/
function getNewHtml(page, keyWord){
    var url = this.location.search;
    var pageEqual = url.indexOf("&page=");
    if (pageEqual > 0) {
        url = url.replace(url.substring(pageEqual, url.length), "&page=" + page);
    } else {
        url += '&project=' + project + '&page=' + page
    }
    var newHtml = '<a href="' + url + '">' + keyWord + ' </a>';
    return newHtml
}
$("#firstPage").html(getNewHtml($("#firstPage").text(), "First"));
$("#previousPage").html(getNewHtml($("#previousPage").text(), "Previous"));
$("#nextPage").html(getNewHtml($("#nextPage").text(), "Next"));
$("#lastPage").html(getNewHtml($("#lastPage").text(), "Last"));
/****** 生成供他人查看自己用例的url ******/
function generateUrl(){
    var scheme = this.location.protocol;
    var host   = this.location.host;
    var path   = this.location.pathname;
    var query  = this.location.search;
    if (query == "") {
        var newQuery = "&project=" + $("#project").val() + "&page=" + $("#thisPage").html();
    } else if (query.indexOf("&time=") > 0) {
        var newQuery = query.substring(0, query.indexOf("&time=")) + "&page=" + $("#thisPage").html();
    } else if (query.indexOf("&time=") == -1 && query.indexOf("&csrfmiddlewaretoken=") > 0) {
        var newQuery = query.substring(0, query.indexOf("&csrfmiddlewaretoken=")) + "&page=" + $("#thisPage").html();
    } else if (query.indexOf("&time=") > 0) {
        var newQuery = query + "&page=" + $("#thisPage").html();
    } else {
        var newQuery = query;
    }
    var finalQuery = newQuery.substring(newQuery.indexOf("&project"), newQuery.length);
    var url = scheme + "//" + host + path + "?u=" + username + "&" + finalQuery.substring(1, finalQuery.length)
    $("#url").html(url);
}
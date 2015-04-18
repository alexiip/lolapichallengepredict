//-----------------------------------------------------------------------------
//Name: script.js
//
//Author: Alexander Popov
//
//-----------------------------------------------------------------------------

$("#name").keyup(function(event){
    if(event.keyCode == 13){
        $("#submitButton").click();
    }
});
$("#submitButton").click(function(){
    var $btn = $("#submitButton").button('loading')
    $("#error").html('');
       
    getResults($btn);
   
});

function getResults(btn) {
    var name = $("#name").val();
     $.get("predict", {'name':''+name+''}, function(data,status,xhr){
        if(status == "success"){
            var win = false;
            var pct = 0;
            
            win = data.win;
            pct = data.pct;
            showGoogleChart(parseInt(pct*100));
            if (win == true)
                $("#result").html("<h2 class=\"text-success\"><strong>You should WIN this game!</strong></h2>");
            else
                $("#result").html("<h2 class=\"text-danger\"> <strong>You should LOOSE this game.</strong></h2>");
        }else{
            console.log("error submitting " + name);
        }
        btn.button('reset')
    })
    .fail(function(xhr, textStatus, errorThrown) {
        console.log(xhr.status)
        if (xhr.status == 404){
            showNotFound();
        }else if( xhr.status == 503){
            showRiotError();
        }else{
            showError();
        }
        btn.button('reset')
    });
}


function showGoogleChart(pct){
    //google.setOnLoadCallback(drawChart(pct));
    drawChart(pct);
    
}

function drawChart(pct){
    var data = google.visualization.arrayToDataTable([
      ['Label', 'Value'],
      ['Confidence', pct]
    ]);

    var options = {
      width: 800, height: 240,
      redFrom: 90, redTo: 100,
      yellowFrom:75, yellowTo: 90,
      minorTicks: 5
    };

    var d = document.getElementById('chart');
    var chart = new google.visualization.Gauge(document.getElementById('chart'));

    chart.draw(data, options);

}

function showNotFound() {
    var alert = "<br/><br/><div class=\"alert alert-danger alert-dismissible fade in\" role=\"alert\"> \
            <button type=\"button\" class=\"close\" data-dismiss=\"alert\"><span aria-hidden=\"true\">x</span> \
            <span class=\"sr-only\">Close</span></button> \
            <strong>Summoner not found in NA live game...</strong></div>";
    $("#error").html(alert);
}

function showError() {
    var alert = "<br/><br/><div class=\"alert alert-danger alert-dismissible fade in\" role=\"alert\"> \
                <button type=\"button\" class=\"close\" data-dismiss=\"alert\"><span aria-hidden=\"true\">x</span> \
                <span class=\"sr-only\">Close</span></button> \
                <strong>Internal Error :(</strong></div>";
    $("#error").html(alert);

}
function showRiotError() {
    var alert = "<br/><br/><div class=\"alert alert-danger alert-dismissible fade in\" role=\"alert\"> \
                <button type=\"button\" class=\"close\" data-dismiss=\"alert\"><span aria-hidden=\"true\">x</span> \
                <span class=\"sr-only\">Close</span></button> \
                <strong>Riot API Servers Down, Can't Get Latest Data</strong></div>";
    $("#error").html(alert);

}
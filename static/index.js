$(document).ready(function () {
  var url = "data/";
  $.get(url).then(function (data) {
    console.log(data);

    var options = {
      rows: ["movie_title"],
      cols: ["cinema_name"],
      vals: ["occupied_seats"],
      aggregatorName: "Integer Sum",
      rendererName: "Heatmap"
    };

    $("#output").pivotUI(data, options);
  });
});

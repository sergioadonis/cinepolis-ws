$(document).ready(function () {
  // var url = "data/";
  // $.get(url).then(function (data) {
  //   console.log(data);

  //   var options = {
  //     rows: ["movie_title"],
  //     cols: ["cinema_name"],
  //     vals: ["occupied_seats"],
  //     aggregatorName: "Integer Sum",
  //     rendererName: "Heatmap"
  //   };

  //   $("#output").pivotUI(data.query_result, options);
  //   $("#title").text(data.title);
  // });

  var url = "get-pivots";
  $.get(url)
    .done(function (data) {
      console.log(data);
      var html = "";
      for (const pivot of data) {
        html += `
      <div class="my-5">
        <h4>${pivot.title}</h4>
        <p>${pivot.description}</p>
        <p><a href="admin/pivots/pivot/${pivot.id}/change">Admin edit</a> | <a href="explorer/${pivot.query_id}">Explorer edit</a></p>
        <div id="${pivot.id}"></div>
      </div>
    `;
      }

      $("#pivots").html(html);

      for (const pivot of data) {
        console.log(pivot.options);
        var options = { ...pivot.options, showUI: false };
        $(`#${pivot.id}`).pivotUI(pivot.query_result, options);
      }
    })
    .always(function () {
      $("#loading").hide();
    });
});

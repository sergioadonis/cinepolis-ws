$(document).ready(function () {

  var url = $('#get_pivot_data_by_id_url').val();

  $.get(url)
    .done(function (data) {
      console.log(data);
      var pivot = data;
      var options = { ...pivot.options, showUI: false };
      $('#pivot').pivotUI(pivot.query_result, options);

    })
    .always(function () {
      $("#loading").hide();
    });
});

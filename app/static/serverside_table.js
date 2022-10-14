/*jslint browser: true*/
/*global $*/


$(function() {
  $('#serverside_table').DataTable({
    bProcessing: true,
    bServerSide: true,
    sPaginationType: "full_numbers",
    lengthMenu: [[10, 25, 50, 100, 50], [10, 25, 50, 100, 50]],
    bjQueryUI: true,
    sAjaxSource: '/ssvision',
    columns: [
      {"data": "Column A"},
      {"data": "Column B"},
      {"data": "Column C"},
      {"data": "Column D"},
      {"data": "Column E"}
    ]
  });
});

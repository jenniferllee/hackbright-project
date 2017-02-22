
// Autocomplete dropdown medication names
var dropDownItems;

$.get('/drug-names.json', function (results) {
  dropDownItems = JSON.parse(results);

  $(function() {
  var drugNames = dropDownItems;
  $('#med-name').autocomplete({
  source: drugNames
});
});
});


    // <!-- JAVASCRIPT START -->
      function showEveryday() {
        if ($('#frequency').val() == 'everyday') {
          $('#everyday').show();
        }
        else {
          $('#everyday').hide();
        }}

      $('#frequency').on('change', showEveryday);

      function chooseEverydayTime() {
        var times_per_day = Number($('#etimes_per_day').val());
        var input_time_field = '<input type="time">';
        var input_remind_field_no = 'Set reminder? <input type="radio" value="no" checked>No';
        var input_remind_field_yes = '<input type="radio" value="yes">Yes';

        $('#everyday-time-input').empty();
        $('#everyday-remind-input').empty();

        for (var i=0; i<times_per_day; i++) {
          // var myDiv = document.createElement('div');

          $('#everyday-time-input').append(input_time_field);
          $('#everyday-time-input').children().last().attr("name", ("everyday-time-" + i));
          // $('#everyday-time-input').append('<br>')

          $('#everyday-time-input').append(input_remind_field_no);
          $('#everyday-time-input').children().last().attr("name", ("everyday-remind-" + i));

          $('#everyday-time-input').append(input_remind_field_yes);
          $('#everyday-time-input').children().last().attr("name", ("everyday-remind-" + i));

          $('#everyday-time-input').append('<br>');
        }}

      $('#etimes_per_day').bind('input', chooseEverydayTime);
    // <!-- JAVASCRIPT END -->
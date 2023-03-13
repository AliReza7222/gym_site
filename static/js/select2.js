$(document).ready(function() {
  $('.js-select2').select2({
    placeholder: 'Select Your Location',
    allowClear: true
  }).on('select2:open', function() {
    $('.select2-search__field').attr('placeholder', 'Search your location .....');
  });
});
function gym_delete(forloop_counter) {
  var result = confirm("Are you sure you want Delete Gym ?" );

  if (result) {
    var url = document.getElementById("delete_gym_" + forloop_counter).href;
    url = url + "?result=" + result;
    document.getElementById("delete_gym_" + forloop_counter).href = url;
    window.location.href = "{% url 'login' %}";
  }
}

function clear_gym(forloop_counter) {
  var result = confirm("Are you sure you want Remove all students from This Gym ?" );

  if (result) {
    var url = document.getElementById("clear_gym_" + forloop_counter).href;
    url = url + "?result=" + result;
    document.getElementById("clear_gym_" + forloop_counter).href = url;
    window.location.href = "";
  }
}

function remove_note(forloop_counter) {
  var result = confirm("Are you sure you want Delete This Notification ?" );

  if (result) {
    var url = document.getElementById("note_master_" + forloop_counter).href;
    url = url + "?result=" + result;
    document.getElementById("note_master_" + forloop_counter).href = url;
    window.location.href = "{% url 'login' %}";
  }
}
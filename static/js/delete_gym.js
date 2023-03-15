function gym_delete(forloop_counter) {
  var result = confirm("Are you sure you want Delete Gym ?" );

  if (result) {
    var url = document.getElementById("delete_gym_" + forloop_counter).href;
    url = url + "?result=" + result;
    document.getElementById("delete_gym_" + forloop_counter).href = url;
    window.location.href = "{% url 'login' %}";
  }
}


function remove_student(forloop_counter) {
  var result = confirm("Are you sure remove student ?" );

  if (result) {
    var url = document.getElementById("num_student_" + forloop_counter).href;
    url = url + "?result=" + result;
    document.getElementById("num_student_" + forloop_counter).href = url;
    window.location.href = "{% url 'login' %}";
  }
}
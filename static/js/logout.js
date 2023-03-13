function logout() {
  var result = confirm("Are you sure you want to log out?");

  if (result) {
    var url = document.getElementById("result-link").href;
    url = url + "?result=" + result;
    document.getElementById("result-link").href = url;
    window.location.href = "{% url 'login' %}";
  }
}


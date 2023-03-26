const myLinks = document.querySelectorAll('a.show-popup');
const overlay = document.querySelector('.overlay');
const confirmButton = document.querySelector('.confirm');
const cancelButton = document.querySelector('.cancel');

myLinks.forEach(function(myLink) {
    myLink.addEventListener('click', function(event) {
        event.preventDefault();
        overlay.style.display = 'block';
        const pk = this.getAttribute("data-pk");
        confirmButton.setAttribute("data-pk", pk);

        // load data based on the pk here
        const url = this.getAttribute("data-url");
        fetch(url)
            .then(response => response.json())
            .then(data => {
                document.querySelector('#tuition').innerHTML = data.monthly_tuition; // set monthly tuition fee
                document.querySelector('#gender').innerHTML = data.gender; // set gender
                document.querySelector('#working-hours-start').innerHTML = data.time_start_working; // set working hours start
                document.querySelector('#working-hours-end').innerHTML = data.time_end_working; // set working hours end
            })
            .catch(error => console.error(error));
    });
});

confirmButton.addEventListener('click', function() {
    overlay.style.display = 'none';
    const pk = this.getAttribute("data-pk");
    const url = "/register_gym/" + pk + '/';
    window.location.href = url;
});

cancelButton.addEventListener('click', function() {
    overlay.style.display = 'none';
});

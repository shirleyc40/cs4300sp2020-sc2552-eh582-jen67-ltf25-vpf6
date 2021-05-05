
$(document).ready(function () {
    let searchbtn1 = document.querySelector('#inputs #submit');
    let searchbtn2 = document.querySelector('.results-form #submit');
    if (searchbtn1 !== null && searchbtn1.innerHTML !== "Submit") {
        searchbtn1.innerHTML = 'Submit';
    }
    if (searchbtn2 !== null && searchbtn2.innerHTML !== "Submit") {
        searchbtn2.innerHTML = 'Submit';
    }
    const item_name = $('.item-name')

    $('.item-des').each(function (index) {
        let name = item_name[index].innerHTML.toLowerCase()
        var text = $(this).text().replace(`${name} :`, '').replace(/[0-9]/g, '');
        $(this).text(text);
    });
    item_name.each(function () {
        replaced = $(this).text().replace(/[0-9]/g, '').trim()
        replaced = replaced[0].toUpperCase() + replaced.slice(1)
        $(this).text(replaced)
    })
    $("div[data-rating]").each(function () {
        rating = $(this)[0].dataset.rating
        const starPercentage = ((rating / 5) + 0.005) * 100 + '%'
        $(this).width(starPercentage)
    });

    $(".global-search").on("submit", () => {
        if ($('#input1').val() !== "") {
            console.log("hi")
            searchbtn1.innerHTML = '<i class = "fa fa-circle-o-notch fa-spin"></i>  Please wait...';
        }
    })
    $(".results-form").on("submit", () => {
        if ($('#diet').val() !== "") {
            searchbtn2.innerHTML = '<i class = "fa fa-circle-o-notch fa-spin"></i>  Please wait...';
        }
    })
    $(".revform").submit(function(e) {
        e.preventDefault();
    });
})


function submitReview() {
    var xhttp2 = new XMLHttpRequest();
    xhttp2.open("POST", "https://bonappetit-final.herokuapp.com/review", true);
    //xhttp2.open("POST", "http://localhost:5000/review", true);
    xhttp2.setRequestHeader('Content-Type', 'application/json');
    var restaurant = document.getElementById("restaurantsInput").value;
    var restrictions = document.getElementById("restrictionsInput").value;
    var foodType = document.getElementById("foodTypeInput").value;
    // var stars = parseFloat(document.getElementById("starsInput").value);
    var stars = document.getElementsByName('stars');
    for (i = 0; i < stars.length; i++) {
        if (stars[i].checked)
            var star = parseFloat(stars[i].value);
    }
    if (restaurant !== '' && restrictions !== '') xhttp2.send('{"stars":' + star + ', "restrictions":"' + restrictions + '", "restaurant":"' + restaurant + '", "foodtype":"' + foodType + '"}');
    xhttp2.onreadystatechange = function () {
        if (xhttp2.readyState == 4) {
            $('.review-container').prepend("<div class='alert alert-success' role='alert'>Submitted! Thank you</div>")
            setTimeout(() => document.location.reload(), 2000);
        }
    }
    
}

// Basic autocomplete taken from https://www.w3schools.com/howto/howto_js_autocomplete.asp
function autocomplete(inp, arr) {
    const matchList = document.getElementById('rest-match');
    var currentFocus;
    /*execute a function when someone writes in the text field:*/
    inp.addEventListener("input", function (e) {
        var val = this.value
        currentFocus = -1;
        let matches = arr.filter(r => {
            const regex = new RegExp(`^${val}`, 'gi');
            return r.match(regex)
        })
        if (val.length === 0) {
            matches = []
            matchList.innerHTML = '';
            matchList.style.height = "0px"
        }
        if (matches.length > 0) {
            const maxPixels = matches.length * 46

            matchList.style.height = Math.min(maxPixels, 200) + 'px'
            const html = matches.map(m => `
                <div class = "match">
                    ${m}
                </div>
            `).join('');
            matchList.innerHTML = html;
            let b = document.getElementsByClassName("match")
            for (var i = 0; i < b.length; i++) {
                b[i].addEventListener('click', function (e) {
                    /*insert the value for the autocomplete text field:*/
                    inp.value = $(this)[0].innerText;
                    /*close the list of autocompleted values,
                    (or any other open lists of autocompleted values:*/
                    matchList.innerHTML = '';
                    matchList.style.height = "0px"
                });
            }
        } else { matchList.style.height = "0px" }
    });
    /*execute a function presses a key on the keyboard:*/
    inp.addEventListener("keydown", function (e) {
        var x = document.getElementsByClassName("match");
        if (e.keyCode == 40) {
            /*If the arrow DOWN key is pressed,
            increase the currentFocus variable:*/
            currentFocus++;
            /*and and make the current item more visible:*/
            addActive(x);
        } else if (e.keyCode == 38) { //up
            /*If the arrow UP key is pressed,
            decrease the currentFocus variable:*/
            currentFocus--;
            /*and and make the current item more visible:*/
            addActive(x);
        } else if (e.keyCode == 13) {
            /*If the ENTER key is pressed, prevent the form from being submitted,*/
            e.preventDefault();
            if (currentFocus > -1) {
                /*and simulate a click on the "active" item:*/
                if (x) x[currentFocus].click();
            }
        }
    });
    function addActive(x) {
        /*a function to classify an item as "active":*/
        if (!x) return false;
        /*start by removing the "active" class on all items:*/
        removeActive(x);
        if (currentFocus >= x.length) currentFocus = 0;
        if (currentFocus < 0) currentFocus = (x.length - 1);
        /*add class "autocomplete-active":*/
        x[currentFocus].classList.add("active");
        x[currentFocus].scrollIntoView()
    }
    function removeActive(x) {
        /*a function to remove the "active" class from all autocomplete items:*/
        for (var i = 0; i < x.length; i++) {
            x[i].classList.remove("active");
        }
    }
    /*execute a function when someone clicks in the document:*/
    document.addEventListener("click", function (e) {
        matchList.innerHTML = '';
        matchList.style.height = "0px";
    });

}



// index.js
document.addEventListener('DOMContentLoaded', function() {

    // Add touch event support
    document.querySelectorAll('.location-link').forEach(function(element) {
        element.addEventListener('touchstart', function() {
            populateList(element.textContent);
        });
    });

    if (typeof optionsMap !== 'undefined' && typeof selectedItinerary !== 'undefined') {
        if (selectedItinerary !== 'None') {
            populateList(selectedItinerary);
        }
    }
});

function changeBackgroundColor(searchText, hover) {
    // when hovered on an itinerary, change its background color
    var listItems = document.querySelectorAll('#itineraries a');

    for (var i = 0; i < listItems.length; i++) {
        var matchedListItem = listItems[i];
        if (matchedListItem.textContent.trim() === searchText) {
            matchedListItem.style.backgroundColor = '#8ac1ff';
        } else {
            matchedListItem.style.backgroundColor = '#85C1E9';
        }
    }
}

function populateList(option) {
    let selectedOption = option;
    changeBackgroundColor(selectedOption, true);

    var mylist = document.getElementById("mylist");
    mylist.innerHTML = "";

    if (selectedOption !== "") {
        let options = optionsMap[selectedOption];
        for (let i = 0; i < options.length; i++) {
            let listElement = document.createElement("li");
            let locationLink = document.createElement("a");
            locationLink.className = "location-link darker-blue";
            locationLink.textContent = options[i];
            locationLink.href = "/process_request/" + encodeURIComponent(selectedOption) + "/" + encodeURIComponent(options[i]);
            listElement.appendChild(locationLink);
            mylist.appendChild(listElement);
        }
    }
}

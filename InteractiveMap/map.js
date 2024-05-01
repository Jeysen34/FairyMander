// Get all path and circle elements
const elements = document.querySelectorAll("path, circle");

// Add event listeners to mouseover, mouseout, and mousemove
elements.forEach((element) => {
  element.addEventListener("mouseover", mouseOver);
  element.addEventListener("mouseout", mouseOut);
  element.addEventListener("mousemove", mouseMove);
});

// Function to handle mouseover event from state(s)
function mouseOver(e) {
  const infoBox = document.getElementById("state-box");
  infoBox.style.display = "block";
  infoBox.innerHTML = e.target.dataset.info;
}

// Function to handle mouseout event from state(s)
function mouseOut() {
  const infoBox = document.getElementById("state-box");
  infoBox.style.display = "none";
  // Reset the innerHTML of the infoBox
  infoBox.innerHTML = "";
}

// Function to handle mousemove event from state(s)
function mouseMove(e) {
  let x = e.pageX;
  let y = e.pageY;
  const infoBox = document.getElementById("state-box");
  infoBox.style.left = x - infoBox.offsetWidth / 2 + "px";
  infoBox.style.top = y - infoBox.offsetHeight - 20 + "px";

  /*
  infoBox.style.top = e.pageY + "px";
  infoBox.style.left = e.pageX + "px";
  */
}

// Add event listener to mousemove
document.addEventListener("mousemove", mouseMove);

// function for hamburger menu
function hamdropdownmenu(menu) {
  menu.classList.toggle("change");
  var menu = document.getElementById("menuItems");
  addEventListener("click", function () {
    menu.classList.toggle("show");
  });
  if (menu.style.display === "block") {
    menu.style.display = "none";
  } else {
    menu.style.display = "block";
  }
}

// sources:

// dropdown menu
// https://stackoverflow.com/questions/59759669/javascript-css-html-click-screen-to-make-dropdown-menu-disappear
// https://www.javatpoint.com/how-to-create-dropdown-list-using-javascript

// interacte map hover effect
// https://github.com/WebsiteBeaver/interactive-and-responsive-svg-map-of-us-states-capitals/blob/master/main.js
// https://www.w3schools.com/jsref/tryit.asp?filename=tryjsref_onmousemove

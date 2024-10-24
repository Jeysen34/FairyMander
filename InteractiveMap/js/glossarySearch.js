function myFunction() {
  // initialize variables
  var input, filter, table, tr, td, index, txtValue;
  // get the user inputed value
  input = document.getElementById("textInput");
  // convert the user inputed value to uppercase if needed
  filter = input.value.toUpperCase();
  // get the table
  table = document.getElementById("glossaryTable");
  // get all the rows in the table
  tr = table.getElementsByTagName("tr");
  // loop through all the rows and hide the ones that don't match the user inputed value
  for (index = 0; index < tr.length; index++) {
    td = tr[index].getElementsByTagName("td")[0];
    // if the row contains the user inputed value, display it
    if (td) {
      // display the row
      txtValue = td.textContent || td.innerText;
      // if the user inputed value is found in the row, display the row
      if (txtValue.toUpperCase().indexOf(filter) > -1) {
        // display the row
        tr[index].style.display = "";
      } else {
        // hide the row
        tr[index].style.display = "none";
      }
    }
  }
}

// source: https://www.w3schools.com/howto/tryit.asp?filename=tryhow_js_filter_table

function confirm_delete(fullname){
    var result = confirm("Are you sure you want to delete " + fullname + "?");
    if (result == true){
    } else {
        return false;
    }
}

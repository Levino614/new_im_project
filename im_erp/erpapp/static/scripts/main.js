function confirm_delete(fullname){
    var result = confirm("Are you sure you want to delete " + fullname + "?");
    if (result == true){
        console.log("wow: " + result);
    } else {
        console.log("Hello world! " + result);
        return false;
    }
}

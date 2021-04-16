$(function(){

    $(".dropdown-menu li a").click(function(){

      $("#dropdownMenuButton").text($(this).text());
      $("#dropdownMenuButton").val($(this).text());

   });

});
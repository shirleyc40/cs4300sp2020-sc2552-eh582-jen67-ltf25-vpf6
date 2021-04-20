
$(document).ready(() => {

    const item_name = $('.item-name')
    $('.item-des').each(function(index) {
        let name = item_name[index].innerHTML.toLowerCase()
        var text = $(this).text().replace(`${name} :`, '');
        $(this).text(text);
    })
})

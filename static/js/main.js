function notify(title, description, icon) {
    console.log(icon)
    if (icon == undefined) { icon = 'success' }
    Swal.fire({
      toast: true,
      icon: icon,
      title: title,
      text: description,
      animation: false,
      position: 'bottom',
      showConfirmButton: false,
      timer: 3000,
      timerProgressBar: true,
      didOpen: (toast) => {
        toast.addEventListener('mouseenter', Swal.stopTimer)
        toast.addEventListener('mouseleave', Swal.resumeTimer)
      }
    })
};

$(document).ready(function () {
      $('#execute').click(function () {
        console.log('click')
        $("#id_loader").show()
        $("#change_warehouse").hide()
          $.post({
            data: {'packages': $('#values').val(), 'prefix': $('#warehouse').val()},
            url: 'api/getpackages',
            error: function (response) {
              notify('Результат',response['responseJSON']['result'], icon='error');
              $("#id_loader").hide();
            },
            success: function(response){
              $("#id_loader").hide();
              resp = response
              console.log(resp)
              console.log(resp['result'])
              $('#result').val(resp['result'])
              notify('Результат',"Количество значений:"+response['count']);
            }
          });
      });
    })

$('#clean').click(function(){
    $('#result').val('')
})

$("#choose_wh").click(function(){
  $("#change_warehouse").show()
})
$("#cancel").click(function(){
  $("#change_warehouse").hide()
})
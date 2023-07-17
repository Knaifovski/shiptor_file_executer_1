OM_LOADED = false
VP_LOADED = false
VVP_LOADED = false
SMM_LOADED = false

MODAL_SUBMITS = document.querySelectorAll(".modal-block button[type='submit']")
FIRST_BUTTONS = document.querySelectorAll(".center-block button[type='button']")

function notify(title, description, icon) {
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


$('#clean').click(function(){
    $('#result').val('')
})

$("#choose_wh").click(function(){
  $("#change_warehouse").show()
  $("#modal-bg").show()
})
$(".modal-cancel").click(function(){
  $("#change_warehouse").hide()
  $("#OM_block").hide()
  $("#VVP_block").hide()
  $("#SMM_block").hide()
  $("#modal-bg").hide()
})



$(document).ready(function () {
  $('#execute').click(function () {
    $("#id_loader").show()
    $("#change_warehouse").hide()
      $.post({
        data: {'packages': $('#values').val(), 'prefix': $('#warehouse').val()},
        url: 'api/getpackages',
        error: function (response) {
          notify('Результат',response['responseJSON']['result'], icon='error');
          $("#id_loader").hide();
          $("#modal-bg").hide()
        },
        success: function(response){
          $("#id_loader").hide();
          $("#modal-bg").hide()
          resp = response
          $('#result').val(resp['result'])
          notify('Результат',"Количество значений:"+response['count']);
        }
      });
  });

  $('#MergeButton').click(function() {
    $("#id_loader").show()
    $.post({
      data: {'om': $('#OM_data').val(), 'vvp': $('#VVP_data').val(), 'smm': $('#SMM_data').val()},
      url: 'api/merge',
      error: function (response) {
        $("#id_loader").hide();
        notify('Результат',"err", icon='error');
      },
      success: function(response){
        $("#id_loader").hide();
        resp = response
        $('#result').val(resp['result'])
        notify('Результат',"Успех");
      }
    });
  })
})

$(MODAL_SUBMITS).each(function(evt,btn){
  $(btn).click(function(){
    if ($("#"+btn.id.replace("load","")+"data").val().length > 1){
      $("#"+btn.id.replace("load","")+"button").removeClass("btn-outline-secondary")
      $("#"+btn.id.replace("load","")+"button").addClass("btn-success")
      notify("Успех", "Данные загружены")
      $(".modal-cancel").click()
    }
    else{
      notify("Ошибка", "Данные не введены", "error")
    }
  })
})

$(FIRST_BUTTONS).each(function(evt,btn){
  $(btn).click(function(){
    $("#"+btn.id.replace("button","")+"block").show()
    $("#modal-bg").show()
  })
})


// $("#OM_button").click(function(){
//   $("#OM_block").show()
//   $("#modal-bg").show()
// })
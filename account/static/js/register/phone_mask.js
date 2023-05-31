// var phoneInput = document.getElementById('phone');
// var myForm = document.forms.myForm;
// var result = document.getElementById('result');  // only for debugging purposes
//
// phoneInput.addEventListener('input', function (e) {
//   var x = e.target.value.replace(/\D/g, '').match(/(\d{0,3})(\d{0,3})(\d{0,4})/);
//   e.target.value = !x[2] ? x[1] : '(' + x[1] + ') ' + x[2] + (x[3] ? '-' + x[3] : '');
// });
//


// django viewdan template olish fetch api orqali
// {#get_form.addEventListener('click', (e) => {#}
// {#    e.preventDefault()#}
// {#    data = {'ok': 'status'}#}
// {#    options = {#}
// {#        method: 'POST',#}
// {#        headers: {#}
// {#            'Content-Type': 'text/html'#}
// {#        },#}
// {#        body: JSON.stringify(data)#}
// {#    }#}
// {#    fetch(url, options).then(response => response.text())#}
// {#        .then((data) => {#}
// {#            form.innerHTML += data#}
// {#        })#}
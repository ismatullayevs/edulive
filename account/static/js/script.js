"use strict"

// function cheak(number) {
//     if (!(isNaN(number)) && number.length == 13) {
//         return true
//     } else {
//         return false
//     }
// }


let form = document.getElementById('form')
let sms_btn = document.getElementById('sms_button')
let phone_number = document.getElementById('phone_number')
let submit = document.getElementById('submit')

let timerBox = document.getElementById('timer_box')
let timer

const activateTimer = (time) => {

    if (time.toString().length < 2) {
        sms_btn.innerHTML = `<code>0${time}:00</code>`
    } else {
        sms_btn.innerHTML = `<code>${time}:00</code>`
    }

    let minutes = time - 1
    let seconds = 60
    let displaySeconds
    let displayMinutes

    timer = setInterval(() => {
        sms_btn.setAttribute('disabled', '')
        seconds--
        if (seconds < 0) {
            seconds = 59
            minutes--
        }
        if (minutes.toString().length < 2) {
            displayMinutes = '0' + minutes
        } else {
            displayMinutes = minutes
        }
        if (seconds.toString().length < 2) {
            displaySeconds = '0' + seconds
        } else {
            displaySeconds = seconds
        }

        if (minutes === 0 && seconds === 0) {
            setTimeout(() => {
                clearInterval(timer)
                sms_btn.removeAttribute('disabled')
                sms_btn.innerHTML = 'send sms'
            })

        }
        sms_btn.innerHTML = `<code>${displayMinutes}:${displaySeconds}</code>`
    }, 1000)
}


phone_number.addEventListener('input', (e) => {
    let elem = e.target
    // str = elem.value
    console.log(elem.value.length)
    let x = elem.value.replace(/\D/g, '').match(/(\d{0,2})(\d{0,3})(\d{0,4})/)
    elem.value = !x[2] ? x[1] : '(' + x[1] + ') ' + x[2] + (x[3] ? '-' + x[3] : '')

    if (elem.value.length === 13) {
        sms_btn.removeAttribute('disabled')
    } else {
        sms_btn.setAttribute('disabled', '')
    }

})

function regex_number(number) {
    const replaced = number.value.replace(/\D/g, '');
    return parseInt(replaced)
}


sms_btn.addEventListener('click', (e) => {
    let phone = regex_number(phone_number)
    if (phone) {

        let options = {
            method: 'POST',
            mode: 'same-origin',
            cache: 'no-cache',

            headers: {
                'X-CSRFToken': csrftoken,
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({'phone': phone})

        }


        fetch(url, options)
            .then((response) => response.json())

            .then((data) => {
                // activateTimer(2)
                console.log(data)
            })


            .catch(error => {
                console.log('error')
            })
    } else {
        alert('notogri')
    }

})


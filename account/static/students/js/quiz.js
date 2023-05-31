const url = window.location.href
const quizBox = document.getElementById('quiz-box')
const scoreBox = document.getElementById('score-box')
const resultBox = document.getElementById('result-box')
const timerBox = document.getElementById('timer-box')
const quizForm = document.getElementById('quiz-form')
const csrf = document.getElementsByName('csrfmiddlewaretoken')

let timer

const activateTimer = (time) => {

    if (time.toString().length < 2) {
        timerBox.innerHTML = `<b>0${time}:00</b>`
    } else {
        timerBox.innerHTML = `<b>${time}:00</b>`
    }

    let minutes = time - 1
    let seconds = 60
    let displaySeconds
    let displayMinutes

    timer = setInterval(() => {
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
            timerBox.innerHTML = "<b>00:00</b>"
            setTimeout(() => {
                clearInterval(timer)
                alert('Time ower')
                sendDate()
            })

        }
        timerBox.innerHTML = `<b>${displayMinutes}:${displaySeconds}</b>`
    }, 1000)
}

$.ajax({
    type: 'GET',
    url: `${url}data`,
    success: function (response) {
        const data = response.data
        let sum = 0
        data.forEach(el => {
            for (const [question, answers] of Object.entries(el)) {
                sum++
                quizBox.innerHTML += `
                    <hr>
                    <div class="mb-2">
                        <b>${sum})${question}</b>
                    </div>
                `

                answers.forEach(answer => {
                    quizBox.innerHTML += `
                        <div class="p-2">
                            <input type="radio" class="ans" id="${sum}" name="${question}" value="${answer}" >
                            <label class="mx-2" for="${question}">${answer}</label>
                        </div>
                        
                    `
                })
            }
        })
        activateTimer(response.time)
    },


    error: function (error) {
        console.log(error, 'bu error')
    },
})

const sendDate = () => {
    const elements = [...document.getElementsByClassName('ans')]
    clearTimeout(timer)

    const data = {}
    data['csrfmiddlewaretoken'] = csrf[0].value
    elements.forEach(el => {
        if (el.checked) {
            data[el.name] = el.value
        } else {
            if (!data[el.name]) {
                data[el.name] = null
            }
        }
    })

    $.ajax({
        type: 'POST',
        url: `${url}save/`,
        data: data,
        success: function (response) {
            const results = response.results
            quizForm.classList.add('hidden')
            scoreBox.innerHTML = `${response.passed ? 'Tabriklaymiz' : 'Afsuskiy  ('} Sizning natijangiz ${response.score}%)`

            sum = 0
            results.forEach(res => {
                sum++
                const resDiv = document.createElement("div")
                for (const [question, resp] of Object.entries(res)) {

                    resDiv.innerHTML += sum + ')' + question
                    const cls = ['container', 'p-3', 'text-light', 'h5']
                    resDiv.classList.add(...cls)

                    if (resp === 'not answered') {
                        resDiv.innerHTML += 'javob berilmadi'
                        resDiv.classList.add('bg-danger')
                    } else {
                        const answer = resp['answered']
                        const correct = resp['correct_answer']

                        if (answer == correct) {
                            resDiv.classList.add('bg-success')
                            resDiv.innerHTML += ` javob: ${answer}`
                        } else {
                            resDiv.classList.add('bg-danger')
                            resDiv.innerHTML += ` | to'g'ri javob : ${correct}`
                            resDiv.innerHTML += ` | berilgan javob: ${answer}`
                        }

                    }

                }

                resultBox.append(resDiv)

            })
        },
        error: function (error) {
            console.log(error)
        }
    })
}

quizForm.addEventListener('submit', e => {
    e.preventDefault()
    sendDate()
})

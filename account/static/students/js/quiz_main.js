console.log('hello world')

const modalBtns = [...document.getElementsByClassName('modal-button')]
const modalBody = document.getElementById('modal-body-confirm')
const modalFooter = document.getElementById('modal-footer-confirm')
const startBtn = document.getElementById('start-button')
// modalBtns.forEach(modalBtn => modalBtn.addEventListener('click', ()+)

const url = window.location.href

modalBtns.forEach(modalBtn => modalBtn.addEventListener('click', () => {
    const pk = modalBtn.getAttribute('data-pk')
    const name = modalBtn.getAttribute('data-quiz')
    const numQuestions = modalBtn.getAttribute('data-questions')
    const difficulty = modalBtn.getAttribute('data-difficulty')
    const scoreToPass = modalBtn.getAttribute('data-pass')
    const time = modalBtn.getAttribute('data-time')
    const attempt = modalBtn.getAttribute('data-attempt')
    const score = modalBtn.getAttribute('data-score')
    let a = attempt.substr(0, 1) * 1
    console.log(score)
    if (a > 0 && a < 4) {
        modalBody.innerHTML = `
             <div class="h5 mb-3">
             <div class="text-center h3">Testni qayta topshirasizmi</div>
            <hr>
            <div class="text-muted">
                <ul class="flex flex-column gap-3">
                    <li><p>Siz ushbu testni avvalroq ${score} ball natija bilan topshirgansiz</b></p></li>
                    <li><p>Testni qaytadan topshirmoqchi bo'lsangiz <b>'Davom etish' </b> tugmasini bosing</p></li>
                    <li><p>Bunda oldingi natijangiz bekor qilinadi.Agar oldingi natijani saqlamoqchi bo'lsangiz <b>'Orqaga'</b> tugmasini bosing:</p></li>
                    <li><p>Sizning bu testda urinishlaringiz soni <b>${attempt} </b>marta</p></li>
                    <li><p>Sizda yana <b>${3 - attempt}</b> marta imkon qoldi</p></li>

                </ul>
            </div>
        </div>
        `
    } else {
        modalBody.innerHTML = `
        <div class="h5 mb-3">
            <b>"${name}"</b> testini boshlash
            <hr>
            <div class="text-muted">
                <ul class="flex flex-column gap-3">
                    <li>qiyinchiligi: <b>${difficulty}</b></li>
                    <li>savolloar soni: <b>${numQuestions}</b></li>
                    <li>o'tish bali: <b>${scoreToPass} ball</b></li>
                    <li>test yechish vaqti: <b>${time}</b> min</li>

                </ul>
            </div>
        </div>
    `
    }

    startBtn.addEventListener('click', () => {
        console.log(url)
        window.location.href = url + pk
    })
}))

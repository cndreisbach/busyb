/* globals fetch, Cookies */

function q (selector) {
  return document.querySelector(selector)
}

function qs (selector) {
  return document.querySelectorAll(selector)
}

document.addEventListener('DOMContentLoaded', function () {
  for (let form of qs('.mark-task-complete')) {
    form.addEventListener('submit', function (event) {
      event.preventDefault()
      const csrftoken = Cookies.get('csrftoken')

      fetch(form.action, {
        method: 'POST',
        headers: { 'X-CSRFToken': csrftoken, 'X-Requested-With': 'XMLHttpRequest' }
      })
        .then(response => {
          if (!response.ok) {
            throw Error(response.statusText)
          }
          q(`#task-${form.dataset['taskHashid']}`).remove()
        })
    })
  }
})

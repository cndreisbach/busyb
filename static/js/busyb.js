/* globals fetch, Cookies */

function q (selector) {
  return document.querySelector(selector)
}

function qs (selector) {
  return document.querySelectorAll(selector)
}

document.addEventListener('DOMContentLoaded', function () {
  const taskList = q('#task-list')
  taskList.addEventListener('submit', function (event) {
    if (event.target && event.target.nodeName === 'FORM' &&
      event.target.classList.contains('mark-task-complete')) {
      event.preventDefault()
      const form = event.target
      const csrftoken = Cookies.get('csrftoken')

      fetch(form.action, {
        method: 'POST',
        headers: { 'X-CSRFToken': csrftoken, 'X-Requested-With': 'XMLHttpRequest' }
      })
        .then(response => {
          if (!response.ok) {
            throw Error(response.statusText)
          }
          let task = q(`#task-${form.dataset['taskHashid']}`)
          task.remove()
        })
    }
  })

  const newTaskForm = q('#new-task-form')
  newTaskForm.addEventListener('submit', function (event) {
    event.preventDefault()
    const csrftoken = Cookies.get('csrftoken')

    let body = 'task='
    const taskField = q('#task-field')
    body += encodeURIComponent(taskField.value)
    taskField.value = ''

    fetch(newTaskForm.action, {
      method: 'POST',
      headers: {
        'X-CSRFToken': csrftoken,
        'X-Requested-With': 'XMLHttpRequest',
        'Content-Type': 'application/x-www-form-urlencoded'
      },
      body: body
    })
      .then(response => {
        if (!response.ok) {
          throw Error(response.statusText)
        }
        return response.text()
      })
      .then(text => {
        const taskFragment = document.createRange().createContextualFragment(text)
        q('#task-list').appendChild(taskFragment)
      })
  })
})

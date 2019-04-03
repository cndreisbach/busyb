const { q, htmlToNodes, checkElementTypeAndClass } = require('./utils')
const { markTaskComplete, toggleTaskNotes, request } = require('./actions')

document.addEventListener('DOMContentLoaded', function () {
  const taskList = q('#task-list')
  taskList.addEventListener('submit', function (event) {
    if (checkElementTypeAndClass(event.target, 'form', 'mark-task-complete')) {
      event.preventDefault()
      const form = event.target
      markTaskComplete(form.dataset['taskHashid'])
    }
  })

  taskList.addEventListener('click', function (event) {
    if (checkElementTypeAndClass(event.target, 'a', 'task-notes-link')) {
      event.preventDefault()
      toggleTaskNotes(event.target.dataset['taskHashid'])
    }
  })

  const newTaskForm = q('#new-task-form')
  newTaskForm.addEventListener('submit', function (event) {
    event.preventDefault()

    const taskField = q('#task-field')
    const body = {
      'task': taskField.value
    }
    taskField.value = ''

    request(newTaskForm.action, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(body)
    })
      .then(response => {
        if (!response.ok) {
          throw Error(response.statusText)
        }
        return response.text()
      })
      .then(text => {
        const taskFragment = htmlToNodes(text)
        q('#task-list').appendChild(taskFragment)
      })
  })
})

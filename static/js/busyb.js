/* globals fetch, Cookies */

function q (selector) {
  return document.querySelector(selector)
}

function qs (selector) {
  return document.querySelectorAll(selector)
}

function checkElementTypeAndClass (element, elementType, className) {
  return (element && element.nodeName === elementType.toUpperCase() &&
      (!className || element.classList.contains(className)))
}

function markTaskComplete (taskHashid) {
  const csrftoken = Cookies.get('csrftoken')

  fetch(`/tasks/{taskHashid}/complete/`, {
    method: 'POST',
    headers: { 'X-CSRFToken': csrftoken, 'X-Requested-With': 'XMLHttpRequest' }
  })
    .then(response => {
      if (!response.ok) {
        throw Error(response.statusText)
      }
      return response.json()
    })
    .then(function (responseData) {
      if (responseData.complete) {
        let task = q(`#task-${responseData.id}`)
        task.remove()
      }
    })
}

function toggleTaskNotes (taskHashid) {
  const taskNode = q(`#task-${taskHashid}`)
  const notesNode = taskNode.querySelector('.notes')

  if (notesNode) {
    taskNode.removeChild(notesNode)
    return
  }

  fetch(`/tasks/${taskHashid}/notes/`, {
    headers: { 'X-Requested-With': 'XMLHttpRequest' }
  })
    .then(response => response.json())
    .then(responseData => {
      const notesDiv = document.createElement('div')
      notesDiv.classList.add('notes')
      for (let note of responseData.notes) {
        let noteDiv = document.createElement('div')
        noteDiv.classList.add('mv2')
        noteDiv.id = `note-${note.id}`
        noteDiv.innerHTML = `<div>${note.text}</div><div>${note.created_at}</div>`
        notesDiv.appendChild(noteDiv)
      }

      taskNode.appendChild(notesDiv)
    })
}

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
    const csrftoken = Cookies.get('csrftoken')

    const taskField = q('#task-field')
    const body = {
      'task': taskField.value
    }
    taskField.value = ''

    fetch(newTaskForm.action, {
      method: 'POST',
      headers: {
        'X-CSRFToken': csrftoken,
        'X-Requested-With': 'XMLHttpRequest',
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
        const taskFragment = document.createRange().createContextualFragment(text)
        q('#task-list').appendChild(taskFragment)
      })
  })
})

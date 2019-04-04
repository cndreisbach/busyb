/* globals fetch */

const Cookies = require('js-cookie')
const deepmerge = require('deepmerge')
const { q } = require('./utils')

function request (url, options) {
  if (!options) {
    options = {}
  }
  const defaultOptions = {
    headers: { 'X-CSRFToken': Cookies.get('csrftoken'), 'X-Requested-With': 'XMLHttpRequest' }
  }

  return fetch(url, deepmerge(defaultOptions, options))
}

function markTaskComplete (taskHashid) {
  request(`/tasks/${taskHashid}/complete/`, { method: 'POST' })
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

  request(`/tasks/${taskHashid}/notes/`)
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

module.exports = {
  toggleTaskNotes: toggleTaskNotes,
  markTaskComplete: markTaskComplete,
  request: request
}

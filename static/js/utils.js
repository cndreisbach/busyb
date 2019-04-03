function htmlToNodes (htmlString) {
  return document.createRange().createContextualFragment(htmlString)
}

function q (selector) {
  return document.querySelector(selector)
}

function checkElementTypeAndClass (element, elementType, className) {
  return (element && element.nodeName === elementType.toUpperCase() &&
            (!className || element.classList.contains(className)))
}

module.exports = {
  htmlToNodes: htmlToNodes,
  q: q,
  checkElementTypeAndClass: checkElementTypeAndClass
}

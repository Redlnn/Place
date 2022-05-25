const canvas = document.getElementById('canvas')
const ctx = canvas.getContext('2d')
const rate = document.getElementById('rate')
const positon = document.getElementById('positon')

const imageObject = new Image()
const websocket = new WebSocket(`ws://${window.location.host}/ws`)

let loaded = false
let leaving = false
let lastZoom = 1
let currentZoom = 1
let placeOffset = {
    x: 0,
    y: 0,
}
let mouseDown = false
let mousePositon = {
    x: 0,
    y: 0,
}
canvas.focus()

ctx.imageSmoothingEnabled = false
ctx.mozImageSmoothingEnabled = false
ctx.webkitImageSmoothingEnabled = false
ctx.msImageSmoothingEnabled = false

const openTxtFile = function (event) {
    var input = event.target
    var reader = new FileReader()
    reader.onload = function () {
        if (reader.result) {
            console.log(input.files[0])
            loadImageFromTxt(reader.result)
        }
    }
    if (input.files[0]) reader.readAsText(input.files[0])
}

const loadImageFromTxt = function (txt) {
    txt = txt.replace(/\r\n/g, '\n')
    txt = txt.replace(/\r/g, '\n')
    txt = txt.replace(/,\n/g, '\n')
    txt = txt.replace(/#/g, '')
    txt = txt.trim()
    rows = txt.split('\n')
    let data = []
    for (let i = 0; i < rows.length; i++) {
        const cols = rows[i].split(',')
        for (let j = 0; j < cols.length; j++) {
            data.push(parseInt(cols[j].substring(0, 2), 16))
            data.push(parseInt(cols[j].substring(2, 4), 16))
            data.push(parseInt(cols[j].substring(4), 16))
            data.push(255)
        }
    }
    const tmpCanvas = document.createElement('canvas')
    tmpCanvas.width = 1280
    tmpCanvas.height = 720
    const tmpCtx = tmpCanvas.getContext('2d')
    const imgData = tmpCtx.createImageData(1280, 720)
    imgData.data.set(data)
    tmpCtx.putImageData(imgData, 0, 0)
    imageObject.src = tmpCanvas.toDataURL()
    ctx.clearRect(0, 0, 1280, 720)
    reDrawImage()
    loaded = true
}

const openImage = (event) => {
    var input = event.target
    var reader = new FileReader()
    reader.onload = () => {
        if (reader.result) {
            imageObject.src = reader.result
            reDrawImage()
            loaded = true
        }
    }
    if (input.files[0]) reader.readAsDataURL(input.files[0])
}

const getImage = () => {
    imageObject.src = '/api/get_full_image'
    imageObject.onload = () => {
        reDrawImage()
        loaded = true
    }
    imageObject.onerror = () => alert('无法获取画布，可能是因为您频繁访问，请稍后再试')
}

const revisePlaceOffset = () => {
    placeOffset.x = placeOffset.x > 0 ? 0 : placeOffset.x
    placeOffset.y = placeOffset.y > 0 ? 0 : placeOffset.y
    placeOffset.x = placeOffset.x < 1280 - 1280 * currentZoom ? 1280 - 1280 * currentZoom : placeOffset.x
    placeOffset.y = placeOffset.y < 720 - 720 * currentZoom ? 720 - 720 * currentZoom : placeOffset.y
}

const reDrawImage = () => {
    revisePlaceOffset()
    if (currentZoom < 1) {
        lastZoom = 1
        currentZoom = 1
        placeOffset.x = 0
        placeOffset.y = 0
    }
    ctx.clearRect(0, 0, 1280, 720)
    ctx.setTransform(1, 0, 0, 1, placeOffset.x, placeOffset.y)
    ctx.scale(currentZoom, currentZoom)
    ctx.drawImage(imageObject, 0, 0)
}

canvas.onclick = () => {
    canvas.focus()
}
canvas.onwheel = (e) => {
    if (!loaded) return
    currentZoom = lastZoom + parseFloat((e.deltaY > 0 ? -1.5 : 1.5).toFixed(2))
    if (lastZoom >= 20 && currentZoom >= lastZoom) {
        currentZoom = lastZoom
        return
    }
    if (currentZoom < 1) {
        lastZoom = currentZoom = placeOffset.x = placeOffset.y = 1
        return
    }
    rate.innerHTML = currentZoom.toFixed(1) + 'x'
    placeOffset.x = e.offsetX - ((e.offsetX - placeOffset.x) * currentZoom) / lastZoom
    placeOffset.y = e.offsetY - ((e.offsetY - placeOffset.y) * currentZoom) / lastZoom
    lastZoom = currentZoom
    reDrawImage()
}
canvas.onmousedown = (e) => {
    if (!loaded) return
    mouseDown = true
    mousePositon.x = e.offsetX
    mousePositon.y = e.offsetY
}
canvas.onmouseup = () => {
    mouseDown = false
}
canvas.onmouseout = () => {
    mouseDown = false
}
// canvas.onmouseleave = (e) => {}
// canvas.onmouseover = (e) => {}
// canvas.onmouseenter = (e) => {}
canvas.onmousemove = (e) => {
    positon.innerHTML = `(x, y)<br />(${parseInt((e.offsetX - placeOffset.x) / currentZoom)}, ${parseInt(
        (e.offsetY - placeOffset.y) / currentZoom
    )})`
    if (!mouseDown || currentZoom === 1) return
    placeOffset.x = placeOffset.x - mousePositon.x + e.offsetX
    placeOffset.y = placeOffset.y - mousePositon.y + e.offsetY
    revisePlaceOffset()
    mousePositon.x = e.offsetX
    mousePositon.y = e.offsetY
    reDrawImage()
}

const rgb2hex = (r, g, b) => {
    return '#' + ((1 << 24) + (r << 16) + (g << 8) + b).toString(16).slice(1)
}

const bgColor2hex = (bgColor) => {
    const rgb = bgColor.match(/\d+/g)
    return rgb2hex(parseInt(rgb[0]), parseInt(rgb[1]), parseInt(rgb[2]))
}

Array.from(document.getElementsByClassName('color')).forEach((element) => {
    element.onmouseenter = (e) => {
        const popout = document.createElement('span')
        popout.className = 'popout'
        popout.innerHTML = bgColor2hex(element.style.backgroundColor)
        element.appendChild(popout)
    }
    element.onmouseleave = (e) => {
        element.removeChild(element.lastChild)
    }
    element.onmousedown = (e) => {
        navigator.clipboard.writeText(element.lastChild.innerHTML)
        element.lastChild.innerHTML = '已复制!'
        setTimeout(() => {
            element.lastChild.innerHTML = bgColor2hex(element.style.backgroundColor)
        }, 800)
    }
})

websocket.onopen = () => {
    console.log('websocket connected')
}
websocket.onmessage = (e) => {
    const data = JSON.parse(e.data)
    const tmpCanvas = document.createElement('canvas')
    tmpCanvas.width = 1280
    tmpCanvas.height = 720
    const tmpCtx = tmpCanvas.getContext('2d')
    tmpCtx.drawImage(imageObject, 0, 0)
    const imageData = tmpCtx.getImageData(0, 0, 1280, 720)
    const i = data['y'] * 1280 * 4 + data['x'] * 4
    imageData.data[i] = data['color'][0]
    imageData.data[i + 1] = data['color'][1]
    imageData.data[i + 2] = data['color'][2]
    console.log(imageData)
    console.log(i, i + 1, i + 2)
    console.log(data['color'], data['color'][0], data['color'][1], data['color'][2])
    tmpCtx.putImageData(imageData, 0, 0)
    imageObject.src = tmpCanvas.toDataURL()
    ctx.drawImage(imageObject, 0, 0)
}
websocket.onerror = () => {
    console.log('websocket error')
    websocket.close()
    alert('WebSocket 连接出错，无法实时更新画布，请刷新页面重试')
}
websocket.onclose = () => {
    console.log('websocket closed')
    if (!leaving) alert('WebSocket 连接已断开，无法实时更新画布，请刷新页面重试')
}
window.onbeforeunload = () => {
    leaving = true
    websocket.close()
}
